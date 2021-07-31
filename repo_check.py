from pathlib import Path
from subprocess import run
import sys


def fix_crlf(path):
    path_str = str(path)
    if any(
        token in path_str
        for token in (".git", ".pytest_cache", "build", "dist", ".png", ".mid")
    ):
        return
    if path.is_dir():
        for subpath in path.iterdir():
            fix_crlf(subpath)
    else:
        try:
            path.write_text(path.read_text().replace("\r\n", "\n"))
        except UnicodeDecodeError:
            pass


if __name__ == "__main__":
    print("========== Removing CRLF...")
    fix_crlf(Path("."))

    print("========== Checking if git repo is clean...")
    porcelain_initial = (
        run(["git", "status", "--porcelain"], capture_output=True)
        .stdout.decode("ascii", errors="ignore")
        .strip()
    )
    if porcelain_initial:
        print(porcelain_initial)
        print("Git repo is dirty.")
        sys.exit(1)

    print("========== Formatting python code...")
    proc = run(["black", "."])
    if proc.returncode != 0:
        print("black failed.")
        sys.exit(1)

    print("========== Checking if tests pass...")
    proc = run(["pytest"])
    if proc.returncode != 0:
        print("pytest failed.")
        sys.exit(1)

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

    print("========== Generating docs...")
    proc = run(["sphinx-build", ".", "docs", "-c", "docs"])
    if proc.returncode != 0:
        print("sphinx-build failed.")
        sys.exit(1)
    fix_crlf(Path("."))

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
            "Repo check caused some files to change.\n"
            "If this is run locally, please commit the files that were just updated.\n"
            "If this is in CI, please run python repo_check.py locally and commit the changes."
        )
        sys.exit(1)

    print("OK, everything is up to date")