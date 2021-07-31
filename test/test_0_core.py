from jchord.knowledge import CHROMATIC, ENHARMONIC
from jchord.core import (
    CompositeObject,
    degree_to_semitone,
    InvalidDegree,
    Note,
    note_diff,
    semitone_to_degree_options,
    split_to_base_and_shift,
)

import pytest


@pytest.mark.parametrize(
    "degree, semitone",
    [
        ("1", 0),
        ("b1", -1),
        ("bb1", -2),
        ("bbb1", -3),
        ("#1", 1),
        ("##1", 2),
        ("2", 2),
        ("b2", 1),
        ("#2", 3),
        ("3", 4),
        ("4", 5),
        ("b4", 4),
        ("#4", 6),
        ("5", 7),
        ("b5", 6),
        ("#5", 8),
        ("6", 9),
        ("b6", 8),
        ("#6", 10),
        ("7", 11),
        ("b7", 10),
        ("#7", 12),
        ("9", 14),
        ("b9", 13),
        ("#9", 15),
        ("11", 17),
        ("b11", 16),
        ("#11", 18),
        ("13", 21),
        ("b13", 20),
        ("#13", 22),
    ],
)
def test_degree_to_semitone(degree, semitone):
    assert degree_to_semitone(degree) == semitone


@pytest.mark.parametrize("degree", ["#b1", "b1#", "asdf", "b99"])
def test_degree_to_semitone_invalid_degree(degree):
    with pytest.raises(InvalidDegree):
        assert degree_to_semitone(degree)


@pytest.mark.parametrize(
    "semitone, n_accidentals, options",
    [
        (-1, 0, []),
        (24, 0, []),
        (0, 0, ["1"]),
        (0, 1, ["1"]),
        (0, 2, ["1", "bb2"]),
        (0, 3, ["1", "bb2"]),
        (0, 4, ["1", "bb2", "bbbb3"]),
        (3, 0, []),
        (3, 1, ["b3", "#2"]),
        (4, 0, ["3"]),
        (4, 1, ["3", "b4"]),
        (8, 1, ["b6", "#5"]),
        (17, 1, ["11", "#10"]),
    ],
)
def test_semitone_to_degree_options(semitone, n_accidentals, options):
    assert semitone_to_degree_options(semitone, n_accidentals) == options


@pytest.mark.parametrize(
    "item, base, shift",
    [
        ("A", "A", 0),
        ("A#", "A", 1),
        ("A##", "A", 2),
        ("A###", "A", 3),
        ("Ab", "A", -1),
        ("Abb", "A", -2),
        ("Abbb", "A", -3),
    ],
)
def test_split_to_base_and_shift_after(item, base, shift):
    assert split_to_base_and_shift(item, name_before_accidental=True) == (base, shift)


@pytest.mark.parametrize(
    "item, base, shift",
    [
        ("9", "9", 0),
        ("#9", "9", 1),
        ("##9", "9", 2),
        ("###9", "9", 3),
        ("b9", "9", -1),
        ("bb9", "9", -2),
        ("bbb9", "9", -3),
    ],
)
def test_split_to_base_and_shift_before(item, base, shift):
    assert split_to_base_and_shift(item, name_before_accidental=False) == (base, shift)


@pytest.mark.parametrize(
    "name, octave, the_repr",
    [
        ("A", 0, "Note('A', 0)"),
        ("A", 1, "Note('A', 1)"),
        ("G#", 1, "Note('G#', 1)"),
        ("Db", 133, "Note('Db', 133)"),
    ],
)
def test_note_repr(name, octave, the_repr):
    assert repr(Note(name, octave)) == the_repr
    assert Note(name, octave) == eval(the_repr)


@pytest.mark.parametrize(
    "sharp, flat, octave",
    [(sharp, flat, octave) for sharp, flat in ENHARMONIC for octave in range(-2, 2)],
)
def test_note_eq(sharp, flat, octave):
    assert Note(sharp, octave) == Note(flat, octave)
    assert Note(flat, octave) == Note(sharp, octave)


@pytest.mark.parametrize(
    "note, octave", [(note, octave) for note in CHROMATIC for octave in range(-2, 2)]
)
def test_note_eq_tuple(note, octave):
    assert Note(note, octave) == (note, octave)


@pytest.mark.parametrize(
    "note, octave, other",
    [
        ("A", 0, None),
        ("A", 0, ("A",)),
        ("A", 0, ("A", 1)),
        ("A", 0, ("Ab", 0)),
        ("A", 0, ("A#", 0)),
        ("A", 0, ("E", 0)),
        ("A", 0, ("A", 0, 0)),
    ],
)
def test_note_neq(note, octave, other):
    assert Note(note, octave) != other


@pytest.mark.parametrize(
    "note_in, octave_in, shift, note_out, octave_out",
    # [
    #    (note, octave, n * 12, note, octave + n)
    #    for n in range(-2, 2)
    #    for octave in range(-2, 2)
    #    for note in CHROMATIC
    # ]
    [
        ("C", 0, 1, "C#", 0),
        ("C#", 0, 1, "D", 0),
        ("D", 0, 1, "D#", 0),
        ("B", 0, 1, "C", 1),
        ("B", 1, 1, "C", 2),
        ("Bb", 4, 1, "B", 4),
        ("Bb", 4, -1, "A", 4),
        ("B", 110, 1, "C", 111),
        ("C#", 0, -1, "C", 0),
        ("D", 0, -1, "C#", 0),
        ("D#", 0, -1, "D", 0),
        ("C", 0, -1, "B", -1),
        ("C", 1, -1, "B", 0),
        ("C", 110, -1, "B", 109),
        ("C", 4, 7, "G", 4),
        ("C", 4, 12 + 7, "G", 5),
        ("A", 3, 3, "C", 4),
    ],
)
def test_transpose(note_in, octave_in, shift, note_out, octave_out):
    assert Note(note_in, octave_in).transpose(shift) == (note_out, octave_out)


@pytest.mark.parametrize(
    "note_in, octave_in, shift, down, note_out, octave_out",
    [
        ("C", 0, "b2", False, "C#", 0),
        ("C", 0, "b2", True, "B", -1),
        ("C#", 0, "#1", False, "D", 0),
        ("D", 0, "b2", False, "D#", 0),
        ("B", 0, "b2", False, "C", 1),
        ("B", 1, "#1", False, "C", 2),
        ("B", 110, "#1", False, "C", 111),
        ("C", 4, "5", False, "G", 4),
        ("C", 4, "5", True, "F", 3),
        ("C", 4, "12", False, "G", 5),
        ("A", 3, "b3", False, "C", 4),
    ],
)
def test_transpose_degree(note_in, octave_in, shift, down, note_out, octave_out):
    assert Note(note_in, octave_in).transpose_degree(shift, down) == (
        note_out,
        octave_out,
    )


@pytest.mark.parametrize(
    "note_low, note_high, diff",
    [
        ("A", "A", 0),
        ("A", "A#", 1),
        ("A", "B", 2),
        ("A", "G", 10),
        ("A#", "A", 11),
        ("B", "A", 10),
        ("G", "A", 2),
    ],
)
def test_note_diff(note_low, note_high, diff):
    assert note_diff(note_low, note_high) == diff


@pytest.mark.parametrize(
    "name, octave, pitch",
    [
        ("A", 4, 440),
        ("A", 0, 27.5),
        ("A#", 0, 29.135235),
        ("C", 8, 4186.009),
        ("C", 4, 261.62556),
    ],
)
def test_note_pitch(name, octave, pitch):
    assert Note(name, octave).pitch() == pytest.approx(pitch)


def test_composite_object_equality():
    with pytest.raises(NotImplementedError):
        CompositeObject() == CompositeObject()


def test_composite_object_hash():
    with pytest.raises(NotImplementedError):
        hash(CompositeObject())

    with pytest.raises(NotImplementedError):
        {CompositeObject(): 1}


@pytest.mark.parametrize(
    "args_a, args_b, equal",
    [
        ((1, 2, 3), (1, 2, 3), True),
        ((1, 2, 3), (1, 2, 2), True),
        ((1, 2, 3), (1, 3, 3), False),
    ],
)
def test_composite_object_subclass(args_a, args_b, equal):
    class ConcreteCompositeObject(CompositeObject):
        def __init__(self, a, b, c):
            self.a, self.b, self.c = a, b, c

        def _keys(self):
            return (self.a, self.b)

    assert (
        ConcreteCompositeObject(*args_a) == ConcreteCompositeObject(*args_b)
    ) == equal
    assert (
        {ConcreteCompositeObject(*args_a): 1} == {ConcreteCompositeObject(*args_b): 1}
    ) == equal
