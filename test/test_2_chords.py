from jchord.knowledge import CHORD_NAMES, CHORD_ALIASES
from jchord.core import Note
from jchord.chords import (
    Chord,
    ChordWithRoot,
    InvalidChord,
    semitones_to_chord_name_options,
)

import pytest


@pytest.mark.parametrize(
    "semi_in, semi_out",
    [
        ([1, 2, 3], [0, 1, 2, 3]),
        ([3, 1, 2], [0, 1, 2, 3]),
        ([1, 1, 1], [0, 1]),
        ([], [0]),
        ([1, 8, 1], [0, 1, 8]),
    ],
)
def test_chord_from_semitones(semi_in, semi_out):
    assert Chord.from_semitones("unnamed", semi_in).semitones == semi_out


@pytest.mark.parametrize(
    "semitones, options",
    [
        (set(list(range(100))), []),
        (set(), ["note"]),
        ({0}, ["note"]),
        ({3}, ["min(no5)", "b3 interval", "#2 interval"]),
        ({4}, ["(no5)", "3 interval", "b4 interval"]),
        ({7}, ["5", "5 interval"]),
        ({13}, ["b9 interval", "#8 interval"]),
        ({12}, ["note"]),
        ({2, 7}, ["sus2"]),
        ({3, 7}, ["min"]),
        ({4, 7}, [""]),
        ({5, 7}, ["sus4"]),
        ({6, 7}, ["lyd"]),
        ({3, 6}, ["dim"]),
        ({4, 8}, ["aug"]),
        ({4, 7, 11}, ["maj7", "min/b6"]),
        ({4, 7, 10}, ["7", "dim/b6"]),
        ({3, 7, 10}, ["min7", "/6"]),
        ({3, 6, 10}, ["min7b5", "min/6"]),
        ({3, 6, 9}, ["dim7", "dim/6"]),
        ({4, 8, 11}, ["augmaj7", "/b6"]),
        ({0, 7, 10, 13}, ["dim/4"]),
        ({1, 2, 3}, []),
        ({3, 10}, ["min7(no5)"]),
        ({4, 10}, ["7(no5)"]),
        ({4, 11}, ["maj7(no5)"]),
        ({3, 11}, ["minmaj7(no5)"]),
        ({7, 11}, ["maj7(no3)"]),
        ({7, 10}, ["7(no3)"]),
    ],
)
def test_semitones_to_chord_options(semitones, options):
    assert semitones_to_chord_name_options(semitones) == options
    if options:
        assert Chord.from_semitones(None, semitones).name == options[0]
    else:
        assert Chord.from_semitones(None, semitones).name == Chord.UNNAMED


@pytest.mark.parametrize(
    "deg_in, semi_out",
    [
        (["b2", "2", "#2"], [0, 1, 2, 3]),
        (["#6", "b7"], [0, 10]),
        (["b13", "#9", "b1"], [-1, 0, 15, 20]),
    ],
)
def test_chord_from_degrees(deg_in, semi_out):
    assert Chord.from_degrees("unnamed", deg_in).semitones == semi_out


@pytest.mark.parametrize(
    "name_in, semi_out",
    [
        ("", [0, 4, 7]),
        ("major", [0, 4, 7]),
        ("minor", [0, 3, 7]),
        ("major7", [0, 4, 7, 11]),
        ("m7b5", [0, 3, 6, 10]),
        ("min7b5", [0, 3, 6, 10]),
        ("ø", [0, 3, 6, 10]),
        ("o", [0, 3, 6, 9]),
        ("min", [0, 3, 7]),
        ("m", [0, 3, 7]),
    ],
)
def test_chord_from_degrees(name_in, semi_out):
    assert Chord.from_name(name_in).semitones == semi_out


@pytest.mark.parametrize(
    "name_in, int_out",
    [
        ("", [4, 3]),
        ("5", [7]),
        ("major", [4, 3]),
        ("minor", [3, 4]),
        ("major7", [4, 3, 4]),
        ("m7b5", [3, 3, 4]),
        ("min7b5", [3, 3, 4]),
        ("ø", [3, 3, 4]),
        ("o", [3, 3, 3]),
        ("min", [3, 4]),
        ("m", [3, 4]),
    ],
)
def test_chord_intervals(name_in, int_out):
    assert Chord.from_name(name_in).intervals() == int_out


@pytest.mark.parametrize(
    "name_in, repr_out",
    [
        ("major", "Chord(name='major', semitones=[0, 4, 7])"),
        ("minor", "Chord(name='minor', semitones=[0, 3, 7])"),
        ("5", "Chord(name='5', semitones=[0, 7])"),
        ("", "Chord(name='major', semitones=[0, 4, 7])"),
    ],
)
def test_chord_repr(name_in, repr_out):
    assert repr(Chord.from_name(name_in)) == repr_out
    assert Chord.from_name(name_in) == eval(repr_out)


@pytest.mark.parametrize(
    "name_in, octave",
    [
        (name, octave)
        for name in list(CHORD_NAMES) + list(CHORD_ALIASES)
        for octave in range(-2, 2)
    ],
)
def test_chord_add_root(name_in, octave):
    name_then_root = Chord.from_name(name_in).with_root(Note("A#", octave))
    name_and_root = ChordWithRoot.from_name("A#" + name_in, octave=octave)
    print(name_and_root._keys())
    assert name_then_root == name_and_root


@pytest.mark.parametrize("name_in", ["goop", "blap", "m8", "A/G/G"])
def test_chord_from_invalid_name(name_in):
    with pytest.raises(InvalidChord):
        Chord.from_name(name_in)


@pytest.mark.parametrize(
    "name_in, root_out, semi_out",
    [
        ("A", "A", [0, 4, 7]),
        ("Ab", "Ab", [0, 4, 7]),
        ("A#", "A#", [0, 4, 7]),
        ("Am", "A", [0, 3, 7]),
        ("A#m", "A#", [0, 3, 7]),
        ("Bmin7b5", "B", [0, 3, 6, 10]),
        ("A/G", "A", [-2, 0, 4, 7]),
        ("C#/C", "C#", [-1, 0, 4, 7]),
        ("C/C#", "C", [-11, 0, 4, 7]),
    ],
)
def test_chord_with_root(name_in, root_out, semi_out):
    assert ChordWithRoot.from_name(name_in).semitones == semi_out
    assert ChordWithRoot.from_name(name_in).root.name == root_out


@pytest.mark.parametrize(
    "name_in, int_out",
    [
        ("A", [4, 3]),
        ("B5", [7]),
        ("Cmajor", [4, 3]),
        ("Dminor", [3, 4]),
        ("Emajor7", [4, 3, 4]),
        ("Fm7b5", [3, 3, 4]),
        ("Gmin7b5", [3, 3, 4]),
        ("A#ø", [3, 3, 4]),
        ("B#o", [3, 3, 3]),
        ("Cbmin", [3, 4]),
        ("Dbm", [3, 4]),
    ],
)
def test_chord_intervals(name_in, int_out):
    assert ChordWithRoot.from_name(name_in).intervals() == int_out


@pytest.mark.parametrize("name_in", ["H", "Amoop"])
def test_chord_with_root_invalid_name(name_in):
    with pytest.raises(InvalidChord):
        assert ChordWithRoot.from_name(name_in)


@pytest.mark.parametrize("name_in, octave, midi", [("A", 0, [21, 25, 28])])
def test_chord_note_to_midi(name_in, octave, midi):
    assert ChordWithRoot.from_name(name_in, octave).midi() == midi


@pytest.mark.parametrize("name_in, shift, name_out", [("A", 2, "B")])
def test_chord_transpose(name_in, name_out, shift):
    assert ChordWithRoot.from_name(name_in).transpose(shift) == ChordWithRoot.from_name(
        name_out
    )


@pytest.mark.parametrize("name_in", ["Amajor", "Bminor", "D"])
def test_chord_repr(name_in):
    assert ChordWithRoot.from_name(name_in) == eval(
        repr(ChordWithRoot.from_name(name_in))
    )


@pytest.mark.parametrize(
    "root, semitones, name",
    [
        ("A", {3}, "Amin(no5)"),
        ("B", {4}, "B(no5)"),
        ("C", {7}, "C5"),
        ("C#", {3, 7}, "C#min"),
        ("Db", {4, 7}, "Db"),
        ("F#", {5, 7}, "F#sus4"),
        ("A", {3, 6, 9}, "Adim7"),
        ("G", {4, 8, 11}, "Gaugmaj7"),
        ("A", {0, 7, 10, 13}, "Edim/A"),
        ("B", {3, 10}, "Bmin7(no5)"),
        ("Bb", {4, 10}, "Bb7(no5)"),
        ("E#", {4, 11}, "E#maj7(no5)"),
    ],
)
def test_chord_from_root_and_semitone(root, semitones, name):
    assert ChordWithRoot.from_root_and_semitones(Note(root, 4), semitones).name == name


@pytest.mark.parametrize(
    "midi, name",
    [
        ({22, 26, 29}, "A#"),
        ({22, 23, 24, 25, 26}, "A#???"),
        ({22, 25, 29}, "A#min"),
        ({23, 26, 30, 34}, "Bminmaj7"),
    ],
)
def test_chord_from_midi(midi, name):
    assert ChordWithRoot.from_midi(midi).name == name
