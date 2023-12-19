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

# TODO
#  Команда /start которая будет иметь кнопку, которая в свою очередь попросит юзера прислать инлайн реквест в чат
#  Инлайн старт, например просто @GameWordsOnRus_bot, появится кнопка (начать игру)


"""
думаю чисто на инлайн режиме сделать
один чел начинает, бот присылает что-то типо "ник_чела начал игру! Его слово: слово"
А снизу кнопка *Продолжить*, которая будет делать инлайн реквест типо @мой_бот uuid4_игры, 
    а подсказка (в виде текста-ответа): *введите слово для игры*
чел вводит слово, и появляется кнопка *продолжить*, или текст *это слово уже было! предложи другое*
надо ещё команду /start прикрутить, что бы было, с чего начинать
"""