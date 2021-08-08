from collections import defaultdict
from math import exp, ceil
from typing import List

from jchord.midi import MidiNote

# Notes separated by less than this much belong to one chord
MIN_SEP_INTERVAL = 0.1

# Bucket size for the KDE algorithm
KDE_BUCKETS_PER_SECOND = 1 / MIN_SEP_INTERVAL


def kernel_default(distance):
    """
    Default kernel
    """
    return exp(-((distance / MIN_SEP_INTERVAL) ** 2))


def group_notes_to_chords(notes: List[MidiNote], kernel=None) -> List[List[MidiNote]]:
    """
    Groups the list of `MidiNote`s by time.

    The return value maps time to a list of `MidiNote`s for that time.
    """
    if kernel is None:
        kernel = kernel_default

    # Degenerate case: no notes -> no chords
    if not notes:
        return []

    # Ensure notes are sorted
    notes = sorted(notes, key=lambda note: note.time)

    # Get the total duration of all notes
    min_time = notes[0].time
    max_time = notes[-1].time

    # Degenerate case: all in one chord
    if (max_time - min_time) <= MIN_SEP_INTERVAL:
        return [notes]

    max_time += notes[-1].duration
    duration = max_time - min_time

    # Do kernel density estimate
    bucket_duration = 1.0 / KDE_BUCKETS_PER_SECOND
    kde = [
        sum(kernel(abs(note.time - i * bucket_duration)) for note in notes)
        for i in range(ceil(KDE_BUCKETS_PER_SECOND * duration))
    ]

    # Find kde_threshold such that the times between the first and last note in a chord
    # always has kde[t] > kde_threshold
    buckets = defaultdict(list)
    kde_threshold = float("inf")
    for note in notes:
        bucket = min(int(note.time / bucket_duration), len(kde) - 1)
        buckets[bucket].append(note)
        kde_threshold = min(kde_threshold, kde[bucket])

    # It needs to be a little bit lower than that to ensure all notes get included in a chord.
    # Arbitrarily reduce by 25%
    kde_threshold *= 0.95

    # Do grouping
    chords = []
    cur_chord = []
    for i, kde_val in enumerate(kde):
        if kde_val > kde_threshold:
            if i in buckets:
                cur_chord.extend(buckets[i])
        else:
            if cur_chord:
                chords.append(cur_chord)
            cur_chord = []
    if cur_chord:
        chords.append(cur_chord)

    return chords
