# fmt: off
from pathlib import Path
from jchord import ChordProgression

prog = ChordProgression.from_midi_file(Path(__file__).parent.parent / "test" / "test_data" / "issue_8.mid")
print(prog.to_string())
