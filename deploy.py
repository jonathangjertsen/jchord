import argparse
import subprocess

def deploy():
    proc = subprocess.run(["pytest"])
    if proc.returncode != 0:
        return
    print("All tests passed")

    proc = subprocess.run(["git", "status", "--porcelain"], stdout=subprocess.PIPE)
    if proc.returncode != 0:
        return

    if proc.stdout:
        print("Git repo is not clean, `git status --porcelain` returned:\n{}".format(proc.stdout.decode("utf-8")))
        return
    print("Git repo is clean.")

    proc = subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])
    if proc.returncode != 0:
        return
    print("Ran setup.py")

    with open("VERSION.TXT") as version_file:
        version = version_file.read().strip()

    if input("Create commit for release?").strip() == "y":
        proc = subprocess.run(["git", "commit", "--allow-empty", "-m", "Commit for release v" + version])
        if proc.returncode != 0:
            return
        print("Created commit for release")

    proc = subprocess.run(["git", "tag", "v" + version], stderr=subprocess.PIPE)
    if proc.returncode != 0:
        if "already exists" in proc.stderr.decode("utf-8"):
            if input("Tag already exists. Delete it?") == "y":
                proc = subprocess.run(["git", "tag", "-d", "v" + version])
                if proc.returncode != 0:
                    return

                proc = subprocess.run(["git", "tag", "v" + version], stderr=subprocess.PIPE)
                if proc.returncode != 0:
                    return
        else:
            return
    print("Created tag for release")

    proc = subprocess.run(["git", "push", "origin", "master"])
    if proc.returncode != 0:
        return
    print("Pushed release commit to git")

    proc = subprocess.run(["git", "push", "origin", "--tags"])
    if proc.returncode != 0:
        return
    print("Pushed release tag to git")

    input("""Go to https://github.com/jonathangjertsen/jchord/releases/new and create a release. Select tag v{version} and enter text:

# Release v{version}

* Changelog:
    * 
* On PyPI: https://pypi.org/project/jchord/{version}/
""".format(version=version))

    proc = subprocess.run(["python", "-m", "twine", "upload", "dist/*", "--verbose"])
    print("Uploaded to PyPI")

if __name__ == "__main__":
    deploy()
