from typing import Hashable, List, Optional, Set

from jchord.knowledge import (
    LETTERS,
    ACCIDENTALS,
    CHORD_NAMES,
    CHORD_ALIASES,
    TRIADS_WITH_FIFTH,
    DYADS,
)
from jchord.core import (
    degree_to_semitone,
    note_diff,
    CompositeObject,
    Note,
    semitone_to_degree_options,
    split_to_base_and_shift,
    transpose,
)
from jchord.midi import note_to_midi, midi_to_note


class InvalidChord(Exception):
    pass


def _chord_options_single_semitone(semitone):
    interval_options = [
        "{} interval".format(interval)
        for interval in semitone_to_degree_options(semitone)
    ]
    if semitone in DYADS:
        return [DYADS[semitone]] + interval_options
    else:
        return interval_options


def _chord_options_two_semitones(semitones, _rec):
    if 7 in semitones:
        for semitone in semitones:
            if semitone != 7 and semitone in TRIADS_WITH_FIFTH:
                return [TRIADS_WITH_FIFTH[semitone]]
    elif 6 in semitones:
        if 3 in semitones:
            return ["dim"]
    elif 8 in semitones:
        if 4 in semitones:
            return ["aug"]
    return [
        option if "(no5)" in option else "{}(no5)".format(option)
        for option in semitones_to_chord_name_options(semitones | {7}, _rec - 1)
        if "/" not in option
    ]


def _chord_options_triad_with_extension(upper_note, lower_triad, _rec):
    if upper_note == 11:
        return [
            "{}maj7".format(option)
            for option in semitones_to_chord_name_options(set(lower_triad), _rec - 1)
        ]
    elif upper_note == 10:
        options = [
            "{}7".format(option)
            for option in semitones_to_chord_name_options(set(lower_triad), _rec - 1)
        ]
        if "dim7" in options:
            options[options.index("dim7")] = "min7b5"
        return options
    elif upper_note == 9:
        if lower_triad == [3, 6]:
            return ["dim7"]
    return []


def _chord_options_triad_with_lower_note(lower_note, upper_triad, _rec):
    bass_degree = semitone_to_degree_options(12 - lower_note)[0]
    upper_triad_shifted = [semitone - lower_note for semitone in upper_triad]
    options = [
        "{}/{}".format(option, bass_degree)
        for option in semitones_to_chord_name_options(
            set(upper_triad_shifted), _rec - 1
        )
    ]
    base_degree, _ = split_to_base_and_shift(bass_degree, name_before_accidental=False)
    return [
        option
        for option in options
        if not ((bass_degree in option and "(no{})".format(base_degree) in option))
    ]


def _chord_options_three_semitones(semitones_sorted, _rec):
    return _chord_options_triad_with_extension(
        upper_note=semitones_sorted[2], lower_triad=semitones_sorted[:2], _rec=_rec
    ) + _chord_options_triad_with_lower_note(
        lower_note=semitones_sorted[0], upper_triad=semitones_sorted[1:], _rec=_rec
    )


def semitones_to_chord_name_options(semitones: Set[int], _rec=5) -> Set[str]:
    if _rec == 0:
        return []

    semitones_no_octaves = semitones.copy()
    for semitone in semitones:
        if semitone % 12 == 0:
            semitones_no_octaves.remove(semitone)
    semitones = semitones_no_octaves

    semitones_sorted = list(sorted(semitones))

    if len(semitones) == 0:
        return ["note"]
    elif len(semitones) == 1:
        return _chord_options_single_semitone(semitones_sorted[0])
    elif len(semitones) == 2:
        return _chord_options_two_semitones(semitones, _rec)
    elif len(semitones) == 3:
        return _chord_options_three_semitones(semitones_sorted, _rec)
    return []


class Chord(CompositeObject):
    UNNAMED = "???"

    def __init__(self, name: str, semitones: List[int]):
        self.name = name
        self.semitones = sorted(list(set(semitones) | {0}))

    def __repr__(self) -> str:
        return "Chord(name={}, semitones={})".format(self.name, self.semitones)

    def _keys(self) -> Hashable:
        return tuple(self.semitones)

    @classmethod
    def from_semitones(cls, name: Optional[str], semitones: List[int]) -> "Chord":
        if name is None:
            name_options = semitones_to_chord_name_options(semitones)
            if name_options:
                name = name_options[0]
            else:
                name = cls.UNNAMED
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
    def from_root_and_semitones(
        cls, root: str, semitones: List[int], octave: int = 4
    ) -> "ChordWithRoot":
        chord = Chord.from_semitones(None, semitones)
        if "/" in chord.name:
            chord_name, bass_degree = chord.name.split("/")
            new_root = transpose(
                Note(root, 0), 12 - degree_to_semitone(bass_degree)
            ).name
            name = "{}{}/{}".format(new_root, chord_name, root)
        else:
            name = root + chord.name
        return cls(name, root, chord, octave)

    @classmethod
    def from_midi(cls, midi: Set[int]) -> "ChordWithRoot":
        midi_min = min(midi)
        semitones = [m - midi_min for m in midi]
        root = midi_to_note(midi_min)
        return cls.from_root_and_semitones(root.name, semitones, root.octave)

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
            midi.append(note_to_midi((note, octave)))
        return midi

    def transpose(self, shift: int) -> "ChordWithRoot":
        root, octave = transpose((self.root, self.octave), shift)
        return ChordWithRoot(root + self.chord.name, root, self.chord, octave)
