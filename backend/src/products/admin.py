import csv

from django.contrib import admin
from django.http import HttpResponse

from products.models import Cart, Group, Order, OrderProduct, Product
from products.selectors import orders_report


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['=id', 'article', 'name', '=amount', '=price']
    list_filter = ('group', 'created_at', 'amount')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ['=id', 'name', 'description']
    list_filter = ('created_at',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    search_fields = ['name', '=id', 'description', 'amount']
    list_filter = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ['=id']
    list_filter = ('is_paid', 'products', 'user')
    actions = ('export_as_csv',)

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv', charset='cp1251')
        filename = 'orders_report'
        response[
            'Content-Disposition'
        ] = f'attachment; filename={filename}.csv'
        writer = csv.writer(response, delimiter=';')
        writer.writerow(('ID заказа', 'Дата', 'Сумма'))
        for obj in orders_report(queryset):
            writer.writerow(
                [obj.get('pk'), obj.get('date'), obj.get('total_sum')]
            )
        return response

    export_as_csv.short_description = "Отчет по заказам"


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    search_fields = ['=id', 'order', 'product', 'amount']
    list_filter = ('created_at',)
