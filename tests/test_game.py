import tempfile
import unittest
from pathlib import Path
from collections import Counter
from pc_build_battle.database import Database
from pc_build_battle.models import Build, CATEGORIES
from pc_build_battle.challenges import featured, generate, MODES
from pc_build_battle.services import compatibility, objectives, score


def sample_build(db):
    lookup={p.id:p for p in db.parts()}
    ids=['cpu-6','cpu_cooler-3','motherboard-2','gpu-16','ram-5','storage-7','psu-8','case-3']
    return Build(featured(),{lookup[id].category:lookup[id] for id in ids})


class GameplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'test.sqlite3'; self.db=Database(self.path)

    def tearDown(self): self.db.close(); self.tmp.cleanup()

    def test_catalog(self):
        counts=Counter(p.category for p in self.db.parts())
        self.assertEqual(sum(counts.values()),120)
        for cat in CATEGORIES: self.assertGreaterEqual(counts[cat],20 if cat=='GPU' else 10 if cat=='CPU Cooler' else 15)

    def test_complete_build_and_restart(self):
        build=sample_build(self.db)
        self.assertEqual(compatibility(build),[])
        self.assertTrue(all(objectives(build).values()))
        self.db.save_draft(build); self.assertEqual(self.db.draft().cost,build.cost)
        result=self.db.submit(build,score(build))
        self.assertGreaterEqual(result['total'],70)
        self.assertIn('Perfect Compatibility',result['unlocked'])
        self.db.close(); self.db=Database(self.path)
        self.assertEqual(len(self.db.history()),1)
        self.assertEqual(self.db.get('xp'),result['xp'])
        self.assertIsNone(self.db.draft())
        self.assertTrue(any(r['player']=='Builder01' for r in self.db.leaderboard()))

    def test_incompatibility_penalty(self):
        good=sample_build(self.db); original=score(good)['total']; lookup={p.id:p for p in self.db.parts()}
        good.parts['CPU']=lookup['cpu-15']; good.parts['RAM']=lookup['ram-1']; good.parts['PSU']=lookup['psu-1']; good.parts['Case']=lookup['case-11']
        self.assertGreaterEqual(len(compatibility(good)),4)
        self.assertLess(score(good)['total'],original)

    def test_objectives_budget_and_events(self):
        build=sample_build(self.db); base=build.cost; build.discounts[build.parts['GPU'].id]=40
        self.assertEqual(build.cost,base-40)
        build.challenge.budget=500
        self.assertFalse(objectives(build)['budget'])
        self.assertLess(score(build)['total'],60)
        self.db.save_draft(build); self.assertEqual(self.db.draft().discounts,build.discounts)

    def test_all_modes_and_repeat_achievements(self):
        for mode in MODES:
            build=sample_build(self.db); build.challenge=generate(mode); result=score(build)
            self.assertGreaterEqual(result['total'],0); self.assertLessEqual(result['total'],100)
        build=sample_build(self.db); first=self.db.submit(build,score(build)); second=self.db.submit(build,score(build))
        self.assertTrue(first['unlocked']); self.assertEqual(second['unlocked'],[])


if __name__=='__main__': unittest.main()
