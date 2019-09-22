import filecmp
import os
import subprocess


def normalize(string):
    return string.strip().replace("\r\n", "\n")


def test_doc_up_to_date():
    tmp_doc_filename = os.path.join(
        os.path.dirname(__file__), "test_data", "test_doc.md"
    )
    with open(
        os.path.join(os.path.dirname(__file__), "..", "readme.md")
    ) as readme_file:
        readme = readme_file.read()
    root_dir = os.path.join(os.path.dirname(__file__), "..")

    proc = subprocess.run(
        ["python", "doc_gen/generate_doc.py"], cwd=root_dir, stdout=subprocess.PIPE
    )
    assert normalize(proc.stdout.decode("utf-8")) == normalize(
        readme
    ), "Documentation is out of date. Run 'python doc_gen/generate_doc.py -o readme.md' to update."
