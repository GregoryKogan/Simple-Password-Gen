import json
import os
from aes_cipher import AESCipher


class Storage:
    def __init__(self, encryption_key: str, filename: str = "storage.txt") -> None:
        self.encryption_key = encryption_key
        self._data = {}

        self._filename = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(self._filename):
            self.load()
        else:
            self.save()

    def __repr__(self) -> str:
        return f"<Storage {json.dumps(self._data)}>"

    def save(self):
        with open(self._filename, "w") as storage:
            storage.write(AESCipher.encrypt(self.encryption_key, json.dumps(self._data)))

    def load(self):
        with open(self._filename, "r") as storage:
            self._data = json.loads(AESCipher.decrypt(self.encryption_key, storage.read()))

    def write(self, key: str, value: object) -> None:
        self._data[key] = value
        self.save()

    def read(self, key: str) -> object:
        return self._data.get(key)

    def stores_key(self, key: str) -> bool:
        return key in self._data
