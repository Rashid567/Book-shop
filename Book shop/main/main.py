from aiohttp import web
import aiohttp_jinja2
import jinja2

from settings import config, BASE_DIR
from routes import setup_routes
from db import close_pg, init_pg

# Создание экземпляра приложения (веб сервера)
app = web.Application()
# Загрузка конфига в приложние
app['config'] = config
# Установка шаблонного движка
aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader(str(BASE_DIR / 'main' / 'templates')))
# Добавление задачи (инициализация БД) при запуске приложения (веб сервера)
app.on_startup.append(init_pg)
# Установка маршрутов
setup_routes(app)
# Добавление задачи (закрытие БД) при запуске приложения (веб сервера)
app.on_cleanup.append(close_pg)
# Запуск приложения (веб сервера)
web.run_app(app, host=config['host'])
