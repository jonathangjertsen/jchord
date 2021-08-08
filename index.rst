.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. include:: README.rst

Examples
========



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

Working with individual notes: ``Note``
---------------------------------------

A ``Note`` represents one of the musical notes in the Western 12-tone system.
It is identified by its pitch class and octave according to `Scientific pitch notation
<https://en.wikipedia.org/wiki/Scientific_pitch_notation>`_; so ``Note('C', 4)`` is Middle C.

.. autoclass:: jchord.Note
   :members:

Working with individual chords: ``Chord`` and ``ChordWithRoot``
---------------------------------------------------------------

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

Working with chord progressions: ``ChordProgression``
-----------------------------------------------------

A chord progression is represented as a list of chords, one after another.

.. autoclass:: jchord.ChordProgression
   :members: chords, midi, transpose, to_string, to_txt, to_xlsx, to_midi
.. autoclass:: jchord.MidiConversionSettings

MIDI features
-------------

.. automodule:: jchord.midi
   :noindex:
.. autoclass:: jchord.midi_effects.MidiEffect
   :members: set_settings, apply
