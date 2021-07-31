from jchord.progressions import ChordProgression

ChordProgression.from_string("Bmaj7 -- D7 -- Gmaj7 -- Bb7 -- -- -- Am7 D7").to_midi(
    "example.midi", tempo=100, beats_per_chord=2, instrument=4
)
