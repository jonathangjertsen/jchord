from jchord.progressions import ChordProgression, MidiConversionSettings
from jchord.midi import Instrument
from jchord.midi_effects import (
    Chain,
    Doubler,
    Arpeggiator,
    VelocityControl,
    Spreader,
    Transposer,
    Shuffle
)

progression = ChordProgression.from_string(
    """
Dm    --  G          -- C      Cadd9   Fmaj7  --
Dm    --  E          -- Am     --      Am9    --
Dm7   --  G7         -- C      C7      Fmaj7  Fmaj7add6
Dm9   --  E7         -- Am     --      Amadd6 --
Esus4 E7  Am         --
Dm7   --  G          -- Cmaj9  Cmaj9/G Fmaj7  --
Dm    --  E          -- Amadd9 Am/G    Am/F#  Fmaj7
E7b9  --  Amadd6add9 -- --     --      Am     --
"""
)

progression.to_midi(
    MidiConversionSettings(
        filename="autumn_leaves_arpeggiated.midi",
        tempo=110,
        beats_per_chord=2,
        instrument=Instrument.VoiceOohs,
        effect=Chain(
            Doubler(12),
            Arpeggiator(
                rate=1 / 16,
                pattern=[
                    (0, 2),  1,      2,   (1, 3),
                    2,       (3, 4), 2,   3,
                    (4, 1),  3,      4,   5,
                    (-2, 0), -3,    -4,  -5,
                ],
                sticky=True,
            )
        ),
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
