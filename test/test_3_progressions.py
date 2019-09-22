import os

import pytest

from jchord.core import Note
from jchord.midi import note_to_midi
from jchord.chords import Chord, ChordWithRoot
from jchord.progressions import ChordProgression, InvalidProgression, Song, SongSection


def test_empty_progression():
    assert ChordProgression.from_string("").progression == []


def test_single_progression():
    assert ChordProgression.from_string("Cm").progression == [
        ChordWithRoot.from_name("Cm")
    ]


def test_longer_progression():
    assert ChordProgression.from_string("C Fm C G7").progression == [
        ChordWithRoot.from_name("C"),
        ChordWithRoot.from_name("Fm"),
        ChordWithRoot.from_name("C"),
        ChordWithRoot.from_name("G7"),
    ]


def test_empty_chords():
    assert ChordProgression.from_string("").chords() == set()


def test_single_chords():
    assert ChordProgression.from_string("Cm").chords() == {
        ChordWithRoot.from_name("Cm")
    }


def test_longer_chords():
    assert ChordProgression.from_string("C Fm C G7").chords() == {
        ChordWithRoot.from_name("C"),
        ChordWithRoot.from_name("Fm"),
        ChordWithRoot.from_name("G7"),
    }


def test_repetition():
    assert ChordProgression.from_string("C -- Fm G7").progression == [
        ChordWithRoot.from_name("C"),
        ChordWithRoot.from_name("C"),
        ChordWithRoot.from_name("Fm"),
        ChordWithRoot.from_name("G7"),
    ]


def test_repeat_nothing():
    with pytest.raises(InvalidProgression):
        assert ChordProgression.from_string("-- C Fm")


def test_whitespace():
    assert ChordProgression.from_string("C -- Fm G7") == ChordProgression.from_string(
        "     C -- Fm G7    "
    )


def test_multiline():
    assert (
        ChordProgression.from_string(
            """C Fm C G7
               C E7 Am G"""
        ).progression
        == [
            ChordWithRoot.from_name("C"),
            ChordWithRoot.from_name("Fm"),
            ChordWithRoot.from_name("C"),
            ChordWithRoot.from_name("G7"),
            ChordWithRoot.from_name("C"),
            ChordWithRoot.from_name("E7"),
            ChordWithRoot.from_name("Am"),
            ChordWithRoot.from_name("G"),
        ]
    )


def test_from_txt():
    txt_filename_in = os.path.join(
        os.path.dirname(__file__), "test_data", "test_progression.txt"
    )
    assert ChordProgression.from_txt(txt_filename_in) == ChordProgression.from_string(
        """C Fm C G7 C E7 Am G G G G G"""
    )


def test_to_txt():
    txt_filename_in = os.path.join(
        os.path.dirname(__file__), "test_data", "test_progression.txt"
    )
    txt_filename_out = os.path.join(
        os.path.dirname(__file__), "test_data", "test_progression_exported.txt"
    )
    prog = ChordProgression.from_string("""C Fm C G7 C E7 Am G G G G G""")
    try:
        prog.to_txt(txt_filename_out)
        assert ChordProgression.from_txt(txt_filename_in) == prog
    finally:
        os.remove(txt_filename_out)


def test_from_xlsx():
    xlsx_filename_in = os.path.join(
        os.path.dirname(__file__), "test_data", "test_progression.xlsx"
    )
    assert ChordProgression.from_xlsx(xlsx_filename_in) == ChordProgression.from_string(
        """C Fm C G7 C E7 Am G G G G G"""
    )


def test_to_xlsx():
    xlsx_filename_in = os.path.join(
        os.path.dirname(__file__), "test_data", "test_progression.xlsx"
    )
    xlsx_filename_out = os.path.join(
        os.path.dirname(__file__), "test_data", "test_progression_exported.xlsx"
    )
    prog = ChordProgression.from_string("""C Fm C G7 C E7 Am G G G G G""")
    try:
        prog.to_xlsx(xlsx_filename_out)
        assert ChordProgression.from_xlsx(xlsx_filename_in) == prog
    finally:
        os.remove(xlsx_filename_out)


def test_progression_midi():
    assert ChordProgression.from_string("""C Fm G7""").midi() == [
        [note_to_midi(("C", 4)), note_to_midi(("E", 4)), note_to_midi(("G", 4))],
        [note_to_midi(("F", 4)), note_to_midi(("G#", 4)), note_to_midi(("C", 5))],
        [
            note_to_midi(("G", 4)),
            note_to_midi(("B", 4)),
            note_to_midi(("D", 5)),
            note_to_midi(("F", 5)),
        ],
    ]


def test_progression_to_midi():
    midi_filename = os.path.join(
        os.path.dirname(__file__), "test_data", "test_progression.midi"
    )

    try:
        ChordProgression.from_string("""C Fm C G7 C E7 Am G G G G G""").to_midi(
            midi_filename
        )
    finally:
        os.remove(midi_filename)


def test_progression_from_midi():
    midi_filename = os.path.join(
        os.path.dirname(__file__), "test_data", "test_progression.midi"
    )

    original = ChordProgression.from_string("""C Fm C G7 C E7 Am G G G G G""")
    try:
        original.to_midi(midi_filename)
        assert ChordProgression.from_midi_file(midi_filename) == original
    finally:
        os.remove(midi_filename)


def test_song_to_string():
    intro = SongSection("Intro", ChordProgression.from_string("""C Fm G7"""))
    main = SongSection("Main", ChordProgression.from_string("""C Fm C G7 C E7 Am G"""))
    song = Song([intro, main, main])
    assert (
        song.to_string()
        == """Intro
=====
C   Fm  G7

Main (x2)
=========
C   Fm  C   G7
C   E7  Am  G
"""
    )


def test_song_repr():
    intro = SongSection("Intro", ChordProgression.from_string("""C Fm G7"""))
    main = SongSection("Main", ChordProgression.from_string("""C Fm C G7 C E7 Am G"""))
    song = Song([intro, main, main])
    assert song == eval(repr(song))
