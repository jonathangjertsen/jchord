import argparse
import subprocess


class ShellExecFailed(Exception):
    pass


def shell_exec(*args, can_skip=False, pass_msg="", skip_msg="", **kwargs):
    if can_skip:
        skip = input("Skip step: {} (YES/n)?".format(args))
        if skip:
            print(skip_msg)
            return
    proc = subprocess.run(*args, **kwargs)
    if proc.returncode != 0:
        if can_skip:
            skip = (
                input(
                    "Process exited with return code {}. Continue (YES/n)? ".format(
                        proc.returncode
                    )
                ).strip()
                == "YES"
            )
            if not skip:
                raise ShellExecFailed("Did not continue after failed step.")
            print(skip_msg)
        else:
            raise ShellExecFailed("Unskippable step failed.")
    print(pass_msg)
    return proc


def deploy():
    # Make sure the tests pass
    shell_exec(["pytest"], pass_msg="All tests succeeded")

    # Format code
    shell_exec(["black", "."], pass_msg="Ran Black")

    # Make sure the repo is clean (or make sure it's OK if it's dirty)
    proc = shell_exec(["git", "status", "--porcelain"], stdout=subprocess.PIPE)
    if proc.stdout:
        print(
            "Git repo is not clean, `git status --porcelain` returned:\n{}".format(
                proc.stdout.decode("utf-8")
            )
        )
        skip = input("Ignore dirty repo (YES/n)?").strip() == "YES"
        if skip:
            print("Ignoring dirty repo.")
        else:
            raise ShellExecFailed("Not ignoring dirty repo.")
    else:
        print("Git repo is clean.")

    # Create wheels for this release
    shell_exec(
        ["python", "setup.py", "sdist", "bdist_wheel"], pass_msg="setup.py succeeded"
    )

    # Read the version for the latest release
    with open("VERSION.TXT") as version_file:
        version = version_file.read().strip()

    # Create a commit for the release
    shell_exec(
        ["git", "commit", "--allow-empty", "-m", "Commit for release v" + version],
        can_skip=True,
        pass_msg="Created commit for release",
        skip_msg="Skipped creating commit for release",
    )

    # Create a tag for the release
    proc = shell_exec(
        ["git", "tag", "v" + version],
        pass_msg="Created tag v" + version,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        if "already exists" in proc.stderr.decode("utf-8"):
            if input("Tag already exists. Delete it?") == "y":
                shell_exec(
                    ["git", "tag", "-d", "v" + version],
                    pass_msg="Deleted tag v" + version,
                )
                shell_exec(
                    ["git", "tag", "v" + version], pass_msg="Created tag v" + version
                )
        else:
            raise ShellExecFailed(proc.stderr.decode("utf-8"))

    # Push latest master to GitHub
    shell_exec(
        ["git", "push", "origin", "master"],
        can_skip=True,
        pass_msg="Pushed release commit to GitHub",
        skip_msg="Skipped pushing to GitHub",
    )

    # Push tags to GitHub
    shell_exec(["git", "push", "origin", "--tags"], pass_msg="Pushed tags to GitHub")

    # Create release on GitHub
    input(
        """Go to https://github.com/jonathangjertsen/jchord/releases/new and create a release. Select tag v{version} and enter text:

# Release v{version}

* Changelog:
    * 
* On PyPI: https://pypi.org/project/jchord/{version}/
""".format(
            version=version
        )
    )

    # Upload to PyPI
    shell_exec(
        ["python", "-m", "twine", "upload", "dist/*", "--verbose", "--skip-existing"],
        can_skip=True,
        pass_msg="Uploaded release to PyPI",
        skip_msg="Skipped uploading release",
    )


if __name__ == "__main__":
    deploy()
