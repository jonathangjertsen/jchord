from setuptools import setup, find_packages

if __name__ == "__main__":
    with open("VERSION.txt") as version_file:
        version = version_file.read().strip()

    with open("README.rst", "r") as readme_file:
        long_description = readme_file.read()

    setup(
        name="jchord",
        version=version,
        description="Python toolkit for working with chord progressions",
        url="https://github.com/jonathangjertsen/jchord",
        author="Jonathan Reichelt Gjertsen",
        author_email="jonath.re@gmail.com",
        long_description=long_description,
        long_description_content_type="text/x-rst",
        packages=find_packages(include=["jchord"]),
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: Implementation :: CPython",
        ],
        extras_require={
            "midi": ["mido"],
            "xlsx": ["openpyxl"],
            "pdf": ["reportlab"],
        },
        entry_points="""
            [console_scripts]
            jchord=jchord.convert:main
        """,
        license="MIT",
        zip_safe=False,
        project_urls={
            "Documentation": "https://github.com/jonathangjertsen/jchord",
            "Source": "https://github.com/jonathangjertsen/jchord",
        },
    )
