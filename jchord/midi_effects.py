import random
from typing import List

from jchord.core import Note
from jchord.midi import MidiNote, midi_to_note
from jchord.progressions import MidiConversionSettings


class MidiEffect(object):
    """Base class for MIDI effects"""

    def __init__(self, *args, **kwargs):
        """
        Nothing to configure
        """

    def set_settings(self, settings: MidiConversionSettings):
        """
        Makes the MIDI conversion settings available.
        This is always applied before apply() during the MIDI conversion
        """
        self.settings = settings

    def apply(self, chord: List[MidiNote]):
        """
        Returns a list where the effect has been applied to the given chord
        """
        raise NotImplementedError


class Chain(MidiEffect):
    """
    Used to combine several effects in a row
    """

    def __init__(self, *effects):
        self.effects = effects

    def set_settings(self, settings: MidiConversionSettings):
        for effect in self.effects:
            effect.set_settings(settings)

    def apply(self, chord):
        for effect in self.effects:
            chord = effect.apply(chord)
        return chord


class Inverter(MidiEffect):
    """
    Returns the list of notes in the opposite order

    This only matters if the notes have different times
    """

    def apply(self, chord):
        return list(reversed(chord))


class AlternatingInverter(MidiEffect):
    """
    Alternates between returning the list of notes in the opposite order and the original order

    Could be used to implement some kind of strumming effect
    """

    def __init__(self, init_state=1):
        self.state = init_state

    def apply(self, chord):
        if self.state == 0:
            self.state = 1
            return chord
        else:
            self.state = 0
            return list(reversed(chord))


class Transposer(MidiEffect):
    """
    Transposes all the notes by the specified interval
    """

    def __init__(self, interval):
        self.interval = interval

    def apply(self, chord):
        return sorted(
            list({note._replace(note=note.note + self.interval) for note in chord})
        )


class Doubler(MidiEffect):
    """
    Adds a transposed copy shifted by the specified interval

    Duplicated notes will not be present
    """

    def __init__(self, interval):
        self.transposer = Transposer(interval)

    def apply(self, chord):
        return sorted(list(set(chord) | set(self.transposer.apply(chord))))


class Spreader(MidiEffect):
    """
    Spreads the notes in time by the specified amount
    Jitter can be used to randomize the spread by some amount
    """

    def __init__(self, amount, jitter):
        """
        Parameters:
        * amount: number of MIDI ticks to delay each subsequent note (each bar is 1920 ticks)
        * jitter: maximum number of MIDI ticks by which to randomize each note's arrival time
        """
        self.amount = amount
        self.jitter = jitter

    def apply(self, chord):
        displacement = 0
        for i, note in enumerate(chord):
            chord[i] = note._replace(
                time=note.time + displacement + self.jitter * (random.random() * 2 - 1)
            )
            displacement += self.amount
        return chord


class Arpeggiator(MidiEffect):
    """
    Arpeggiation effect
    """

    def __init__(self, rate: float, pattern: list, sticky=False):
        """
        Parameters:
        * rate (1/8 gives eight notes, 1/16 gives quarter notes etc)
        * pattern: List of indices into each chord.
                   Each index is modulo'd with the length of the chord, so out-of-bounds indices are OK.
                   Will be cycled through for as long as the chord is held.
                   Negative indices work like usual.
        * sticky: If True, the arpeggiator will keep its place in the pattern
                  If False, it will restart with every chord
        """
        self.rate = rate
        self.pattern = pattern
        self.sticky = sticky
        self.offset = 0

    def apply(self, chord):
        min_start = float("inf")
        max_stop = -float("inf")
        for note in chord:
            min_start = min(min_start, note.time)
            max_stop = max(max_stop, note.time + note.duration)
        duration = max_stop - min_start
        one_beat = 1920
        ticks_per_note = self.rate * one_beat
        out = []
        total_duration = 0
        i = 0
        while total_duration < duration:
            indices = self.pattern[(i + self.offset) % len(self.pattern)]
            if isinstance(indices, int):
                indices = [indices]
            for index in indices:
                note = chord[index % len(chord)]
                out.append(
                    MidiNote(
                        time=note.time + int(ticks_per_note * i),
                        duration=ticks_per_note,
                        note=note.note,
                        velocity=self.settings.velocity,
                    )
                )
            i += 1
            total_duration += ticks_per_note
        self.offset += i * self.sticky
        return out


class Shuffle(MidiEffect):
    def __init__(self, percent=100 * 2 / 3, base_rate=1 / 16, tolerance_ticks=100):
        """ """
        self.base_rate = base_rate
        self.percent = percent
        self.tolerance_ticks = tolerance_ticks

    def apply(self, chord):
        dt = 1920 * self.base_rate
        two_dt = 2 * dt
        out = []
        for note in chord:
            rel_time = note.time % two_dt
            if dt - self.tolerance_ticks <= rel_time <= dt + self.tolerance_ticks:
                shift = (self.percent - 50) * dt / 100
                out.append(note._replace(time=note.time + shift))
            else:
                out.append(note)
        return out


class VelocityControl(MidiEffect):
    def __init__(self, keyframes):
        self.keyframes_ticks = sorted(
            [(bar * 1920, velocity) for bar, velocity in keyframes]
        )
        self.duration = max(bar for bar, velocity in self.keyframes_ticks) - min(
            bar for bar, velocity in self.keyframes_ticks
        )

    def apply(self, chord):
        out = []
        for note in chord:
            t = note.time % self.duration
            for t0, v0 in reversed(self.keyframes_ticks):
                if t0 < t:
                    break
            for t1, v1 in self.keyframes_ticks:
                if t1 > t:
                    break
            v = v0 + (t - t0) * (v1 - v0) / (t1 - t0)
            out.append(note._replace(velocity=v))
        return out


class Harmonizer(MidiEffect):
    """
    Adds a transposed copy shifted by the specified interval
    """

    def __init__(self, scale, degrees, root):
        self.scale = scale
        self.degrees = degrees
        self.root = Note(root, octave=4)
        assert scale[0] == 0
        assert all(degree >= 1 for degree in degrees)

    def apply(self, chord):
        out = []
        for note in chord:
            out.append(note)
            offset = (midi_to_note(note.note) - self.root) % 12
            if offset not in self.scale:
                raise ValueError(
                    "Note with MIDI number {} is not in the scale (offset from root is {}, should be one of: {})".format(
                        note.note, offset, self.scale
                    )
                )
            degree_in = self.scale.index(offset)
            for degree in self.degrees:
                scale_out = self.scale[(degree_in + degree - 1) % len(self.scale)]
                semitones_diff = (scale_out - offset) % 12
                out.append(note._replace(note=note.note + semitones_diff))
        return out
