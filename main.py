import dotenv


_dot_env_file = ".env" and input("Введите название файла с переменными (примеры: .env или env/.env):")
_env_in_dirs = dotenv.load_dotenv(_dot_env_file, verbose=True)
if not _env_in_dirs:
    DICT_API = input("Input your Yandex dictionary API "
                     "(can be finded in https://yandex.ru/dev/dictionary/keys/get/?service=dict): ")
    BOT_API = input("Input your bot's token (can be finded in @botfather): ")

    dotenv.set_key(_dot_env_file, "DICT_API", DICT_API)
    dotenv.set_key(_dot_env_file, "BOT_API", BOT_API)

else:
    DICT_API = dotenv.get_key(_dot_env_file, "DICT_API")
    BOT_API = dotenv.get_key(_dot_env_file, "BOT_API")

