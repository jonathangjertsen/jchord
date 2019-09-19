from jchord.core import (
    degree_to_semitone,
    LETTERS,
    ACCIDENTALS,
    CompositeObject,
    transpose,
)
from jchord.midi import get_midi


class InvalidChord(Exception):
    pass


CHORD_NAMES = {
    # Major
    "maj": ["3", "5"],
    "maj7": ["3", "5", "7"],
    "maj9": ["3", "5", "7", "9"],
    "maj11": ["3", "5", "7", "9", "11"],
    "maj13": ["3", "5", "7", "9", "11", "13"],
    "6": ["3", "5", "6"],
    "69": ["3", "5", "6", "9"],
    "5": ["5"],
    # Dominant
    "7": ["3", "5", "b7"],
    "9": ["3", "5", "b7", "9"],
    "7#9": ["3", "5", "b7", "#9"],
    "7b9": ["3", "5", "b7", "b9"],
    "11": ["3", "5", "b7", "9", "11"],
    "7b11": ["3", "5", "b7", "9", "b11"],
    "7#11": ["3", "5", "b7", "9", "#11"],
    "13": ["3", "5", "b7", "9", "11", "13"],
    "7b13": ["3", "5", "b7", "9", "11", "b13"],
    "7#13": ["3", "5", "b7", "9", "11", "#13"],
    # Minor
    "m": ["b3", "5"],
    "m6": ["b3", "5", "6"],
    "m7": ["b3", "5", "b7"],
    "m9": ["b3", "5", "b7", "9"],
    "m11": ["b3", "5", "b7", "9", "11"],
    "m13": ["b3", "5", "b7", "9", "11", "13"],
    # Diminished
    "dim": ["b3", "b5"],
    "m7b5": ["b3", "b5", "b7"],
    "dim7": ["b3", "b5", "bb7"],
    # Augmented
    "aug": ["3", "#5"],
    # Suspended
    "sus2": ["2", "5"],
    "sus4": ["4", "5"],
    "7sus2": ["2", "5", "b7"],
    "7sus4": ["4", "5", "b7"],
}

CHORD_ALIASES = {
    # Major
    "major": "maj",
    "maj": "maj",
    # Minor
    "-": "m",
    "min": "m",
    "minor": "m",
    # Dominant
    "dom": "7",
    # Diminished
    "o": "dim7",
    "ø": "m7b5",
    # Augmented
    "+": "aug",
}


class Chord(CompositeObject):
    def __init__(self, name, semitones):
        self.name = name

        semitone_set = set(semitones)
        semitone_set.add(0)
        self.semitones = sorted(list(semitone_set))

    def __repr__(self):
        return "Chord(name={}, semitones={})".format(self.name, self.semitones)

    def _keys(self):
        return tuple(self.semitones)

    @classmethod
    def from_semitones(cls, name, semitones):
        return cls(name, semitones)

    @classmethod
    def from_degrees(cls, name, degrees):
        return cls(name, [degree_to_semitone(degree) for degree in degrees])

    @classmethod
    def from_name(cls, name):
        # Very special case: empty string is major
        if name == "":
            return cls.from_name("major")

        # Look it up in the canonical names
        if name in CHORD_NAMES:
            return cls.from_degrees(name, CHORD_NAMES[name])

        # Look it up in the chord aliases
        for alias in CHORD_ALIASES:
            if alias in name:
                canonical = name.replace(alias, CHORD_ALIASES[alias])
                if canonical in CHORD_NAMES:
                    return cls.from_degrees(name, CHORD_NAMES[canonical])

        # Nope
        raise InvalidChord("No chord found for name: {}".format(name))

    def intervals(self):
        intervals = []
        for i in range(1, len(self.semitones)):
            intervals.append(self.semitones[i] - self.semitones[i - 1])
        return intervals

    def with_root(self, root):
        return ChordWithRoot(root + self.name, root, self)


class ChordWithRoot(CompositeObject):
    def __init__(self, name, root, chord: Chord, octave=4):
        self.name = name
        self.root = root
        self.octave = octave
        self.chord = chord
        self.semitones = chord.semitones

    def __repr__(self):
        return "ChordWithRoot(name={}, root={}, chord={}, octave={})".format(
            self.name, self.root, self.chord, self.octave
        )

    def _keys(self):
        return (self.chord, self.root, self.octave)

    @classmethod
    def from_name(cls, name, octave=4):
        root = None

        for letter in LETTERS:
            if name.startswith(letter):
                root_no_accidental = letter
                break
        else:
            raise InvalidChord(name)

        # Very special case: major chord with no accidentals
        if len(name) == len(root_no_accidental):
            return cls(name, root_no_accidental, Chord.from_name("major"), octave)

        possibly_accidental = name[len(root_no_accidental)]
        if possibly_accidental in ACCIDENTALS:
            root = root_no_accidental + possibly_accidental
        else:
            root = root_no_accidental

        return cls(name, root, Chord.from_name(name[len(root) :]), octave)

    def intervals(self):
        return self.chord.intervals()

    def midi(self):
        midi = []
        for semitone in self.semitones:
            note, octave = transpose(self.root, self.octave, semitone)
            midi.append(get_midi(note, octave))
        return midi

    def transpose(self, shift):
        root, octave = transpose(self.root, self.octave, shift)
        return ChordWithRoot(root + self.chord.name, root, self.chord, octave)
