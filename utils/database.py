import logging
import json

logger = logging.getLogger(__name__)
database_name = "source/database.json"


def _load_raw() -> dict:
    with open(database_name, encoding="utf-8", mode="r") as file:
        raw = json.load(file)
    return raw


def _save_raw(raw: dict) -> dict:
    with open(database_name, encoding="utf-8", mode="w") as file:
        json.dump(raw, file, ensure_ascii=False, sort_keys=True, indent=4)
    return raw


def create_game(key: str, uid_n_word: str) -> dict:
    raw = _load_raw()
    raw[key] = []
    uid, word = uid_n_word.split("*")
    raw[key].append({uid: word})
    return _save_raw(raw)


def get_game(key: str) -> any:
    raw = _load_raw()
    return key in raw and raw[key]


def is_new_user(key: str, uid: str) -> bool:
    raw = _load_raw()
    for _uid_n_word in raw[key]:
        if list(_uid_n_word.keys())[0] == uid:
            return False
    else:
        return True


def get_next_user(key: str) -> str:
    raw = _load_raw()
    users = raw[key]

    result = []
    for uid_n_word in list(reversed(users)):
        uid = list(uid_n_word.keys())[0]
        if uid in result:
            continue
        else:
            result.append(uid)
    logger.debug(f"{result=}")
    return result[len(result)-1]


def get_users(key: str) -> list:
    raw = _load_raw()
    users = raw[key]

    result = []
    for uid_n_word in list(reversed(users)):
        uid = list(uid_n_word.keys())[0]
        if uid in result:
            continue
        else:
            result.append(uid)
    return result


def get_words(key: str) -> list:
    raw = _load_raw()
    users = raw[key]

    result = [(list(uid_n_word.values())[0]) for uid_n_word in users]
    return result


def get_last_word(key: str) -> str:
    raw = _load_raw()
    return key in raw and list(raw[key][-1].values())[0]


def get_last_act(key: str) -> dict:
    raw = _load_raw()
    return raw[key][-1] if (key in raw) else {}


def is_in_game(key: str, value: str):
    raw = _load_raw()
    for _dict in raw[key]:
        if _dict[list(_dict.keys())[0]] == value:
            return True
    else:
        return False


def exist_game(key: str):
    raw = _load_raw()
    return key in raw


def append_word(key: str, uid_n_word: str) -> dict:
    raw = _load_raw()
    raw: dict[str, list[dict[str, str]]]
    uid, word = uid_n_word.split("*")
    for _u_v in raw[key]:
        if word == list(_u_v.values())[0]:
            break
    else:
        raw[key].append({uid: word})
    return _save_raw(raw)


def delete_game(key: str) -> dict:
    raw: dict[str, list[str]]
    raw = _load_raw()
    raw.pop(key, None)
    return _save_raw(raw)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    create_game("test", "test1*мама")
    append_word("test", "test1*арбуз")
    append_word("test", "test2*зебра")
    print(get_next_user("test"))
    append_word("test", "test1*аршина")
    print(get_next_user("test"))
    append_word("test", "test3*алгебра")
    print(get_next_user("test"))
    append_word("test", "test2*арест")
    print(get_next_user("test"))
    append_word("test", "test4*тыква")
    print(get_next_user("test"))
    append_word("test", "test1*артикуль")
    print(get_next_user("test"))
    delete_game("test")
