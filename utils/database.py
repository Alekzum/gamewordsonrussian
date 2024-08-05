import logging
import json
import os

    
class Logs(dict):
    Act = dict[str, str]
    Message = str

    games = dict[str, list[Act]]
    binds = dict[str, list[Message]]


def _load_raw() -> Logs:
    with open(database_name, encoding="utf-8") as file:
        raw = json.load(file)
    return raw


def _save_raw(raw: dict) -> dict[str, dict[str, list[str]]]:
    with open(database_name, encoding="utf-8", mode="w") as file:
        json.dump(raw, file, ensure_ascii=False, sort_keys=True, indent=4)
    return raw


logger = logging.getLogger(__name__)
database_name = f"source{os.sep}database.json"

if not os.path.isfile(database_name):
    _save_raw({})


# Message uids
def get_messages(key: str) -> list[str]:
    raw = _load_raw()
    return raw["binds"].get(key, [])


def append_message(key: str, message_inline_id: str) -> dict:
    raw = _load_raw()
    if key not in raw["binds"]:
        raw["binds"][key] = []
    raw["binds"][key].append(message_inline_id)
    return _save_raw(raw)


def delete_messages(key: str):
    raw = _load_raw()
    raw["binds"][key] = None
    return _save_raw(raw)


# Games
def create_game(key: str, uid_n_word: str) -> dict:
    raw = _load_raw()
    raw["games"][key] = []
    uid, word = uid_n_word.split("*")
    raw["games"][key].append({uid: word})
    return _save_raw(raw)


def get_game(key: str) -> any:
    raw = _load_raw()
    return key in raw["games"] and raw["games"][key]

{
    'binds':{
        'time.userid':['inline_message_id1', 'inline_message_id2']
    },
    'games':{
        'time.userid':[
            {'user': 'word'},
            {'user2': 'word2'}
        ]
    }
}


def is_new_user(key: str, uid: str) -> bool:
    raw = _load_raw()
    games = raw['games']
    acts = games.get(key, [{'0': None}])
    uids = set(map(lambda d: list(d.values())[0], acts))
    return not(uid in uids)
    # for _uid_n_word in raw["games"][key]:
    #     if list(_uid_n_word.keys())[0] == uid:
    #         return False
    # else:
    #     return True


def get_next_user(key: str) -> str:
    raw = _load_raw()
    users = raw["games"][key]

    result = []
    for uid_n_word in list(reversed(users)):
        uid = list(uid_n_word.keys())[0]
        if uid in result:
            continue
        else:
            result.append(uid)
    logger.debug(f"{result=}")
    return result[len(result) - 1]


def get_users(key: str) -> list:
    raw = _load_raw()
    users = raw["games"][key]

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
    users = raw["games"][key]

    result = [(list(uid_n_word.values())[0]) for uid_n_word in users]
    return result


def get_last_letter(key: str) -> str:
    word = get_last_word(key)
    return word[-2] if word[-1] in "ьъы" else word[-1]


def get_last_word(key: str) -> str:
    raw = _load_raw()
    return key in raw["games"] and list(raw["games"][key][-1].values())[0]


def get_last_act(key: str) -> dict:
    raw = _load_raw()
    return raw["games"][key][-1] if (key in raw["games"]) else {}


def is_in_game(key: str, value: str):
    raw = _load_raw()
    for _dict in raw["games"][key]:
        if _dict[list(_dict.keys())[0]] == value:
            return True
    else:
        return False


def exist_game(key: str):
    raw = _load_raw()
    return key in raw["games"]


def append_word(key: str, uid_n_word: str) -> dict:
    raw = _load_raw()
    uid, word = uid_n_word.split("*")
    for _u_v in raw["games"][key]:
        if word == list(_u_v.values())[0]:
            break
    else:
        raw["games"][key].append({uid: word})
    return _save_raw(raw)


def delete_game(key: str) -> dict:
    raw = _load_raw()
    games = raw["games"]
    games.pop(key, None)
    raw["games"] = games
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
