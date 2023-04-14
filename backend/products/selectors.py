from django.db.models import DateField, F, QuerySet, Sum
from django.db.models.functions import Cast

from products.models import Order


def orders_report(queryset: QuerySet[Order]) -> QuerySet[Order]:
    """
    Parameters
    ----------
    queryset :
        кверист заказов QuerySet[Order]

    Returns
    -------
    queryset :
        аннотированный кверист заказов QuerySet[Order]
    """
    return queryset.annotate(
        date=Cast('created_at', DateField())
    ).values('pk', 'date').annotate(
        total_sum=Sum(
            F('products__price') * F('products__amount'))
    )
