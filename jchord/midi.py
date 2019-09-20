from jchord.knowledge import MAJOR_FROM_C, MAJOR_SCALE_OFFSETS
from jchord.core import split_to_base_and_shift


class InvalidNote(Exception):
    pass


def get_midi(note: str, octave: int) -> int:
    c0_code = 12
    note, shift = split_to_base_and_shift(note, note_before_accidental=True)
    for candidate, offset in zip(MAJOR_FROM_C, MAJOR_SCALE_OFFSETS.values()):
        if note == candidate:
            return c0_code + offset + shift + 12 * octave
    raise InvalidNote(note)
