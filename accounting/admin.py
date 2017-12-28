# -*- coding: utf-8 -*-

from django.contrib import admin
from catalog.accounting.models import Type, Size, Exchange, Manufacturer, Catalog, Country, Dealer, Currency, Rent, Wheel_Size, Bicycle_Storage, Bicycle_Photo, GroupType, YouTube, PhoneStatus



class TypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name', 'description')
    ordering = ('-name',)
    search_fields = ('name', 'description')
  
admin.site.register(Type, TypeAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('-name',)
    search_fields = ('name',)

admin.site.register(Country, CountryAdmin)


class DealerAdmin(admin.ModelAdmin):
    list_display = ('name','country', 'city', 'street', 'www', 'description', 'director')
    ordering = ('-name',)
    search_fields = ('name',)

admin.site.register(Dealer, DealerAdmin)


class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'hight')
    list_filter = ('name', 'width', 'hight')
    ordering = ('-name',)
    search_fields = ('name',)

admin.site.register(Size, SizeAdmin)

class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('date', 'currency', 'value')
    list_filter = ('date', 'currency', 'value')
    ordering = ('-date',)
    search_fields = ('date',)

admin.site.register(Exchange, ExchangeAdmin)

	
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'www', 'country')
    ordering = ('name', 'description', 'www', 'country')
    search_fields = ('name',)

admin.site.register(Manufacturer, ManufacturerAdmin)


class CatalogAdmin(admin.ModelAdmin):
    list_display = ('ids', 'name', 'manufacturer', 'type', 'size', 'photo', 'weight', 'sale', 'country', 'description')
    ordering = ('-name',)
    search_fields = ('ids', 'name',)

admin.site.register(Catalog, CatalogAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('ids', 'ids_char', 'name', 'country')
    ordering = ('-ids',)
    search_fields = ('ids', 'name',)
    
admin.site.register(Currency, CurrencyAdmin)


class RentAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'client', 'date_start', 'date_end', 'count', 'deposit', 'status', 'description')
    ordering = ('client',)
    search_fields = ('catalog', 'status',)
    
admin.site.register(Rent, RentAdmin)


class Wheel_SizeAdmin(admin.ModelAdmin):
    pass 

admin.site.register(Wheel_Size, Wheel_SizeAdmin)


class Bicycle_StorageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Bicycle_Storage, Bicycle_StorageAdmin)


class Bicycle_PhotoAdmin(admin.ModelAdmin):
    pass

admin.site.register(Bicycle_Photo, Bicycle_PhotoAdmin)


class GroupTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(GroupType, GroupTypeAdmin)


class YouTubeAdmin(admin.ModelAdmin):
    pass

admin.site.register(YouTube, YouTubeAdmin)


class PhoneStatusAdmin(admin.ModelAdmin):
    pass 

admin.site.register(PhoneStatus, PhoneStatusAdmin)






