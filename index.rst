.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. include:: README.rst

Examples
========

The following examples make use of the MIDI subsystem in ``jchord``, which uses the ``mido`` package.
Installing with ``pip install jchord[midi]`` will ensure this package is installed.

Example: Autumn Leaves in two styles
------------------------------------

This example generates two MIDI files: one with fancy synth arpeggios, another with a basic strumming guitar.

.. literalinclude:: /examples/autumn_leaves.py
   :language: python
   :lines: 2-

Example: Parse MIDI
----------------------

``jchord`` can parse MIDI files that are a sequence of block chords.
It uses a kernel density estimation algorithm to group notes into chords, allowing it to handle slight imperfections.
If the file has arpeggios, melodies or other flourishes, it will not work.

.. literalinclude:: /examples/parse_midi.py
   :language: python
   :lines: 2-

Example: Harmonization
----------------------

This example shows the ``Harmonizer`` effect, building 7th chords from single notes. Use the `n` suffix to indicate a single note.

.. literalinclude:: /examples/harmonizer.py
   :language: python
   :lines: 2-

API reference
=============

Objects at a glance
--------------------

These are the key objects defined by `jchord`:

* ``Note``
* ``Intervals``
* ``Chord``
* ``ChordProgression``
* ``Song``

The highest-level object is ``Song``.
A ``Song`` has a ``sections`` property, which is a list of ``ChordProgression`` objects.
A ``ChordProgression`` has a ``progression`` property, which is a list of ``Chord`` objects.
A ``Chord`` object has a ``chord`` property, which is a ``Intervals`` object; and a ``root`` property, which is a ``Note`` object.

Working with individual notes: ``Note``
---------------------------------------

A ``Note`` represents one of the musical notes in the Western 12-tone system.
It is identified by its pitch class and octave according to `Scientific pitch notation
<https://en.wikipedia.org/wiki/Scientific_pitch_notation>`_; so ``Note('C', 4)`` is Middle C.

.. autoclass:: jchord.Note
   :members:

Working with individual chords: ``Intervals`` and ``Chord``
---------------------------------------------------------------

The meaning of a chord is slightly ambiguous, and jchord has two classes to disambiguate
between the case where we refer to a chord *with* a root (say, "Am7" or "C#maj7#11"), and
the case where we refer to the interval structure without reference to any particular root note
(say, "maj7" or "min11"):

* ``Chord`` refers to a root note AND the interval structure.
* ``Intervals`` refers to just the interval structure.

.. autoclass:: jchord.Intervals
   :members: interval_sequence, add_semitone, remove_semitone, rotate_semitones, with_root
.. autoclass:: jchord.Chord
   :members: semitones, bass, interval_sequence, midi, transpose
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
