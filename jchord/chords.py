from typing import Hashable, List

from jchord.knowledge import LETTERS, ACCIDENTALS, CHORD_NAMES, CHORD_ALIASES
from jchord.core import degree_to_semitone, note_diff, CompositeObject, transpose
from jchord.midi import get_midi


class InvalidChord(Exception):
    pass


class Chord(CompositeObject):
    def __init__(self, name: str, semitones: List[int]):
        self.name = name

        semitone_set = set(semitones)
        semitone_set.add(0)
        self.semitones = sorted(list(semitone_set))

    def __repr__(self) -> str:
        return "Chord(name={}, semitones={})".format(self.name, self.semitones)

    def _keys(self) -> Hashable:
        return tuple(self.semitones)

    @classmethod
    def from_semitones(cls, name: str, semitones: List[int]) -> "Chord":
        return cls(name, semitones)

    @classmethod
    def from_degrees(cls, name: str, degrees: List[str]) -> "Chord":
        return cls(name, [degree_to_semitone(degree) for degree in degrees])

    @classmethod
    def from_name(cls, name: str) -> "Chord":
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

    def intervals(self) -> List[int]:
        intervals = []
        for i in range(1, len(self.semitones)):
            intervals.append(self.semitones[i] - self.semitones[i - 1])
        return intervals

    def with_root(self, root: str) -> "ChordWithRoot":
        return ChordWithRoot(root + self.name, root, self)

    def add_semitone(self, semitone: int):
        self.semitones = sorted(list(set(self.semitones) | {semitone}))


class ChordWithRoot(CompositeObject):
    def __init__(self, name: str, root: str, chord: Chord, octave: int = 4):
        self.name = name
        self.root = root
        self.octave = octave
        self.chord = chord

    @property
    def semitones(self):
        return self.chord.semitones

    def __repr__(self) -> str:
        return "ChordWithRoot(name={}, root={}, chord={}, octave={})".format(
            self.name, self.root, self.chord, self.octave
        )

    def _keys(self) -> Hashable:
        return (self.chord, self.root, self.octave)

    @classmethod
    def from_name(cls, name: str, octave: int = 4) -> "ChordWithRoot":
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

        name_without_root = name[len(root) :]
        has_slash = "/" in name_without_root

        if has_slash:
            name_without_root, bass = name_without_root.split("/")
            chord = cls(name, root, Chord.from_name(name_without_root), octave)
            chord.chord.add_semitone(-note_diff(bass, root))
            return chord
        else:
            return cls(name, root, Chord.from_name(name_without_root), octave)

    def intervals(self) -> List[int]:
        return self.chord.intervals()

    def midi(self) -> List[int]:
        midi = []
        for semitone in self.semitones:
            note, octave = transpose((self.root, self.octave), semitone)
            midi.append(get_midi((note, octave)))
        return midi

    def transpose(self, shift: int) -> "ChordWithRoot":
        root, octave = transpose((self.root, self.octave), shift)
        return ChordWithRoot(root + self.chord.name, root, self.chord, octave)
