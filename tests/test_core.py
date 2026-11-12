import unittest
from time_ordered_key_value_store_kit import TimeOrderedKeyValueStore, Entry


class TestTimeOrderedKeyValueStore(unittest.TestCase):
    def test_insert_and_get(self):
        store = TimeOrderedKeyValueStore()
        store.insert("a", 1, 100.0)
        self.assertEqual(store.get("a"), 1)
        self.assertIsNone(store.get("missing"))

    def test_insert_overwrites_value_but_keeps_timestamp(self):
        store = TimeOrderedKeyValueStore()
        store.insert("a", 1, 100.0)
        store.insert("a", 2, 200.0)
        self.assertEqual(store.get("a"), 2)
        entries = store.range_query(0, 1000)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].timestamp, 100.0)
        self.assertEqual(entries[0].value, 2)

    def test_range_query_inclusive(self):
        store = TimeOrderedKeyValueStore()
        store.insert("a", 1, 10.0)
        store.insert("b", 2, 20.0)
        store.insert("c", 3, 30.0)
        self.assertEqual([e.key for e in store.range_query(10.0, 20.0)], ["a", "b"])
        self.assertEqual([e.key for e in store.range_query(11.0, 29.0)], ["b"])
        self.assertEqual(store.range_query(31.0, 40.0), [])
        self.assertEqual(store.range_query(40.0, 30.0), [])

    def test_range_query_duplicate_timestamps(self):
        store = TimeOrderedKeyValueStore()
        store.insert("a", 1, 5.0)
        store.insert("b", 2, 5.0)
        store.insert("c", 3, 5.0)
        entries = store.range_query(5.0, 5.0)
        self.assertEqual([e.key for e in entries], ["a", "b", "c"])

    def test_most_recent(self):
        store = TimeOrderedKeyValueStore()
        store.insert("a", 1, 1.0)
        store.insert("b", 2, 2.0)
        store.insert("c", 3, 3.0)
        recent = store.most_recent(2)
        self.assertEqual([e.key for e in recent], ["c", "b"])
        self.assertEqual([e.value for e in recent], [3, 2])

    def test_most_recent_more_than_available(self):
        store = TimeOrderedKeyValueStore()
        store.insert("a", 1, 1.0)
        recent = store.most_recent(5)
        self.assertEqual([e.key for e in recent], ["a"])

    def test_most_recent_zero_or_negative(self):
        store = TimeOrderedKeyValueStore()
        store.insert("a", 1, 1.0)
        self.assertEqual(store.most_recent(0), [])
        self.assertEqual(store.most_recent(-1), [])

    def test_len(self):
        store = TimeOrderedKeyValueStore()
        self.assertEqual(len(store), 0)
        store.insert("a", 1, 1.0)
        store.insert("b", 2, 2.0)
        self.assertEqual(len(store), 2)
        store.insert("a", 3, 3.0)
        self.assertEqual(len(store), 2)

    def test_entry_is_namedtuple(self):
        entry = Entry(1.0, "k", "v")
        self.assertEqual(entry.timestamp, 1.0)
        self.assertEqual(entry.key, "k")
        self.assertEqual(entry.value, "v")

    def test_insert_out_of_order(self):
        store = TimeOrderedKeyValueStore()
        store.insert("c", 3, 30.0)
        store.insert("a", 1, 10.0)
        store.insert("b", 2, 20.0)
        self.assertEqual([e.key for e in store.range_query(0, 100)], ["a", "b", "c"])
        self.assertEqual([e.key for e in store.most_recent(3)], ["c", "b", "a"])


if __name__ == "__main__":
    unittest.main()
