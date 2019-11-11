import aiohttp_jinja2
from aiohttp import web
import db


# Шаблон стратовой страницы
@aiohttp_jinja2.template('base.html')
async def base(request):
    return None


# Запуск процесса получения данных и дальнейшее их предстваление
# 1 Получение данных о всех пользователях
async def index(request):
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.user.select())
        records = await cursor.fetchall()
        users = [dict(q) for q in records]
        return web.Response(text=str(users))


# 1.1 Получение данных о конкретном пользователя по id
async def user_id_index(request):
    async with request.app['db'].acquire() as conn:
        u = request.match_info['UserId']
        try:
            query = await db.get_user(conn, uii=u)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return web.Response(text=str(query[0]))


# 1.2 Получение данных о конкретном пользователя по email
async def user_email_index(request):
    async with request.app['db'].acquire() as conn:
        e = request.match_info['Email']
        try:
            query = await db.get_user(conn, ei=e)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return web.Response(text=str(query[0]))


# 2.1 Просмотр истории заказов конкретного пользователя по id
async def orders_id_index(request):
    async with request.app['db'].acquire() as conn:
        pointer = request.match_info['UserId']
        try:
            query = await db.get_order_list(conn, id_pointer=pointer)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return web.Response(text=str(query))


# 2.2 Просмотр истории заказов конкретного пользователя по email
async def orders_email_index(request):
    async with request.app['db'].acquire() as conn:
        pointer = request.match_info['Email']
        try:
            query = await db.get_order_list(conn, email_pointer=pointer)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return web.Response(text=str(query))


# 3.1 Просмотр ассортимента определенного магазина по id
async def stock_id_index(request):
    async with request.app['db'].acquire() as conn:
        pointer = request.match_info['ShopId']
        try:
            query = await db.get_stock_list(conn, id_pointer=pointer)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return web.Response(text=str(query[0]) + '\n\n\n' + str(query[1]))


# 3.2 Просмотр ассортимента определенного магазина по name
async def stock_name_index(request):
    async with request.app['db'].acquire() as conn:
        pointer = request.match_info['ShopName']
        try:
            query = await db.get_stock_list(conn, name_pointer=pointer)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return web.Response(text=str(query[0]) + '\n\n\n' + str(query[1]))


# 4 Добавление нового заказа
async def add_order_index(request):
    async with request.app['db'].acquire() as conn:
        # получение и проверка данных введеных пользователем на стартовой стр.
        data = await request.post()
        try:
            user_pointer = int(data['user'])
            book__pointer = int(data['book'])
            book_number = int(data['number'])
            shop_pointer = int(data['shop'])
        except (KeyError, TypeError, ValueError) as e:
            raise web.HTTPBadRequest(
                text='You have not specified user-id, '
                     'book-id and book number') from e
        # Запуск процесса добавления нового заказа
        try:
            left_books = await db.add_order(conn, user_pointer, book__pointer,
                                            book_number, shop_pointer)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return web.Response(text='Order added successfully. \n' +
                            'Books left: ' + str(left_books))
