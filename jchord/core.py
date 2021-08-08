"""
Basic utilities for working with notes, base classes for objects etc.
"""
import itertools
from typing import Hashable, List

from jchord.knowledge import MAJOR_SCALE_OFFSETS, CHROMATIC, ENHARMONIC


class InvalidDegree(Exception):
    """Raised if the string one attempts to interpret is not a valid scale degree"""


class CompositeObject(object):
    """
    Base class for objects which can be represented by a few attributes.

    Subclasses must implement a `_keys()` function which returns a hashable
    representation of these attributes (e.g. returns them as a tuple).

    A CompositeObject is considered equal to another if the return value of their
    `_keys()` function is equal.

    Iterating over a CompositeObject is like iterating over the return value of its
    `_keys()` function.
    """

    def _keys(self) -> Hashable:
        """Returns a hashable representation of the attributes that the object wraps."""
        raise NotImplementedError

    def __eq__(self, other: "CompositeObject") -> bool:
        try:
            return self._keys() == other._keys()
        except AttributeError:
            return False

    def __hash__(self) -> Hashable:
        return hash(self._keys())

    def __iter__(self):
        self.__i = 0
        self.__keys = self._keys()
        return self

    def __next__(self):
        self.__i += 1
        try:
            return self.__keys[self.__i - 1]
        except IndexError:
            del self.__i
            del self.__keys
            raise StopIteration

    def __repr__(self):
        return f"{type(self).__name__}({', '.join(repr(key) for key in self._keys())})"


class Note(CompositeObject):
    """
    Represents an absolute note with a name and an octave.
    To create a Note, provide the name as a string and the octave as an integer:

    >>> Note(name="A", octave=3)
    Note('A', 3)

    Two instances of ``Note`` are equal if they have the same name and octave,
    or if they have the same octave and their names are enharmonic:

    >>> Note('G#', 4) == Note('Ab', 4)
    True
    >>> Note('G#', 4) == Note('Ab', 3)
    False

    You can subtract two ``Note`` instances to get the number of semitones between them:

    >>> Note('G#', 4) - Note('Ab', 3)
    12
    >>> Note('Ab', 3) - Note('G#', 4)
    -12

    ``Note`` is hashable, so instances can be used as dictionary keys or members of sets.
    """

    def __init__(self, name: str, octave: int):
        self.name = name
        self.octave = octave

    def _keys(self):
        return (self.name, self.octave)

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        try:
            other_name = other.name
            other_octave = other.octave
        except AttributeError:
            try:
                if len(other) != 2:
                    return False
            except TypeError:
                return False

            other_name = other[0]
            other_octave = other[1]
        if self.octave != other_octave:
            return False
        if self.name == other_name:
            return True
        for sharp, flat in ENHARMONIC:
            if self.name == sharp:
                return other_name == flat
            elif self.name == flat:
                return other_name == sharp
        return False

    def __sub__(self, other):
        """Returns the number of semitones between the two notes"""
        from jchord import midi

        return midi.note_to_midi(self) - midi.note_to_midi(other)

    def pitch(self) -> float:
        """Returns the absolute pitch of the note in Hz.

        >>> Note("A", 4).pitch()
        440.0
        >>> Note("A", 0).pitch()
        27.5
        >>> Note("C", 4).pitch()
        261.6255653005986
        """
        from jchord import midi

        return midi.midi_to_pitch(midi.note_to_midi(self))

    def _shift_up(self: "Note") -> "Note":
        for i, other in enumerate(CHROMATIC):
            if self == Note(other, octave=self.octave):
                if i == len(CHROMATIC) - 1:
                    return Note(name=CHROMATIC[0], octave=self.octave + 1)
                else:
                    return Note(name=CHROMATIC[i + 1], octave=self.octave)
        raise RuntimeError(f"Can't shift up {self}")

    def _shift_down(self: "Note") -> "Note":
        for i, other in enumerate(CHROMATIC):
            if self == Note(other, octave=self.octave):
                if i == 0:
                    return Note(name=CHROMATIC[-1], octave=self.octave - 1)
                else:
                    return Note(name=CHROMATIC[i - 1], octave=self.octave)
        raise RuntimeError(f"Can't shift down {self}")

    def transpose(self: "Note", shift: int) -> "Note":
        """Transposes the note by the given number of semitones.

        >>> Note("C", 0).transpose(1)
        Note('C#', 0)
        >>> Note("C", 4).transpose(19)
        Note('G', 5)
        """
        note = self
        if shift > 0:
            for _ in itertools.repeat(None, shift):
                note = note._shift_up()
        else:
            for _ in itertools.repeat(None, -shift):
                note = note._shift_down()
        return note

    def transpose_degree(self: "Note", shift: str, down: bool = False) -> "Note":
        """
        Transposes the given note by the given scale degree.

        >>> Note("C", 0).transpose_degree("b2")
        Note('C#', 0)
        >>> Note("C", 4).transpose_degree("5")
        Note('G', 4)
        >>> Note("C", 4).transpose_degree("5", down=True)
        Note('F', 3)
        """
        factor = -1 if down else 1
        return self.transpose(factor * degree_to_semitone(shift))


def split_to_base_and_shift(
    name_or_degree: str, name_before_accidental: bool
) -> (str, int):
    """Takes a string representation of a note name or a degree. Returns a
    tuple where the first element is the string representation of the degree
    with accidentals removed, and the second element is the number of semitones
    needed to account fo accidentals.

    Examples:

    * `split_to_base_and_shift("A#", name_before_accidental=True) == ("A", 1)`
    * `split_to_base_and_shift("Ab", name_before_accidental=True) == ("A", -1)`
    * `split_to_base_and_shift("A", name_before_accidental=True) == ("A", 0)`
    * `split_to_base_and_shift("Abbbb", name_before_accidental=True) == ("A", -4)`
    * `split_to_base_and_shift("b9", name_before_accidental=False) == ("9", -1)`
    * `split_to_base_and_shift("#9", name_before_accidental=False) == ("9", 1)`
    """
    if "b" in name_or_degree and "#" in name_or_degree:
        raise InvalidDegree("Both sharp and flat in degree")

    shift = 0
    if name_before_accidental:
        while name_or_degree.endswith("b"):
            shift -= 1
            name_or_degree = name_or_degree[:-1]
        while name_or_degree.endswith("#"):
            shift += 1
            name_or_degree = name_or_degree[:-1]
    else:
        while name_or_degree.startswith("b"):
            shift -= 1
            name_or_degree = name_or_degree[1:]
        while name_or_degree.startswith("#"):
            shift += 1
            name_or_degree = name_or_degree[1:]
    return name_or_degree, shift


def degree_to_semitone(degree: str) -> int:
    """Converts a string representation of a scale degree to the number of semitones between the root and that scale degree.

    Examples:

    * `degree_to_semitone("b9") == 13`
    * `degree_to_semitone("5") == 7`
    """
    degree, shift = split_to_base_and_shift(degree, name_before_accidental=False)

    # Now the remaining string should be an int
    try:
        int_degree = int(degree)
    except ValueError:
        raise InvalidDegree(degree)

    # Consider one octave above
    if int_degree > 7:
        int_degree -= 7
        shift += 12

    # Return
    try:
        return MAJOR_SCALE_OFFSETS[int_degree] + shift
    except KeyError as error:
        raise InvalidDegree(degree) from error


def semitone_to_degree_options(semitone: int, max_accidentals: int = 1) -> List[str]:
    """Converts the number of semitones between the root and the wanted scale degree to
    a list of possible names for that scale degree.

    The list of options is sorted by "reasonableness":

    * If option A has fewer accidentals than option B, option A comes first.
    * If option A has the same number of accidentals as option B, then the option with a "b" comes before the option with a "#".

    Examples:

    * `semitone_to_degree_options(semitone=3, max_accidentals=1) = ["b3", "#2"]`
    * `semitone_to_degree_options(semitone=3, max_accidentals=0) = []`
    * `semitone_to_degree_options(semitone=17, max_accidentals=1) = ["11", "#10"]`
    """
    degrees = MAJOR_SCALE_OFFSETS.copy()
    degrees.update(
        {degree + 7: semitone + 12 for degree, semitone in MAJOR_SCALE_OFFSETS.items()}
    )

    if semitone < 0 or semitone >= 24:
        return []

    options_with_priority = []

    for cand_degree, cand_semitone in degrees.items():
        for n_accidentals in range(max_accidentals + 1):
            if semitone == cand_semitone - n_accidentals:
                options_with_priority.append(
                    (f"{'b' * n_accidentals}{cand_degree}", n_accidentals)
                )
            if semitone == cand_semitone + n_accidentals:
                options_with_priority.append(
                    (
                        f"{'#' * n_accidentals}{cand_degree}",
                        n_accidentals + 0.5,
                    )
                )

    sorted_options = [
        option
        for option, priority in sorted(
            options_with_priority, key=lambda opt_pri: opt_pri[1]
        )
    ]
    sorted_options_no_duplicates = []
    for option in sorted_options:
        if sorted_options_no_duplicates and sorted_options_no_duplicates[-1] == option:
            continue
        sorted_options_no_duplicates.append(option)
    return sorted_options_no_duplicates


def note_diff(name_low: str, name_high: str) -> int:
    """Returns the number of semitones between the first note and the second note.
    The first note is assumed to be the lower of the two notes.

    Examples:

    * `note_diff("G", "A") == 2`
    * `note_diff("A", "Bb") == 1`
    * `note_diff("A", "G") == 10`
    * `note_diff("A", "A") == 0`
    """
    diff = 0
    note = Note(name_low, 0)
    while note.name != name_high:
        note = note._shift_up()
        diff += 1
    return diff
