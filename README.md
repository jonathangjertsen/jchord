# jchord - Python toolkit for working with chord progressions

[![Build Status](https://travis-ci.com/jonathangjertsen/jchord.svg?branch=master)](https://travis-ci.com/jonathangjertsen/jchord)
[![codecov](https://codecov.io/gh/jonathangjertsen/jchord/branch/master/graph/badge.svg)](https://codecov.io/gh/jonathangjertsen/jchord)

```
>>> from jchord.progressions import ChordProgression
>>> prog = ChordProgression.from_string("C -- Fm7 -- C -- G7 -- C -- E7 Am F Bm7b5 E7 Am9 F Bo C69 --")
>>> print(prog.to_string())
C      --     Fm7    --
C      --     G7     --
C      --     E7     Am
F      Bm7b5  E7     Am9
F      Bo     C69    --
>>> prog.to_midi("example.midi", tempo=100, beats_per_chord=2, instrument=4)
```

* Chord progressions can be imported from:
    - string (`prog = ChordProgression.from_string(string)`)
    - text file (`prog = ChordProgression.from_txt(filename)`)
    - XLSX file (`prog = ChordProgression.from_xlsx(filename)`)
* Chord progressions can be exported to:
    - string (`print(prog.to_string(...optional))`)
    - text file (`prog.to_txt(filename, ..optional)`)
    - XLSX file (`prog.to_xlsx(filename, ...optional)`)
    - MIDI file (`prog.to_midi(filename, ...optional)`)

# Install

* git clone it, then `pip install -e .`
* Install the right requirements:
    * All functionality: `pip install -r requirements_full.txt`
    * No XLSX or MIDI conversion: `pip install -r requirements_minimal.txt`
    * Package development: `pip install -r requirements_dev.txt`

# Development

## Testing

To run the tests:

```
pytest --cov-report term-missing --cov jchord
```

Make sure all tests pass and that the code has 100% test coverage.

## Formatting

The code is formatted with black. In the root of the repo, run:

```
black .
```

## Documenting

To generate documentation, run the documentation generation script:

```
python doc_gen/generate_doc.py
```

The script appends documentation from each source module to `doc_gen/index.md`. If the script ran successfully, README.md should contain a section called "Documentation" below.

To decide which parts should be present in the documentation, go and edit `doc_gen/pydocmd.yml`. The reason for the format is that I originally wanted to use `pydocmd` (but found it too limiting).

---

# Documentation

## Table of contents
* <a href='#jchordcore'>`jchord.core`</a>
    * Class <a href='#Note'>`Note`</a>
        * Method `Note.__init__(self, name: str, octave: int)`
        * Method `Note.pitch(self) -> float`
        * Method `Note.transpose(self: 'Note', shift: int) -> 'Note'`
        * Method `Note.transpose_degree(self: 'Note', shift: str) -> 'Note'`
    * Class <a href='#CompositeObject'>`CompositeObject`</a>
        * Method `CompositeObject._keys(self) -> Hashable`
    * Function `split_to_base_and_shift(name_or_degree: str, name_before_accidental: bool) -> (<class 'str'>, <class 'int'>)`
    * Function `degree_to_semitone(degree: str) -> int`
    * Function `semitone_to_degree_options(semitone: int, max_accidentals: int = 1) -> List[str]`
    * Function `note_diff(name_low: str, name_high: str) -> int`
    * Exception `InvalidDegree`
* <a href='#jchordmidi'>`jchord.midi`</a>
    * Class <a href='#PlayedNote'>`PlayedNote`</a>
        * Method `PlayedNote.time(self)`
        * Method `PlayedNote.note(self)`
        * Method `PlayedNote.duration(self)`
    * Function `note_to_midi(note: jchord.core.Note) -> int`
    * Function `midi_to_note(midi: int) -> jchord.core.Note`
    * Function `midi_to_pitch(midi: int) -> float`
    * Function `read_midi_file(filename: str) -> List[jchord.midi.PlayedNote]`
    * Function `group_notes_to_chords(notes: List[jchord.midi.PlayedNote]) -> Dict[float, jchord.midi.PlayedNote]`
    * Exception `InvalidNote`
* <a href='#jchordknowledge'>`jchord.knowledge`</a>
* <a href='#jchordchords'>`jchord.chords`</a>
    * Class <a href='#Chord'>`Chord`</a>
        * Method `Chord.__init__(self, name: str, semitones: List[int])`
        * Method `Chord.from_semitones(name: Union[str, NoneType], semitones: List[int]) -> 'Chord'`
        * Method `Chord.from_degrees(name: str, degrees: List[str]) -> 'Chord'`
        * Method `Chord.from_name(name: str) -> 'Chord'`
        * Method `Chord.intervals(self) -> List[int]`
        * Method `Chord.with_root(self, root: jchord.core.Note) -> 'ChordWithRoot'`
        * Method `Chord.add_semitone(self, semitone: int)`
    * Class <a href='#ChordWithRoot'>`ChordWithRoot`</a>
        * Method `ChordWithRoot.__init__(self, name: str, root: jchord.core.Note, chord: jchord.chords.Chord)`
        * Method `ChordWithRoot.from_root_and_semitones(root: jchord.core.Note, semitones: List[int]) -> 'ChordWithRoot'`
        * Method `ChordWithRoot.from_midi(midi: Set[int]) -> 'ChordWithRoot'`
        * Method `ChordWithRoot.from_name(name: str, octave: int = 4) -> 'ChordWithRoot'`
        * Method `ChordWithRoot.semitones(self)`
        * Method `ChordWithRoot.intervals(self) -> List[int]`
        * Method `ChordWithRoot.midi(self) -> List[int]`
        * Method `ChordWithRoot.transpose(self, shift: int) -> 'ChordWithRoot'`
    * Function `semitones_to_chord_name_options(semitones: Set[int], _rec=5) -> List[str]`
    * Exception `InvalidChord`
* <a href='#jchordprogressions'>`jchord.progressions`</a>
    * Class <a href='#ChordProgression'>`ChordProgression`</a>
        * Method `ChordProgression.__init__(self, progression: List[jchord.chords.ChordWithRoot])`
        * Method `ChordProgression.from_string(string: str) -> 'ChordProgression'`
        * Method `ChordProgression.from_txt(filename: str) -> 'ChordProgression'`
        * Method `ChordProgression.from_xlsx(filename: str) -> 'ChordProgression'`
        * Method `ChordProgression.from_midi_file(filename: str) -> 'ChordProgression'`
        * Method `ChordProgression.chords(self) -> Set[jchord.chords.ChordWithRoot]`
        * Method `ChordProgression.midi(self) -> List[List[int]]`
        * Method `ChordProgression.to_string(self, chords_per_row: int = 4, column_spacing: int = 2, newline: str = '\n') -> str`
        * Method `ChordProgression.to_txt(self, filename: str, chords_per_row: int = 4, column_spacing: int = 2, newline: str = '\n')`
        * Method `ChordProgression.to_xlsx(self, filename: str, chords_per_row: int = 4)`
        * Method `ChordProgression.to_midi(self, filename: str, instrument: int = 1, tempo: int = 120, beats_per_chord: int = 2, velocity: int = 100)`
    * Class <a href='#SongSection'>`SongSection`</a>
        * Method `SongSection.name(self)`
        * Method `SongSection.progression(self)`
    * Class <a href='#Song'>`Song`</a>
        * Method `Song.__init__(self, sections: List[jchord.progressions.SongSection])`
        * Method `Song.to_string(self, chords_per_row: int = 4, column_spacing: int = 2, newline: str = '\n')`
    * Exception `InvalidProgression`

## `jchord.core`


Basic utilities for working with notes, base classes for objects etc.

### Classes

#### `Note`

Represents an absolute note with a name and an octave.

Two `Note`s are equal if they have the same name and octave,
or if they have the same octave and their names are enharmonic
(so `Note('A#', 4) == Note('Gb', 4)`)


##### Methods

###### `__init__(self, name: str, octave: int)`




###### `pitch(self) -> float`

Returns the absolute pitch of the note in Hz.

Examples (equalities are approximate):

* `Note("A", 4).pitch() == 440.0`
* `Note("A", 0).pitch() == 27.5`
* `Note("C", 4).pitch() == 261.62556`



###### `transpose(self: 'Note', shift: int) -> 'Note'`

Transposes the note by the given number of semitones.

Examples:

* `Note("C", 0).transpose(1) == Note("C#", 0)`
* `Note("C", 4).transpose(19) == Note("G", 5)`



###### `transpose_degree(self: 'Note', shift: str) -> 'Note'`

Transposes the given note by the given scale degree

Examples:

* `Note("C", 0).transpose_degree("b2") == Note("C#", 0)`
* `Note("C", 4).transpose_degree("12") == Note("G", 5)`



---



#### `CompositeObject`


Base class for objects which can be represented by a few attributes.

Subclasses must implement a `_keys()` function which returns a hashable
representation of these attributes (e.g. returns them as a tuple).

A CompositeObject is considered equal to another if the return value of their 
`_keys()` function is equal.

Iterating over a CompositeObject is like iterating over the return value of its
`_keys()` function.


##### Methods

###### `_keys(self) -> Hashable`

Returns a hashable representation of the attributes that the object wraps.


---


### Functions

#### `split_to_base_and_shift(name_or_degree: str, name_before_accidental: bool) -> (<class 'str'>, <class 'int'>)`

Takes a string representation of a note name or a degree. Returns a 
tuple where the first element is the string representation of the degree
with accidentals removed, and the second element is the number of semitones
needed to account fo accidentals.

Examples:

* `split_to_base_and_shift("A#", name_before_accidental=True) == ("A", 1)`
* `split_to_base_and_shift("Ab", name_before_accidental=True) == ("A", -1)`
* `split_to_base_and_shift("A", name_before_accidental=True) == ("A", 0)`
* `split_to_base_and_shift("Abbbb", name_before_accidental=True) == ("A", -4)`
* `split_to_base_and_shift("b9", name_before_accidental=False) == ("9", -1)`
* `split_to_base_and_shift("#9", name_before_accidental=False) == ("9", 1)`



#### `degree_to_semitone(degree: str) -> int`

Converts a string representation of a scale degree to the number of semitones between the root and that scale degree.

Examples:

* `degree_to_semitone("b9") == 13`
* `degree_to_semitone("5") == 7`



#### `semitone_to_degree_options(semitone: int, max_accidentals: int = 1) -> List[str]`

Converts the number of semitones between the root and the wanted scale degree to
a list of possible names for that scale degree.

The list of options is sorted by "reasonableness":

* If option A has fewer accidentals than option B, option A comes first.
* If option A has the same number of accidentals as option B, then the option with a "b" comes before the option with a "#".

Examples:

* `semitone_to_degree_options(semitone=3, max_accidentals=1) = ["b3", "#2"]`
* `semitone_to_degree_options(semitone=3, max_accidentals=0) = []`
* `semitone_to_degree_options(semitone=17, max_accidentals=1) = ["11", "#10"]`



#### `note_diff(name_low: str, name_high: str) -> int`

Returns the number of semitones between the first note and the second note.
The first note is assumed to be the lower of the two notes.

Examples:

* `note_diff("G", "A") == 2`
* `note_diff("A", "Bb") == 1`
* `note_diff("A", "G") == 10`
* `note_diff("A", "A") == 0`


### Exceptions

#### `InvalidDegree`

Raised if the string one attempts to interpret is not a valid scale degree



---



## `jchord.midi`


Tools for working with MIDI.

### Classes

#### `PlayedNote`

namedtuple which represents a (MIDI) note played at a given time for a given duration.

##### Methods

###### `time(self)`

Alias for field number 0


###### `note(self)`

Alias for field number 1


###### `duration(self)`

Alias for field number 2


---


### Functions

#### `note_to_midi(note: jchord.core.Note) -> int`

Returns the midi value corresponding to the given `Note`.


#### `midi_to_note(midi: int) -> jchord.core.Note`

Returns the `Note` corresponding to the given MIDI note value.


#### `midi_to_pitch(midi: int) -> float`

Returns the absolute pitch in Hz for the given MIDI note value.


#### `read_midi_file(filename: str) -> List[jchord.midi.PlayedNote]`

Reads the MIDI file for the given filename and returns the corresponding list of `PlayedNote`s.


#### `group_notes_to_chords(notes: List[jchord.midi.PlayedNote]) -> Dict[float, jchord.midi.PlayedNote]`

Groups the list of `PlayedNote`s by time.

The return value maps time to a list of `PlayedNote`s for that time.

There is no attempt at quantization at this time, so the notes must be played
at the exact same time to be grouped together.


### Exceptions

#### `InvalidNote`

Raised when trying to get the MIDI value of a note that doesn't seem valid.



---



## `jchord.knowledge`


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



---



## `jchord.chords`


Tools for working with chords.

### Classes

#### `Chord`

Represents a chord quality (no root).

##### Methods

###### `__init__(self, name: str, semitones: List[int])`




###### `from_semitones(name: Union[str, NoneType], semitones: List[int]) -> 'Chord'`

Creates a Chord from a list of semitones from the root.

If `name` is `None`, `semitones_to_chord_name_options` is used to guess a good name for the chord.



###### `from_degrees(name: str, degrees: List[str]) -> 'Chord'`

Creates a Chord from a list of scale degrees.

If `name` is `None`, `semitones_to_chord_name_options` is used to guess a good name for the chord.



###### `from_name(name: str) -> 'Chord'`

Creates a Chord from a name.
The `CHORD_NAMES` and `CHORD_ALIASES` dictionaries in `jchord.knowledge` are used to find the semitones in the chord.

Raises `InvalidChord` if no chord is found.



###### `intervals(self) -> List[int]`

Returns the list of internal intervals in the chord.

Examples:

* `Chord.from_name("minor").intervals() == [3, 4]`
* `Chord.from_name("major7").intervals() == [4, 3, 4]`



###### `with_root(self, root: jchord.core.Note) -> 'ChordWithRoot'`

Returns a `ChordWithRoot` based on the chord and the provided root.


###### `add_semitone(self, semitone: int)`

Adds the given semitone (as a difference from the root degree) to the chord.

The name of the chord does not get re-calculated, so use with care.



---



#### `ChordWithRoot`

Represents a chord with a chord quality and a root note.

##### Methods

###### `__init__(self, name: str, root: jchord.core.Note, chord: jchord.chords.Chord)`




###### `from_root_and_semitones(root: jchord.core.Note, semitones: List[int]) -> 'ChordWithRoot'`

Creates a ChordWithRoot from a root `Note` and a list of semitones from the root.

`semitones_to_chord_name_options` is used to guess a good name for the chord.



###### `from_midi(midi: Set[int]) -> 'ChordWithRoot'`

Creates a ChordWithRoot from a set of MIDI note values.

`semitones_to_chord_name_options` is used to guess a good name for the chord.



###### `from_name(name: str, octave: int = 4) -> 'ChordWithRoot'`

Creates a ChordWithRoot from a name.

`semitones_to_chord_name_options` is used to guess a good name for the chord.



###### `semitones(self)`

Returns the semitones in the chord.


###### `intervals(self) -> List[int]`

Returns the semitones in the chord.


###### `midi(self) -> List[int]`

Returns the list of MIDI note values in the chord.


###### `transpose(self, shift: int) -> 'ChordWithRoot'`

Transposes the chord by the given shift (in semitones).


---


### Functions

#### `semitones_to_chord_name_options(semitones: Set[int], _rec=5) -> List[str]`

Returns a set of chord names corresponding to the given set of semitones.

The function tries to put the most reasonable chord names first and the more dubious ones last.

The `_rec` argument is for internal use only; in some cases, it prevents infinite recursion while computing the chord name.


### Exceptions

#### `InvalidChord`

Raised if trying to construct a chord from an invalid chord name.



---



## `jchord.progressions`


Tools for working with chord progressions.

### Classes

#### `ChordProgression`

Represents a chord progression.

##### Methods

###### `__init__(self, progression: List[jchord.chords.ChordWithRoot])`




###### `from_string(string: str) -> 'ChordProgression'`

Creates a `ChordProgression` from its string representation.


###### `from_txt(filename: str) -> 'ChordProgression'`

Creates a `ChordProgression` from a text file with its string representation.


###### `from_xlsx(filename: str) -> 'ChordProgression'`

Creates a `ChordProgression` from an Excel file.


###### `from_midi_file(filename: str) -> 'ChordProgression'`

Creates a `ChordProgression` from an MIDI file.

There is no attempt at quantization at this time, so the notes must be played
at the exact same time to be grouped together as chords.



###### `chords(self) -> Set[jchord.chords.ChordWithRoot]`

Returns the set of chords in the progression.


###### `midi(self) -> List[List[int]]`

Returns the MIDI values for each chord in the progression.


###### `to_string(self, chords_per_row: int = 4, column_spacing: int = 2, newline: str = '\n') -> str`

Returns the string representation of the chord progression.


###### `to_txt(self, filename: str, chords_per_row: int = 4, column_spacing: int = 2, newline: str = '\n')`

Saves the string representation of the chord progression to a text file.


###### `to_xlsx(self, filename: str, chords_per_row: int = 4)`

Saves the chord progression to an Excel file.


###### `to_midi(self, filename: str, instrument: int = 1, tempo: int = 120, beats_per_chord: int = 2, velocity: int = 100)`

Saves the chord progression to a MIDI file.


---



#### `SongSection`

Represents a section in a Song.

##### Methods

###### `name(self)`

Alias for field number 0


###### `progression(self)`

Alias for field number 1


---



#### `Song`

Represents a song (a series of sections).

##### Methods

###### `__init__(self, sections: List[jchord.progressions.SongSection])`




###### `to_string(self, chords_per_row: int = 4, column_spacing: int = 2, newline: str = '\n')`

Returns the string representation of the song.


---


### Exceptions

#### `InvalidProgression`

Raised when encountering what seems like an invalid chord progression.



---


