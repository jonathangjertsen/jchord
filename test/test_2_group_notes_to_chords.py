from jchord.group_notes_to_chords import group_notes_to_chords


class StubNote(object):
    def __init__(self, time):
        self.time = time
        self.duration = 1.0

    def __repr__(self):
        return f"StubNote(time={self.time:.2f})"

    def __eq__(self, other):
        return self.time == other.time

    def __hash__(self):
        return hash((self.time, self.duration))


def test_group_notes_to_chords_empty():
    assert group_notes_to_chords([]) == []


def test_group_notes_to_chords_one():
    assert group_notes_to_chords([StubNote(time=1)]) == [[StubNote(time=1)]]


def test_group_notes_to_chords_two_plus_one():
    assert group_notes_to_chords(
        [StubNote(time=1), StubNote(time=1), StubNote(time=2)]
    ) == [[StubNote(time=1), StubNote(time=1)], [StubNote(time=2)]]


def test_group_notes_to_chords_one_cluster():
    assert group_notes_to_chords(
        [
            StubNote(time=0.97),
            StubNote(time=0.98),
            StubNote(time=0.99),
            StubNote(time=1),
            StubNote(time=1.01),
            StubNote(time=1.02),
            StubNote(time=1.03),
        ]
    ) == [
        [
            StubNote(time=0.97),
            StubNote(time=0.98),
            StubNote(time=0.99),
            StubNote(time=1),
            StubNote(time=1.01),
            StubNote(time=1.02),
            StubNote(time=1.03),
        ]
    ]


def test_group_notes_to_chords_two_clusters():
    assert group_notes_to_chords(
        [
            StubNote(time=0.97),
            StubNote(time=0.98),
            StubNote(time=0.99),
            StubNote(time=1),
            StubNote(time=1.01),
            StubNote(time=1.02),
            StubNote(time=1.03),
            StubNote(time=1.97),
            StubNote(time=1.98),
            StubNote(time=1.99),
            StubNote(time=2),
            StubNote(time=2.01),
            StubNote(time=2.02),
            StubNote(time=2.03),
        ]
    ) == [
        [
            StubNote(time=0.97),
            StubNote(time=0.98),
            StubNote(time=0.99),
            StubNote(time=1),
            StubNote(time=1.01),
            StubNote(time=1.02),
            StubNote(time=1.03),
        ],
        [
            StubNote(time=1.97),
            StubNote(time=1.98),
            StubNote(time=1.99),
            StubNote(time=2),
            StubNote(time=2.01),
            StubNote(time=2.02),
            StubNote(time=2.03),
        ],
    ]


def test_group_notes_to_chords_two_clusters_and_extra_note():
    assert group_notes_to_chords(
        [
            StubNote(time=0.97),
            StubNote(time=0.98),
            StubNote(time=0.99),
            StubNote(time=1),
            StubNote(time=1.01),
            StubNote(time=1.02),
            StubNote(time=1.03),
            StubNote(time=1.50),
            StubNote(time=1.97),
            StubNote(time=1.98),
            StubNote(time=1.99),
            StubNote(time=2),
            StubNote(time=2.01),
            StubNote(time=2.02),
            StubNote(time=2.03),
        ]
    ) == [
        [
            StubNote(time=0.97),
            StubNote(time=0.98),
            StubNote(time=0.99),
            StubNote(time=1),
            StubNote(time=1.01),
            StubNote(time=1.02),
            StubNote(time=1.03),
        ],
        [StubNote(time=1.50)],
        [
            StubNote(time=1.97),
            StubNote(time=1.98),
            StubNote(time=1.99),
            StubNote(time=2),
            StubNote(time=2.01),
            StubNote(time=2.02),
            StubNote(time=2.03),
        ],
    ]
