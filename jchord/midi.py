from collections import defaultdict, namedtuple
from typing import Dict, List

from jchord.knowledge import CHROMATIC, MAJOR_FROM_C, MAJOR_SCALE_OFFSETS
from jchord.core import Note, split_to_base_and_shift

PlayedNote = namedtuple("PlayedNote", "time, note, duration")


class InvalidNote(Exception):
    pass


def note_to_midi(note: Note) -> int:
    c0_code = 12
    name, octave = note
    name, shift = split_to_base_and_shift(name, name_before_accidental=True)
    for candidate, offset in zip(MAJOR_FROM_C, MAJOR_SCALE_OFFSETS.values()):
        if name == candidate:
            return c0_code + offset + shift + 12 * octave
    raise InvalidNote(name)


def midi_to_note(midi: int) -> Note:
    return Note(CHROMATIC[midi % 12], (midi - 12) // 12)


def midi_to_pitch(midi: int) -> float:
    return 440 * (2 ** ((midi - 69) / 12))


def _read_midi_file_to_events(filename: str) -> list:
    from mido import MidiFile

    mid = MidiFile(filename)
    events = defaultdict(list)
    time = 0

    for msg in mid:
        if msg.is_meta:
            continue
        if msg.type not in {"note_on", "note_off"}:
            continue
        time += msg.time
        events[time].append(msg)

    return events


def _events_to_notes(events: list) -> List[PlayedNote]:
    notes = []
    times = list(events.keys())

    for i, time in enumerate(times):
        events_for_time = events[time]
        for event in events_for_time:
            if event.type != "note_on":
                continue

            for j in range(i, len(times)):
                time_end = times[j]
                events_for_end_time = events[time_end]
                found = False
                for event_end in events_for_end_time:
                    if event_end.type != "note_off" or event.note != event_end.note:
                        continue
                    played_note = PlayedNote(
                        time=time, note=event.note, duration=time_end - time
                    )
                    notes.append(played_note)
                    found = True
                    break
                if found:
                    break
    return notes


def read_midi_file(filename: str) -> List[PlayedNote]:
    events = _read_midi_file_to_events(filename)
    notes = _events_to_notes(events)
    return notes


def group_notes_to_chords(notes: List[PlayedNote]) -> Dict[float, PlayedNote]:
    result = defaultdict(list)
    for note in notes:
        result[note.time].append(note)
    return result
