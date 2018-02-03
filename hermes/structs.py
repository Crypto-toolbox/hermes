"""Data structs for use within the hermes ecosystem."""

import logging
import json
import time
import sys
from functools import reduce

from hermes.utils import check_pairs

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


class PricedMessage(Message):
    """Defines classes that have a price associated with them."""

    # pylint: disable=too-many-arguments
    __slots__ = ['pair', 'price', 'size', 'side', 'api_ts']

    def __init__(self, pair, price, size, side, api_ts=None, ts=None):
        """Initialize a PricedMessage instance.

        :param pair: Symbol of trading pair this quote is valid for
        :param price: price of the quote per unit
        :param size: number of units to buy or sell in this quote
        :param side: 'bid' or 'ask'
        :param api_ts: timestamp provided by the API, if present, else current ts
        :param ts: timestamp of creation of this struct, defaults to current ts
        """
        super(PricedMessage, self).__init__(ts)
        self.pair = pair
        self.price = str(price)
        self.size = str(size)
        if side not in ('bid', 'ask', 'buy', 'sell', 'N/A'):
            raise ValueError("'side' argument must be either 'bid' or 'ask' "
                             "or 'N/A'!")
        self.side = side
        self.api_ts = api_ts if api_ts else time.time()


class Quotes(Message):
    """Container class for quotes.

    Enables batch sending of Quotes, instead of sending them separately.

    """
    def __init__(self, quotes, ts=None):
        super(Quotes, self).__init__(ts)
        self.quotes = quotes

    def pop(self):
        """Remove the first quote from the internal quotes attribute and convert to Quote instance.

        If self.quotes is empty, return None
        """
        try:
            q_data = self.quotes.pop(0)
        except IndexError:
            return None
        return Quote(*q_data)


class Quote(PricedMessage):
    """
    Class to represent a Quote in an order book.

    Provides support for level aggregation via the '+' operator, but requires
    pairs and price to match in order for this addition to work.
    """

    # pylint: disable=too-many-arguments

    __slots__ = ['uid']

    def __init__(self, pair, price, size, side, uid=None, api_ts=None, ts=None):
        """
        Initialize a Quote instance.

        :param pair: Symbol of trading pair this quote is valid for
        :param price: price of the quote per unit
        :param size: number of units to buy or sell in this quote
        :param side: 'bid' or 'ask'
        :param uid: Unique Identifier for quote, if available.
        :param api_ts: timestamp provided by the API, if present, else None
        :param ts: timestamp of creation of this struct, defaults to current ts
        """
        super(Quote, self).__init__(pair, price, size, side, api_ts, ts)
        self.uid = uid

    @staticmethod
    def empty():
        """Return an empty Quote instance."""
        return Quote(None, None, None, 'N/A')

    @check_pairs
    def __add__(self, other):
        """
        Consolidate two quotes by adding them.

        Only works if both have the same side and price. Otherwise
        exceptions are thrown (IncompatibleSidesError or ValueError,
        respectively)

        :param other: Quote instance
        :return:
        """
        if other.side == self.side and self.price == other.price:
            # consolidate
            return Quote(self.pair, self.price, self.size + other.size, self.side)
        elif other.side != self.side:
            raise IncompatibleSidesError
        elif other.price != self.price:
            raise ValueError("Price levels do not match! Cannot add Quotes!")

    @check_pairs
    def __sub__(self, other):
        """
        Substract a Quote from another Quote.

        Only works if both have the same side and price. Otherwise
        exceptions are thrown (IncompatibleSidesError or ValueError,
        respectively)

        :param other: Quote instance
        :return:
        """
        if other.side == self.side and self.price == other.price:
            # consolidate
            return Quote(self.pair, self.price, self.size - other.size, self.side)
        elif other.side != self.side:
            raise IncompatibleSidesError
        elif other.price != self.price:
            raise ValueError("Price levels do not match! Cannot subtract "
                             "Quotes!")

    def __repr__(self):
        """Construct a basic string-represenation of this class instance."""
        return "Quote(pair=%r, price=%r, size=%r, side=%r, api_timestamp=%r, " \
               "cts_timestamp=%r)" % (self.pair, self.price, self.size,
                                      self.side, self.api_ts, self.ts)


class Order(PricedMessage):
    """
    Data structure to hold and create Order data.

    This struct is used to issue a trade to the API.

    Also works as a converter from quotes to Order instances.
    """

    # pylint: disable=too-many-arguments
    __slots__ = ['flags']

    def __init__(self, pair, price, size, side, api_ts=None, ts=None, **flags):
        """
        Initialize a Order instance.

        :param pair: Symbol of trading pair this order is valid for
        :param price: price of the order per unit
        :param size: number of units to buy or sell in this order, 0 if the order was deleted.
        :param side: 'bid' or 'ask'
        :param api_ts: timestamp of the creation of the order within the CTS
        :param ts: timestamp of creation of this struct, defaults to current ts
        :param flags: Additional options for the Order
        """
        super(Order, self).__init__(pair, price, size, side, api_ts,
                                    ts=ts)
        self.flags = flags

    @staticmethod
    def empty():
        """Return an empty Order instance."""
        return Order(None, None, None, 'N/A')

    @staticmethod
    def from_quote(quote, same_side=False, **flags):
        """
        Create a new Order instance from the given Quote.

        By default, this returns an Order on the opposite side of the Quote
        passed to the function. To avoid this, pass same_side=True.

        :param quote: Quote class instance
        :param same_side: Bool, whether to post opposite to quote or not
        :param flags: additional options for the execution of the trade
        :return: Order instance
        """
        if same_side:
            side = quote.side
        else:
            side = 'bid' if quote.side == 'ask' else 'ask'
        return Order(quote.pair, quote.price, quote.size, side, time.time(),
                     **flags)

    def __repr__(self):
        """Construct a basic string-represenation of this class instance."""
        return ("Order(pair=%r, price=%r, size=%s, side=%s, flags=%s, "
                "api_ts=%r, ts=%r" % (self.pair, self.price, self.size,
                                      self.side, self.flags, self.api_ts,
                                      self.ts))


class Trades(Message):
    """
    Data struct to hold post-trade information about a Trade.

    It is created after the trade and received by the CTS from the API.
    """

    # pylint: disable=too-many-arguments
    __slots__ = ['trades']

    def __init__(self, *trades, ts=None):
        """
        Initialize a Trade instance.

            Expected format of trades:
                [(pair, price, size, side, uid, misc, ts),
                (pair, price, size, side, uid, misc, ts), ..]

        :param trades: list or tuple of tuples containing at least 6 items each.
        :param api_ts: timestamp as provided by the API of this trade
        :param ts: timestamp of creation of this struct, defaults to current ts
        """
        if trades:
            assert all(len(item) == 7 for item in trades)
            trades = [[str(x) if x else x for x in t] for t in trades]

        else:
            trades = []
        super(Trades, self).__init__(ts=ts)
        self.trades = trades

    @staticmethod
    def empty():
        """Return an empty Trade instance."""
        return Trades()

    def __repr__(self):
        """Construct a basic string-represenation of this class instance."""
        return "Trade(trades=%r, ts=%r)" % (self.trades, self.ts)


class Candle(Message):
    """
    Data Structure for OHLC candle data.

    Provides merge() method to combine several candles into a single one, and
    also allows simple addition of two candles using the '+' operator (USE WITH
    CAUTION!).

    """

    # pylint: disable=too-many-arguments

    __slots__ = ['pair', 'open', 'high', 'low', 'close', 'frame']

    def __init__(self, pair, _open=None, high=None, low=None, close=None,
                 ts=None, frame=None):
        """
        Initialize a Candle instance.

        :param pair: Currency Pair
        :param _open: Open price
        :param high: high price
        :param low:  low price
        :param close: closing price
        :param timestamp: timestamp as float
        :param frame: frame as seconds
        """
        super(Candle, self).__init__(ts=ts)
        self.pair = pair
        self.open = str(_open)
        self.high = str(high)
        self.low = str(low)
        self.close = str(close)
        self.frame = frame

    @staticmethod
    def empty():
        """Return an empty Candle instance."""
        return Candle(None)

    def merge(self, *others):
        """
        Merge all given Candles into a single candle.

        This assigns OHLC correctly - max(all_high_vals), min(all_low_vals),
        open value of candle with the smallest timestamp, close value of candle
        with biggest timestamp, (frame of last ts - earliest ts) + last candle
        frame.

        :param others: Candle() instances
        :return: Candle() instance
        """
        highs = [c.high for c in (self, *others)]
        lows = [c.low for c in (self, *others)]
        last_candle = max((self, *others), key=lambda x: x.ts)
        first_candle = min((self, *others), key=lambda x: x.ts)
        new_frame = (last_candle.ts - first_candle.ts) + last_candle.frame
        return Candle(self.pair, first_candle.open, max(highs), min(lows),
                      last_candle.close, first_candle.ts, new_frame)

    def __repr__(self):
        """Construct a basic string-represenation of this class instance."""
        return "Candle(_open=%r, high=%r, low=%r, close=%r, timestamp=%r, " \
               "frame=%r)" % (self.open, self.high, self.low, self.close,
                              self.ts, self.frame)


class TopLevel(Message):
    """Struct representing the best bid and ask quote of a given order book."""

    __slots__ = ['bid', 'ask', 'pair']

    def __init__(self, pair, bid, ask, ts=None):
        """
        Initialize the class instance.

        :param pair: symbol pair this TopLevel instance refers to.
        :param bid: 3-item tuple of (price, size, ts)
        :param ask: 3-item tuple of (price, size, ts)
        :param ts: unix time stamp of creation of this instance.
        """
        super(TopLevel, self).__init__(ts)
        self.bid = tuple([str(x) for x in bid])
        self.ask = tuple([str(x) for x in ask])
        self.pair = pair

    @staticmethod
    def empty():
        """Return an empty class instance."""
        return TopLevel(None, tuple(), tuple())


class Book(Message):
    """Struct representing the level 2 order book for a given pair."""

    __slots__ = ['bids', 'asks', 'pair']

    def __init__(self, pair, bids, asks, ts=None):
        """
        Initialize the instance.

        :param bids: list, tuple  of bid quotes
        :param asks: list, tuple of ask quotes
        :param pair: symbol the quotes relate to
        :param ts: unix timestamp of instance creation
        """
        super(Book, self).__init__(ts)
        self.bids = self.format_quotes(bids)
        self.asks = self.format_quotes(asks)
        self.pair = pair

    @staticmethod
    def format_quotes(iterable):
        """
        Format the given iterable containing quotes.

        list or tuples must have three-item-sized elements
        (i.e. [('price', 'size', 'ts'), ('price', 'size', 'ts'), ..])

        :param iterable: list, tuple
        :return: tuple of tuples
        """
        if isinstance(iterable, (list, tuple)):
            if (all(len(item) == 3 for item in iterable) and
                    all(all(isinstance(x, str) for x in item) for item in iterable)):
                return tuple([tuple(item) for item in iterable])
            raise TypeError("Each quote must be a three-item-tuple of strings!")
        raise TypeError("Quotes must be passed as tuple or list, not %r!" % type(iterable))

    @staticmethod
    def empty():
        """Return an empty class instance."""
        return Book(None, tuple(), tuple())


class RawBook(Book):
    """Struct representing the level 3 order book for a given pair."""

    __slots__ = []

    @staticmethod
    def format_quotes(iterable):
        """
        Format the given iterable containing quotes.

        list or tuples must have four-item-sized elements
        (i.e. [('price', 'size', 'ts', 'tid'), ('price', 'size', 'ts', 'tid'), ..])

        :param iterable: list, tuple
        :return: tuple of tuples
        """
        if isinstance(iterable, (list, tuple)):
            if (all(len(item) == 4 for item in iterable) and
                    all(all(isinstance(x, str) for x in item) for item in iterable)):
                return tuple([tuple(item) for item in iterable])
            raise TypeError("Each quote must be a four-item-tuple of strings!")
        raise TypeError("Quotes must be passed as tuple or list, not %r!" % type(iterable))

    @staticmethod
    def empty():
        """Return an empty class instance."""
        return RawBook(None, tuple(), tuple())