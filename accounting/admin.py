# -*- coding: utf-8 -*-

from django.contrib import admin
from catalog.accounting.models import Type, Size, Exchange, Manufacturer, Catalog, Country, Dealer, DealerManager, Currency, Rent, Wheel_Size, Bicycle_Storage, Bicycle_Photo, YouTube, PhoneStatus, Bicycle_Parts
from catalog.accounting.models import CheckPay, Check, Schedules, Shop, CashType, Bank, Discount, FrameSize, ShopDailySales, ClientInvoice, DealerInvoice, Client, WorkTicket, CostType, Costs, ClientMessage, Bicycle_Store
from catalog.accounting.models import GroupType, WorkStatus, WorkShop, ClientReturn, Bicycle_Sale, Bicycle_Type, WorkGroup, CatalogAttributeValue, CatalogAttribute, Season, StorageBox, BoxName, InventoryList, ClientInvoiceStorageBox

from django.contrib.admin.options import ModelAdmin

import datetime


def mark_shop_K(ModelAdmin, request, queryset):
    queryset.update(shop=Shop.objects.get(name = 'Кавказька'))
    #queryset.update(description = 'test mark K')
mark_shop_K.short_description = "Mark selected. Shop = Кавказька"

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
    autocomplete_fields = ('type', 'manufacturer')
    list_display = ('ids', 'name', 'type', 'size', 'photo', 'weight', 'sale', 'country', 'created_date', 'description') #'manufacturer',
    ordering = ('-name',)
    search_fields = ('ids', 'name', 'type__name', 'manufacturer__name')

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


class ShopAdmin(admin.ModelAdmin):
    pass
admin.site.register(Shop, ShopAdmin)


class SchedulesAdmin(admin.ModelAdmin):
    pass

admin.site.register(Schedules, SchedulesAdmin)


def an_action(modeladmin, request, queryset):
    for obj in queryset:
        obj.description = obj.description.upper()
        obj.save()
   #pass
an_action.short_description = 'my label'

#@admin.register(Wheel_Size)
class Wheel_SizeAdmin(admin.ModelAdmin):
#    actions = ["uppercase", "lowercase"] # Necessary 
    actions = [an_action]
#    @admin.action(description='Make selected persons uppercase')
    def uppercase(modeladmin, request, queryset):
        for obj in queryset:
            obj.description = obj.description.upper()
            obj.save()
            messages.success(request, "Successfully made uppercase!")

#    @admin.action(description='Make selected persons lowercase')
    def lowercase(modeladmin, request, queryset):
        for obj in queryset:
            obj.description = obj.description.lower()
            obj.save()
            messages.success(request, "Successfully made lowercase!")
  

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
    list_display = ("url", "date", "user", "description",)

admin.site.register(YouTube, YouTubeAdmin)


class PhoneStatusAdmin(admin.ModelAdmin):
    pass 

admin.site.register(PhoneStatus, PhoneStatusAdmin)


class Bicycle_PartsAdmin(admin.ModelAdmin):
    pass
admin.site.register(Bicycle_Parts, Bicycle_PartsAdmin)


class CheckAdmin(admin.ModelAdmin):
    pass
admin.site.register(Check, CheckAdmin)


class CheckPayAdmin(admin.ModelAdmin):
    pass
admin.site.register(CheckPay, CheckPayAdmin)


class CashTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'shop', 'pay_status', 'cash', 'term']
    actions = [mark_shop_K]
    pass
admin.site.register(CashType, CashTypeAdmin)


class BankAdmin(admin.ModelAdmin):
    pass
admin.site.register(Bank, BankAdmin)


class DiscountAdmin(admin.ModelAdmin):
    pass
admin.site.register(Discount, DiscountAdmin)


class FrameSizeAdmin(admin.ModelAdmin):
    pass
admin.site.register(FrameSize, FrameSizeAdmin)

admin.site.register(Client)
admin.site.register(WorkTicket)
admin.site.register(Costs)
admin.site.register(CostType)
admin.site.register(ClientMessage)
admin.site.register(WorkStatus)
admin.site.register(WorkShop)
admin.site.register(ClientReturn)
admin.site.register(Bicycle_Sale)
admin.site.register(DealerManager)
admin.site.register(Bicycle_Type)
admin.site.register(WorkGroup)
admin.site.register(ShopDailySales)
admin.site.register(Season)
admin.site.register(CatalogAttribute)
admin.site.register(BoxName)
admin.site.register(InventoryList)
admin.site.register(DealerInvoice)



class StorageBoxAdmin(admin.ModelAdmin):
    list_display = ("box_name", "catalog", "count", "count_real", "count_last", "user", "shop",)
    readonly_fields = ("catalog", )
    ordering = ['-date_create',]

admin.site.register(StorageBox, StorageBoxAdmin)


class ClientInvoiceStorageBoxAdmin(admin.ModelAdmin):
    list_display = ("sbox", "cinvoice", "count", "date_create", "user_create", "user_accept", "date_accept",)
    readonly_fields = ("cinvoice", "sbox")
    ordering = ['-date_create',]
    
admin.site.register(ClientInvoiceStorageBox, ClientInvoiceStorageBoxAdmin)

#admin.site.register()

def mark_K(modeladmin, request, queryset):
    queryset.update(shop=Shop.objects.get(name = 'Кавказька'))
    queryset.update(description = 'test mark K')
mark_K.short_description = "Mark selected client invoice to shop = Кавказька"

def mark_M(modeladmin, request, queryset):
    queryset.update(shop=Shop.objects.get(name = 'Міцкевича'))
    queryset.update(description = 'test mark K')
mark_M.short_description = "Mark selected client invoice to shop = Міцкевича"

class ClientInvoiceAdmin(admin.ModelAdmin):
    list_display = ['catalog', 'client', 'shop']
    ordering = ['-date',]
    search_fields = ['catalog__ids', 'client__name',]
    actions = [mark_K, mark_M]
    
admin.site.register(ClientInvoice, ClientInvoiceAdmin)

class BicycleStoreAdmin(admin.ModelAdmin):
    list_display = ['model', 'count', 'shop']
    search_fields = ['model__model', 'model__brand__name',]
    ordering = ['-count', ]
    actions = [mark_K, mark_M]
    
admin.site.register(Bicycle_Store, BicycleStoreAdmin)


from django.utils import timezone
from django.utils.timezone import activate

class CatalogAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attr_id", "value", "value_float", "icon", "description", "created_date", "updated_user", "updated_date",)
    readonly_fields = ("updated_date",)
    
    def save_model(self, request, obj, form, change):
        obj.updated_user = request.user
#        tz = timezone.now()
        tz = datetime.datetime.now()
 #       print "\nTIME Zone = " + str(tz)
 #       print "TIME Now = " + str(datetime.datetime.now()) + "\n"
#        print "ZONE - " + str(activate('Europe/Kyiv')) # settings.TIME_ZONE))
        obj.updated_date = tz #datetime.datetime.now() #today()
#        obj.created_date = datetime.datetime.now()
        super(CatalogAttributeValueAdmin, self).save_model(request, obj, form, change)
    
admin.site.register(CatalogAttributeValue, CatalogAttributeValueAdmin)
