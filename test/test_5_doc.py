import filecmp
from os.path import dirname, join
import subprocess
import sys

import pytest


def normalize(string):
    return string.strip().replace("\r\n", "\n")


@pytest.mark.skipif(
    sys.version_info < (3, 7) or sys.version_info > (3, 8),
    reason="Only need to generate documentation for Python 3.7-3.8",
)
def test_doc_up_to_date():
    tmp_doc_filename = join(dirname(__file__), "test_data", "test_doc.md")
    root_dir = dirname(dirname(__file__))
    with open(join(root_dir, "README.md")) as readme_file:
        readme = readme_file.read()

    proc = subprocess.run(
        ["python", "doc_gen/generate_doc.py"], cwd=root_dir, stdout=subprocess.PIPE
    )
    assert normalize(proc.stdout.decode("utf-8")) == normalize(
        readme
    ), "Documentation is out of date. Run 'python doc_gen/generate_doc.py -o README.md' to update."
