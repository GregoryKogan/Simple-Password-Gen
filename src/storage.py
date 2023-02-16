import json
import os
from argon2.low_level import hash_secret
from aes_cipher import AESCipher
import config


class Storage:
    def __init__(self, encryption_key: str, filename: str = "storage.json"):
        self._encryption_key = encryption_key
        self._data = {}

        self._filename = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(self._filename):
            self._load()
        else:
            self._save()

    def __repr__(self) -> str:
        return f"<Storage {json.dumps(self._data)}>"

    @staticmethod
    def exists(filename: str = "storage.json") -> bool:
        filename = os.path.join(os.path.dirname(__file__), filename)
        return os.path.exists(filename)

    @staticmethod
    def _hash(data: str, salt: str) -> str:
        return (
            hash_secret(
                data.encode(),
                salt.encode(),
                time_cost=config.HASHER_PARAMS.time_cost,
                memory_cost=config.HASHER_PARAMS.memory_cost,
                parallelism=config.HASHER_PARAMS.parallelism,
                hash_len=config.HASHER_PARAMS.hash_len,
                type=config.HASHER_PARAMS.type,
            ).decode("utf-8")
        )

    def _save(self):
        with open(self._filename, "w") as storage:
            json.dump({
                config.STORAGE_SALT_KEY: "SUPER SECURE SALT",
                config.STORAGE_DATA_KEY: AESCipher.encrypt(
                    Storage._hash(
                        data=self._encryption_key,
                        salt="SUPER SECURE SALT"
                    ),
                    json.dumps(self._data)
                )
            }, storage)

    def _load(self):
        with open(self._filename, "r") as storage:
            storage_data = json.load(storage)
            self._data = json.loads(
                AESCipher.decrypt(
                    Storage._hash(
                        data=self._encryption_key,
                        salt=storage_data.get(config.STORAGE_SALT_KEY)
                    ),
                    storage_data.get(config.STORAGE_DATA_KEY)
                )
            )

    def write(self, key: str, value: object) -> None:
        self._data[key] = value
        self._save()

    def read(self, key: str) -> object:
        return self._data.get(key)

    def stores_key(self, key: str) -> bool:
        return key in self._data
