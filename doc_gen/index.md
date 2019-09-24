# jchord - Python toolkit for working with chord progressions

[![Build Status](https://travis-ci.com/jonathangjertsen/jchord.svg?branch=master)](https://travis-ci.com/jonathangjertsen/jchord)
[![codecov](https://codecov.io/gh/jonathangjertsen/jchord/branch/master/graph/badge.svg)](https://codecov.io/gh/jonathangjertsen/jchord)

```
>>> from jchord.progressions import ChordProgression
>>> prog = ChordProgression.from_string("C -- Fm7 -- C -- G7 -- C -- E7 Am F Bm7b5 E7 Am9 F Bo C69 --")
>>> print(prog.to_string())
C      --     Fm7    --
C      --     G7     --
C      --     E7     Am
F      Bm7b5  E7     Am9
F      Bo     C69    --
>>> prog.to_midi("example.midi", tempo=100, beats_per_chord=2, instrument=4)
```

* Chord progressions can be imported from:
    - string (`prog = ChordProgression.from_string(string)`)
    - text file (`prog = ChordProgression.from_txt(filename)`)
    - XLSX file (`prog = ChordProgression.from_xlsx(filename)`)
* Chord progressions can be exported to:
    - string (`print(prog.to_string(...optional))`)
    - text file (`prog.to_txt(filename, ..optional)`)
    - XLSX file (`prog.to_xlsx(filename, ...optional)`)
    - MIDI file (`prog.to_midi(filename, ...optional)`)

# Install

* `pip install jchord`
* If you want to use the MIDI and XLSX functionality, also `pip install mido openpyxl`

# Development

Clone the repo, and in the folder run `pip install -r requirements_dev.txt`

## Testing

To run the tests:

```
pytest --cov-report term-missing --cov jchord -vvv
```

Make sure all tests pass and that the code has 100% test coverage.

## Formatting

The code is formatted with black. In the root of the repo, run:

```
black .
```

## Documenting

To generate documentation, run the documentation generation script:

```
python doc_gen/generate_doc.py -o README.md
```

The script appends documentation from each source module to `doc_gen/index.md`. If the script ran successfully, README.md should contain a section called "Documentation" below.

To decide which parts should be present in the documentation, go and edit `doc_gen/pydocmd.yml`. The reason for the format is that I originally wanted to use `pydocmd` (but found it too limiting).
