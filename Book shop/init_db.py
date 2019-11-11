from sqlalchemy import create_engine, MetaData
from main.settings import config
from main.db import user, book, shop, shop_inventory, order, order_position
import csv
import random

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


# Функция создания таблиц в БД
def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[user, book, shop, shop_inventory,
                                         order, order_position])


# Функция создания данных для таблиц, но не их загрузка в БД
def create_data():
    user_data, book_data, shop_data, shop_inven_data, order_data, order_pos_data = [[] for i in range(6)]

    with open(
        '.\\data_for_db_fill\\data_for_User_table.csv',
        newline='',
        encoding='utf-8'
    ) as user_csv:
        user_reader = csv.DictReader(user_csv)
        for user in user_reader:
            user_data.append({
                'name': user['first_name'],
                'surname': user['last_name'],
                'fathers_name': user['father_name'],
                'email': user['email']})


    with open(
        '.\\data_for_db_fill\\Data_for_Book_table.csv',
        newline='',
        encoding='utf-8'
    ) as book_csv:

        book_reader = csv.DictReader(book_csv)
        for book in book_reader:
            book_data.append({
                'name': book['Book_name'],
                'author': book['Author'],
                'isbn': book['isbn'],
                'price': round(random.uniform(300, 700), 2)})

    with open(
        '.\\data_for_db_fill\\Data_for_Shop_table.csv',
        newline='',
        encoding='utf-8'
    ) as shop_csv:
        shop_reader = csv.DictReader(shop_csv, delimiter=';')
        for shop in shop_reader:
            shop_data.append({
                'name': shop['name'],
                'address': shop['adsress'],
                'post_code': shop['post_code']})

    for i in range(1, 11):
        for j in range(1, 100):
            shop_inven_data.append({
                'shop_id': i,
                'book_id': j,
                'book_quantity': random.randint(0, 10)})

    with open(
        '.\\data_for_db_fill\\Data_for_Order_table.csv',
        newline='',
        encoding="utf-8"
    ) as order_csv:
        order_reader = csv.DictReader(order_csv)
        for data in order_reader:
            order_data.append({
                'reg_date': data['day'],
                'user_id': random.randint(1, 40)})

    for i in range(1, 19):
        order_pos_data.append({
            'order_id': i,
            'book_id': random.randint(1, 99),
            'book_quantity': random.randint(1, 3),
            'shop_id': random.randint(1, 10)})


    return user_data, book_data, shop_data, shop_inven_data, order_data, order_pos_data


# Функция для вставки созданных данных в таблицы БД
def sample_data(engine):
    conn = engine.connect()
    tabs = [user, book, shop, shop_inventory, order, order_position]
    data = create_data()  # [user, book, shop, shop_inven, order, order_pos]
    for i in range(6):
        conn.execute(tabs[i].insert(), data[i])
    conn.close()


# Запуск процессов: создания таблиц и данных, и вставки созданных данных в БД
if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    sample_data(engine)
