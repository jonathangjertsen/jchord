"""
Tools for working with MIDI.
"""
from collections import defaultdict, namedtuple
from enum import IntEnum
from typing import List

from jchord.knowledge import CHROMATIC, MAJOR_FROM_C, MAJOR_SCALE_OFFSETS
from jchord.core import Note, split_to_base_and_shift

MidiNote = namedtuple("MidiNote", "time, note, duration, velocity")
MidiNote.__doc__ = "namedtuple which represents a (MIDI) note played at a given time for a given duration."


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


def _events_to_notes(events: list) -> List[MidiNote]:
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
                    played_note = MidiNote(
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
                events_out.append(
                    {
                        **event,
                        "type": "note_off",
                        "abs_time": max(0, event["abs_time"] - margin),
                    }
                )
            events_out.append(event)
            hold_counts[event["note"]] += 1
        elif event["type"] == "note_off":
            if hold_counts[event["note"]] <= 1:
                events_out.append(event)
            hold_counts[event["note"]] -= 1
    return events_out


def notes_to_messages(notes: List[MidiNote], velocity=100):
    from mido import Message

    if not notes:
        return []

    events = []
    for note in notes:
        events.append(
            {
                "type": "note_on",
                "note": note.note,
                "velocity": velocity,
                "abs_time": note.time,
            }
        )
        events.append(
            {
                "type": "note_off",
                "note": note.note,
                "velocity": velocity,
                "abs_time": note.time + note.duration,
            }
        )
    events = sorted(events, key=lambda event: event["abs_time"])
    events = remove_overlap(events)

    messages = []
    last_event_time = events[0]["abs_time"]
    for event in events:
        event_time = event.pop("abs_time")
        messages.append(
            Message(**event, time=int(max(0, event_time - last_event_time)))
        )
        last_event_time = event_time

    return messages


def read_midi_file(filename: str) -> List[MidiNote]:
    """Reads the MIDI file for the given filename and returns the corresponding list of `MidiNote`s."""
    events = _read_midi_file_to_events(filename)
    notes = _events_to_notes(events)
    return notes


class Instrument(IntEnum):
    AcousticGrandPiano = 1
    BrightAcousticPiano = 2
    ElectricGrandPiano = 3
    HonkyTonkPiano = 4
    ElectricPiano1 = 5
    ElectricPiano2 = 6
    Harpsichord = 7
    Clavi = 8
    Celesta = 9
    Glockenspiel = 10
    MusicBox = 11
    Vibraphone = 12
    Marimba = 13
    Xylophone = 14
    TubularBells = 15
    Dulcimer = 16
    DrawbarOrgan = 17
    PercussiveOrgan = 18
    RockOrgan = 19
    ChurchOrgan = 20
    ReedOrgan = 21
    Accordion = 22
    Harmonica = 23
    TangoAccordion = 24
    AcousticGuitarNylon = 25
    AcousticGuitarSteel = 26
    ElectricGuitarJazz = 27
    ElectricGuitarClean = 28
    ElectricGuitarMuted = 29
    OverdrivenGuitar = 30
    DistortionGuitar = 31
    GuitarHarmonics = 32
    AcousticBass = 33
    ElectricBassFinger = 34
    ElectricBassPick = 35
    FretlessBass = 36
    SlapBass1 = 37
    SlapBass2 = 38
    SynthBass1 = 39
    SynthBass2 = 40
    Violin = 41
    Viola = 42
    Cello = 43
    Contrabass = 44
    TremoloStrings = 45
    PizzicatoStrings = 46
    OrchestralHarp = 47
    Timpani = 48
    StringEnsemble1 = 49
    StringEnsemble2 = 50
    SynthStrings1 = 51
    SynthStrings2 = 52
    ChoirAahs = 53
    VoiceOohs = 54
    SynthVoice = 55
    OrchestraHit = 56
    Trumpet = 57
    Trombone = 58
    Tuba = 59
    MutedTrumpet = 60
    FrenchHorn = 61
    BrassSection = 62
    SynthBrass1 = 63
    SynthBrass2 = 64
    SopranoSax = 65
    AltoSax = 66
    TenorSax = 67
    BaritoneSax = 68
    Oboe = 69
    EnglishHorn = 70
    Bassoon = 71
    Clarinet = 72
    Piccolo = 73
    Flute = 74
    Recorder = 75
    PanFlute = 76
    BlownBottle = 77
    Shakuhachi = 78
    Whistle = 79
    Ocarina = 80
    Lead1 = 81
    Lead2 = 82
    Lead3 = 83
    Lead4 = 84
    Lead5 = 85
    Lead6 = 86
    Lead7 = 87
    Lead8 = 88
    Pad1 = 89
    Pad2 = 90
    Pad3 = 91
    Pad4 = 92
    Pad5 = 93
    Pad6 = 94
    Pad7 = 95
    Pad8 = 96
    FX1 = 97
    FX2 = 98
    FX3 = 99
    FX4 = 100
    FX5 = 101
    FX6 = 102
    FX7 = 103
    FX8 = 104
    Sitar = 105
    Banjo = 106
    Shamisen = 107
    Koto = 108
    Kalimba = 109
    Bagpipe = 110
    Fiddle = 111
    Shanai = 112
    TinkleBell = 113
    Agogo = 114
    SteelDrums = 115
    Woodblock = 116
    TaikoDrum = 117
    MelodicTom = 118
    SynthDrum = 119
    ReverseCymbal = 120
    GuitarFretNoise = 121
    BreathNoise = 122
    Seashore = 123
    BirdTweet = 124
    TelephoneRing = 125
    Helicopter = 126
    Applause = 127
    Gunshot = 128
