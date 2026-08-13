import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import industry_cache as ic


class TestIndustryCache(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache_path = os.path.join(self.tmpdir, "data", "industry_cache.json")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_load_cache_missing_file_returns_empty_structure(self):
        cache = ic.load_cache(self.cache_path)
        self.assertEqual(cache, {"companies": {}, "industries": {}})

    def test_save_then_load_round_trips(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재", today="2026-08-13")
        ic.save_cache(cache, self.cache_path)
        loaded = ic.load_cache(self.cache_path)
        self.assertEqual(loaded, cache)

    def test_add_company_creates_company_and_industry_entries(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재", today="2026-08-13")

        company = ic.get_company(cache, "009540")
        self.assertEqual(company["name"], "HD한국조선해양")
        self.assertEqual(company["induty_code"], "31114")
        self.assertEqual(company["industry_labels"], ["조선·조선기자재"])
        self.assertEqual(company["cached_at"], "2026-08-13")

        industry = ic.get_industry(cache, "조선·조선기자재")
        self.assertEqual(industry["tickers"], ["009540"])
        self.assertEqual(industry["induty_codes"], ["31114"])
        self.assertEqual(industry["first_seen"], "2026-08-13")

    def test_add_company_twice_does_not_duplicate(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재", today="2026-08-13")
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재", today="2026-08-14")

        industry = ic.get_industry(cache, "조선·조선기자재")
        self.assertEqual(industry["tickers"], ["009540"])
        self.assertEqual(industry["induty_codes"], ["31114"])

    def test_add_company_same_ticker_multiple_industries(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재")
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "방산·항공")

        company = ic.get_company(cache, "009540")
        self.assertEqual(company["industry_labels"], ["조선·조선기자재", "방산·항공"])

    def test_get_company_missing_returns_none(self):
        cache = ic.empty_cache()
        self.assertIsNone(ic.get_company(cache, "999999"))

    def test_get_industry_missing_returns_none(self):
        cache = ic.empty_cache()
        self.assertIsNone(ic.get_industry(cache, "없는산업"))

    def test_list_industries_sorted(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "1", "가", "1", "다산업")
        ic.add_company(cache, "2", "나", "2", "가산업")
        self.assertEqual(ic.list_industries(cache), ["가산업", "다산업"])


if __name__ == "__main__":
    unittest.main()
