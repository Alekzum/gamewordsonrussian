from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, InlineQuery


__all__ = ["InlineLen", "InlineIndex", "CallbackLen", "CallbackIndex"]


# For inline
class InlineLen(BaseFilter):
    """Return len(inline's query) == index"""
    def __init__(self, index: int):
        self.index = index

    async def __call__(self, inline: InlineQuery):
        if inline.query == "":
            index = 0
        else:
            args = inline.query.split(" ")
            index = len(args)

        return self.index == index


class InlineIndex(BaseFilter):
    """Return (inline's query).index(what) == index"""
    def __init__(self, index: int, what: str):
        self.index = index
        self.what = what

    async def __call__(self, inline: InlineQuery):
        if inline.query == "":
            query_list = []
        else:
            query_list = inline.query.split(" ")

        return self.what in query_list and query_list.index(self.what) == self.index


# For callback_query
class CallbackLen(BaseFilter):
    """Return len(callback_query's query) == index"""
    def __init__(self, index: int):
        self.index = index

    async def __call__(self, callback_query: InlineQuery):
        if callback_query.query == "":
            index = 0
        else:
            args = callback_query.query.split(" ")
            index = len(args)

        return self.index == index


class CallbackIndex(BaseFilter):
    """Return (callback_query's query).index(what) == index"""
    def __init__(self, index: int, what: str):
        self.index = index
        self.what = what

    async def __call__(self, callback_query: InlineQuery):
        if callback_query.query == "":
            query_list = []
        else:
            query_list = callback_query.query.split(" ")

        return self.what in query_list and query_list.index(self.what) == self.index
