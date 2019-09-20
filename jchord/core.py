import itertools

from jchord.knowledge import MAJOR_SCALE_OFFSETS, CHROMATIC


class InvalidDegree(Exception):
    pass


def split_to_base_and_shift(note_or_degree, note_before_accidental):
    if "b" in note_or_degree and "#" in note_or_degree:
        raise InvalidDegree("Both sharp and flat in degree")

    shift = 0
    if note_before_accidental:
        while note_or_degree.endswith("b"):
            shift -= 1
            note_or_degree = note_or_degree[:-1]
        while note_or_degree.endswith("#"):
            shift += 1
            note_or_degree = note_or_degree[:-1]
    else:
        while note_or_degree.startswith("b"):
            shift -= 1
            note_or_degree = note_or_degree[1:]
        while note_or_degree.startswith("#"):
            shift += 1
            note_or_degree = note_or_degree[1:]
    return note_or_degree, shift


def degree_to_semitone(degree: str) -> int:
    degree, shift = split_to_base_and_shift(degree, note_before_accidental=False)

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


def shift_up(note, octave):
    for i, other in enumerate(CHROMATIC):
        if note == other:
            if i == len(CHROMATIC) - 1:
                return CHROMATIC[0], octave + 1
            else:
                return CHROMATIC[i + 1], octave


def shift_down(note, octave):
    for i, other in enumerate(CHROMATIC):
        if note == other:
            if i == 0:
                return CHROMATIC[-1], octave - 1
            else:
                return CHROMATIC[i - 1], octave


def transpose(note, octave, shift):
    if shift > 0:
        for _ in itertools.repeat(None, shift):
            note, octave = shift_up(note, octave)
    else:
        for _ in itertools.repeat(None, -shift):
            note, octave = shift_down(note, octave)
    return note, octave


def note_diff(note_low: str, note_high: str) -> int:
    diff = 0
    octave = 0
    while note_low != note_high:
        note_low, octave = shift_up(note_low, octave)
        diff += 1
    return diff


class CompositeObject(object):
    def _keys(self):
        raise NotImplementedError

    def __eq__(self, other):
        try:
            return self._keys() == other._keys()
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self._keys())
