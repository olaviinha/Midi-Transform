import math

class EventRegistry(object):
    Events = {}
    MetaEvents = {}

    @classmethod
    def register_event(cls, event, bases):
        if (Event in bases) or (NoteEvent in bases):
            assert event.statusmsg not in cls.Events, \
                            "Event %s already registered" % event.name
            cls.Events[event.statusmsg] = event
        elif (MetaEvent in bases) or (MetaEventWithText in bases):
            assert event.metacommand not in cls.MetaEvents, \
                            "Event %s already registered" % event.name
            cls.MetaEvents[event.metacommand] = event
        else:
            raise ValueError("Unknown bases class in event type: " + event.name)


class RegistryMixin:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in ['AbstractEvent', 'Event', 'MetaEvent', 'NoteEvent',
                                'MetaEventWithText']:
            EventRegistry.register_event(cls, cls.__bases__)


class AbstractEvent(RegistryMixin):
    __slots__ = ['tick', 'data']
    name = "Generic MIDI Event"
    length = 0
    statusmsg = 0x0

    class __metaclass__(type):
        def __init__(cls, name, bases, dict):
            if name not in ['AbstractEvent', 'Event', 'MetaEvent', 'NoteEvent',
                            'MetaEventWithText']:
                EventRegistry.register_event(cls, bases)

    def __init__(self, **kw):
        if type(self.length) == int:
            defdata = [0] * self.length
        else:
            defdata = []
        self.tick = 0
        self.data = defdata
        for key in kw:
            setattr(self, key, kw[key])

    def __cmp__(self, other):
        if self.tick < other.tick: return -1
        elif self.tick > other.tick: return 1
        return cmp(self.data, other.data)

    def __baserepr__(self, keys=[]):
        keys = ['tick'] + keys + ['data']
        body = []
        for key in keys:
            val = getattr(self, key)
            keyval = "%s=%r" % (key, val)
            body.append(keyval)
        body = str.join(', ', body)
        return "midi.%s(%s)" % (self.__class__.__name__, body)

    def __repr__(self):
        return self.__baserepr__()


class Event(AbstractEvent):
    __slots__ = ['channel']
    name = 'Event'

    def __init__(self, **kw):
        if 'channel' not in kw:
            kw = kw.copy()
            kw['channel'] = 0
        super(Event, self).__init__(**kw)

    def copy(self, **kw):
        _kw = {'channel': self.channel, 'tick': self.tick, 'data': self.data}
        _kw.update(kw)
        return self.__class__(**_kw)

    def __cmp__(self, other):
        if self.tick < other.tick: return -1
        elif self.tick > other.tick: return 1
        return 0

    def __repr__(self):
        return self.__baserepr__(['channel'])

    def is_event(cls, statusmsg):
        return (cls.statusmsg == (statusmsg & 0xF0))
    is_event = classmethod(is_event)


"""
MetaEvent is a special subclass of Event that is not meant to
be used as a concrete class.  It defines a subset of Events known
as the Meta events.
"""

class MetaEvent(AbstractEvent):
    statusmsg = 0xFF
    metacommand = 0x0
    name = 'Meta Event'

    def is_event(cls, statusmsg):
        return (statusmsg == 0xFF)
    is_event = classmethod(is_event)


"""
NoteEvent is a special subclass of Event that is not meant to
be used as a concrete class.  It defines the generalities of NoteOn
and NoteOff events.
"""

class NoteEvent(Event):
    __slots__ = ['_pitch', '_velocity']
    length = 2

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, val):
        self._pitch = val

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, val):
        self._velocity = val

class NoteOnEvent(NoteEvent):
    statusmsg = 0x90
    name = 'Note On'

class NoteOffEvent(NoteEvent):
    statusmsg = 0x80
    name = 'Note Off'

class AfterTouchEvent(Event):
    statusmsg = 0xA0
    length = 2
    name = 'After Touch'

class ControlChangeEvent(Event):
    __slots__ = ['_control', '_value']
    statusmsg = 0xB0
    length = 2
    name = 'Control Change'

    @property
    def control(self):
        return self._control

    @control.setter
    def control(self, val):
        self._control = val

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

class ProgramChangeEvent(Event):
    __slots__ = ['_value']
    statusmsg = 0xC0
    length = 1
    name = 'Program Change'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

class ChannelAfterTouchEvent(Event):
    __slots__ = ['_value']
    statusmsg = 0xD0
    length = 1
    name = 'Channel After Touch'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

class PitchWheelEvent(Event):
    __slots__ = ['_pitch']
    statusmsg = 0xE0
    length = 2
    name = 'Pitch Wheel'

    @property
    def pitch(self):
        return ((self._pitch[1] << 7) | self._pitch[0]) - 0x2000

    @pitch.setter
    def pitch(self, value):
        adjusted_value = value + 0x2000
        self._pitch[0] = adjusted_value & 0x7F
        self._pitch[1] = (adjusted_value >> 7) & 0x7F


class SysexEvent(Event):
    statusmsg = 0xF0
    name = 'SysEx'
    length = 'varlen'

    def is_event(cls, statusmsg):
        return (cls.statusmsg == statusmsg)
    is_event = classmethod(is_event)

class SequenceNumberMetaEvent(MetaEvent):
    name = 'Sequence Number'
    metacommand = 0x00
    length = 2

class MetaEventWithText(MetaEvent):
    def __init__(self, **kw):
        super(MetaEventWithText, self).__init__(**kw)
        if 'text' not in kw:
            self.text = ''.join(chr(datum) for datum in self.data)
    
    def __repr__(self):
        return self.__baserepr__(['text'])

class TextMetaEvent(MetaEventWithText):
    name = 'Text'
    metacommand = 0x01
    length = 'varlen'

class CopyrightMetaEvent(MetaEventWithText):
    name = 'Copyright Notice'
    metacommand = 0x02
    length = 'varlen'

class TrackNameEvent(MetaEventWithText):
    name = 'Track Name'
    metacommand = 0x03
    length = 'varlen'

class InstrumentNameEvent(MetaEventWithText):
    name = 'Instrument Name'
    metacommand = 0x04
    length = 'varlen'

class LyricsEvent(MetaEventWithText):
    name = 'Lyrics'
    metacommand = 0x05
    length = 'varlen'

class MarkerEvent(MetaEventWithText):
    name = 'Marker'
    metacommand = 0x06
    length = 'varlen'

class CuePointEvent(MetaEventWithText):
    name = 'Cue Point'
    metacommand = 0x07
    length = 'varlen'

class SomethingEvent(MetaEvent):
    name = 'Something'
    metacommand = 0x09

class ChannelPrefixEvent(MetaEvent):
    name = 'Channel Prefix'
    metacommand = 0x20
    length = 1

class PortEvent(MetaEvent):
    name = 'MIDI Port/Cable'
    metacommand = 0x21

class TrackLoopEvent(MetaEvent):
    name = 'Track Loop'
    metacommand = 0x2E

class EndOfTrackEvent(MetaEvent):
    name = 'End of Track'
    metacommand = 0x2F

class SetTempoEvent(MetaEvent):
    __slots__ = ['_bpm', '_mpqn']
    name = 'Set Tempo'
    metacommand = 0x51
    length = 3

    @property
    def bpm(self):
        return float(6e7) / self.mpqn

    @bpm.setter
    def bpm(self, value):
        self._mpqn = int(float(6e7) / value)

    @property
    def mpqn(self):
        assert(len(self.data) == 3)
        # vals = [self.data[x] << (0o16 - (8 * x)) for x in range(3)]
        vals = [self.data[x] << (0o20 - (8 * x)) for x in range(3)]
        return sum(vals)

    @mpqn.setter
    def mpqn(self, value):
        self.data = [(value >> (0o16 - (8 * x)) & 0xFF) for x in range(3)]

class SmpteOffsetEvent(MetaEvent):
    name = 'SMPTE Offset'
    metacommand = 0x54

import math

class TimeSignatureEvent(MetaEvent):
    __slots__ = ['_numerator', '_denominator', '_metronome', '_thirtyseconds']
    name = 'Time Signature'
    metacommand = 0x58
    length = 4

    @property
    def numerator(self):
        return self.data[0]

    @numerator.setter
    def numerator(self, value):
        self.data[0] = value

    @property
    def denominator(self):
        return 2 ** self.data[1]

    @denominator.setter
    def denominator(self, value):
        self.data[1] = int(math.log(value, 2))

    @property
    def metronome(self):
        return self.data[2]

    @metronome.setter
    def metronome(self, value):
        self.data[2] = value

    @property
    def thirtyseconds(self):
        return self.data[3]

    @thirtyseconds.setter
    def thirtyseconds(self, value):
        self.data[3] = value


class KeySignatureEvent(MetaEvent):
    __slots__ = ['_alternatives', '_minor']
    name = 'Key Signature'
    metacommand = 0x59
    length = 2

    @property
    def alternatives(self):
        d = self.data[0]
        return d - 256 if d > 127 else d

    @alternatives.setter
    def alternatives(self, value):
        self.data[0] = 256 + value if value < 0 else value

    @property
    def minor(self):
        return self.data[1]

    @minor.setter
    def minor(self, value):
        self.data[1] = value


class SequencerSpecificEvent(MetaEvent):
    name = 'Sequencer Specific'
    metacommand = 0x7F

