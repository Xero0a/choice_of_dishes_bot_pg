import os
from typing import Tuple

from dotenv import load_dotenv
from telebot import TeleBot

from bot_answers import (
    cb_admin_answer, cb_create_menu_answer, cb_add_category_answer, cb_add_dish_answer, cb_back_to_start_answer,
    cb_menu_answer,
)
from db_services import (
    create_table_menu_categories,
    create_table_dishes,
    get_all_categories_data,
)
from services import (
    get_start_keyboard,
    get_menu_keyboard,
    get_admin_keyboard,
    add_category_in_menu,
    add_dish_in_category, get_nice_categories_format,
)
from validators import (
    admin_chat_id_validator, get_menu_validator, allowable_lenght_validator, )

load_dotenv()
bot = TeleBot(os.getenv("BOT_TOKEN"))
last_message_data = []


def rewrite_last_message(func):
    """Декоратор, созданный для перезаписи последнего сообщения."""

    def wrapper(*args, **kwargs):
        global last_message_data

        if last_message_data:
            bot.delete_message(*last_message_data)

        last_message_data = func(*args, **kwargs)

    return wrapper


@bot.message_handler(commands=["start"])
@rewrite_last_message
def start(message) -> Tuple[int, int]:
    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=f"Здравствуйте, {message.from_user.full_name}, выберите действие:",
        reply_markup=get_start_keyboard(),
    )
    return message.chat.id, last_message.id


@bot.message_handler(commands=["add_category"])
@rewrite_last_message
def add_category(message) -> Tuple[int, int]:
    """Добавляет полученное по шаблону название категории в меню."""

    validation_result = allowable_lenght_validator(message.text, 60)
    result = add_category_in_menu(message) if validation_result else cb_add_category_answer.false_answer
    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=result,
        reply_markup=get_admin_keyboard() if validation_result else None,
    )
    return message.chat.id, last_message.id


@bot.message_handler(commands=["add_dish"])
@rewrite_last_message
def add_dish(message) -> Tuple[int, int]:
    """Добавляет полученное по шаблону блюдо в соответствующую категорию меню."""

    result = add_dish_in_category(message=message)
    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=result,
        reply_markup=get_admin_keyboard(),
    )
    return message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "menu")
@rewrite_last_message
def callback_menu(callback) -> Tuple[int, int]:
    """Выводит категории меню или сообщение об его отсутствии."""

    validation_result = get_menu_validator()
    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_menu_answer.answer if validation_result else cb_menu_answer.false_answer,
        reply_markup=get_menu_keyboard() if validation_result else None,
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "admin")
@rewrite_last_message
def callback_admin(callback) -> Tuple[int, int]:
    """Выводит функционал администратора если id чата соответствует зарегистрированному админскому id."""

    validation_result = admin_chat_id_validator(callback.message.chat.id)

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_admin_answer.answer if validation_result else cb_admin_answer.false_answer,
        reply_markup=get_admin_keyboard() if validation_result else None,
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "create_menu")
@rewrite_last_message
def callback_create_menu(callback) -> Tuple[int, int]:
    """При нажатии кнопки 'Создать меню' создает пустые таблицы для меню в бд и уведомит об этом пользователя."""

    create_table_menu_categories()
    create_table_dishes()
    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_create_menu_answer.answer,
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "add_category")
@rewrite_last_message
def callback_add_category(callback) -> Tuple[int, int]:
    """Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новую категорию."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_add_category_answer.answer,
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "add_dish")
@rewrite_last_message
def callback_add_dish(callback) -> Tuple[int, int]:
    """
    Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новое блюдо.

    В ответном сообщении присутствуют текущие доступные категории из меню, чтобы пользователь понимал с чем работать.
    """

    categories_data = get_all_categories_data()
    categories_text = get_nice_categories_format(categories_data) if categories_data else 'Доступных категорий нет'

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_add_dish_answer.answer + f"<i>{categories_text}</i>",
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "back_to_start")
@rewrite_last_message
def callback_back_to_start(callback) -> Tuple[int, int]:
    """Отправляет пользователю кнопки стартового меню."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_back_to_start_answer.answer,
        reply_markup=get_start_keyboard(),
    )
    return callback.message.chat.id, last_message.id


if __name__ == "__main__":
    bot.polling(non_stop=True, interval=0)
