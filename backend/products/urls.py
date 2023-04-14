from django.urls import path

from products.views import (ProductView, add_to_cart, create_order,
                            import_groups, import_products)

urlpatterns = [
    path(
        'import', import_products,
        name='import_products'
    ),
    path(
        'groups/import', import_groups,
        name='import_groups'
    ),
    path(
        '', ProductView.as_view({'get': 'list'}),
        name='products'
    ),
    path(
        '<str:pk>', ProductView.as_view({'get': 'retrieve'}),
        name='product'
    ),
    path(
        '<str:pk>/cart/add', add_to_cart,
        name='add_to_cart'
    ),
    path(
        'cart/order', create_order,
        name='create_order'
    ),
]
