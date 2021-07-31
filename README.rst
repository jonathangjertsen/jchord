jchord - toolkit for working with chord progressions
====================================================

.. image:: https://github.com/jonathangjertsen/jchord/actions/workflows/build.yml/badge.svg
    :target: https://github.com/jonathangjertsen/jchord/actions/workflows/build.yml

.. image:: https://codecov.io/gh/jonathangjertsen/jchord/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jonathangjertsen/jchord

``jchord`` provides tools for working with chord progressions.

``jchord``:

* has object representations for notes, chords, and progressions (in the Western 12-tone system)
* knows about naming conventions for chords, and can convert back and forth between objects and names
* can be used as a converter between strings, text files, XLSX files, and MIDI files.

Here is an example that parses a chord progression written as a string, transposes it upwards by 2 semitones,
converts it back to a string and then creates a midi file from it.

   >>> from jchord import ChordProgression, MidiConversionSettings
   >>> prog = ChordProgression.from_string("C -- Fm7 -- C -- G7 -- C -- E7 Am F Bm7b5 E7 Am9 F Bo C69 --")
   >>> prog = prog.transpose(+2)
   >>> print(prog.to_string())
   D       --      Gm7     --
   D       --      A7      --
   D       --      F#7     Bm
   G       C#m7b5  F#7     Bm9
   G       C#o     D69     --
   >>> prog.to_midi(MidiConversionSettings(filename="example.midi", tempo=100, beats_per_chord=2, instrument=4))

For more examples, see the `documentation <https://jonathangjertsen.github.io/jchord/#examples>`_

Documentation
=============

Documentation lives here: `jonathangjertsen.github.io/jchord/ <https://jonathangjertsen.github.io/jchord/>`_

Contributing
============
