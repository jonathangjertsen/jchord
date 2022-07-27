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
* can be used as a converter between strings, text files, XLSX files, and MIDI files.

Get it
======

Basic installation:

   ``pip install jchord``

Installation with dependencies for reading and writing MIDI/XLSX files:

   ``pip install jchord[midi,xlsx]``


Using jchord
============

Here is an example that parses a chord progression written as a string, transposes it upwards by 2 semitones,
converts it back to a string and then creates a midi file from it.

.. literalinclude:: /examples/basic.py
    :language: python
    :lines: 2-

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
