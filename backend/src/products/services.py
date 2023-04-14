import codecs
import csv

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import APIException, ParseError

from products.models import Cart, Group, Order, Product
from products.serializers import GroupSerializer, ProductSerializer


def import_products_csv(file: InMemoryUploadedFile) -> None:
    """
    Parameters
    ----------
    file :
        файл InMemoryUploadedFile
    Raises
    -------
    ParseError
    """
    csvfile = csv.DictReader(codecs.iterdecode(file, 'cp1251'))
    bulk_create = []
    groups_pk = set(Group.objects.values_list('pk', flat=True))

    for el in csvfile:

        serializer = ProductSerializer(data=el)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        group_id = data.get('group_id')
        if group_id not in groups_pk:
            name = data.get('name')
            raise APIException(
                f'группа {group_id} отутсвует в продукте {name}'
            )
        bulk_create.append(Product(**data))
    if not bulk_create:
        raise ParseError('Не найдены данные для импорта')
    Product.objects.bulk_create(bulk_create)


def import_groups_csv(file: InMemoryUploadedFile) -> None:
    """
    Parameters
    ----------
    file :
        файл InMemoryUploadedFile
    Raises
    -------
    ParseError
    """
    csvfile = csv.DictReader(codecs.iterdecode(file, 'cp1251'))
    bulk_create = []
    groups_name = set(Group.objects.values_list('name', flat=True))

    for el in csvfile:
        serializer = GroupSerializer(data=el)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data.get('name') in groups_name:
            data.pop('name')
        bulk_create.append(Group(**data))
    if not bulk_create:
        raise ParseError('Не найдены данные для импорта')
    Group.objects.bulk_create(bulk_create)


@transaction.atomic
def cart_to_order(cart: QuerySet[Cart], user) -> Order:
    order = Order.objects.create(user=user)
    order.add_products(cart)
    order.save()
    cart.delete()
    return order
