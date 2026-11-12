import bisect
from collections import namedtuple
from typing import Any, Callable, Dict, List, Optional, Tuple

Entry = namedtuple("Entry", ["timestamp", "key", "value"])


class TimeOrderedKeyValueStore:
    """
    A key-value store that indexes entries by timestamp.

    Entries are inserted with an explicit timestamp (a float). The store keeps
    a sorted list of timestamps for efficient range queries and a mapping from
    key to value for O(1) key lookups. Insertion is O(n) due to the sorted
    list insertion, but range queries are O(log n + k) where k is the number
    of results.

    The timestamp is provided by the caller, not taken from the system clock.
    This makes the store deterministic and testable. If you need wall-clock
    timestamps, pass time.time as the timestamp argument at insertion time.
    """

    def __init__(self) -> None:
        # Sorted list of timestamps. Duplicates are allowed; entries with the
        # same timestamp are ordered by insertion order.
        self._timestamps: List[float] = []
        # Parallel list of Entry objects, aligned with _timestamps.
        self._entries: List[Entry] = []
        # Mapping from key to value. Later insertions overwrite earlier ones.
        self._data: Dict[Any, Any] = {}

    def insert(self, key: Any, value: Any, timestamp: float) -> None:
        """
        Insert or update a key with a value at the given timestamp.

        If the key already exists, its value is updated. The timestamp of the
        original insertion is kept; the new timestamp is ignored for the
        existing entry. This decision keeps the store consistent: a key has
        one timestamp, the time it first appeared. If you need to record
        updates as separate events, use distinct keys.
        """
        entry = Entry(timestamp, key, value)
        if key in self._data:
            # Update the value in the existing entry, preserving its timestamp.
            # We must find the entry in the sorted list to update it in place.
            # Since entries are sorted by timestamp and then insertion order,
            # we can find the first entry with this key. To avoid O(n) search
            # on every update, we accept O(n) here because updates are expected
            # to be less frequent than inserts. The sorted list is small enough
            # in typical use.
            for i, e in enumerate(self._entries):
                if e.key == key:
                    self._entries[i] = Entry(e.timestamp, key, value)
                    self._data[key] = value
                    return
            # Should never reach here because key is in _data.
            raise RuntimeError("inconsistent store state")
        # New key: insert into sorted lists.
        idx = bisect.bisect_right(self._timestamps, timestamp)
        self._timestamps.insert(idx, timestamp)
        self._entries.insert(idx, entry)
        self._data[key] = value

    def get(self, key: Any) -> Optional[Any]:
        """Return the value for key, or None if not present."""
        return self._data.get(key)

    def range_query(self, start: float, end: float) -> List[Entry]:
        """
        Return all entries with timestamp in [start, end], inclusive.

        Results are ordered by timestamp, then by insertion order for ties.
        """
        if start > end:
            return []
        left = bisect.bisect_left(self._timestamps, start)
        right = bisect.bisect_right(self._timestamps, end)
        return self._entries[left:right]

    def most_recent(self, n: int) -> List[Entry]:
        """
        Return the n most recent entries, ordered from newest to oldest.

        If n is greater than the number of entries, all entries are returned.
        If n <= 0, an empty list is returned.
        """
        if n <= 0:
            return []
        # The entries list is sorted by timestamp ascending. The most recent
        # are at the end. We take a slice and reverse it to get newest first.
        total = len(self._entries)
        if n >= total:
            return list(reversed(self._entries))
        return list(reversed(self._entries[-n:]))

    def __len__(self) -> int:
        return len(self._entries)
