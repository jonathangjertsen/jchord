import subprocess

def deploy():
    proc = subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])
    if proc.returncode != 0:
        return

    proc = subprocess.run(["python", "-m", "twine", "upload", "dist/*", "--verbose"])

if __name__ == "__main__":
    deploy()
