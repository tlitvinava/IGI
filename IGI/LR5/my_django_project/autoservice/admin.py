# autoservice/admin.py

from django.contrib import admin
from .models import (
    Service,
    Client,
    MasterSpecialization,
    Master,
    AutoType,
    SparePart,
    Order,
)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name', 'description')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone')
    search_fields = ('full_name', 'email')


@admin.register(MasterSpecialization)
class MasterSpecializationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone')
    filter_horizontal = ('specializations',)  # удобный выбор через горизонтальный фильтр
    search_fields = ('full_name', 'email')


@admin.register(AutoType)
class AutoTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'master', 'service', 'order_date', 'total_cost')
    date_hierarchy = 'order_date'
    search_fields = ('client__full_name', 'master__full_name')
    filter_horizontal = ('spare_parts',)  # для удобного выбора запчастей
