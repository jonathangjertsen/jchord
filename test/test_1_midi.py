from jchord.core import Note
from jchord.midi import get_midi, InvalidNote

import pytest


@pytest.mark.parametrize(
    "note, octave, midi",
    [
        ("A", 0, 21),
        ("A#", 0, 22),
        ("Ab", 0, 20),
        ("Bb", 0, 22),
        ("A#", 1, 22 + 12),
        ("A#", 5, 22 + 12 * 5),
        ("E", 0, 16),
    ],
)
def test_get_midi(note, octave, midi):
    assert get_midi(Note(note, octave)) == midi


def test_get_midi_invalid_note():
    with pytest.raises(InvalidNote):
        get_midi(Note("bA", 0))
