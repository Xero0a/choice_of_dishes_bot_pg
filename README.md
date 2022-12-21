# Сhoice_of_dishes_bot_pg

Telegramm бот для создания, просмотра и изменения меню.

![.](https://github.com/Xero0a/Images/blob/main/333.gif)

Бот обладает функцией админ-панели, с помощью которой можно добавлять категории и блюда в меню.
Для доступа к ней, нужен chat_id администратора.

![.](https://github.com/Xero0a/Images/blob/main/222.gif)

Так же бот собирает статистику о выбранных блюдах, занося в отдельную таблицу информацию о имени пользователя, выбранном блюде и дате просмотра блюда.

## Запуск проекта
   * Версия python 3.10.7
   * Устанавливаем зависимости из requirements.txt: `pip install -r requirements.txt` Для Unix-систем вместо `pip` потребуется `pip3`.
   * Создаём пустого телеграмм бота и получаем его токен.
   * Создаём базу данных PostgreSql.
   * Создаём файл .env в папке проекта, в файле .env создаём переменные окружения:
     - `BOT_TOKEN` (токен вашего телеграмм бота)
     - `DB_NAME` (имя вашей базы данных)
     - `DB_USER` (имя вашего пользователя PostgreSQL)
     - `DB_PASSWORD (пароль вашего пользователя PostgreSQL)
     - `DB_HOST (хост вашей базы данных)
     - `ADMIN_CHAT_ID (chat_id администратора для доступа к админ-панели)
   * Создаём таблицы необходимые для работы бота, с помощью функций в файле db_services.py  
     
     