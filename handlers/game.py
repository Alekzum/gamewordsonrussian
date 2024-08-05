from aiogram import Bot
from aiogram.filters import Command
from utils.my_filters import InlineLen, CallbackLen
from aiogram.types import Message, InlineQuery, CallbackQuery, ChosenInlineResult
from importlib import reload
import aiogram


router = aiogram.Router()


@router.message(Command("start"))
async def _cmd_start(message: Message):
    import scripts.cmd_start as cmd_start
    cmd_start = reload(cmd_start)
    await cmd_start.main(message)


@router.chosen_inline_result()
async def _chosen_inline_result(cir: ChosenInlineResult):
    import scripts.chosen_inline_result as chosen_inline_result
    chosen_inline_result = reload(chosen_inline_result)
    await chosen_inline_result.main(cir)
    # print(cir, cir.__dict__)


@router.callback_query(CallbackLen(2))
async def _callback_continue(callback_query: CallbackQuery):
    import scripts.callback_continue as callback_continue
    callback_continue = reload(callback_continue)
    await callback_continue.main(callback_query)


@router.inline_query(InlineLen(2))
async def _inline_delete_game(inline_query: InlineQuery):
    import scripts.inline_game as inline_game
    inline_game = reload(inline_game)
    await inline_game.main(inline_query)


# @router.callback_query(F.len(F.query.split() or []) == 1)
@router.inline_query(InlineLen(1))
async def _inline_start(inline_query: InlineQuery):
    import scripts.inline_start as inline_start
    inline_start = reload(inline_start)
    await inline_start.main(inline_query)