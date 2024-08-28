NAME = 'bot_keyboard'
from aiogram import Bot, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

start = types.ReplyKeyboardMarkup(resize_keyboard=True)
 
stats = types.KeyboardButton("Собрать статистику")
summary = types.KeyboardButton("Суммаризация статьи")
archive = types.KeyboardButton("Собрать архив постов")
vision_board = types.KeyboardButton("Составить вижнборд")

start.add(stats, summary, archive, vision_board)
stats = InlineKeyboardMarkup()
summary = InlineKeyboardMarkup()
archive = InlineKeyboardMarkup()
vision_board = InlineKeyboardMarkup()