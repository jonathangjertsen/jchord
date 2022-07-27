jchord - toolkit for working with chord progressions
====================================================

.. image:: https://github.com/jonathangjertsen/jchord/actions/workflows/build.yml/badge.svg
    :target: https://github.com/jonathangjertsen/jchord/actions/workflows/build.yml

.. image:: https://codecov.io/gh/jonathangjertsen/jchord/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jonathangjertsen/jchord

What's this then?
=================

``jchord`` is a Python package which provides tools for working with chord progressions. ``jchord``:

* has object representations for notes, chords, and progressions (in the Western 12-tone system)
* knows about naming conventions for chords, and can convert back and forth between objects and names
* can be used as a converter between strings, text files, XLSX files, PDFs and MIDI files (see "converter script" below)

Get it
======

Basic installation:

   ``pip install jchord``

Installation with dependencies for reading and writing MIDI/XLSX/PDF files:

   ``pip install jchord[midi,xlsx,pdf]``


Convert between formats
=======================

.. highlight:: none

If you just want the converter functionality, invoke `jchord` on the command line::

   usage: jchord [-h] [--midi MIDI] [--pdf PDF] file_in file_out

   Converts between different representations of the same format

   positional arguments:
     file_in      Input progression as string, .txt, .xlsx or .midi
     file_out     Output file as .txt, .xlsx, .midi or .pdf

   optional arguments:
     -h, --help   show this help message and exit
     --midi MIDI  comma separated list of arguments for midi, e.g. tempo=8,beats_per_chord=2
     --pdf PDF    comma separated list of arguments for pdf, e.g. chords_per_row=8,fontsize=30

.. highlight:: bash

Example::

   jchord "Cm A E7 F#m7" example.mid --midi tempo=80,beats_per_chord=1

As a library
============

.. highlight:: python

Here is an example that parses a chord progression written as a string, transposes it upwards by 2 semitones,
converts it back to a string and then creates a midi file from it.::


   from jchord import ChordProgression, MidiConversionSettings
   prog = ChordProgression.from_string("C -- Fm7 -- C -- G7 -- C -- E7 Am F Bm7b5 E7 Am9 F Bo C69 --")
   prog = prog.transpose(+2)
   print(prog.to_string())
   prog.to_midi(MidiConversionSettings(filename="example.midi", tempo=100, beats_per_chord=2, instrument=4))

.. highlight:: none

Output::

   D       --      Gm7     --
   D       --      A7      --
   D       --      F#7     Bm
   G       C#m7b5  F#7     Bm9
   G       C#o     D69     --

For more examples, see the `documentation <https://jonathangjertsen.github.io/jchord/#examples>`_.

Documentation
=============

Documentation lives here: `jonathangjertsen.github.io/jchord/ <https://jonathangjertsen.github.io/jchord/>`_

Contributing
============

To contribute, open an issue or create a Pull Request in the `Github repo <https://github.com/jonathangjertsen/jchord>`_.
