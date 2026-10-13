#!/usr/bin/env python3
"""Read-only media inventory; local SQLite search with evidence-aware annotations.

Examples:
  broll_index.py scan --root cinematic=/Volumes/MyDisk/cinematic --root friends=/Volumes/MyDisk/friends
  broll_index.py search aquarium --min-duration 3
  broll_index.py search kitchen --reviewed-only
  broll_index.py annotate ASSET_ID --tags 'kitchen,food' --description 'Food on a counter' --start 1 --end 4 --evidence /local/contact-sheet.jpg
  broll_index.py show ASSET_ID

Source directories are never written. No network calls. Legacy labels are hints,
not verified observations; sampled fingerprints are not proof of exact duplicates.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

VIDEO = {'.mp4', '.mov', '.mkv', '.mxf', '.avi', '.m4v', '.webm', '.mts', '.m2ts'}
AUDIO = {'.mp3', '.m4a', '.wav', '.aif', '.aiff', '.flac', '.aac', '.ogg'}
IMAGE = {'.jpg', '.jpeg', '.png', '.heic', '.tif', '.tiff', '.webp'}
SCHEMA = '''
CREATE TABLE IF NOT EXISTS roots(alias TEXT PRIMARY KEY,path TEXT NOT NULL,last_scan REAL,online INTEGER);
CREATE TABLE IF NOT EXISTS files(
 asset_id TEXT PRIMARY KEY,root_alias TEXT NOT NULL,relative_path TEXT NOT NULL,
 size INTEGER,mtime_ns INTEGER,device INTEGER,inode INTEGER,kind TEXT,role TEXT,
 online INTEGER NOT NULL DEFAULT 1,last_seen REAL,probe_status TEXT,probe_error TEXT,
 duration REAL,width INTEGER,height INTEGER,fps REAL,rotation REAL,color_json TEXT,
 audio_json TEXT,probe_json TEXT,fingerprint TEXT,sha256 TEXT,
 review_status TEXT NOT NULL DEFAULT 'unreviewed',
 UNIQUE(root_alias,relative_path));
CREATE TABLE IF NOT EXISTS annotations(
 annotation_id TEXT PRIMARY KEY,asset_id TEXT NOT NULL,source TEXT NOT NULL,
 tags_json TEXT,description TEXT,scene TEXT,motion TEXT,start REAL,end REAL,
 evidence TEXT,created_at REAL,source_json TEXT);
CREATE INDEX IF NOT EXISTS annotations_asset ON annotations(asset_id);
CREATE TABLE IF NOT EXISTS issues(root_alias TEXT,path TEXT,error TEXT,created_at REAL);
'''


def connect(catalog):
    catalog = Path(catalog).expanduser()
    catalog.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(catalog / 'catalog.sqlite')
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    db.execute('PRAGMA journal_mode=WAL')
    return db


def asset_id(alias, relative):
    return hashlib.sha256((alias + '\0' + relative).encode()).hexdigest()[:24]


def classify(relative):
    p = Path(relative)
    if p.name.startswith('._'):
        return 'support', 'appledouble'
    if '.broll_cache' in p.parts:
        return 'support', 'cache'
    if any(x.startswith('.') for x in p.parts):
        return 'support', 'hidden'
    suffix = p.suffix.lower()
    kind = 'video' if suffix in VIDEO else 'audio' if suffix in AUDIO else 'image' if suffix in IMAGE else 'other'
    return kind, 'media' if kind != 'other' else 'support'


def sampled_fingerprint(path, size):
    h = hashlib.sha256(str(size).encode() + b'\0')
    block = 65536
    with open(path, 'rb') as f:
        for offset in sorted({0, max(0, size // 2 - block // 2), max(0, size - block)}):
            f.seek(offset)
            h.update(str(offset).encode() + b'\0' + f.read(block))
    return h.hexdigest()


def fraction(value):
    try:
        a, b = value.split('/')
        return float(a) / float(b) if float(b) else None
    except (ValueError, AttributeError, ZeroDivisionError):
        return None


def probe(path, timeout):
    try:
        out = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)],
                             capture_output=True, text=True, timeout=timeout, check=True)
        raw = json.loads(out.stdout)
        video = next((s for s in raw.get('streams', []) if s.get('codec_type') == 'video'), {})
        audio = [dict((k, s.get(k)) for k in ('codec_name', 'sample_rate', 'channels', 'channel_layout', 'duration'))
                 for s in raw.get('streams', []) if s.get('codec_type') == 'audio']
        rotation = video.get('tags', {}).get('rotate')
        for side in video.get('side_data_list', []):
            if 'rotation' in side:
                rotation = side['rotation']
        dur = raw.get('format', {}).get('duration', video.get('duration'))
        return dict(probe_status='ok', probe_error=None, duration=float(dur) if dur is not None else None,
                    width=video.get('width'), height=video.get('height'),
                    fps=fraction(video.get('avg_frame_rate')) or fraction(video.get('r_frame_rate')),
                    rotation=float(rotation) if rotation is not None else 0,
                    color_json=json.dumps({k: video.get(k) for k in ('pix_fmt', 'color_range', 'color_space', 'color_transfer', 'color_primaries')}),
                    audio_json=json.dumps(audio), probe_json=json.dumps(raw))
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        detail = getattr(e, 'stderr', None) or str(e)
        return dict(probe_status='failed', probe_error=str(detail)[:2000])


def inspect(item, timeout):
    path, size, aid = item
    result = probe(path, timeout)
    try:
        result['fingerprint'] = sampled_fingerprint(path, size)
    except OSError as e:
        result['probe_error'] = (result.get('probe_error') or '') + ' fingerprint: ' + str(e)
    return aid, result


def update(db, aid, values):
    db.execute('UPDATE files SET ' + ','.join(k + '=?' for k in values) + ' WHERE asset_id=?', list(values.values()) + [aid])


def parse_root(spec):
    alias, sep, path = spec.partition('=')
    if not sep or not alias or not path:
        raise ValueError('roots must be ALIAS=/absolute/path')
    return alias, str(Path(path).expanduser().absolute())


def scan(db, args):
    roots = dict(parse_root(s) for s in (args.root or []))
    if not roots:
        roots = dict(db.execute('SELECT alias,path FROM roots'))
    if not roots:
        raise ValueError('No roots configured. Supply --root ALIAS=/path at first scan.')
    catalog_path = Path(args.catalog).expanduser().resolve()
    for path in roots.values():
        source_path = Path(path).resolve()
        if catalog_path == source_path or source_path in catalog_path.parents:
            raise ValueError('Catalog must be outside source roots; source directories are read-only.')
    now = time.time()
    jobs = []
    for alias, path in roots.items():
        root = Path(path)
        exists = root.is_dir()
        db.execute('INSERT INTO roots VALUES(?,?,?,?) ON CONFLICT(alias) DO UPDATE SET path=excluded.path,last_scan=excluded.last_scan,online=excluded.online',
                   (alias, path, now, int(exists)))
        db.execute('UPDATE files SET online=0 WHERE root_alias=?', (alias,))
        db.execute('DELETE FROM issues WHERE root_alias=?', (alias,))
        if not exists:
            db.execute('INSERT INTO issues VALUES(?,?,?,?)', (alias, path, 'Root offline or unavailable', now))
            continue
        def onerror(error):
            db.execute('INSERT INTO issues VALUES(?,?,?,?)', (alias, error.filename, str(error), now))
        for directory, dirs, names in os.walk(root, onerror=onerror, followlinks=False):
            # Never follow source symlinks outside the two authorized scopes.
            dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
            for name in sorted(names):
                p = Path(directory) / name
                relative = str(p.relative_to(root))
                aid = asset_id(alias, relative)
                try:
                    stat = p.lstat()
                except OSError as e:
                    db.execute('INSERT INTO issues VALUES(?,?,?,?)', (alias, str(p), str(e), now))
                    continue
                kind, role = ('support', 'symlink') if p.is_symlink() else classify(relative)
                old = db.execute('SELECT * FROM files WHERE asset_id=?', (aid,)).fetchone()
                changed = not old or old['size'] != stat.st_size or old['mtime_ns'] != stat.st_mtime_ns
                db.execute('''INSERT INTO files(asset_id,root_alias,relative_path,size,mtime_ns,device,inode,kind,role,online,last_seen,probe_status)
                           VALUES(?,?,?,?,?,?,?,?,?,1,?,?) ON CONFLICT(asset_id) DO UPDATE SET
                           size=excluded.size,mtime_ns=excluded.mtime_ns,device=excluded.device,inode=excluded.inode,
                           kind=excluded.kind,role=excluded.role,online=1,last_seen=excluded.last_seen''',
                           (aid,alias,relative,stat.st_size,stat.st_mtime_ns,stat.st_dev,stat.st_ino,kind,role,now,'pending' if role == 'media' else 'not_applicable'))
                if changed:
                    update(db, aid, dict(probe_status='pending' if role == 'media' else 'not_applicable',
                        probe_error=None,duration=None,width=None,height=None,fps=None,rotation=None,color_json=None,
                        audio_json=None,probe_json=None,fingerprint=None,sha256=None,review_status='unreviewed'))
                    if old:
                        # Annotations describe the previous bytes; never silently reuse them after change.
                        db.execute('DELETE FROM annotations WHERE asset_id=?', (aid,))
                if role == 'media' and (changed or old['probe_status'] in ('pending', 'failed') or args.reprobe):
                    jobs.append((str(p),stat.st_size,aid))
        db.commit()
    print(json.dumps({'queued_media_probes':len(jobs),'roots':roots}), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for n, (aid,result) in enumerate(pool.map(lambda item: inspect(item,args.timeout),jobs),1):
            update(db,aid,result)
            if n % 25 == 0:
                db.commit()
                print(json.dumps({'probed':n,'total':len(jobs)}), flush=True)
    db.commit()
    if args.import_legacy:
        import_legacy(db)
    if args.verify_duplicates:
        verify_duplicates(db)
    export(db, args.catalog)
    print(json.dumps(summary(db),indent=2))


def import_legacy(db):
    matched = unmatched = 0
    for root in db.execute('SELECT * FROM roots WHERE online=1').fetchall():
        p = Path(root['path']) / '.broll_index.json'
        if not p.is_file():
            continue
        try:
            legacy = json.loads(p.read_text()).get('clips', {})
        except (OSError, ValueError) as e:
            db.execute('INSERT INTO issues VALUES(?,?,?,?)', (root['alias'],str(p),'Legacy import: '+str(e),time.time()))
            continue
        files = db.execute("SELECT * FROM files WHERE root_alias=? AND role='media' AND online=1", (root['alias'],)).fetchall()
        for oldpath, label in legacy.items():
            # Old mount paths vary. Require basename AND exact size; skip ambiguity.
            candidates = [f for f in files if Path(f['relative_path']).name == Path(oldpath).name and f['size'] == label.get('size')]
            if len(candidates) != 1:
                unmatched += 1
                continue
            f = candidates[0]
            annid = hashlib.sha256((str(p)+'\0'+oldpath).encode()).hexdigest()[:24]
            db.execute('''INSERT OR REPLACE INTO annotations VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                       (annid,f['asset_id'],'legacy_unverified',json.dumps(label.get('tags',[])),label.get('caption',''),
                        label.get('scene'),label.get('motion'),None,None,str(p),time.time(),json.dumps({'old_path':oldpath,'original':label,'match':'unique_basename_and_size'})))
            db.execute("UPDATE files SET review_status='legacy_unverified' WHERE asset_id=? AND review_status='unreviewed'", (f['asset_id'],))
            matched += 1
    db.commit()
    print(json.dumps({'legacy_labels_matched':matched,'legacy_labels_unmatched_or_ambiguous':unmatched}),flush=True)


def verify_duplicates(db):
    groups = db.execute("SELECT fingerprint FROM files WHERE role='media' AND online=1 AND fingerprint IS NOT NULL GROUP BY fingerprint HAVING COUNT(*)>1").fetchall()
    for group in groups:
        files = db.execute('SELECT f.*,r.path FROM files f JOIN roots r ON f.root_alias=r.alias WHERE fingerprint=? AND f.online=1',group).fetchall()
        for f in files:
            if f['sha256']:
                continue
            h = hashlib.sha256()
            try:
                with open(Path(f['path']) / f['relative_path'],'rb') as source:
                    while data := source.read(4*1024*1024):
                        h.update(data)
                update(db,f['asset_id'],{'sha256':h.hexdigest()})
                db.commit()
            except OSError as e:
                db.execute('INSERT INTO issues VALUES(?,?,?,?)',(f['root_alias'],f['relative_path'],'Full hash: '+str(e),time.time()))
    db.commit()


def annotation(row):
    obj = dict(row)
    obj['tags'] = json.loads(obj.pop('tags_json') or '[]')
    obj['source_data'] = json.loads(obj.pop('source_json') or '{}')
    return obj


def record(db,row,full=False):
    obj = dict(row)
    root = db.execute('SELECT path FROM roots WHERE alias=?',(obj['root_alias'],)).fetchone()
    obj['path'] = str(Path(root['path']) / obj['relative_path'])
    obj['available_now'] = bool(obj['online'] and Path(obj['path']).is_file())
    obj['annotations'] = [annotation(a) for a in db.execute('SELECT * FROM annotations WHERE asset_id=? ORDER BY source,created_at',(obj['asset_id'],))]
    for field in ('color_json','audio_json','probe_json'):
        value = obj.pop(field)
        if full or field != 'probe_json':
            obj[field.removesuffix('_json')] = json.loads(value) if value else None
    if not full:
        for field in ('device','inode','last_seen'):
            obj.pop(field,None)
    return obj


def search(db,args):
    sql = "SELECT * FROM files WHERE role='media'"
    params = []
    if not args.include_offline:
        sql += ' AND online=1'
    if args.kind:
        sql += ' AND kind=?'; params.append(args.kind)
    if args.min_duration is not None:
        sql += ' AND duration>=?'; params.append(args.min_duration)
    if args.root:
        sql += ' AND root_alias=?'; params.append(args.root)
    if args.reviewed_only:
        sql += " AND review_status='reviewed'"
    results = []
    seen = set()
    tokens = (args.query or '').casefold().split()
    for row in db.execute(sql,params):
        obj = record(db,row)
        if not args.include_offline and not obj['available_now']:
            continue
        anns = obj['annotations']
        # Reviewed-only means legacy hints cannot create a semantic search match.
        searchable = [a for a in anns if not args.reviewed_only or a['source']=='visual_review']
        hay = (' '.join([obj['relative_path'],obj['root_alias']]+[a['description']+' '+' '.join(a['tags']) for a in searchable])).casefold()
        if not all(t in hay for t in tokens):
            continue
        if args.deduplicate and obj['sha256']:
            if obj['sha256'] in seen:
                continue
            seen.add(obj['sha256'])
        obj['match_basis'] = 'reviewed visual annotations or path' if args.reviewed_only else 'visual annotations, unverified legacy labels, or path'
        results.append(obj)
    results.sort(key=lambda o:(o['review_status']!='reviewed',o['root_alias'],o['relative_path']))
    print(json.dumps({'total_matches':len(results),'results':results[:args.limit]},indent=2))


def annotate(db,args):
    row = db.execute('SELECT * FROM files WHERE asset_id=?',(args.asset_id,)).fetchone()
    if not row:
        raise ValueError('Unknown asset ID')
    if args.start < 0 or args.end < args.start or (row['duration'] is not None and args.end > row['duration']+0.1):
        raise ValueError('Review interval must lie within media duration')
    if not Path(args.evidence).expanduser().is_file():
        raise ValueError('Evidence must be a local frame/contact-sheet file you actually inspected')
    now = time.time()
    annid = hashlib.sha256((args.asset_id+str(now)).encode()).hexdigest()[:24]
    db.execute('INSERT INTO annotations VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
               (annid,args.asset_id,'visual_review',json.dumps([s.strip() for s in args.tags.split(',') if s.strip()]),
                args.description,args.scene,args.motion,args.start,args.end,str(Path(args.evidence).expanduser().absolute()),now,
                json.dumps({'reviewer':args.reviewer,'scope':'sampled frames; interval is reviewed coverage, not guaranteed continuous usable action','motion_evidence':args.motion_evidence})))
    db.execute("UPDATE files SET review_status='reviewed' WHERE asset_id=?",(args.asset_id,))
    db.commit()
    print(json.dumps({'asset_id':args.asset_id,'annotation_id':annid}))


def summary(db):
    def groups(column):
        return dict(db.execute('SELECT '+column+',COUNT(*) FROM files GROUP BY '+column))
    return {'files':db.execute('SELECT COUNT(*) FROM files').fetchone()[0],
            'kind':groups('kind'),'role':groups('role'),'online':groups('online'),
            'probe_status':groups('probe_status'),'review_status':groups('review_status'),
            'video_review_status':dict(db.execute("SELECT review_status,COUNT(*) FROM files WHERE kind='video' GROUP BY review_status")),
            'legacy_label_records':db.execute("SELECT COUNT(*) FROM annotations WHERE source='legacy_unverified'").fetchone()[0],
            'legacy_label_assets':db.execute("SELECT COUNT(DISTINCT asset_id) FROM annotations WHERE source='legacy_unverified'").fetchone()[0],
            'roots':[dict(r) for r in db.execute('SELECT * FROM roots')],
            'issues':[dict(r) for r in db.execute('SELECT * FROM issues')],
            'exact_duplicate_groups':db.execute('SELECT COUNT(*) FROM (SELECT sha256 FROM files WHERE sha256 IS NOT NULL GROUP BY sha256 HAVING COUNT(*)>1)').fetchone()[0],
            'sampled_fingerprint_notice':'Only matching full sha256 establishes exact duplicates; sampled fingerprints are candidates.'}


def export(db,catalog):
    directory = Path(catalog).expanduser()
    target = directory/'inventory.jsonl'
    temp = directory/'inventory.jsonl.tmp'
    with temp.open('w') as f:
        for row in db.execute('SELECT * FROM files ORDER BY root_alias,relative_path'):
            f.write(json.dumps(record(db,row),ensure_ascii=False)+'\n')
    temp.replace(target)
    (directory/'summary.json').write_text(json.dumps(summary(db),indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--catalog',default='~/.rojeru-format/broll')
    commands = p.add_subparsers(dest='command',required=True)
    s = commands.add_parser('scan'); s.add_argument('--root',action='append'); s.add_argument('--workers',type=int,default=4)
    s.add_argument('--timeout',type=float,default=25); s.add_argument('--reprobe',action='store_true')
    s.add_argument('--import-legacy',action='store_true'); s.add_argument('--verify-duplicates',action='store_true')
    s = commands.add_parser('search'); s.add_argument('query',nargs='?',default=''); s.add_argument('--kind',choices=['video','audio','image'],default='video')
    s.add_argument('--root'); s.add_argument('--min-duration',type=float); s.add_argument('--reviewed-only',action='store_true')
    s.add_argument('--include-offline',action='store_true'); s.add_argument('--deduplicate',action='store_true'); s.add_argument('--limit',type=int,default=10)
    s = commands.add_parser('show'); s.add_argument('asset_id')
    s = commands.add_parser('annotate'); s.add_argument('asset_id'); s.add_argument('--tags',required=True); s.add_argument('--description',required=True)
    s.add_argument('--start',required=True,type=float); s.add_argument('--end',required=True,type=float); s.add_argument('--evidence',required=True)
    s.add_argument('--scene'); s.add_argument('--motion',default='unreviewed'); s.add_argument('--motion-evidence')
    s.add_argument('--reviewer',default='agent')
    commands.add_parser('summary'); commands.add_parser('export')
    args = p.parse_args()
    if args.command=='scan' and (args.workers<1 or args.workers>8 or args.timeout<=0):
        p.error('workers must be 1–8 and timeout positive')
    if args.command=='annotate' and args.motion!='unreviewed' and not args.motion_evidence:
        p.error('Observed motion needs --motion-evidence describing consecutively inspected frames/playback')
    if args.command == 'scan':
        catalog_path = Path(args.catalog).expanduser().resolve()
        for spec in args.root or []:
            try:
                _, root_path = parse_root(spec)
            except ValueError as e:
                p.error(str(e))
            root_path = Path(root_path).resolve()
            if catalog_path == root_path or root_path in catalog_path.parents:
                p.error('Catalog must be outside source roots; source directories are read-only.')
    db = connect(args.catalog)
    try:
        if args.command=='scan': scan(db,args)
        elif args.command=='search': search(db,args)
        elif args.command=='annotate': annotate(db,args)
        elif args.command=='summary': print(json.dumps(summary(db),indent=2))
        elif args.command=='export': export(db,args.catalog)
        elif args.command=='show':
            row = db.execute('SELECT * FROM files WHERE asset_id=?',(args.asset_id,)).fetchone()
            if not row: raise ValueError('Unknown asset ID')
            print(json.dumps(record(db,row,True),indent=2))
    except (ValueError,OSError) as e:
        p.exit(1,str(e)+'\n')
    finally:
        db.close()

if __name__=='__main__':
    main()
