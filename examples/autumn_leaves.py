from jchord.progressions import ChordProgression, MidiConversionSettings
from jchord.midi import Instrument
from jchord.midi_effects import (
    Chain,
    Doubler,
    Arpeggiator,
    AlternatingInverter,
    Spreader,
    Transposer,
)

progression = ChordProgression.from_string(
    """
Dm    --  G  --  C      Cadd9 Fmaj7 --
Dm    --  E  --  Am     --    Am9   --
Dm7   --  G7 --  C      --    Fmaj7 --
Dm7   --  E7 --  Am     --    --    --
Esus4 E   Am --
Dm7   --  G  --  C      --    Fmaj7 --
Dm    --  E  --  Amadd9 Am/G  Am/F# F7
E7b9  --  Am --  --     --    --    --
"""
)

progression.to_midi(
    MidiConversionSettings(
        filename="autumn_leaves_arpeggiated.midi",
        tempo=85,
        beats_per_chord=2,
        instrument=Instrument.VoiceOohs,
        effect=Chain(
            Doubler(12),
            Arpeggiator(
                rate=1 / 16,
                pattern=[0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5, -2, -3, -4, -5],
                sticky=True,
            ),
        ),
        velocity=50,
    )
)

progression.to_midi(
    MidiConversionSettings(
        filename="autumn_leaves_strummed.midi",
        tempo=180,
        beats_per_chord=2,
        instrument=Instrument.AcousticGuitarSteel,
        effect=Chain(Transposer(-12), Spreader(amount=30, jitter=6)),
        velocity=50,
    )
)
