"""
DART_API_KEY / FRED_API_KEY 온보딩 — 없으면 채팅으로 물어보고 .env에 저장한다.

사용:
    python tools/env_keys.py check
    python tools/env_keys.py save DART_API_KEY=xxxx FRED_API_KEY=yyyy
"""
import os
import sys

REQUIRED_KEYS = ["DART_API_KEY", "FRED_API_KEY"]

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ENV_PATH = os.path.join(_REPO_ROOT, ".env")

ONBOARDING_TEMPLATE = (
    "이 스킬은 {keys}가 필요합니다. 채팅에 바로 붙여넣어 주세요.\n"
    " - DART: https://opendart.fss.or.kr 에서 발급\n"
    " - FRED: https://fred.stlouisfed.org/docs/api/api_key.html 에서 발급\n"
    "(다음부터 다시 안 묻도록 로컬 .env에 저장합니다)"
)


def read_env_file(path):
    values = {}
    if not os.path.exists(path):
        return values
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip()
    return values


def find_missing_keys(path=DEFAULT_ENV_PATH, environ=None):
    environ = os.environ if environ is None else environ
    file_values = read_env_file(path)
    missing = []
    for key in REQUIRED_KEYS:
        if environ.get(key) or file_values.get(key):
            continue
        missing.append(key)
    return missing


def save_keys(new_keys, path=DEFAULT_ENV_PATH):
    existing = read_env_file(path)
    existing.update(new_keys)
    with open(path, "w", encoding="utf-8") as f:
        for k, v in existing.items():
            f.write("{}={}\n".format(k, v))


def onboarding_message(missing):
    return ONBOARDING_TEMPLATE.format(keys=", ".join(missing))


def main(argv):
    if not argv:
        print("usage: env_keys.py check | save KEY=VALUE [KEY=VALUE ...]")
        return 2
    cmd = argv[0]
    if cmd == "check":
        missing = find_missing_keys()
        if missing:
            print("MISSING:" + ",".join(missing))
            print(onboarding_message(missing))
            return 1
        print("OK")
        return 0
    if cmd == "save":
        pairs = {}
        for item in argv[1:]:
            if "=" not in item:
                print("bad pair: {}".format(item))
                return 2
            k, v = item.split("=", 1)
            pairs[k.strip()] = v.strip()
        if not pairs:
            print("no KEY=VALUE pairs given")
            return 2
        save_keys(pairs)
        print("SAVED:" + ",".join(pairs.keys()))
        return 0
    print("unknown command: {}".format(cmd))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
