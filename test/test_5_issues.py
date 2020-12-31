import os

from jchord.chords import ChordWithRoot, InvalidChord
from jchord.progressions import ChordProgression


def make_midi_file(chord_names, beats_per_chord, out_file):
    chords = []
    for name in chord_names:
        try:
            chord = ChordWithRoot.from_name(name)
        except InvalidChord:
            chord = ChordProgression.DUMMY_CHORD
        chords.append(chord)

    progression = ChordProgression(chords)
    progression.to_midi(out_file, instrument=11, beats_per_chord=beats_per_chord)


def test_github_issue_56():
    """https://github.com/jonathangjertsen/jchord/issues/56"""
    midi_filename_reference = os.path.join(
        os.path.dirname(__file__), "test_data", "issue_56.mid"
    )
    midi_filename_generated = os.path.join(
        os.path.dirname(__file__), "test_data", "issue_56_generated.mid"
    )

    # Data from the image
    names = ["N", "B:min", "B:min", "B:min", "B:min", "G:maj", "G:maj", "G:maj"]
    beats_per_chord = [1, 2, 1, 2, 0.5, 0.25, 0.75, 2]
    # Convert names to what the library expects
    names = [name.replace(":", "") for name in names]

    # Generate a file
    make_midi_file(names, beats_per_chord, midi_filename_generated)

    with open(midi_filename_generated, "rb") as generated_file:
        generated_bytes = generated_file.read()

    with open(midi_filename_reference, "rb") as reference_file:
        reference_bytes = reference_file.read()

    assert generated_bytes == reference_bytes
    os.remove(midi_filename_generated)
