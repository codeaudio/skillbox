from django.contrib import admin

from users.models import User


@admin.register(User)
class CartAdmin(admin.ModelAdmin):
    search_fields = ['email', 'username', '=id']
    list_filter = ('date_joined',)
