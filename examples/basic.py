# fmt: off
from jchord import ChordProgression, MidiConversionSettings

prog = ChordProgression.from_string("C -- Fm7 -- C -- G7 -- C -- E7 Am F Bm7b5 E7 Am9 F Bo C69 --")
prog = prog.transpose(+2)
print(prog.to_string())
prog.to_midi(MidiConversionSettings(filename="example.midi", tempo=100, beats_per_chord=2, instrument=4))
