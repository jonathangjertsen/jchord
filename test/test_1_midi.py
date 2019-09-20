from jchord.core import Note
from jchord.midi import get_midi, midi_to_pitch, InvalidNote

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


@pytest.mark.parametrize(
    "midi, pitch",
    [(69, 440), (21, 27.5), (22, 29.135235), (108, 4186.009), (60, 261.62556)],
)
def test_midi_to_pitch(midi, pitch):
    assert midi_to_pitch(midi) == pytest.approx(pitch)
