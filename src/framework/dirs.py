from pathlib import Path

_this_file = Path(__file__).resolve()

DIR_REPO = _this_file.parent.parent.parent

DIR_CONFIG = DIR_REPO / "config"

DIR_IDEA = DIR_REPO / ".idea"

DIR_SRC = DIR_REPO / "src"
DIR_FRAMEWORK = DIR_SRC / "framework"
DIR_MAIN = DIR_SRC / "main"

DIR_SCRIPTS = DIR_REPO / "scripts"

DIR_TESTS = DIR_REPO / "tests"

DIR_TEST_ARTIFACTS = DIR_REPO / ".tests_artifacts"
DIR_TEST_ARTIFACTS.mkdir(exist_ok=True)

DIR_DB = DIR_MAIN / "db"
DIR_MIGRATIONS = DIR_DB / "migrations"

DIR_TEMPLATES = DIR_MAIN / "templates"
