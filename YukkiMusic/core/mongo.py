#
# File-based Database replacement for MongoDB
# Uses JSON files instead of MongoDB for persistence
#

import json
import os
from pathlib import Path

DB_DIR = Path("filedb")
DB_DIR.mkdir(exist_ok=True)


def _get_path(collection: str) -> Path:
    return DB_DIR / f"{collection}.json"


def _load(collection: str) -> list:
    path = _get_path(collection)
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save(collection: str, data: list):
    path = _get_path(collection)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


class FakeCursor:
    def __init__(self, items):
        self._items = items

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item

    async def to_list(self, length=None):
        if length:
            return self._items[:length]
        return self._items


class FakeCollection:
    def __init__(self, name: str):
        self._name = name

    def _data(self):
        return _load(self._name)

    def _write(self, data):
        _save(self._name, data)

    async def find_one(self, query: dict):
        data = self._data()
        for doc in data:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    def find(self, query: dict = None):
        data = self._data()
        if not query:
            return FakeCursor(data)
        results = []
        for doc in data:
            match = True
            for k, v in query.items():
                if isinstance(v, dict):
                    doc_val = doc.get(k)
                    for op, op_val in v.items():
                        if op == "$gt" and not (doc_val is not None and doc_val > op_val):
                            match = False
                        elif op == "$lt" and not (doc_val is not None and doc_val < op_val):
                            match = False
                else:
                    if doc.get(k) != v:
                        match = False
            if match:
                results.append(doc)
        return FakeCursor(results)

    async def insert_one(self, document: dict):
        data = self._data()
        data.append(document)
        self._write(data)
        return document

    async def update_one(self, query: dict, update: dict, upsert: bool = False):
        data = self._data()
        found = False
        for i, doc in enumerate(data):
            if all(doc.get(k) == v for k, v in query.items()):
                if "$set" in update:
                    data[i].update(update["$set"])
                found = True
                break
        if not found and upsert:
            new_doc = {**query}
            if "$set" in update:
                new_doc.update(update["$set"])
            data.append(new_doc)
        self._write(data)

    async def delete_one(self, query: dict):
        data = self._data()
        for i, doc in enumerate(data):
            if all(doc.get(k) == v for k, v in query.items()):
                data.pop(i)
                break
        self._write(data)


class FakeDatabase:
    def __getattr__(self, name: str) -> FakeCollection:
        return FakeCollection(name)


# Public exports
mongodb = FakeDatabase()
pymongodb = FakeDatabase()
