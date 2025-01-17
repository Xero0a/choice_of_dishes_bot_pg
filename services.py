from typing import Tuple, List, Optional, Dict

from telebot import types

from db_services import (
    get_all_categories_data,
    get_all_tables_name_from_db,
    insert_category_in_table_menu_categories,
    get_category_id_where_category_name,
    insert_dish_in_dishes_table,
    get_dishes_from_category_where,
    get_top_dishes_from_selection_dishes_table,
    get_top_users_from_selection_dishes_table,
    get_last_messages,
)


def get_start_keyboard():
    """Возвращает кнопки выпадающие при старте бота."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Меню", callback_data="menu"))
    keyboard.add(
        types.InlineKeyboardButton(text="Панель администратора", callback_data="admin")
    )
    return keyboard


def get_menu_keyboard():
    """Возвращает кнопки с названиями категорий, если таковые имеются."""

    categories_data = get_all_categories_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="Назад", callback_data="back_to_start")
    )
    if categories_data:
        for category_id, category_name in categories_data:
            keyboard.add(
                types.InlineKeyboardButton(
                    text=category_name, callback_data="category_" + str(category_id)
                )
            )
    return keyboard


def get_admin_keyboard():
    """Возвращает кнопки с функциями администратора."""

    keyboard = types.InlineKeyboardMarkup()
    all_tables_in_db = get_all_tables_name_from_db()

    keyboard.add(
        types.InlineKeyboardButton(text="Назад", callback_data="back_to_start")
    )
    if ("menu_categories",) not in all_tables_in_db:
        keyboard.add(
            types.InlineKeyboardButton(text="Создать меню", callback_data="create_menu")
        )
    else:
        keyboard.add(
            types.InlineKeyboardButton(
                text="Добавить категорию", callback_data="add_category"
            )
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text="Добавить блюдо в категорию", callback_data="add_dish"
            )
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text="Топ 3 самых популярных блюда", callback_data="top_dishes_report"
            )
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text="Топ 3 самых активных пользователя",
                callback_data="top_users_report",
            )
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text="Последние полученные сообщения",
                callback_data="last_messages_report",
            )
        )

    return keyboard


def get_dishes_keyboard(category_id):
    """Возвращает кнопки соответствующие позициям из конкретной категории меню."""

    keyboard = types.InlineKeyboardMarkup()
    all_dishes_from_category = get_dishes_from_category_where(category_id)

    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_to_menu"))

    if all_dishes_from_category:
        for dish_id, dish_name in all_dishes_from_category:
            keyboard.add(
                types.InlineKeyboardButton(
                    text=dish_name, callback_data="dish_" + str(dish_id)
                )
            )
    return keyboard


def add_category_in_menu(message) -> str:
    """
    Достает из полученного сообщения название категории и добавляет его в таблицу с категориями меню.

    Если сообщение не имеет данных о категории, возвращает текстовую ошибку.
    """

    list_message_words = message.text.split()
    if len(list_message_words) != 1:
        category_name = " ".join(list_message_words[1:])
        insert_category_in_table_menu_categories(category_name)
        return "Категория успешно создана!"
    return "Вы не передали название категории."


def back_to_dishes_button(category_id: int):
    """Возвращает кнопку для перехода блюдам соответствующей категории меню."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="Назад", callback_data=f"category_{category_id}"
        )
    )
    return keyboard


def add_dish_in_category(message) -> Optional[bool]:
    """Добавляет блюдо переданное в сообщении message в соответсвующую категорию меню."""

    parameters = _dish_in_category_message_converter(message)

    if parameters:
        insert_dish_in_dishes_table(
            dish_name=parameters["dish"],
            category_id=parameters["category"],
            price=parameters["price"],
            description=parameters["description"],
        )
        return True


def get_nice_categories_format(categories_data: List[Tuple[str, ...]]) -> str:
    """Преобразует список с данными категорий меню в удобочитаемый строчный формат."""

    return "\n".join(map(lambda category_data: category_data[1], categories_data))


def _dish_in_category_message_converter(message) -> Optional[Dict[str, str]]:
    """
    Обрабатывает полученное сообщение с данными о блюде, которое нужно добавить в меню.

    В случае, если блюдо соответствует шаблону корректного ввода, возвращает словарь с данными, подготовленными для
    добавления в таблицу dish базы данных. В остальных случаях вернет None.
    """

    list_message_words = message.text.split()[1:]
    inner_parameters = {"category": "", "dish": "", "price": "", "description": ""}
    list_parameters_keys = list(inner_parameters.keys())

    if 5 > len(list_message_words) >= 3:

        for index, word in enumerate(list_message_words):
            inner_parameters[list_parameters_keys[index]] = " ".join(word.split("_"))

        category_id = get_category_id_where_category_name(
            category_name=inner_parameters["category"]
        )

        if _price_validator(inner_parameters["price"]) and category_id:
            inner_parameters["category"] = str(category_id)
            return inner_parameters


def get_most_popular_dishes_report(count: int) -> str:
    """Возвращает пользователю текстовый отчет с информацией о самых популярных позициях в меню."""

    list_top_dishes_data = get_top_dishes_from_selection_dishes_table(limit=count)
    text_report = f"<b>Топ {count} самых популярных блюд меню:</b>\n\n"
    place = 1

    for dish, count in list_top_dishes_data:
        text_report += f"<i>{place}. {dish} - выбрано {count} раз</i>\n"
        place += 1

    return text_report


def get_most_popular_users_report(count: int) -> str:
    """Возвращает пользователю текстовый отчет с информацией о самых активных пользователях."""

    list_top_users_data = get_top_users_from_selection_dishes_table(limit=count)
    text_report = f"<b>Топ {count} самых активных пользователей:</b>\n\n"
    place = 1

    for username, count in list_top_users_data:
        text_report += f"<i>{place}. {username} - выбрал блюдо {count} раз</i>\n"
        place += 1

    return text_report


def get_last_messages_report(count: int) -> str:
    """Возвращает пользователю текстовый отчет с информацией о последних сообщениях от пользователя."""

    list_last_messages = get_last_messages(limit=count)
    text_report = f"<b> Последние {count} сообщений от пользователей:</b>\n\n"

    for place, message in enumerate(list_last_messages, 1):
        text_report += f"<i>{place}. {message[0]}</i>\n"

    return text_report


def _price_validator(price: str) -> bool:
    """Проверяет, является ли строка с информацией о цене товара числом и больше 0."""

    price.replace(",", ".")
    try:
        float(price)
        return True
    except ValueError:
        return False
