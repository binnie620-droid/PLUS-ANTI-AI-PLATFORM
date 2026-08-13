import io
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import migrate_industry_cache as migrate_mod
import industry_cache as ic


FIXTURE_CSV = (
    "industry,ticker,name,ksic_code\n"
    "조선·조선기자재,009540,HD한국조선해양,\n"
    "조선·조선기자재,042660,한화오션,\n"
    "방산·항공,012450,한화에어로스페이스,\n"
)


class TestMigrateIndustryCache(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.source_path = os.path.join(self.tmpdir, "industry_universe.csv")
        self.cache_path = os.path.join(self.tmpdir, "industry_cache.json")
        self.dart_cache_path = os.path.join(self.tmpdir, "dart_corp_codes.csv")
        with io.open(self.source_path, "w", encoding="utf-8") as f:
            f.write(FIXTURE_CSV)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_migrate_without_api_key_leaves_induty_code_none(self):
        cache = migrate_mod.migrate(
            api_key=None,
            source_path=self.source_path,
            cache_path=self.cache_path,
            dart_cache_path=self.dart_cache_path,
        )
        company = ic.get_company(cache, "009540")
        self.assertEqual(company["name"], "HD한국조선해양")
        self.assertIsNone(company["induty_code"])

        industry = ic.get_industry(cache, "조선·조선기자재")
        self.assertEqual(sorted(industry["tickers"]), ["009540", "042660"])

        self.assertTrue(os.path.exists(self.cache_path))

    def test_migrate_with_api_key_fills_induty_code(self):
        def fake_fetcher(url):
            raise AssertionError("this test doesn't need real DART calls")

        # Patch get_induty_code to avoid needing real HTTP fixtures here —
        # dart_lookup's own network behavior is already covered in Task 3's tests.
        original = migrate_mod.dart_lookup.get_induty_code
        migrate_mod.dart_lookup.get_induty_code = (
            lambda ticker, api_key, cache_path=None, fetcher=None: {
                "corp_code": "X", "corp_name": "n/a", "induty_code": "31114"
            }
        )
        try:
            cache = migrate_mod.migrate(
                api_key="APIKEY",
                source_path=self.source_path,
                cache_path=self.cache_path,
                dart_cache_path=self.dart_cache_path,
            )
        finally:
            migrate_mod.dart_lookup.get_induty_code = original

        company = ic.get_company(cache, "009540")
        self.assertEqual(company["induty_code"], "31114")

    def test_migrate_covers_all_rows(self):
        cache = migrate_mod.migrate(
            api_key=None,
            source_path=self.source_path,
            cache_path=self.cache_path,
            dart_cache_path=self.dart_cache_path,
        )
        self.assertEqual(sorted(ic.list_industries(cache)), ["방산·항공", "조선·조선기자재"])
        self.assertEqual(len(cache["companies"]), 3)


if __name__ == "__main__":
    unittest.main()
