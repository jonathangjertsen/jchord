from jchord.progressions import ChordProgression, MidiConversionSettings
from jchord.midi import Instrument
from jchord.midi_effects import Harmonizer

progression = ChordProgression.from_string("""Fn Gn En An""")

progression.to_midi(
    MidiConversionSettings(
        filename="harmonizer.midi",
        tempo=85,
        beats_per_chord=2,
        instrument=Instrument.VoiceOohs,
        effect=Harmonizer(scale=[0, 2, 4, 5, 7, 9, 11], degrees=[1, 3, 5, 7], root="C"),
    )
)
