import random

class MidiEffect(object):
    def apply(self, chord):
        pass


class Inverter(MidiEffect):
    def apply(self, chord):
        return list(reversed(chord))


class AlternatingInverter(MidiEffect):
    def __init__(self, init_state=1):
        self.state = init_state

    def apply(self, chord):
        if self.state == 0:
            self.state = 1
            return chord
        else:
            self.state = 0
            return list(reversed(chord))

class Transposer(MidiEffect):
    def __init__(self, interval):
        self.interval = interval

    def apply(self, chord):
        return sorted(list({ note._replace(note=note.note + self.interval) for note in chord }))


class Doubler(MidiEffect):
    def __init__(self, interval):
        self.transposer = Transposer(interval)

    def apply(self, chord):
        return sorted(list(set(chord) | set(self.transposer.apply(chord))))



class Spreader(MidiEffect):
    def __init__(self, amount, jitter):
        self.amount = amount
        self.jitter = jitter

    def apply(self, chord):
        displacement = 0
        for i, note in enumerate(chord):
            chord[i] = note._replace(time=note.time + displacement + self.jitter * (random.random() * 2 - 1))
            displacement += self.amount
        return chord


class Chain(MidiEffect):
    def __init__(self, *effects):
        self.effects = effects

    def apply(self, chord):
        for effect in self.effects:
            chord = effect.apply(chord)
        return chord
