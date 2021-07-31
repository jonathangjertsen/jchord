from subprocess import run
import sys

if __name__ == "__main__":
    requirements = "\n".join(
        line.strip()
        for line in run(["pip", "freeze"], capture_output=True)
        .stdout.decode("ascii", errors="ignore")
        .strip()
        .split("\n")
        if "certif" not in line
        and "wincertstore" not in line
        and "#egg" not in line
        and line.strip()
    )
    with open("requirements.txt", "w") as file:
        file.write(requirements)
