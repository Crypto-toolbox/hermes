# Import Built-Ins
import logging
import unittest
import json

# Import Homebrew
from hermes import Envelope, Message
from hermes.structs import Quote, Candle, Order, Trades, Book, RawBook, TopLevel

# Init Logging Facilities
log = logging.getLogger(__name__)


class StructsTests(unittest.TestCase):

    def test_Envelope_dumps_and_loads_data_correctly(self):
        # Assert dump and load works for arbitrary iterable
        msg = Envelope('test/message', 'testsuite', ['this', 'is', 'data'])
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Envelope.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Envelope)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, list)
        for item in loaded_msg.data:
            self.assertIsInstance(item, str)

    def test_Message_dumps_and_loads_correctly(self):
        m = Message()
        serialized = m.serialize()
        self.assertIsInstance(serialized, bytes)
        try:
            decoded_m = json.loads(serialized.decode("utf-8"))
        except UnicodeDecodeError:
            self.fail("Encoding is not UTF-8!")
        except json.JSONDecodeError:
            self.fail("Data is not JSON-serialized!")
        m2 = Message()
        m2 = m2.load(decoded_m)
        self.assertEqual(m2.dtype, m.dtype)
        self.assertEqual(m2.ts, m.ts)

    def test_slots_list_is_generated_correctly(self):
        slots = Message()._slots()
        self.assertEqual(slots[0], 'dtype')
        self.assertEqual(slots[1], 'ts')
        self.assertIsInstance(Message()._class_to_string(), str)

    def test_repr_prints_expected_output(self):
        m = Message()
        expected_str = "Message(dtype=Message, ts=%r)" % m.ts
        self.assertEqual(m.__repr__(), expected_str)

    def test_quote_constructs_as_expected(self):
        with self.assertRaises(ValueError):
            Quote('BTCUSD', 1000, 10, 'spaghetti', api_ts=None)

        q = Quote('BTCUSD', 1000, 10, 'bid')
        self.assertIsInstance(q.ts, float)
        self.assertIsInstance(q.api_ts, float)

    def test_order_instance_is_generated_correctly(self):
        q = Quote('BTCUSD', 1000, 10, 'bid')
        opposite_order = Order.from_quote(q)
        self.assertEqual(opposite_order.side, 'ask')
        self.assertEqual(opposite_order.price, str(1000))
        self.assertEqual(opposite_order.size, str(10))
        self.assertEqual(opposite_order.pair, 'BTCUSD')
        same_side_order = Order.from_quote(q, same_side=True)
        self.assertEqual(same_side_order.side, 'bid')
        self.assertEqual(same_side_order.price, str(1000))
        self.assertEqual(same_side_order.size, str(10))
        self.assertEqual(same_side_order.pair, 'BTCUSD')

    def test_Message_converts_Quote_class_correctly(self):
        pair, price, size, side = 'BTCUSD', 1000, 10, 'bid'
        quote = Quote(pair, price, size, side)
        msg = Message('test/message', 'testsuite', quote)
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Message.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Message)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, Quote, msg=loaded_msg.data)
        self.assertIsInstance(loaded_msg.data.pair, str)
        self.assertEqual(loaded_msg.data.pair, pair)
        self.assertIsInstance(loaded_msg.data.price, str)
        self.assertEqual(loaded_msg.data.price, str(price))
        self.assertIsInstance(loaded_msg.data.size, str)
        self.assertEqual(loaded_msg.data.size, str(size))
        self.assertIsInstance(loaded_msg.data.side, str)
        self.assertEqual(loaded_msg.data.side, side)

    def test_Message_converts_Order_class_correctly(self):
        pair, price, size, side = 'BTCUSD', 1000, 10, 'bid'
        order = Order(pair, price, size, side)
        msg = Message('test/message', 'testsuite', order)
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Message.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Message)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, Order, msg=loaded_msg.data)
        self.assertIsInstance(loaded_msg.data.pair, str)
        self.assertEqual(loaded_msg.data.pair, pair)
        self.assertIsInstance(loaded_msg.data.price, str)
        self.assertEqual(loaded_msg.data.price, str(price))
        self.assertIsInstance(loaded_msg.data.size, str)
        self.assertEqual(loaded_msg.data.size, str(size))
        self.assertIsInstance(loaded_msg.data.side, str)
        self.assertEqual(loaded_msg.data.side, side)

    def test_Message_converts_Trades_class_correctly(self):
        pair, price, size, side = 'BTCUSD', 1000, 10, 'bid'
        t = pair, price, size, side, 'UID1000', None, 22
        trades = Trades(*[t for i in range(10)])
        msg = Message('test/message', 'testsuite', trades)
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Message.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Message)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, Trades, msg=loaded_msg.data)
        for trade in loaded_msg.data.trades:
            symbol, price, size, side, uid, misc, ts = trade
            self.assertEqual(pair, symbol)
            self.assertIsInstance(price, str)
            self.assertEqual(price, str(price))
            self.assertIsInstance(size, str)
            self.assertEqual(size, str(size))
            self.assertIsInstance(side, str)
            self.assertEqual(side, side)
            self.assertEqual(uid, 'UID1000')
            self.assertEqual(misc, None)
            self.assertEqual(ts, str(22))

    def test_Message_converts_Candle_class_correctly(self):
        o, h, l, c = 100, 1000, 0, 50
        pair = 'BTCUSD'
        candle = Candle(pair, o, h, l, c, None)
        msg = Message('test/message', 'testsuite', candle)
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Message.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Message)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, Candle, msg=loaded_msg.data)
        self.assertIsInstance(loaded_msg.data.pair, str)
        self.assertEqual(loaded_msg.data.pair, pair)
        self.assertIsInstance(loaded_msg.data.open, str)
        self.assertEqual(loaded_msg.data.open, str(o))
        self.assertIsInstance(loaded_msg.data.high, str)
        self.assertEqual(loaded_msg.data.high, str(h))
        self.assertIsInstance(loaded_msg.data.low, str)
        self.assertEqual(loaded_msg.data.low, str(l))
        self.assertIsInstance(loaded_msg.data.close, str)
        self.assertEqual(loaded_msg.data.close, str(c))

    def test_Message_converts_Book_class_correctly(self):
        pair = 'BTCUSD'
        bids = [['1000', 15, '121314255.00'], ['999', 155, '121314254.00']]
        bids_as_stringified_list = [[str(i) for i in x] for x in bids]
        asks = [['1001', 15, '121314255.00'], ['1002', 155, '121314254.00']]
        asks_as_stringified_list = [[str(i) for i in x] for x in asks]
        with self.assertRaises(TypeError):
            Book(pair, bids, asks, None)
        book = Book(pair, bids_as_stringified_list, asks_as_stringified_list, None)
        msg = Message('test/message', 'testsuite', book)
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Message.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Message)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, Book, msg=loaded_msg.data)
        self.assertIsInstance(loaded_msg.data.pair, str)
        self.assertEqual(loaded_msg.data.pair, pair)
        self.assertIsInstance(loaded_msg.data.bids, list)
        self.assertEqual(loaded_msg.data.bids, bids_as_stringified_list)
        self.assertIsInstance(loaded_msg.data.asks, list)
        self.assertEqual(loaded_msg.data.asks, asks_as_stringified_list)

    def test_Message_converts_RawBook_class_correctly(self):
        pair = 'BTCUSD'
        bids = [['1000', 15, '121314255.00', 'id-111-1'],
                ['999', 150, '121314254.00', 'id-0124-2']]
        bids_as_stringified_list = [[str(i) for i in x] for x in bids]
        asks = [['1001', 15, '121314255.00',  'id-111-2'],
                ['1002', 150, '121314254.00', 'id-0124-3']]
        asks_as_stringified_list = [[str(i) for i in x] for x in asks]
        with self.assertRaises(TypeError):
            RawBook(pair, bids, asks, None)

        book = RawBook(pair, bids_as_stringified_list, asks_as_stringified_list, None)
        msg = Message('test/message', 'testsuite', book)
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Message.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Message)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, Book, msg=loaded_msg.data)
        self.assertIsInstance(loaded_msg.data.pair, str)
        self.assertEqual(loaded_msg.data.pair, pair)
        self.assertIsInstance(loaded_msg.data.bids, list)
        self.assertEqual(loaded_msg.data.bids, bids_as_stringified_list)
        self.assertIsInstance(loaded_msg.data.asks, list)
        self.assertEqual(loaded_msg.data.asks, asks_as_stringified_list)

    def test_Message_converts_TopLevel_class_correctly(self):
        bid, ask = ['1000', 11, '442345441'], ['999', 142, '415251525']
        bid_as_stringified_list = [str(x) for x in bid]
        ask_as_stringified_list = [str(x) for x in ask]
        pair = 'BTCUSD'
        tlevel = TopLevel(pair, bid, ask, None)
        msg = Message('test/message', 'testsuite', tlevel)
        dumped_msg = msg.convert_to_frames()
        self.assertIsInstance(dumped_msg, (list, tuple))
        for item in dumped_msg:
            self.assertIsInstance(item, bytes)

        loaded_msg = Message.load_from_frames(dumped_msg)
        self.assertIsInstance(loaded_msg, Message)
        self.assertIsInstance(loaded_msg.topic, str)
        self.assertIsInstance(loaded_msg.origin, str)
        self.assertIsInstance(loaded_msg.ts, float)
        self.assertIsInstance(loaded_msg.data, TopLevel, msg=loaded_msg.data)
        self.assertIsInstance(loaded_msg.data.pair, str)
        self.assertEqual(loaded_msg.data.pair, pair)
        self.assertIsInstance(loaded_msg.data.bid, list)
        self.assertEqual(loaded_msg.data.bid, bid_as_stringified_list)
        self.assertIsInstance(loaded_msg.data.ask, list)
        self.assertEqual(loaded_msg.data.ask, ask_as_stringified_list)