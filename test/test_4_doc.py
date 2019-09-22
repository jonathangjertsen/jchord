import filecmp
import os
import subprocess


def test_doc_up_to_date():
    tmp_doc_filename = os.path.join(
        os.path.dirname(__file__), "test_data", "test_doc.md"
    )
    real_readme_filename = os.path.join(os.path.dirname(__file__), "..", "readme.md")
    root_dir = os.path.join(os.path.dirname(__file__), "..")

    try:
        subprocess.run(
            "python doc_gen/generate_doc.py -o {}".format(tmp_doc_filename),
            cwd=root_dir,
        )
        assert filecmp.cmp(
            tmp_doc_filename, real_readme_filename
        ), "Documentation is out of date. Run 'python doc_gen/generate_doc.py' to update."
    finally:
        os.remove(tmp_doc_filename)
