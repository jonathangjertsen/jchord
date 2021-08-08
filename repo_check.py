from pathlib import Path
from subprocess import run
import sys

TASKS = {}


def task(func):
    TASKS[func.__name__] = func
    return func


@task
def build_docs():
    print("========== Generating docs...")
    proc = run(["sphinx-build", ".", "docs", "-c", "docs"])
    if proc.returncode != 0:
        print("sphinx-build failed.")
        sys.exit(1)


@task
def fix_crlf():
    print("========== Removing CRLF...")

    def helper(path):
        path_str = str(path)
        if any(
            token in path_str
            for token in (".git", ".pytest_cache", "build", "dist", ".png", ".mid")
        ):
            return
        if path.is_dir():
            for subpath in path.iterdir():
                helper(subpath)
        else:
            try:
                path.write_text(path.read_text().replace("\r\n", "\n"))
            except UnicodeDecodeError:
                pass

    helper(Path("."))


@task
def check_clean():
    print("========== Checking if anything changed...")
    porcelain_after = (
        run(["git", "status", "--porcelain"], capture_output=True)
        .stdout.decode("ascii", errors="ignore")
        .strip()
    )
    if porcelain_after:
        print(porcelain_after)
        run(["git", "status", "-vvv"])
        print(
            "Repo is dirty.\n"
            "If this is run locally, please commit the files that were updated.\n"
            "If this is in CI, please run python repo_check.py locally and commit the changes."
        )
        sys.exit(1)


@task
def format():
    print("========== Formatting python code...")
    proc = run(["black", "."])
    if proc.returncode != 0:
        print("black failed.")
        sys.exit(1)


@task
def pytest():
    print("========== Checking if tests pass...")
    proc = run(["pytest"])
    if proc.returncode != 0:
        print("pytest failed.")
        sys.exit(1)


@task
def doctest():
    print("========== Checking if doctests pass...")
    proc = run(
        [
            "python",
            "-m",
            "doctest",
            "-v",
            "jchord/core.py",
            "jchord/chords.py",
            "jchord/progressions.py",
        ]
    )
    if proc.returncode != 0:
        print("pytest failed.")
        sys.exit(1)


if __name__ == "__main__":
    fix_crlf()
    check_clean()
    format()
    pytest()
    doctest()
    build_docs()
    fix_crlf()
    check_clean()
    print("OK, everything is up to date")
