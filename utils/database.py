import json


file_name = "soucrce/database.json"


def _load_raw() -> dict:
    with open(file_name, encoding="utf-8", mode="r") as file:
        raw = json.load(file)
    return raw


def _save_raw(raw: dict) -> dict:
    with open(file_name, encoding="utf-8", mode="w") as file:
        json.dump(raw, file, ensure_ascii=False, indent=4, sort_keys=True)
    return raw


def create(key: str, value) -> dict:
    raw = _load_raw()
    raw[key] = value
    return _save_raw(raw)


def append(key: str, value: str) -> dict:
    raw = _load_raw()
    raw[key] = raw[key].append(value)
    return _save_raw(raw)


def delete(key: str) -> dict:
    raw: dict[str, list[str]]
    raw = _load_raw()
    raw.pop(key)
    return _save_raw(raw)
