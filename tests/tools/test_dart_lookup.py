import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import dart_lookup as dl


def make_corp_code_zip(rows):
    """rows: list of (corp_code, corp_name, stock_code, modify_date) -> zip bytes with corpCode.xml inside"""
    parts = ["<result>"]
    for corp_code, corp_name, stock_code, modify_date in rows:
        parts.append(
            "<list><corp_code>{}</corp_code><corp_name>{}</corp_name>"
            "<stock_code>{}</stock_code><modify_date>{}</modify_date></list>".format(
                corp_code, corp_name, stock_code, modify_date
            )
        )
    parts.append("</result>")
    xml_bytes = "".join(parts).encode("utf-8")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("CORPCODE.xml", xml_bytes)
    return buf.getvalue()


class TestParseCorpCodeZip(unittest.TestCase):
    def test_filters_out_unlisted_rows(self):
        zip_bytes = make_corp_code_zip([
            ("00126380", "삼성전자", "005930", "20260101"),
            ("00999999", "비상장회사", "", "20260101"),
        ])
        rows = dl.parse_corp_code_zip(zip_bytes)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["stock_code"], "005930")
        self.assertEqual(rows[0]["corp_name"], "삼성전자")


class TestCorpCodeCache(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache_path = os.path.join(self.tmpdir, "dart_corp_codes.csv")
        self.zip_bytes = make_corp_code_zip([
            ("00126380", "삼성전자", "005930", "20260101"),
            ("00164742", "HD한국조선해양", "009540", "20260101"),
        ])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_build_corp_code_cache_writes_csv(self):
        calls = []

        def fake_fetcher(url):
            calls.append(url)
            return self.zip_bytes

        rows = dl.build_corp_code_cache("APIKEY", path=self.cache_path, fetcher=fake_fetcher)
        self.assertEqual(len(rows), 2)
        self.assertTrue(os.path.exists(self.cache_path))
        self.assertEqual(len(calls), 1)
        self.assertIn("APIKEY", calls[0])

    def test_get_corp_code_uses_existing_cache_without_refetch(self):
        dl.build_corp_code_cache("APIKEY", path=self.cache_path, fetcher=lambda url: self.zip_bytes)

        def fail_if_called(url):
            raise AssertionError("should not refetch when cache already has the ticker")

        corp_code = dl.get_corp_code("005930", "APIKEY", cache_path=self.cache_path, fetcher=fail_if_called)
        self.assertEqual(corp_code, "00126380")

    def test_get_corp_code_builds_cache_when_missing(self):
        corp_code = dl.get_corp_code(
            "009540", "APIKEY", cache_path=self.cache_path, fetcher=lambda url: self.zip_bytes
        )
        self.assertEqual(corp_code, "00164742")

    def test_get_corp_code_unknown_ticker_returns_none(self):
        corp_code = dl.get_corp_code(
            "000000", "APIKEY", cache_path=self.cache_path, fetcher=lambda url: self.zip_bytes
        )
        self.assertIsNone(corp_code)


class TestCompanyInfoAndIndutyCode(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache_path = os.path.join(self.tmpdir, "dart_corp_codes.csv")
        self.zip_bytes = make_corp_code_zip([("00164742", "HD한국조선해양", "009540", "20260101")])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_fetch_company_info_parses_json(self):
        payload = json.dumps({
            "status": "000", "corp_name": "HD한국조선해양", "induty_code": "31114"
        }).encode("utf-8")
        info = dl.fetch_company_info("00164742", "APIKEY", fetcher=lambda url: payload)
        self.assertEqual(info["induty_code"], "31114")
        self.assertEqual(info["corp_name"], "HD한국조선해양")

    def test_get_induty_code_happy_path(self):
        fetch_log = []

        def fake_fetcher(url):
            fetch_log.append(url)
            if "corpCode.xml" in url:
                return self.zip_bytes
            return json.dumps({"status": "000", "corp_name": "HD한국조선해양", "induty_code": "31114"}).encode("utf-8")

        result = dl.get_induty_code("009540", "APIKEY", cache_path=self.cache_path, fetcher=fake_fetcher)
        self.assertEqual(result, {
            "corp_code": "00164742", "corp_name": "HD한국조선해양", "induty_code": "31114"
        })

    def test_get_induty_code_unknown_ticker_returns_none_without_company_call(self):
        fetch_log = []

        def fake_fetcher(url):
            fetch_log.append(url)
            return self.zip_bytes

        result = dl.get_induty_code("999999", "APIKEY", cache_path=self.cache_path, fetcher=fake_fetcher)
        self.assertIsNone(result)
        # only the corpCode.xml lookup should have happened, never company.json
        self.assertEqual(len(fetch_log), 1)
        self.assertIn("corpCode.xml", fetch_log[0])

    def test_fetch_company_info_raises_on_dart_error_status(self):
        error_payload = json.dumps({
            "status": "020", "message": "일일 이용 한도량 초과"
        }).encode("utf-8")
        with self.assertRaises(RuntimeError) as context:
            dl.fetch_company_info("00164742", "APIKEY", fetcher=lambda url: error_payload)
        self.assertIn("status=020", str(context.exception))
        self.assertIn("일일 이용 한도량 초과", str(context.exception))


if __name__ == "__main__":
    unittest.main()
