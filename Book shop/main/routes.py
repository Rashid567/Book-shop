from views import (
    base,
    index, user_id_index, user_email_index,
    orders_id_index, orders_email_index,
    stock_id_index, stock_name_index,
    add_order_index
)


# Создание маршрутов


def setup_routes(app):

    # Страртовая страница
    app.router.add_get('/', base)
    # Получение данных пользователя (имя, адрес эл. Почты и т.п.)
    app.router.add_get('/users-info', index)
    app.router.add_get('/users-info/id/{UserId}', user_id_index)
    app.router.add_get('/users-info/email/{Email}', user_email_index)

    # Просмотр истории заказов пользователя
    app.router.add_get('/orders/id/{UserId}', orders_id_index)
    app.router.add_get('/orders/email/{Email}', orders_email_index)

    # Просмотр ассортимента определенного магазина stock
    app.router.add_get('/shop-stock/id/{ShopId}', stock_id_index)
    app.router.add_get('/shop-stock/name/{ShopName}', stock_name_index)

    # Добавление нового заказа (N книг каждая из которых в M количестве)
    app.router.add_post('/new-order', add_order_index)
