"""데이터 파일 위치 해석 — 저장소 clone 과 플러그인 설치 두 경우를 모두 지원한다.

이 저장소는 두 가지 방식으로 쓰인다.

    1) git clone 해서 그 폴더에서 직접 실행       → data/ 는 저장소 안
    2) Claude Code 플러그인으로 설치              → 코드는 ~/.claude/plugins/cache/...
                                                    아래 **읽기 전용**으로 놓인다

2번에서 번들된 위치에 쓰려고 하면 실패하거나, 성공해도 플러그인 업데이트 때
통째로 날아간다. 그래서 **읽기와 쓰기의 기준 경로를 분리**한다.

    source(name)   읽을 때  — 작업본이 있으면 그것, 없으면 번들된 씨앗
    target(name)   쓸 때    — 항상 작업본

작업본 위치는 아래 순서로 정한다.

    1. DPIC_DATA_DIR         명시적 지정이 항상 이긴다
    2. CLAUDE_PROJECT_DIR    Claude Code 가 넣어주는 사용자 프로젝트 루트
    3. 저장소 안 data/       clone 해서 쓰는 경우

두 함수 모두 디렉터리를 만들지 않는다 — import 만으로 남의 폴더에 data/ 가
생기면 곤란하다. 실제로 쓰기 직전에 ensure_dir() 를 부른다.
"""
import os
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED_DATA = os.path.join(REPO_ROOT, "data")


def data_dir():
    """쓰기 가능한 데이터 디렉터리 경로. 만들지는 않는다."""
    explicit = os.environ.get("DPIC_DATA_DIR")
    if explicit:
        return explicit
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project:
        return os.path.join(project, "data")
    return BUNDLED_DATA


def target(name):
    """쓰기용 경로 — 항상 작업본."""
    return os.path.join(data_dir(), name)


def source(name):
    """읽기용 경로 — 작업본 우선, 없으면 번들된 씨앗."""
    working = target(name)
    if os.path.exists(working):
        return working
    return os.path.join(BUNDLED_DATA, name)


def ensure_dir(path):
    """파일 경로를 받아 상위 디렉터리를 만든다. 쓰기 직전에 부른다."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    return path


def seed(name):
    """작업본이 없으면 번들 씨앗을 복사해온다. 기존 행을 보존해야 하는
    도구(fetch_consensus 등)가 플러그인 환경에서 씨앗을 잃지 않게 한다."""
    working = target(name)
    if os.path.exists(working):
        return working
    bundled = os.path.join(BUNDLED_DATA, name)
    if os.path.exists(bundled) and os.path.abspath(bundled) != os.path.abspath(working):
        ensure_dir(working)
        shutil.copy2(bundled, working)
    return working
