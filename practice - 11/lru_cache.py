"""Вопрос с собеседования: LRU-кэш с get/put за O(1) (LeetCode 146)."""
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()  # самые свежие ключи - в конце

    def get(self, key):
        if key not in self.data:
            return -1
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)  # вытесняем самый давний


if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    print(cache.get(1))   # 1
    cache.put(3, 3)       # вытесняется ключ 2
    print(cache.get(2))   # -1
    cache.put(4, 4)       # вытесняется ключ 1
    print(cache.get(1))   # -1
    print(cache.get(3))   # 3
    print(cache.get(4))   # 4
