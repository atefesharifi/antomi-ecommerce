from django.contrib import admin
from .models import Cart

class CartAdmin(admin.ModelAdmin):
    list_display = ['user','product','variant','quantity','id']

admin.site.register(Cart,CartAdmin)
