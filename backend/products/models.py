from django.db import models
from django.db.models import CASCADE, SET_NULL, QuerySet

from users.models import User


class Product(models.Model):
    article = models.CharField(
        max_length=150, unique=True,
        verbose_name='Артикул'
    )
    name = models.CharField(max_length=150, verbose_name='Название')
    amount = models.IntegerField(verbose_name='Кол-во')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Цена'
    )
    group = models.ForeignKey(
        'Group', related_name='products', on_delete=SET_NULL,
        null=True, verbose_name='Группа'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
    )

    class Meta:
        db_table = 'product'
        verbose_name = 'Товары'
        ordering = ['-id']

    def __str__(self):
        return (
            f'id {self.pk}'
            f' Товар {self.article},'
            f' Навзание товара {self.name},'
            f' Кол-во {self.amount},'
            f' Цена {self.price},'
            f' Группа {self.group}'
        )


class Group(models.Model):
    name = models.CharField(
        max_length=150, unique=True,
        verbose_name='Название'
    )
    description = models.CharField(
        max_length=200, null=True, verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
    )

    class Meta:
        db_table = 'group'
        verbose_name = 'Группы товаров'
        ordering = ['-id']

    def __str__(self):
        return (
            f'id {self.pk}'
            f' Название группы {self.name},'
            f' Описание {self.description}'
        )


class Cart(models.Model):
    product = models.ForeignKey(
        Product, related_name='cart', on_delete=SET_NULL, null=True,
        verbose_name='Товар'
    )
    user = models.ForeignKey(
        User, related_name='cart', on_delete=CASCADE,
        verbose_name='Пользователь'
    )
    amount = models.IntegerField(verbose_name='Кол-во')
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
    )

    def total_price(self):
        return self.product.price * self.amount

    class Meta:
        db_table = 'cart'
        verbose_name = 'Корзина'
        ordering = ['-id']

    def __str__(self):
        return (
            f'id {self.pk}'
            f' Название продукта {self.product.name},'
            f' Кол-во {self.amount},'
            f' Пользователь {self.user.email}'
        )


class Order(models.Model):
    products = models.ManyToManyField(
        Product, related_name='order', through='OrderProduct',
        verbose_name='Товары'
    )
    user = models.ForeignKey(
        User, related_name='order', on_delete=SET_NULL, null=True,
        verbose_name='Пользователь'
    )
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
    )

    @property
    def total_price(self):
        return sum(
            product.price * product.amount for product in self.products.all()
        )

    def add_products(self, cart: QuerySet[Cart]):
        bulk_create = []
        for el in cart:
            bulk_create.append(
                OrderProduct(order=self, product=el.product, amount=el.amount)
            )
        OrderProduct.objects.bulk_create(bulk_create)

    class Meta:
        db_table = 'order'
        verbose_name = 'Заказ'
        ordering = ['-id']

    def __str__(self):
        return f'id {self.pk}, пользователь {self.user.email}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order, on_delete=CASCADE, related_name='order_products',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product, related_name='order_products', on_delete=SET_NULL,
        null=True, verbose_name='Товар'
    )
    amount = models.IntegerField(verbose_name='Кол-во')
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
    )

    class Meta:
        db_table = 'order_product'
        verbose_name = 'Товары в заказе'
        ordering = ['-id']

    def __str__(self):
        return (
            f'id {self.pk},'
            f' id заказа {self.order.pk},'
            f' id продукта {self.product.pk}'
            f' Кол-во {self.amount}'
        )
