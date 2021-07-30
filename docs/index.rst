.. toctree::
   :maxdepth: 2
   :caption: Contents:

jchord - toolkit for working with chord progressions
====================================================

``jchord`` provides tools for working with chord progressions.

``jchord``:

* has object representations for notes, chords, and progressions (in the Western 12-tone system)
* knows about naming conventions for chords, and can convert back and forth between objects and names
* can be used as a converter between strings, text files, XLSX files, and MIDI files.

Example
=======

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

API reference
=============

Objects at a glance
--------------------

These are the key objects defined by `jchord`:

* ``Note``
* ``Chord``
* ``ChordWithRoot``
* ``ChordProgression``
* ``Song``

The highest-level object is ``Song``.
A ``Song`` has a ``sections`` property, which is a list of ``ChordProgression`` objects.
A ``ChordProgression`` has a ``progression`` property, which is a list of ``ChordWithRoot`` objects.
A ``ChordWithRoot`` object has a ``chord`` property, which is a ``Chord`` object; and a ``root`` property, which is a ``Note`` object.

Working with individual notes
-----------------------------

A ``Note`` represents one of the musical notes in the Western 12-tone system.
It is identified by its pitch class and octave according to `Scientific pitch notation
<https://en.wikipedia.org/wiki/Scientific_pitch_notation>`_; so ``Note('C', 4)`` is Middle C.

.. autoclass:: jchord.Note
   :members:

Working with individual chords
------------------------------

The meaning of a chord is slightly ambiguous, and jchord has two classes to disambiguate
between the case where we refer to a chord *with* a root (say, "Am7" or "C#maj7#11"), and
the case where we refer to the interval structure without reference to any particular root note
(say, "maj7" or "min11"):

* ``ChordWithRoot`` refers to a root note AND the interval structure.
* ``Chord`` refers to just the interval structure.

.. autoclass:: jchord.Chord
   :members: intervals, add_semitone, remove_semitone, rotate_semitones, with_root
.. autoclass:: jchord.ChordWithRoot
   :members: semitones, bass, intervals, midi, transpose
.. autoclass:: jchord.InvalidChord

Working with chord progressions
-------------------------------

A chord progression is represented as a list of chords, one after another.

.. autoclass:: jchord.ChordProgression
   :members: chords, midi, transpose, to_string, to_txt, to_xlsx, to_midi
.. autoclass:: jchord.MidiConversionSettings
