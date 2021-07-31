"""
Contains various literals that are used for computations throughout the library.

* `REPETITION_SYMBOL` (`str`): The symbol that's used to indicate repetition in textual representations of chord progressions.
* `MAJOR_SCALE_OFFSETS` (`Dict[int, int]`): Maps the scale degrees of the major scale to number of semitones from the root.
* `ACCIDENTALS` (`Set[str]`): The set of accidentals.
* `MAJOR_FROM_C` (`List[str]`): A list of the 7 note names in the C major scale.
* `CHROMATIC` (`List[str]`): A list of the 12 chromatic notes starting from C. Only sharp notes are included here.
* `ENHARMONIC` (`List[Tuple[str, str]])`): A list of the 5 pairs of enharmonic note names.
* `CHORD_NAMES` (`Dict[str, List[str]]`): Maps chord names to the list of scale degrees in the chord, not including the root.
* `CHORD_ALIASES`: (`Dict[str, str]`): Maps alternative chord names to the canonical chord name in `CHORD_NAMES`.
* `DYADS`: (`Dict[int, str]`): A collection of two-note chords with names. Maps the number of semitones between the root and the other note to the chord name.
* `TRIADS_WITH_FIFTH` (`Dict[int, str]`): A collection of three-note chords with names. All of these triads include a fifth. Maps the semitone that is not the root or the fifth to the chord name.
"""
REPETITION_SYMBOL = "--"
MAJOR_SCALE_OFFSETS = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}
ACCIDENTALS = {"b", "#"}
MAJOR_FROM_C = ["C", "D", "E", "F", "G", "A", "B"]
ROMAN = ["III", "IV", "II", "I", "VII", "VI", "V"]
LETTERS = ROMAN + MAJOR_FROM_C
CHROMATIC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ENHARMONIC = [("C#", "Db"), ("D#", "Eb"), ("F#", "Gb"), ("G#", "Ab"), ("A#", "Bb")]
CHORD_NAMES = {
    # Major
    "maj": ["3", "5"],
    "maj7": ["3", "5", "7"],
    "maj9": ["3", "5", "7", "9"],
    "maj11": ["3", "5", "7", "9", "11"],
    "maj13": ["3", "5", "7", "9", "11", "13"],
    "6": ["3", "5", "6"],
    "69": ["3", "5", "6", "9"],
    "5": ["5"],
    # Dominant
    "7": ["3", "5", "b7"],
    "9": ["3", "5", "b7", "9"],
    "11": ["3", "5", "b7", "9", "11"],
    "13": ["3", "5", "b7", "9", "11", "13"],
    # Minor
    "m": ["b3", "5"],
    "m6": ["b3", "5", "6"],
    "m7": ["b3", "5", "b7"],
    "m9": ["b3", "5", "b7", "9"],
    "m11": ["b3", "5", "b7", "9", "11"],
    "m13": ["b3", "5", "b7", "9", "11", "13"],
    # Diminished
    "dim": ["b3", "b5"],
    "m7b5": ["b3", "b5", "b7"],
    "dim7": ["b3", "b5", "bb7"],
    # Augmented
    "aug": ["3", "#5"],
    # Suspended
    "7sus2": ["2", "5", "b7"],
    "7sus4": ["4", "5", "b7"],
    # Note
    "n": [],
}
CHORD_ALIASES = {
    # Major
    "major": "maj",
    "maj": "maj",
    # Minor
    "-": "m",
    "min": "m",
    "minor": "m",
    # Dominant
    "dom": "7",
    # Diminished
    "o": "dim7",
    "ø": "m7b5",
    # Augmented
    "+": "aug",
    # Note
    "note": "n",
}
DYADS = {3: "min(no5)", 4: "(no5)", 7: "5"}
TRIADS_WITH_FIFTH = {
    1: "phryg",
    2: "sus2",
    3: "min",
    4: "",
    5: "sus4",
    6: "lyd",
    8: "b6(no3)",
    9: "6(no3)",
    10: "7(no3)",
    11: "maj7(no3)",
}
