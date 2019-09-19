from jchord.chords import Chord, ChordWithRoot, InvalidChord, CHORD_NAMES, CHORD_ALIASES

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
        ("major", "Chord(name=major, semitones=[0, 4, 7])"),
        ("minor", "Chord(name=minor, semitones=[0, 3, 7])"),
        ("5", "Chord(name=5, semitones=[0, 7])"),
        ("", "Chord(name=major, semitones=[0, 4, 7])"),
    ],
)
def test_chord_repr(name_in, repr_out):
    assert repr(Chord.from_name(name_in)) == repr_out


@pytest.mark.parametrize("name_in", list(CHORD_NAMES) + list(CHORD_ALIASES))
def test_chord_add_root(name_in):
    assert Chord.from_name(name_in).with_root("A#") == ChordWithRoot.from_name(
        "A#" + name_in
    )


@pytest.mark.parametrize("name_in", ["goop", "blap", "m8"])
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
    ],
)
def test_chord_with_root(name_in, root_out, semi_out):
    assert ChordWithRoot.from_name(name_in).semitones == semi_out
    assert ChordWithRoot.from_name(name_in).root == root_out


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
def test_chord_get_midi(name_in, octave, midi):
    assert ChordWithRoot.from_name(name_in, octave).midi() == midi


@pytest.mark.parametrize("name_in, shift, name_out", [("A", 2, "B")])
def test_chord_transpose(name_in, name_out, shift):
    assert ChordWithRoot.from_name(name_in).transpose(shift) == ChordWithRoot.from_name(
        name_out
    )


@pytest.mark.parametrize(
    "name_in, repr_out",
    [
        (
            "Amajor",
            "ChordWithRoot(name=Amajor, root=A, chord=Chord(name=major, semitones=[0, 4, 7]), octave=4)",
        ),
        (
            "Bminor",
            "ChordWithRoot(name=Bminor, root=B, chord=Chord(name=minor, semitones=[0, 3, 7]), octave=4)",
        ),
        (
            "D",
            "ChordWithRoot(name=D, root=D, chord=Chord(name=major, semitones=[0, 4, 7]), octave=4)",
        ),
    ],
)
def test_chord_repr(name_in, repr_out):
    assert repr(ChordWithRoot.from_name(name_in)) == repr_out
