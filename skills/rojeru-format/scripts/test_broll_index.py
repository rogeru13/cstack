"""Focused catalog checks: source preservation, resumability, evidence and duplicates."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import broll_index as b


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base/'source'
        self.root.mkdir()
        self.catalog = self.base/'catalog'
        self.db = b.connect(self.catalog)
        self.args = argparse.Namespace(root=['clips='+str(self.root)],workers=2,timeout=1,
                                       reprobe=False,import_legacy=False,verify_duplicates=False,catalog=str(self.catalog))

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def scan(self):
        with contextlib.redirect_stdout(io.StringIO()), patch.object(b,'probe',return_value={'probe_status':'ok','duration':8,'width':1920,'height':1080}):
            b.scan(self.db,self.args)

    def test_inventory_excludes_resource_forks_and_cache_from_media(self):
        (self.root/'clip.MP4').write_bytes(b'original footage')
        (self.root/'._clip.MP4').write_bytes(b'appledouble')
        (self.root/'.broll_cache').mkdir()
        (self.root/'.broll_cache'/'frame.jpg').write_bytes(b'preview')
        before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.scan()
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM files').fetchone()[0],3)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM files WHERE role='media'").fetchone()[0],1)
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        with patch.object(b,'probe',side_effect=AssertionError('unchanged file was reprobed')),contextlib.redirect_stdout(io.StringIO()):
            b.scan(self.db,self.args)

    def test_offline_inventory_is_retained(self):
        (self.root/'clip.MP4').write_bytes(b'x')
        self.scan()
        self.root.rename(self.base/'unmounted')
        self.scan()
        row=self.db.execute('SELECT * FROM files').fetchone()
        self.assertEqual(row['online'],0)
        self.assertEqual(row['duration'],8)
        self.assertFalse(b.record(self.db,row)['available_now'])

    def test_changed_file_invalidates_prior_review(self):
        clip=self.root/'clip.MP4';clip.write_bytes(b'x');self.scan()
        aid=self.db.execute('SELECT asset_id FROM files').fetchone()[0]
        evidence=self.base/'evidence.jpg';evidence.write_bytes(b'frame')
        args=argparse.Namespace(asset_id=aid,tags='kitchen',description='A kitchen',start=1,end=3,evidence=str(evidence),scene='interior',motion='unreviewed',motion_evidence=None,reviewer='test')
        with contextlib.redirect_stdout(io.StringIO()): b.annotate(self.db,args)
        self.assertEqual(self.db.execute('SELECT review_status FROM files').fetchone()[0],'reviewed')
        clip.write_bytes(b'replacement');self.scan()
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM annotations').fetchone()[0],0)
        self.assertEqual(self.db.execute('SELECT review_status FROM files').fetchone()[0],'unreviewed')

    def test_legacy_requires_unique_basename_and_size(self):
        for folder in ('a','b'):
            (self.root/folder).mkdir();(self.root/folder/'clip.MP4').write_bytes(b'x')
        (self.root/'.broll_index.json').write_text(json.dumps({'clips':{'/old/clip.MP4':{'size':1,'tags':['forest']}}}))
        self.scan()
        with contextlib.redirect_stdout(io.StringIO()): b.import_legacy(self.db)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM annotations').fetchone()[0],0)

    def test_exact_duplicate_evidence_and_path_ids(self):
        for name in ('one.MP4','two.MP4'):(self.root/name).write_bytes(b'identical content')
        self.scan()
        rows=self.db.execute('SELECT * FROM files').fetchall()
        self.assertNotEqual(rows[0]['asset_id'],rows[1]['asset_id'])
        self.assertEqual(rows[0]['fingerprint'],rows[1]['fingerprint'])
        self.assertIsNone(rows[0]['sha256'])
        b.verify_duplicates(self.db)
        self.assertEqual(b.summary(self.db)['exact_duplicate_groups'],1)

    def test_reviewed_search_does_not_match_unverified_hints(self):
        (self.root/'clip.MP4').write_bytes(b'x');self.scan()
        aid=self.db.execute('SELECT asset_id FROM files').fetchone()[0]
        self.db.execute("UPDATE files SET review_status='reviewed'")
        self.db.execute('INSERT INTO annotations VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',('legacy',aid,'legacy_unverified','["forest"]','Forest',None,None,None,None,'legacy.json',0,'{}'))
        args=argparse.Namespace(query='forest',kind='video',root=None,min_duration=3,reviewed_only=True,include_offline=False,deduplicate=False,limit=10)
        output=io.StringIO()
        with contextlib.redirect_stdout(output):b.search(self.db,args)
        self.assertEqual(json.loads(output.getvalue())['total_matches'],0)


if __name__=='__main__':unittest.main()
