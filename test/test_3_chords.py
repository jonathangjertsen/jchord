from jchord.knowledge import CHORD_NAMES, CHORD_ALIASES
from jchord.core import Note
from jchord.chords import (
    Intervals,
    Chord,
    InvalidChord,
    semitones_to_name_options,
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
    assert Intervals.from_semitones(semi_in).semitones == semi_out


@pytest.mark.parametrize(
    "semitones, options, selected",
    [
        (set(list(range(100))), [], Intervals.UNNAMED),
        (set(), ["note"], "note"),
        ({0}, ["note"], "note"),
        ({3}, ["min(no5)", "b3 interval", "#2 interval"], "min(no5)"),
        ({4}, ["(no5)", "3 interval", "b4 interval"], "(no5)"),
        ({7}, ["5", "5 interval"], "5"),
        ({13}, ["b9 interval", "#8 interval"], "b9 interval"),
        ({12}, ["note"], "note"),
        ({2, 7}, ["sus2"], "sus2"),
        ({3, 7}, ["min"], "min"),
        ({4, 7}, [""], ""),
        ({5, 7}, ["sus4"], "sus4"),
        ({6, 7}, ["lyd"], "lyd"),
        ({3, 6}, ["dim"], "dim"),
        ({4, 8}, ["aug"], "aug"),
        ({4, 7, 11}, ["maj7", "min/b6"], "maj7"),
        ({4, 7, 10}, ["7", "dim/b6"], "7"),
        ({3, 7, 10}, ["min7", "/6"], "min7"),
        ({3, 6, 10}, ["min7b5", "min/6"], "min7b5"),
        ({3, 6, 9}, ["dim7", "dim/6"], "dim7"),
        ({4, 8, 11}, ["augmaj7", "/b6"], "augmaj7"),
        ({0, 7, 10, 13}, ["dim/4", "phryg7"], "phryg7"),
        ({1, 2, 3}, [], Intervals.UNNAMED),
        ({3, 10}, ["min7(no5)"], "min7(no5)"),
        ({4, 10}, ["7(no5)"], "7(no5)"),
        ({4, 11}, ["maj7(no5)"], "maj7(no5)"),
        ({3, 11}, ["minmaj7(no5)"], "minmaj7(no5)"),
        ({7, 11}, ["maj7(no3)"], "maj7(no3)"),
        ({7, 10}, ["7(no3)"], "7(no3)"),
        ({7, 12, 16}, [""], ""),
        ({7, 12, 15}, ["min"], "min"),
        ({7, 10, 12, 15}, ["min7"], "min7"),
        ({2, 7, 10, 12}, ["7sus2"], "7sus2"),
        ({5, 7, 10, 12}, ["7sus4"], "7sus4"),
        ({2, 7, 11, 12}, ["maj7sus2"], "maj7sus2"),
    ],
)
def test_semitones_to_chord_options(semitones, options, selected):
    computed_options = semitones_to_name_options(semitones)
    assert set(computed_options) >= set(options)
    assert Intervals.from_semitones(semitones).name == selected


@pytest.mark.parametrize(
    "deg_in, semi_out",
    [
        (["b2", "2", "#2"], [0, 1, 2, 3]),
        (["#6", "b7"], [0, 10]),
        (["b13", "#9", "b1"], [-1, 0, 15, 20]),
    ],
)
def test_chord_from_degrees(deg_in, semi_out):
    assert Intervals.from_degrees(deg_in).semitones == semi_out


@pytest.mark.parametrize(
    "name_in, semi_out",
    [
        ("", [0, 4, 7]),
        ("major", [0, 4, 7]),
        ("inv1", [4, 7, 12]),
        ("inv2", [7, 12, 16]),
        ("inv3", [0, 4, 7]),
        ("inv4", [4, 7, 12]),
        ("inv5", [7, 12, 16]),
        ("inv6", [0, 4, 7]),
        ("inv7", [4, 7, 12]),
        ("minor", [0, 3, 7]),
        ("sus2", [0, 2, 7]),
        ("sus4", [0, 5, 7]),
        ("7sus4", [0, 5, 7, 10]),
        ("m7sus4b9no5", [0, 3, 5, 10, 13]),
        ("augsus2", [0, 2, 8]),
        ("major7", [0, 4, 7, 11]),
        ("m7b5", [0, 3, 6, 10]),
        ("min7b5", [0, 3, 6, 10]),
        ("ø", [0, 3, 6, 10]),
        ("o", [0, 3, 6, 9]),
        ("min", [0, 3, 7]),
        ("m", [0, 3, 7]),
        ("13", [0, 4, 7, 10, 14, 17, 21]),
        ("13no5no7b11#9", [0, 4, 10, 15, 16, 21]),
        ("13b11#9no5no7", [0, 4, 15, 16, 21]),
        ("13b11#9no5no7inv2", [0, 3, 4, 9]),
        ("7#9", [0, 4, 7, 10, 15]),
        ("7b9", [0, 4, 7, 10, 13]),
        ("7b11", [0, 4, 7, 10, 14, 16]),
        ("7#11", [0, 4, 7, 10, 14, 18]),
        ("7b13", [0, 4, 7, 10, 14, 17, 20]),
        ("7#13", [0, 4, 7, 10, 14, 17, 22]),
        ("addb9", [0, 4, 7, 13]),
        ("add9", [0, 4, 7, 14]),
        ("add#9", [0, 4, 7, 15]),
        ("addb11", [0, 4, 7, 16]),
        ("add11", [0, 4, 7, 17]),
        ("add#11", [0, 4, 7, 18]),
        ("addb13", [0, 4, 7, 20]),
        ("add13", [0, 4, 7, 21]),
        ("add#13", [0, 4, 7, 22]),
    ],
)
def test_chord_from_name_semitones(name_in, semi_out):
    assert Intervals.from_name(name_in).semitones == semi_out


@pytest.mark.parametrize(
    "name_in, modifications",
    [
        ("", []),
        ("major", []),
        ("minor", []),
        ("sus2", ["sus2"]),
        ("sus4", ["sus4"]),
        ("7sus4", ["sus4"]),
        ("m7sus4b9no5", ["sus4", "b9", "no5"]),
        ("augsus2", ["sus2"]),
        ("major7", []),
        ("m7b5", ["b5"]),
        ("min7b5", ["b5"]),
        ("ø", []),
        ("o", []),
        ("min", []),
        ("m", []),
        ("13", []),
        ("13no5no7b11#9", ["no5", "no7", "b11", "#9"]),
        ("13b11#9no5no7", ["b11", "#9", "no5", "no7"]),
        ("7#9", ["#9"]),
        ("7b9", ["b9"]),
        ("7b11", ["b11"]),
        ("7#11", ["#11"]),
        ("7b13", ["b13"]),
        ("7#13", ["#13"]),
        ("addb9", ["addb9"]),
        ("add9", ["add9"]),
        ("add#9", ["add#9"]),
        ("addb11", ["addb11"]),
        ("add11", ["add11"]),
        ("add#11", ["add#11"]),
        ("addb13", ["addb13"]),
        ("add13", ["add13"]),
        ("add#13", ["add#13"]),
    ],
)
def test_chord_from_name_modifications(name_in, modifications):
    assert Intervals.from_name(name_in).modifications == modifications


# These could be improved
@pytest.mark.parametrize(
    "name_in, name_out",
    [
        ("", ""),
        ("major", ""),
        ("minor", "min"),
        ("min", "min"),
        ("m", "min"),
        ("sus2", "sus2"),
        ("sus4", "sus4"),
        ("7sus4", "7sus4"),
        ("m7sus4b9no5", Intervals.UNNAMED),
        ("augsus2", Intervals.UNNAMED),
        ("major7", "maj7"),
        ("m7b5", "min7b5"),
        ("min7b5", "min7b5"),
        ("ø", "min7b5"),
        ("o", "dim7"),
        ("13", Intervals.UNNAMED),
        ("13no5no7b11#9", Intervals.UNNAMED),
        ("13b11#9no5no7", "maj7sus4(no5)/b6"),
        ("7#9", Intervals.UNNAMED),
        ("7b9", Intervals.UNNAMED),
        ("7b11", Intervals.UNNAMED),
        ("7#11", Intervals.UNNAMED),
        ("7b13", Intervals.UNNAMED),
        ("7#13", Intervals.UNNAMED),
        ("addb9", "dim/7"),
        ("add9", "min7(no5)/b6"),
        ("add#9", "minmaj7(no5)/b6"),
        ("addb11", ""),
        ("add11", Intervals.UNNAMED),
        ("add#11", Intervals.UNNAMED),
        ("addb13", Intervals.UNNAMED),
        ("add13", Intervals.UNNAMED),
        ("add#13", "7"),
    ],
)
def test_chord_name_roundtrip(name_in, name_out):
    assert (
        Intervals.from_semitones(Intervals.from_name(name_in).semitones).name
        == name_out
    )


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
def test_chord_from_name_intervals(name_in, int_out):
    assert Intervals.from_name(name_in).interval_sequence() == int_out


@pytest.mark.parametrize(
    "name_in, repr_out",
    [
        ("major", "Intervals(name='major', semitones=[0, 4, 7])"),
        ("minor", "Intervals(name='minor', semitones=[0, 3, 7])"),
        ("5", "Intervals(name='5', semitones=[0, 7])"),
        ("", "Intervals(name='', semitones=[0, 4, 7])"),
    ],
)
def test_chord_repr(name_in, repr_out):
    assert repr(Intervals.from_name(name_in)) == repr_out
    assert Intervals.from_name(name_in) == eval(repr_out)


@pytest.mark.parametrize(
    "name_in, octave",
    [
        (name, octave)
        for name in list(CHORD_NAMES) + list(CHORD_ALIASES)
        for octave in range(-2, 2)
    ],
)
def test_chord_add_root(name_in, octave):
    name_then_root = Intervals.from_name(name_in).with_root(Note("A#", octave))
    name_and_root = Chord.from_name(f"{octave}A#{name_in}")
    assert name_then_root == name_and_root


@pytest.mark.parametrize("name_in", ["goop", "blap", "m8", "A/G/G"])
def test_chord_from_invalid_name(name_in):
    with pytest.raises(InvalidChord):
        Intervals.from_name(name_in)


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
    assert Chord.from_name(name_in).semitones == semi_out
    assert Chord.from_name(name_in).root.name == root_out


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
def test_chord_with_root_intervals(name_in, int_out):
    assert Chord.from_name(name_in).interval_sequence() == int_out


@pytest.mark.parametrize("name_in", ["H", "Amoop"])
def test_chord_with_root_invalid_name(name_in):
    with pytest.raises(InvalidChord):
        assert Chord.from_name(name_in)


@pytest.mark.parametrize("name_in, midi", [("0A", [21, 25, 28])])
def test_chord_note_to_midi(name_in, midi):
    assert Chord.from_name(name_in).midi() == midi


@pytest.mark.parametrize("name_in, shift, name_out", [("A", 2, "B")])
def test_chord_transpose(name_in, name_out, shift):
    assert Chord.from_name(name_in).transpose(shift) == Chord.from_name(name_out)


@pytest.mark.parametrize("name_in", ["Amajor", "Bminor", "D"])
def test_chord_with_root_repr(name_in):
    assert Chord.from_name(name_in) == eval(repr(Chord.from_name(name_in)))


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
        ("A", {0, 7, 10, 13}, "Aphryg7"),
        ("B", {3, 10}, "Bmin7(no5)"),
        ("Bb", {4, 10}, "Bb7(no5)"),
        ("E#", {4, 11}, "E#maj7(no5)"),
    ],
)
def test_chord_from_root_and_semitone(root, semitones, name):
    assert Chord.from_root_and_semitones(Note(root, 4), semitones).name == name


@pytest.mark.parametrize(
    "midi, name",
    [
        ({22, 26, 29}, "A#"),
        ({22, 23, 24, 25, 26}, "A#<unknown>"),
        ({22, 25, 29}, "A#min"),
        ({23, 26, 30, 34}, "Bminmaj7"),
    ],
)
def test_chord_from_midi(midi, name):
    assert Chord.from_midi(midi).name == name
