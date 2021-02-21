"""
Tools for working with MIDI.
"""
from collections import defaultdict, namedtuple
from typing import Dict, List

from jchord.knowledge import CHROMATIC, MAJOR_FROM_C, MAJOR_SCALE_OFFSETS
from jchord.core import Note, split_to_base_and_shift

PlayedNote = namedtuple("PlayedNote", "time, note, duration, velocity")
PlayedNote.__doc__ = "namedtuple which represents a (MIDI) note played at a given time for a given duration."


class InvalidNote(Exception):
    """Raised when trying to get the MIDI value of a note that doesn't seem valid."""


def note_to_midi(note: Note) -> int:
    """Returns the midi value corresponding to the given `Note`."""
    c0_code = 12
    name, octave = note
    name, shift = split_to_base_and_shift(name, name_before_accidental=True)
    for candidate, offset in zip(MAJOR_FROM_C, MAJOR_SCALE_OFFSETS.values()):
        if name == candidate:
            return c0_code + offset + shift + 12 * octave
    raise InvalidNote(name)


def midi_to_note(midi: int) -> Note:
    """Returns the `Note` corresponding to the given MIDI note value."""
    return Note(CHROMATIC[midi % 12], (midi - 12) // 12)


def midi_to_pitch(midi: int) -> float:
    """Returns the absolute pitch in Hz for the given MIDI note value."""
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
                        time=time,
                        note=event.note,
                        duration=time_end - time,
                        velocity=event.velocity,
                    )
                    notes.append(played_note)
                    found = True
                    break
                if found:
                    break
    return notes

def remove_overlap(events, margin=1):
    hold_counts = defaultdict(int)
    events_out = []
    for event in events:
        if event["type"] == "note_on":
            if hold_counts[event["note"]] > 0:
                events_out.append({**event, "type": "note_off", "abs_time": max(0, event["abs_time"] - margin) })
            events_out.append(event)
            hold_counts[event["note"]] += 1
        elif event["type"] == "note_off":
            if hold_counts[event["note"]] <= 1:
                events_out.append(event)
            hold_counts[event["note"]] -= 1
    return events_out



def notes_to_messages(notes: List[PlayedNote], velocity=100):
    from mido import Message

    if not notes:
        return []

    events = []
    for note in notes:
        events.append({ "type": "note_on", "note": note.note, "velocity": velocity, "abs_time": note.time })
        events.append({ "type": "note_off", "note": note.note, "velocity": velocity, "abs_time": note.time + note.duration })
    events = sorted(events, key=lambda event: event["abs_time"])
    events = remove_overlap(events)

    messages = []
    last_event_time = events[0]["abs_time"]
    for event in events:
        event_time = event.pop("abs_time")
        messages.append(Message(**event, time=int(max(0, event_time - last_event_time))))
        last_event_time = event_time

    return messages


def read_midi_file(filename: str) -> List[PlayedNote]:
    """Reads the MIDI file for the given filename and returns the corresponding list of `PlayedNote`s."""
    events = _read_midi_file_to_events(filename)
    notes = _events_to_notes(events)
    return notes


def group_notes_to_chords(notes: List[PlayedNote]) -> Dict[float, PlayedNote]:
    """Groups the list of `PlayedNote`s by time.

    The return value maps time to a list of `PlayedNote`s for that time.

    There is no attempt at quantization at this time, so the notes must be played
    at the exact same time to be grouped together.
    """
    result = defaultdict(list)
    for note in notes:
        result[note.time].append(note)
    return result
