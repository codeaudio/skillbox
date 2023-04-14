from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers
from rest_framework.decorators import (api_view, parser_classes,
                                       permission_classes)
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from products.models import Cart, Order, Product
from products.permissions import ImportPermission, UserItemPermission
from products.serializers import (CartSerializer, FileSerializer,
                                  OrderSerializer, ProductSerializer)
from products.services import (cart_to_order, import_groups_csv,
                               import_products_csv)


class ProductView(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        group = self.request.query_params.get('group')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if group:
            queryset = queryset.filter(group_id=group)
        return queryset


class CartView(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (UserItemPermission,)
    lookup_field = 'pk'


class OrderView(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (UserItemPermission,)
    lookup_field = 'pk'


@extend_schema(
    request=inline_serializer(
        name='add_to_cart', fields={'amount': serializers.IntegerField()},
    ),
    responses={200: None}, methods=('POST',)
)
@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def add_to_cart(request, pk):
    data = {
        'user': request.user.pk,
        'product': pk,
        'amount': request.data.get('amount')
    }
    serializer = CartSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data=serializer.data, status=201)


@extend_schema(
    responses={200: None}, methods=('POST',)
)
@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def create_order(request):
    cart = request.user.cart.all()
    if not cart:
        raise NotFound('Не найдены товары в корзине')
    instance = cart_to_order(cart, request.user)
    data = OrderSerializer(instance).data
    return Response(data=data, status=201)


@extend_schema(
    request=FileSerializer, responses={201: None}, methods=('POST',)
)
@api_view(('POST',))
@permission_classes((ImportPermission,))
@parser_classes((FileUploadParser,))
def import_products(request):
    serializer = FileSerializer(data=request.FILES)
    serializer.is_valid(raise_exception=True)
    import_products_csv(serializer.validated_data.get('file'))
    return Response(status=201)


@extend_schema(
    request=FileSerializer, responses={201: None}, methods=('POST',)
)
@api_view(('POST',))
@permission_classes((ImportPermission,))
@parser_classes((FileUploadParser,))
def import_groups(request):
    serializer = FileSerializer(data=request.FILES)
    serializer.is_valid(raise_exception=True)
    import_groups_csv(serializer.validated_data.get('file'))
    return Response(status=201)
