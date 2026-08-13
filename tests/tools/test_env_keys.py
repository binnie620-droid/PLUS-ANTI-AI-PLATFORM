import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import env_keys


class TestEnvKeys(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.env_path = os.path.join(self.tmpdir, ".env")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_find_missing_keys_when_nothing_set(self):
        missing = env_keys.find_missing_keys(self.env_path, environ={})
        self.assertEqual(sorted(missing), ["DART_API_KEY", "FRED_API_KEY"])

    def test_find_missing_keys_reads_from_environ(self):
        missing = env_keys.find_missing_keys(
            self.env_path, environ={"DART_API_KEY": "abc"}
        )
        self.assertEqual(missing, ["FRED_API_KEY"])

    def test_find_missing_keys_reads_from_dotenv_file(self):
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write("DART_API_KEY=abc\nFRED_API_KEY=def\n")
        missing = env_keys.find_missing_keys(self.env_path, environ={})
        self.assertEqual(missing, [])

    def test_read_env_file_ignores_comments_and_blank_lines(self):
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write("# comment\n\nDART_API_KEY=abc\n")
        values = env_keys.read_env_file(self.env_path)
        self.assertEqual(values, {"DART_API_KEY": "abc"})

    def test_read_env_file_missing_file_returns_empty_dict(self):
        values = env_keys.read_env_file(os.path.join(self.tmpdir, "nope.env"))
        self.assertEqual(values, {})

    def test_save_keys_creates_file_and_round_trips(self):
        env_keys.save_keys({"DART_API_KEY": "abc"}, self.env_path)
        values = env_keys.read_env_file(self.env_path)
        self.assertEqual(values, {"DART_API_KEY": "abc"})

    def test_save_keys_preserves_existing_keys(self):
        env_keys.save_keys({"DART_API_KEY": "abc"}, self.env_path)
        env_keys.save_keys({"FRED_API_KEY": "def"}, self.env_path)
        values = env_keys.read_env_file(self.env_path)
        self.assertEqual(values, {"DART_API_KEY": "abc", "FRED_API_KEY": "def"})

    def test_save_keys_overwrites_same_key(self):
        env_keys.save_keys({"DART_API_KEY": "abc"}, self.env_path)
        env_keys.save_keys({"DART_API_KEY": "xyz"}, self.env_path)
        values = env_keys.read_env_file(self.env_path)
        self.assertEqual(values, {"DART_API_KEY": "xyz"})

    def test_onboarding_message_lists_missing_keys(self):
        msg = env_keys.onboarding_message(["DART_API_KEY", "FRED_API_KEY"])
        self.assertIn("DART_API_KEY", msg)
        self.assertIn("FRED_API_KEY", msg)
        self.assertIn("opendart.fss.or.kr", msg)
        self.assertIn("fred.stlouisfed.org", msg)


if __name__ == "__main__":
    unittest.main()
