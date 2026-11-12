# time_ordered_key_value_store_kit

A key-value store that indexes entries by an explicit timestamp, supporting range queries and retrieval of the most recent entries.

## Usage

```python
from time_ordered_key_value_store_kit import TimeOrderedKeyValueStore

store = TimeOrderedKeyValueStore()
store.insert("alpha", 1, timestamp=100.0)
store.insert("beta", 2, timestamp=200.0)
store.insert("gamma", 3, timestamp=300.0)

# Range query: entries with timestamp in [150.0, 250.0]
for entry in store.range_query(150.0, 250.0):
    print(entry.key, entry.value, entry.timestamp)  # beta 2 200.0

# Most recent 2 entries, newest first
for entry in store.most_recent(2):
    print(entry.key, entry.value)  # gamma 3, beta 2

# Key lookup
print(store.get("alpha"))  # 1
```

## Why this library exists

Many key-value stores order by insertion order but do not let you query by time. This library adds a timestamp index so you can ask for all entries in a time window or the latest N entries. The trade-off is that insertion is O(n) because the timestamp index is a sorted list; range queries are O(log n + k). For small to medium stores this is a good balance. If you need O(log n) inserts, use a balanced tree, but that adds complexity and dependencies.

## Awkward edge

If you insert a key that already exists, the value is updated but the original timestamp is kept. This means the store does not record update times. If you need to treat updates as separate events, use distinct keys for each event.
