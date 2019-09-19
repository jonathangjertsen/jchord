from jchord.knowledge import LETTERS, ACCIDENTALS, CHORD_NAMES, CHORD_ALIASES
from jchord.core import degree_to_semitone, CompositeObject, transpose
from jchord.midi import get_midi


class InvalidChord(Exception):
    pass


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
