"""
Tools for working with chords.
"""
from collections import deque
from typing import Hashable, List, Optional, Set, Tuple

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
)
from jchord.midi import note_to_midi, midi_to_note


class InvalidChord(Exception):
    """Raised if trying to construct a chord from an invalid chord name."""


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
        for option in semitones_to_chord_name_options(
            list(set(semitones) | {7}), _rec - 1
        )
        if "/" not in option
    ]


def _with_extension(base, extension):
    if "sus" in base:
        return "{}{}".format(extension, base)
    else:
        return "{}{}".format(base, extension)


def _chord_options_triad_with_extension(upper_note, lower_triad, _rec):
    if upper_note == 11:
        return [
            _with_extension(option, "maj7")
            for option in semitones_to_chord_name_options(set(lower_triad), _rec - 1)
        ]
    elif upper_note == 10:
        options = [
            _with_extension(option, "7")
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


def _chord_options_three_semitones(semitones, _rec):
    return _chord_options_triad_with_extension(
        upper_note=semitones[2], lower_triad=semitones[:2], _rec=_rec
    ) + _chord_options_triad_with_lower_note(
        lower_note=semitones[0], upper_triad=semitones[1:], _rec=_rec
    )


def _chord_options_upper_extensions(semitones, _rec):
    return []


def _separate_octave(name: str) -> Tuple[Optional[int], str]:
    # Probably too generous to check from -15 to +15
    max_octave_abs = 15

    # Need to check absolute octave in reverse order so that "10" is detected before "1"
    # and "-10" is detected before "-1"
    found_octave = None
    found_octave_str = None
    for octave in range(max_octave_abs, -1, -1):
        unsigned_octave = str(octave)
        pos_octave = "+" + unsigned_octave
        neg_octave = "-" + unsigned_octave

        if name.startswith(unsigned_octave):
            found_octave_str = unsigned_octave
            found_octave = octave
            break

        if name.startswith(pos_octave):
            found_octave_str = pos_octave
            found_octave = octave
            break

        if name.startswith(neg_octave):
            found_octave_str = neg_octave
            found_octave = -octave
            break

    if found_octave_str is not None:
        name = name[len(found_octave_str) :]

    return found_octave, name


def semitones_to_chord_name_options(semitones: Set[int], _rec=5) -> List[str]:
    """Returns a set of chord names corresponding to the given set of semitones.

    The function tries to put the most reasonable chord names first and the more dubious ones last.

    The `_rec` argument is for internal use only; in some cases, it prevents infinite recursion while computing the chord name.
    """
    if _rec == 0:
        return []

    # Ensure the notes are sorted
    semitones = list(sorted(semitones))

    # Remove octaves
    semitones_no_octaves = set()
    for semitone in semitones:
        is_octave = False
        for seen_semitone in semitones_no_octaves | {0}:
            if (seen_semitone - semitone) % 12 == 0:
                is_octave = True
                break
        if not is_octave:
            semitones_no_octaves.add(semitone)
    semitones = semitones_no_octaves
    semitones = list(sorted(semitones))

    # Try known strategies for chords with up to 4 notes
    if len(semitones) == 0:
        result = ["note"]
    elif len(semitones) == 1:
        result = _chord_options_single_semitone(semitones[0])
    elif len(semitones) == 2:
        result = _chord_options_two_semitones(semitones, _rec)
    elif len(semitones) == 3:
        result = _chord_options_three_semitones(semitones, _rec)
    else:
        result = _chord_options_upper_extensions(semitones, _rec)

    # Try moving everything into the same octave
    semitones_single_octave = {semitone % 12 for semitone in semitones}
    if semitones != semitones_single_octave:
        result_single_octave = semitones_to_chord_name_options(
            semitones_single_octave, _rec - 1
        )

        # We lose information about the particular intervals here, so remove all 'interval' candidates
        result_single_octave = [
            result for result in result_single_octave if not "interval" in result
        ]
        result += result_single_octave

    # Ensure all results are unique
    result_no_duplicates = []
    for res in result:
        if res not in result_no_duplicates:
            result_no_duplicates.append(res)
    result = result_no_duplicates

    return result


def remove_if_possible(options, predicate):
    """
    Removes all entries in options where the predicate is true,
    unless that would leave an empty list of options.
    """
    pred_vec = [predicate(option) for option in options]
    if any(pred_vec) and not all(pred_vec):
        options = [option for option, pred in zip(options, pred_vec) if not pred]
    return options


def select_name(options):
    """
    Select the best available name.
    Current strategy: remove chords with ugly names, then arbitrarily select
    the first of the remainder.
    """
    options = remove_if_possible(options, lambda option: "interval" in option)
    options = remove_if_possible(options, lambda option: "(no5)" in option)
    options = remove_if_possible(options, lambda option: "/" in option)

    return options[0]


### Chord modifications - undocumented section


class _ChordModification(object):
    def __init__(self, token, apply):
        self.token = token
        self.apply = apply

    def matches(self, name):
        return name.endswith(self.token)

    def strip_modifier(self, name):
        return name[: -len(self.token)]

    def resolve(self, cls, name):
        base_chord = cls.from_name(self.strip_modifier(name))
        chord = self.apply(base_chord)
        chord.name += self.token
        chord.modifications = base_chord.modifications + [self.token]
        return chord


def _semitone_subtractor(*semitones):
    def _remover(chord):
        for semitone in semitones:
            for octave in range(9):
                chord = chord.remove_semitone(
                    semitone + octave * 12, recalculate_name=False
                )
        return chord

    return _remover


def _semitone_adder(*semitones):
    def _adder(chord):
        for semitone in semitones:
            chord = chord.add_semitone(semitone, recalculate_name=False)
        return chord

    return _adder


def _semitone_replacer(remove, *adds):
    def _replacer(chord):
        for octave in range(9):
            chord = chord.remove_semitone(remove + octave * 12, recalculate_name=False)
        for add in adds:
            chord = chord.add_semitone(add, recalculate_name=False)
        return chord

    return _replacer


def _semitone_rotator(x):
    return lambda chord: chord.rotate_semitones(x, recalculate_name=False)


_MODIFICATIONS = [
    _ChordModification(token="no2", apply=_semitone_subtractor(1, 2)),
    _ChordModification(token="no3", apply=_semitone_subtractor(3, 4)),
    _ChordModification(token="no4", apply=_semitone_subtractor(5)),
    _ChordModification(token="no#4", apply=_semitone_subtractor(6)),
    _ChordModification(token="nob5", apply=_semitone_subtractor(6)),
    _ChordModification(token="no5", apply=_semitone_subtractor(7)),
    _ChordModification(token="no6", apply=_semitone_subtractor(8, 9)),
    _ChordModification(token="no7", apply=_semitone_subtractor(10, 11)),
    _ChordModification(token="no8", apply=_semitone_subtractor(12)),
    _ChordModification(token="no9", apply=_semitone_subtractor(14)),
    _ChordModification(token="addb6", apply=_semitone_adder(8)),
    _ChordModification(token="add6", apply=_semitone_adder(9)),
    _ChordModification(token="addb9", apply=_semitone_adder(13)),
    _ChordModification(token="add9", apply=_semitone_adder(14)),
    _ChordModification(token="add#9", apply=_semitone_adder(15)),
    _ChordModification(token="addb11", apply=_semitone_adder(16)),
    _ChordModification(token="add11", apply=_semitone_adder(17)),
    _ChordModification(token="add#11", apply=_semitone_adder(18)),
    _ChordModification(token="addb13", apply=_semitone_adder(20)),
    _ChordModification(token="add13", apply=_semitone_adder(21)),
    _ChordModification(token="add#13", apply=_semitone_adder(22)),
    _ChordModification(token="sus2", apply=_semitone_replacer(4, 2)),
    _ChordModification(token="sus4", apply=_semitone_replacer(4, 5)),
    _ChordModification(token="#4", apply=_semitone_replacer(5, 6)),
    _ChordModification(token="b5", apply=_semitone_replacer(7, 6)),
    _ChordModification(token="#5", apply=_semitone_replacer(7, 8)),
    _ChordModification(token="b9", apply=_semitone_replacer(14, 10, 13)),
    _ChordModification(token="#9", apply=_semitone_replacer(14, 10, 15)),
    _ChordModification(token="b11", apply=_semitone_replacer(17, 10, 14, 16)),
    _ChordModification(token="#11", apply=_semitone_replacer(17, 10, 14, 18)),
    _ChordModification(token="b13", apply=_semitone_replacer(21, 10, 14, 17, 20)),
    _ChordModification(token="#13", apply=_semitone_replacer(21, 10, 14, 17, 22)),
    *[
        _ChordModification(token="inv{}".format(x), apply=_semitone_rotator(x))
        for x in range(1, 10)
    ],
]

# Ensure we see the more specific ones first
_tokens = set()
for _modification in reversed(_MODIFICATIONS):
    assert not any(token.endswith(_modification.token) for token in _tokens)
    _tokens.add(_modification.token)

### Chord modifications - end of undocumented section


class Chord(CompositeObject):
    """
    Represents a *chord quality*, that is, not with a root.
    Examples of chord qualities are major, minor, dominant, major 7, etc.

    There are several ways to construct a ``Chord``. You can either specify the name or the
    interval structure of the chord, and the other will be inferred.

    To **specify the name and infer the semitones**, use ``from_name``:

    >>> Chord.from_name("maj7")
    Chord(name='maj7', semitones=[0, 4, 7, 11])
    >>> Chord.from_name("7sus4#13")
    Chord(name='7sus4#13', semitones=[0, 5, 7, 10, 14, 17, 22])

    If no chord can be generated from the name, an ``InvalidChòrd`` exception is raised.

    To **specify the semitones and infer the name**, use ``from_semitones`` or ``from_degrees``.

    >>> Chord.from_semitones([0, 3, 7, 11])
    Chord(name='minmaj7', semitones=[0, 3, 7, 11])
    >>> Chord.from_semitones([3, 7, 11]) # the 0 is optional
    Chord(name='minmaj7', semitones=[0, 3, 7, 11])
    >>> Chord.from_semitones([3, 7, 11], name='mMaj7') # you can override the name
    Chord(name='mMaj7', semitones=[0, 3, 7, 11])
    >>> Chord.from_semitones([1, 2, 3, 4]) # no common name
    Chord(name='<unknown>', semitones=[0, 1, 2, 3, 4])
    """

    UNNAMED = "<unknown>"

    def __init__(
        self, semitones: List[int], name: str, implicit_zero=True, source_chord=None
    ):
        if implicit_zero:
            semitones_set = set(semitones) | {0}
        else:
            semitones_set = set(semitones)
        self.semitones = sorted(list(semitones_set))
        self.name = name
        self.modifications = []
        self._inversions = 0

    def __repr__(self) -> str:
        if 0 not in self.semitones:
            implicit_zero_arg = ", implicit_zero=False"
        else:
            implicit_zero_arg = ""
        return "Chord(name='{}', semitones={}{})".format(
            self.name, self.semitones, implicit_zero_arg
        )

    def _keys(self) -> Hashable:
        return tuple(self.semitones)

    @classmethod
    def get_name_from_semitones(cls, semitones: List[int]) -> str:
        name_options = semitones_to_chord_name_options(semitones)
        if name_options:
            return select_name(name_options)
        else:
            return cls.UNNAMED

    @classmethod
    def from_semitones(
        cls, semitones: List[int], name: Optional[str] = None
    ) -> "Chord":
        if name is None:
            name = cls.get_name_from_semitones(semitones)
        return cls(semitones, name)

    @classmethod
    def from_degrees(cls, degrees: List[str], name: Optional[str] = None) -> "Chord":
        return cls([degree_to_semitone(degree) for degree in degrees], name)

    @classmethod
    def from_name(cls, name: str) -> "Chord":
        # Very special case: empty string is major
        if name == "":
            obj = cls.from_name("major")
            obj.name = ""
            return obj

        # Recursively resolve modifications
        for modification in _MODIFICATIONS:
            if modification.matches(name):
                return modification.resolve(cls, name)

        # Look it up in the canonical names
        if name in CHORD_NAMES:
            return cls.from_degrees(CHORD_NAMES[name], name)

        # Look it up in the chord aliases
        for alias in CHORD_ALIASES:
            if alias in name:
                canonical = name.replace(alias, CHORD_ALIASES[alias])
                if canonical in CHORD_NAMES:
                    return cls.from_degrees(CHORD_NAMES[canonical], name)

        # Nope
        raise InvalidChord(name)

    def intervals(self) -> List[int]:
        """
        Returns the list of internal intervals in the chord.

        >>> Chord.from_name("minor").intervals()
        [3, 4]
        >>> Chord.from_name("major7").intervals()
        [4, 3, 4]
        """
        intervals = []
        for i in range(1, len(self.semitones)):
            intervals.append(self.semitones[i] - self.semitones[i - 1])
        return intervals

    def with_root(self, root: Note) -> "ChordWithRoot":
        """
        Returns a ``ChordWithRoot`` based on the chord and the provided root.

        >>> Chord.from_name("m").with_root(Note("A", 5))
        ChordWithRoot(name='Am', root=Note('A', 5), chord=Chord(name='m', semitones=[0, 3, 7]))
        """
        return ChordWithRoot(root.name + self.name, root, self)

    def add_semitone(self, semitone: int, recalculate_name: bool = True) -> "Chord":
        """
        Returns a new ``Chord`` where the given semitone (as a difference from the root
        degree) has been added. The name will be recalculated unless the optional parameter
        ``recalculate_name`` is set to ``False``.

        >>> Chord.from_name("m").add_semitone(10)
        Chord(name='min7', semitones=[0, 3, 7, 10])
        """
        semitones = sorted(list(set(self.semitones) | {semitone}))
        if recalculate_name:
            name = self.__class__.get_name_from_semitones(semitones)
        else:
            name = self.name
        return Chord(semitones, name)

    def remove_semitone(self, semitone: int, recalculate_name: bool = True) -> "Chord":
        """
        Returns a new ``Chord`` where the given semitone (as a difference from the root
        degree) has been removed (if it was present). The name will be recalculated unless
        the optional parameter ``recalculate_name`` is set to ``False``.

        >>> Chord.from_name("maj7").remove_semitone(11)
        Chord(name='', semitones=[0, 4, 7])
        """
        semitones = sorted(list(set(self.semitones) - {semitone}))
        if recalculate_name:
            name = self.__class__.get_name_from_semitones(semitones)
        else:
            name = self.name
        return Chord(semitones, name)

    def rotate_semitones(self, n: int, recalculate_name: bool = True) -> "Chord":
        """
        Returns a new ``Chord`` where the semitones have been rotated, ``n`` times.
        In other words, ``chord.rotate_semitones(1)`` is the 1st inversion of
        ``chord``, ``chord.rotate_semitones(2)`` is the 2nd inversion, etc.
        The name will be recalculated unless the optional parameter ``recalculate_name`` is
        set to False.

        >>> Chord.from_name("maj7").rotate_semitones(2)
        Chord(name='maj7inv2', semitones=[7, 11, 12, 16], implicit_zero=False)
        """
        semitones = self.semitones.copy()
        for i in range(n):
            semitones[i % len(semitones)] += 12
        while all(semitone >= 12 for semitone in semitones):
            semitones = {semitone - 12 for semitone in semitones}
        semitones = sorted(list(set(semitones)))
        prev_inv = self._inversions
        new_inv = (prev_inv + n) % len(semitones)
        if recalculate_name:
            prev_inv_identifier = "inv{}".format(prev_inv)
            new_inv_identifier = "inv{}".format(new_inv)
            name = self.name.replace(prev_inv_identifier, "") + new_inv_identifier
        else:
            name = self.name
        chord = Chord(semitones, name, implicit_zero=False)
        chord._inversions = new_inv
        return chord


class ChordWithRoot(CompositeObject):
    """
    Represents a chord with a chord quality and a root note.

    There are several ways to construct a ``ChordWithRoot``. You can either specify the name
    or a root note + interval structure of the chord, and the other will be inferred.

    To **specify the name and infer the notes**, use ``from_name``:

    >>> ChordWithRoot.from_name("Amaj7")
    ChordWithRoot(name='Amaj7', root=Note('A', 4), chord=Chord(name='maj7', semitones=[0, 4, 7, 11]))
    >>> ChordWithRoot.from_name("B7sus4#13")
    ChordWithRoot(name='B7sus4#13', root=Note('B', 4), chord=Chord(name='7sus4#13', semitones=[0, 5, 7, 10, 14, 17, 22]))

    ``ChordWithRoot`` supports all the same names as ``Chord``, as well as slash chords.

    >>> ChordWithRoot.from_name("Amaj7/C")
    ChordWithRoot(name='Amaj7/C', root=Note('A', 4), chord=Chord(name='<unknown>', semitones=[-9, 0, 4, 7, 11]))

    If no chord can be generated from the name, an ``InvalidChòrd`` exception is raised.

    To **specify the root and semitones and infer the name**, use ``from_root_and_semitones``.

    >>> ChordWithRoot.from_root_and_semitones(Note('A', 5), [0, 3, 7, 11])
    ChordWithRoot(name='Aminmaj7', root=Note('A', 5), chord=Chord(name='minmaj7', semitones=[0, 3, 7, 11]))

    In addition to the methods above, you can specify a **set of MIDI values**:

    >>> ChordWithRoot.from_midi({ 77, 80, 84 })
    ChordWithRoot(name='Fmin', root=Note('F', 5), chord=Chord(name='min', semitones=[0, 3, 7]))
    """

    def __init__(self, name: str, root: Note, chord: Chord):
        self.name = name
        self.root = root
        self.chord = chord

    @property
    def semitones(self) -> List[int]:
        """
        Returns the semitones in the chord.

        >>> ChordWithRoot.from_name("Am7").semitones
        [0, 3, 7, 10]
        """
        return self.chord.semitones

    def __repr__(self) -> str:
        return "ChordWithRoot(name='{}', root={}, chord={})".format(
            self.name, self.root, self.chord
        )

    def _keys(self) -> Hashable:
        return (self.chord, self.root)

    @property
    def bass(self) -> Note:
        """
        Returns the lowest note in the chord.

        Unless the chord is a slash chord, this is the same as ``chord.root``.

        >>> ChordWithRoot.from_name("Am7").bass
        Note('A', 4)
        >>> ChordWithRoot.from_name("Am7/B").bass
        Note('B', 3)
        """
        return self.root.transpose(min(self.chord.semitones))

    @classmethod
    def from_root_and_semitones(
        cls, root: Note, semitones: List[int]
    ) -> "ChordWithRoot":
        chord = Chord.from_semitones(semitones)
        if "/" in chord.name:
            chord_name, bass_degree = chord.name.split("/")
            new_root = (
                Note(root.name, 0).transpose(12 - degree_to_semitone(bass_degree)).name
            )
            name = "{}{}/{}".format(new_root, chord_name, root.name)
        else:
            name = root.name + chord.name
        return cls(name, root, chord)

    @classmethod
    def from_midi(cls, midi: Set[int]) -> "ChordWithRoot":
        midi_min = min(midi)
        semitones = [m - midi_min for m in midi]
        root = midi_to_note(midi_min)
        return cls.from_root_and_semitones(root, semitones)

    @classmethod
    def from_name(cls, name: str) -> "ChordWithRoot":
        # First determine the octave
        octave, name = _separate_octave(name)
        if octave is None:
            octave = 4

        root = None

        for letter in LETTERS:
            if name.startswith(letter):
                root_no_accidental = letter
                break
        else:
            raise InvalidChord(name)

        # Very special case: major chord with no accidentals
        if len(name) == len(root_no_accidental):
            return cls(name, Note(root_no_accidental, octave), Chord.from_name(""))

        possibly_accidental = name[len(root_no_accidental)]
        if possibly_accidental in ACCIDENTALS:
            root = Note(root_no_accidental + possibly_accidental, octave)
        else:
            root = Note(root_no_accidental, octave)

        name_without_root = name[len(root.name) :]
        has_slash = "/" in name_without_root

        if has_slash:
            name_without_root, bass = name_without_root.split("/")
            chord = cls(name, root, Chord.from_name(name_without_root))
            chord.chord = chord.chord.add_semitone(-note_diff(bass, root.name))
            return chord
        else:
            return cls(name, root, Chord.from_name(name_without_root))

    def intervals(self) -> List[int]:
        """
        Returns the semitones in the chord.

        Returns the list of internal intervals in the chord.

        >>> ChordWithRoot.from_name("Aminor").intervals()
        [3, 4]
        >>> ChordWithRoot.from_name("Amajor7").intervals()
        [4, 3, 4]
        """
        return self.chord.intervals()

    def midi(self) -> List[int]:
        """
        Returns the list of MIDI note values in the chord.

        >>> ChordWithRoot.from_name("Amajor7").midi()
        [69, 73, 76, 80]
        """
        return [
            note_to_midi(self.root.transpose(semitone)) for semitone in self.semitones
        ]

    def transpose(self, shift: int) -> "ChordWithRoot":
        """
        Transposes the chord by the given shift (in semitones).

        >>> ChordWithRoot.from_name("Amajor7").transpose(-12).midi()
        [57, 61, 64, 68]
        """
        root = self.root.transpose(shift)
        return ChordWithRoot(root.name + self.chord.name, root, self.chord)
