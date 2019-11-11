import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, Numeric,
    select, and_
)
import datetime as date


meta = MetaData()

# Определение таблиц БД
user = Table(
    'user', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(20), nullable=False),
    Column('surname', String(20), nullable=False),
    Column('fathers_name', String(20), nullable=False),
    Column('email', String(30), nullable=False, unique=True)
)

book = Table(
    'book', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(60), nullable=False),
    Column('author', String(30), nullable=False),
    Column('isbn', String(20), nullable=False, unique=True),
    Column('price', Numeric, nullable=False)
)

shop = Table(
    'shop', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(20), nullable=False),
    Column('address', String(100), nullable=False),
    Column('post_code', Integer, nullable=False)
)

shop_inventory = Table(
    'shop_inventory', meta,

    Column('id', Integer, primary_key=True),
    Column('shop_id', Integer, ForeignKey('shop.id')),
    Column('book_id', Integer, ForeignKey('book.id')),
    Column('book_quantity', Integer, server_default='0', nullable=False)
)

order = Table(
    'order', meta,

    Column('id', Integer, primary_key=True),
    Column('reg_date', Date, nullable=False,
           server_default=date.datetime.today().strftime("%Y-%m-%d")),
    Column('user_id', Integer, ForeignKey('user.id'))
)

order_position = Table(
    'order_position', meta,

    Column('id', Integer, primary_key=True),
    Column('order_id', Integer, ForeignKey('order.id')),
    Column('book_id', Integer, ForeignKey('book.id')),
    Column('book_quantity', Integer, server_default='0', nullable=False),
    Column('shop_id', Integer, ForeignKey('shop.id'))
)


# Создание экзепляра 'двигателя (engine)' для возмжности отправки запросов в БД
async def init_pg(app):
    # Загрузка конфигурации БД
    conf = app['config']['postgres']
    # Создание экземпляра 'двигателя'
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    # Присвоение экзепляра двигателя нашему приложению
    app['db'] = engine


# Отключение экземпляра двигателя
async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


# Определения новго класса ошибок разного рода при выполнении запросов в БД:
class RecordNotFound(Exception):
    """Requested record in database was not found"""


# Функция отправки запроса для получения данных пользователя
async def get_user(conn, uii=None, ei=None):
    # Определение параметра с помощью которого будет выполнен запрос
    # Является ли это id пользователя или email
    temp = None
    if uii:
        temp = uii
        col = user.c.id
    elif ei:
        temp = ei
        col = user.c.email
    # Сам запрос
    query = await conn.execute(
        user.select()
        .where(col == temp))
    result = await query.fetchall()
    # Проверка наличия данных в ответе на запроса
    if not result:
        msg = "User with id/email: {} does not exists"
        raise RecordNotFound(msg.format(temp))
    record = [dict(q) for q in result]
    return record


# Функия получения истории запросов пользователя
async def get_order_list(conn, id_pointer=None, email_pointer=None):
    # Определение параметра (id/email) с помощью которого будет выполнен запрос
    temp = None
    if id_pointer:
        temp = id_pointer
        col = user.c.id
    elif email_pointer:
        temp = email_pointer
        col = user.c.email
    # Объединение таблиц
    j1 = user.join(order, user.c.id == order.c.user_id)
    j2 = j1.join(order_position, j1.c.order_id == order_position.c.order_id)
    j3 = j2.join(book, j2.c.order_position_book_id == book.c.id)
    # Выполнение запроса
    query = await conn.execute(select([user.c.id,
                                       user.c.name,
                                       order.c.reg_date,
                                       book.c.id,
                                       book.c.name,
                                       order_position.c.book_quantity,
                                       book.c.price
                                       ],
                                      use_labels=True
                                      )
                               .select_from(j3)
                               .where(col == temp))
    result = await query.fetchall()
    # Проверка наличия данных в ответе на запрос
    if not result:
        msg = "User with id/email: {} doesn't exists or doesn't have any order"
        raise RecordNotFound(msg.format(temp))
    record = [dict(q) for q in result]
    return record


# Функция для определения инвентаря магазина
async def get_stock_list(conn, id_pointer=None, name_pointer=None):
    # Определение параметра (id/name) с помощью которого будет выполнен запрос
    temp = None
    if id_pointer:
        temp = id_pointer
        col = shop.c.id
    elif name_pointer:
        temp = name_pointer
        col = shop.c.name
    # Объединение таблиц
    j1 = shop_inventory.join(book, shop_inventory.c.book_id == book.c.id)
    j2 = j1.join(shop, j1.c.shop_inventory_shop_id == shop.c.id)
    # Выполнение запроса о состоянии инвентаря в БД
    query = await conn.execute(select([shop_inventory.c.book_id,
                                       book.c.name,
                                       shop_inventory.c.book_quantity
                                       ]
                                      )
                               .select_from(j2)
                               .where(col == temp)
                               )

    # Чтобы скрыть отсутствующие книги:
    # .where(and_(col == temp,shop_inventory.c.book_quantity != 0))

    result = await query.fetchall()

    # Проверка наличия данных в ответе на запрос
    if not result:
        msg = "Shop with id/name: {} does not exists"
        raise RecordNotFound(msg.format(temp))

    record = [dict(q) for q in result]

    # Запрос в БД для получения информации о магазине (id, name, address)
    query2 = await conn.execute(shop.select().where(col == temp))
    result2 = await query2.fetchall()
    record2 = [dict(q) for q in result2]
    return record2, record


# Функция добавления нового заказа в БД
async def add_order(
    conn, user_pointer, book_pointer,
    book_number, shop_pointer
):
    # Проверка наличия user-id в БД
    check_user = await conn.execute(user.select()
                                    .where(user.c.id == user_pointer))
    check_user_res = await check_user.fetchall()
    if not check_user_res:
        msg = '''User with id:{} doesn't exists.
                 To add an order, first create a user.'''
        raise RecordNotFound(msg.format(user_pointer))

    # Проверка наличия book-id в БД
    check_book = await conn.execute(book.select()
                                    .where(book.c.id == book_pointer))
    check_book_res = await check_book.fetchall()
    if not check_book_res:
        msg = '''Book with id: {} does not exists.
                 To add an order, first create a book.'''
        raise RecordNotFound(msg.format(book_pointer))

    # Проверка наличия shop-id в БД
    check_shop = await conn.execute(shop.select()
                                    .where(shop.c.id == shop_pointer))
    check_shop_res = await check_shop.fetchall()
    if not check_shop_res:
        msg = '''Shop with id: {} does not exists.
                 To add an order, first create a shop.'''
        raise RecordNotFound(msg.format(shop_pointer))

    # Определение количества книги в наличии
    shop_inventory
    query_book_have = await conn.execute(
        select([shop_inventory.c.book_quantity])
        .select_from(shop_inventory)
        .where(and_(shop_inventory.c.shop_id == shop_pointer,
                    shop_inventory.c.book_id == book_pointer))
    )
    book_have = await query_book_have.fetchone()

    # Сравнение требуемого количества книг с наличием
    if book_number > book_have[0]:
        msg = '''The store (id: {}) does not have the required number of the book.
        Number of the book available: {}'''
        raise RecordNotFound(msg.format(shop_pointer, book_have[0]))

    # Добавление новой записи в таблицу Order
    await conn.execute(order.insert()
                            .values(user_id=user_pointer))

    # Получение id из таб. Order, для последующей вставки в таб. Order_position
    query_order_id = await conn.execute(select([order.c.id])
                                        .order_by(order.c.id.desc()))
    record_order_id = await query_order_id.fetchone()

    # Добавление новой записи в таблицу Order_position
    await conn.execute(order_position.insert()
                                     .values(order_id=record_order_id[0],
                                             book_id=book_pointer,
                                             book_quantity=book_number,
                                             shop_id=shop_pointer))

    # Обновление количества книг в наличии в таблице shop_inventory
    books_left = book_have[0] - book_number
    await conn.execute(
        shop_inventory.update()
        .where(and_(shop_inventory.c.shop_id == shop_pointer,
                    shop_inventory.c.book_id == book_pointer))
        .values(book_quantity=books_left)
    )
    return books_left
