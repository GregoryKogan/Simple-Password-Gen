import json
import os


class Storage:
    def __init__(self, filename: str = "storage.json") -> None:
        self._filename = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(self._filename):
            with open(self._filename, "w") as storage:
                storage.write("{}")

    def write(self, key: str, value: object) -> None:
        with open(self._filename, "r") as f:
            data = json.load(f)
        data[key] = value
        with open(self._filename, "w") as f:
            json.dump(data, f)

    def read(self, key: str) -> object:
        with open(self._filename, "r") as f:
            data = json.load(f)
        return data.get(key)
