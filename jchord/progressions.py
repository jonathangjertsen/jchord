from math import ceil
from typing import Hashable, List, Set

from jchord.knowledge import REPETITION_SYMBOL
from jchord.core import CompositeObject
from jchord.chords import ChordWithRoot


class InvalidProgression(Exception):
    pass


def _string_to_progression(string: str) -> List[ChordWithRoot]:
    string = string.strip()

    if string == "":
        return []

    progression = []

    for name in string.split():
        name = name.strip()

        if name == REPETITION_SYMBOL:
            if not progression:
                raise InvalidProgression(
                    "Can't repeat before at least one chord has been added"
                )

            progression.append(progression[-1])
        else:
            progression.append(ChordWithRoot.from_name(name))
    return progression


class ChordProgression(CompositeObject):
    def __init__(self, progression: List[ChordWithRoot]):
        self.progression = progression

    def _keys(self) -> Hashable:
        return tuple(self.progression)

    @classmethod
    def from_string(cls, string: str) -> "ChordProgression":
        return cls(_string_to_progression(string))

    @classmethod
    def from_txt(cls, filename: str) -> "ChordProgression":
        with open(filename) as file:
            return cls(_string_to_progression(file.read()))

    @classmethod
    def from_xlsx(cls, filename: str) -> "ChordProgression":
        from openpyxl import load_workbook

        workbook = load_workbook(filename)
        sheet = workbook.active
        names = []
        for row in sheet.iter_rows():
            for cell in row:
                name = cell.value
                if not name:
                    name = REPETITION_SYMBOL
                names.append(name)
        return cls.from_string(" ".join(names))

    def chords(self) -> Set[ChordWithRoot]:
        return set(self.progression)

    def midi(self) -> List[List[int]]:
        return [chord.midi() for chord in self.progression]

    def to_txt_string(
        self, chords_per_row: int = 4, column_spacing: int = 2, newline: str = "\n"
    ) -> str:
        max_len = max(len(chord.name) for chord in self.progression)
        column_width = max_len + column_spacing

        column = 0
        output = []
        prev_chord = None
        for chord in self.progression:
            if prev_chord == chord:
                chord_name = REPETITION_SYMBOL
            else:
                chord_name = chord.name

            output.append(chord_name)
            output.append(" " * (column_width - len(chord_name)))

            column += 1
            if column % chords_per_row == 0:
                column = 0
                output.append(newline)

            prev_chord = chord

        return "".join(output) + newline

    def to_txt(
        self,
        filename: str,
        chords_per_row: int = 4,
        column_spacing: int = 2,
        newline: str = "\n",
    ):
        output_str = self.to_txt_string(
            chords_per_row=chords_per_row,
            column_spacing=column_spacing,
            newline=newline,
        )
        with open(filename, "w") as file:
            file.write(output_str)

    def to_xlsx(self, filename: str, chords_per_row: int = 4):
        from openpyxl import Workbook

        workbook = Workbook()
        worksheet = workbook.active

        row = 1
        column = 1
        prev_chord = None
        for chord in self.progression:
            if prev_chord == chord:
                chord_name = REPETITION_SYMBOL
            else:
                chord_name = chord.name

            worksheet.cell(row=row, column=column).value = chord_name

            column += 1
            if (column - 1) % chords_per_row == 0:
                column = 1
                row += 1

            prev_chord = chord

        workbook.save(filename)

    def to_midi(
        self,
        filename: str,
        instrument: int = 1,
        tempo: int = 120,
        beats_per_chord: int = 2,
        velocity: int = 100,
    ):
        import mido

        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)

        seconds_per_chord = (60 / tempo) * beats_per_chord
        ticks_per_chord = int(
            mido.second2tick(
                seconds_per_chord, mid.ticks_per_beat, mido.bpm2tempo(tempo)
            )
        )

        track.append(mido.Message("program_change", program=instrument))
        for i, notes in enumerate(self.midi()):
            for note in notes:
                track.append(
                    mido.Message("note_on", note=note, velocity=velocity, time=0)
                )

            # Hack due to mido requiring "delta times"
            track.append(
                mido.Message("note_off", note=0, velocity=0, time=ticks_per_chord)
            )

            for note in notes:
                track.append(
                    mido.Message("note_off", note=note, velocity=velocity, time=0)
                )

        mid.save(filename)
