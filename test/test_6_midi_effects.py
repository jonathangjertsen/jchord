import random

import pytest

from jchord.midi import MidiNote
from jchord.midi_effects import (
    AlternatingInverter,
    Chain,
    Doubler,
    Inverter,
    Spreader,
    Transposer,
)


def notes(ints):
    return [MidiNote(note=x, time=0, duration=0, velocity=0) for x in ints]


def test_interter():
    assert Inverter().apply(notes([1, 2, 4, 3])) == notes([3, 4, 2, 1])


def test_alternating_inverter():
    effect = AlternatingInverter(init_state=1)
    assert effect.apply(notes([1, 2, 4, 3])) == notes([3, 4, 2, 1])
    assert effect.apply(notes([1, 2, 4, 3])) == notes([1, 2, 4, 3])
    assert effect.apply(notes([1, 2, 4, 3])) == notes([3, 4, 2, 1])

    effect = AlternatingInverter(init_state=0)
    assert effect.apply(notes([1, 2, 4, 3])) == notes([1, 2, 4, 3])
    assert effect.apply(notes([1, 2, 4, 3])) == notes([3, 4, 2, 1])
    assert effect.apply(notes([1, 2, 4, 3])) == notes([1, 2, 4, 3])


def test_transposer():
    assert Transposer(1).apply(notes([1, 2, 3, 4])) == notes([2, 3, 4, 5])
    assert Transposer(-2).apply(notes([1, 2, 3, 4])) == notes([-1, 0, 1, 2])


def test_doubler():
    assert Doubler(1).apply(notes([1, 2, 3, 4])) == notes([1, 2, 3, 4, 5])
    assert Doubler(-2).apply(notes([1, 2, 3, 4])) == notes([-1, 0, 1, 2, 3, 4])


def test_spreader():
    assert Spreader(amount=10, jitter=0).apply(notes([1, 2, 3, 4])) == [
        MidiNote(time=pytest.approx(0.0), note=1, duration=0, velocity=0),
        MidiNote(time=pytest.approx(10.0), note=2, duration=0, velocity=0),
        MidiNote(time=pytest.approx(20.0), note=3, duration=0, velocity=0),
        MidiNote(time=pytest.approx(30.0), note=4, duration=0, velocity=0),
    ]

    random.seed(0)
    assert Spreader(amount=10, jitter=10).apply(notes([1, 2, 3, 4])) == [
        MidiNote(time=pytest.approx(6.888437030500962), note=1, duration=0, velocity=0),
        MidiNote(
            time=pytest.approx(15.159088058806049), note=2, duration=0, velocity=0
        ),
        MidiNote(
            time=pytest.approx(18.411431616616902), note=3, duration=0, velocity=0
        ),
        MidiNote(
            time=pytest.approx(25.178335005859267), note=4, duration=0, velocity=0
        ),
    ]


def test_chain():
    assert Chain(Doubler(12), Spreader(amount=10, jitter=0), Inverter()).apply(
        notes([1, 2, 3, 4, 12])
    ) == [
        MidiNote(time=90.0, note=24, duration=0, velocity=0),
        MidiNote(time=80.0, note=16, duration=0, velocity=0),
        MidiNote(time=70.0, note=15, duration=0, velocity=0),
        MidiNote(time=60.0, note=14, duration=0, velocity=0),
        MidiNote(time=50.0, note=13, duration=0, velocity=0),
        MidiNote(time=40.0, note=12, duration=0, velocity=0),
        MidiNote(time=30.0, note=4, duration=0, velocity=0),
        MidiNote(time=20.0, note=3, duration=0, velocity=0),
        MidiNote(time=10.0, note=2, duration=0, velocity=0),
        MidiNote(time=0.0, note=1, duration=0, velocity=0),
    ]
