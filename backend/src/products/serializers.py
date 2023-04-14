from django.db import transaction
from rest_framework import serializers

from products.models import Cart, Group, Order, Product


class FileSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    @staticmethod
    def validate_file(value):
        if not value.content_type == 'text/csv':
            raise serializers.ValidationError('Ожидался тип контента text/csv')
        return value


class ProductSerializer(serializers.ModelSerializer):
    group_id = serializers.IntegerField()

    class Meta:
        model = Product
        exclude = ('group',)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

    @staticmethod
    def validate_amount(value: int):
        if value <= 0:
            raise serializers.ValidationError(
                'Кол-во товаров не может быть меньше 1'
            )
        return value

    @staticmethod
    def check_amount(amount: int):
        if amount <= 0:
            raise serializers.ValidationError(
                'Нельзя добавить товар не в наличии'
            )

    @transaction.atomic
    def create(self, validated_data):
        user = validated_data.get('user')
        product = validated_data.get('product')
        amount = validated_data.get('amount')
        cart = self.Meta.model.objects.select_for_update().filter(
            user=user, product=product
        )
        if cart.exists():
            cart = cart.first()
            diff_amount = amount - cart.amount
            cart.amount = amount
            product.amount -= diff_amount
            self.check_amount(product.amount)
            product.save()
            cart.save()
        else:
            product.amount -= amount
            self.check_amount(product.amount)
            product.save()
            return Cart.objects.create(
                user=user, amount=amount, product=product
            )
        return cart


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    @staticmethod
    def get_total_price(obj):
        return obj.total_price
