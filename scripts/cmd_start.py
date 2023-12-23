from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import enums


async def main(message: Message):
    user: User = message.from_user
    mention = user.mention_html()
    message_text = (
        f"{mention}, здравствуй! Что бы начать играть в «слова», нажми на кнопку, выбери где / с кем играть, "
        f"и начинай играть в «слова»!")
    inline_button = InlineKeyboardButton(text="Начать новую игру", switch_inline_query="")

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])
    await message.answer(message_text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
