"""Data structs for use within the hermes ecosystem."""

import logging
import json
import time
import sys
from functools import reduce


log = logging.getLogger(__name__)


class Envelope:
    """Transport Object for data being sent between hermes components via ZMQ.

    It is encouraged to use :class:`hermes.Message` as data for more complex data objects, but
    all JSON-serializable built-in data types are supported.

    They track topic and origin of the data they transport, as well as the
    timestamp it was last updated at. Updates occur automatically whenever
    :meth:`hermes.Envelope.serialize` is called.
    This timestamp can be used to detect Slow-Subscriber-Syndrome by :class:`hermes.Receiver` and
    to initiate the suicidal snail pattern.
    """

    __slots__ = ['topic', 'origin', 'data', 'ts']

    def __init__(self, topic_tree, origin, data, ts=None):
        """Initialize an :class:`hermes.Envelope` instance.

        :param topic_tree: topic this data belongs to
        :param origin: the sender of this message (Publisher)
        :param data: data struct transported by this instance
        :param ts: timestamp of this message, defaults to current unix ts if
                   None
        """
        self.topic = topic_tree
        self.origin = origin
        self.data = data
        self.ts = ts or time.time()

    def __repr__(self):
        """Construct a basic string-represenation of this class instance."""
        return ("Envelope(topic=%r, origin=%r, data=%r, ts=%r)" %
                (self.topic, self.origin, self.data, self.ts))

    @staticmethod
    def load_from_frames(frames, encoding=None):
        """
        Load json to a new :class:`hermes.Envelope` instance.

        Automatically converts to string if the passed object is
        a :class:`bytes.encode()` object.

        :param frames: Frames, as received by :meth:`zmq.socket.recv_multipart`
        :param encoding: The encoding to use for :meth:`bytes.encode()`; default UTF-8
        :return: :class:`hermes.Envelope` instance
        """
        encoding = encoding if encoding else 'utf-8'
        topic, origin, data, ts = [json.loads(x.decode(encoding)) for x in frames]
        data_dtype = data[0]

        def load_class_from_string(class_name):
            """Load the data into its relevant dtype, if available."""
            return reduce(getattr, class_name.split("."), sys.modules[__name__]).empty().load(data)
        try:
            data = load_class_from_string(data_dtype)
        except AttributeError:
            pass

        return Envelope(topic, origin, data, ts)

    def convert_to_frames(self, encoding=None):
        """
        Encode the :class:`hermes.Envelope` attributes as a list of json-serialized strings.

        :param encoding: the encoding to us for :meth:`str.encode()`, default UTF-8
        :return: list of :class:`bytes`
        """
        encoding = encoding if encoding else 'utf-8'
        self.update_ts()

        topic = json.dumps(self.topic).encode(encoding)
        origin = json.dumps(self.origin).encode(encoding)
        ts = json.dumps(self.ts).encode(encoding)

        try:
            data = self.data.serialize(encoding)
        except AttributeError:
            data = json.dumps(self.data).encode(encoding)

        return topic, origin, data, ts

    def update_ts(self):
        """Update the :class:`hermes.Envelope` timestamp."""
        self.ts = time.time()


class Message:
    """
    Basic Struct class for data sent via an :class:`hermes.Envelope`.

    Provides basic and dynamic load and dump functions to easily load
    data to and from it.

    If you have complex data types, consider extending this class, as it requires less overhead
    than, for example, dictionaries, by using __slots__.

    The class's timestamp attribute (ts) denotes the time of which the data was received.
    """

    __slots__ = ['dtype', 'ts']

    def __init__(self, ts=None):
        """
        Initialize a :class:`hermes.Message` instance.

        ts is the timestamp which should be used as reference when calculating
        the age of the :class:`hermes.Message` instance.

        :param ts: timestamp at which the message was created.
        """
        self.ts = time.time() if not ts else ts
        self.dtype = self._class_to_string()

    def load(self, data):
        """
        Load data into a new data struct.

        :param data: iterable, as transported by :class:`hermes.Envelope`
        :return: :class:`hermes.Message`
        """
        for value, attr in zip(data, self._slots()):
            setattr(self, attr, value)

        return self

    def serialize(self, encoding=None):
        """
        Serialize this data struct to :class:`bytes`.

        :param encoding: Encoding to use in str.encode()
        :return: data of this struct as :class:`bytes`
        """
        encoding = 'utf-8' if not encoding else encoding
        data = [getattr(self, attr) for attr in self._slots()]
        return json.dumps(data).encode(encoding)

    def _slots(self):
        """
        Get the instance's attributes as defined in its __slots__ attribute.

         This includes all parents' __slots__ values.

         Returns it in order of inheritance (base class __slots__ first).

        :return: :class:`list`, copy of __slots__
        """
        slot_attrs = []
        class_slots = [cls for cls in reversed(type(self).__mro__[:-1])]
        for cls in class_slots:
            for attr in cls.__slots__:
                slot_attrs.append(attr)
        return slot_attrs

    def _class_to_string(self):
        """Convert this class name into a :class:`str`."""
        return self.__class__.__qualname__

    # pylint: disable=too-many-format-args
    def __repr__(self):
        """Construct a basic string-represenation of this class instance."""
        attributes_as_strings = '('
        for attr in self._slots():
            attributes_as_strings += '{0}={1}, '.format(attr, getattr(self, attr))
        attributes_as_strings = attributes_as_strings[:-2] + ')'
        s = "{0}{1}".format(self._class_to_string(), attributes_as_strings)
        return s
