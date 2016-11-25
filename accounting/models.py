# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ModelForm
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Type = Component category 
class Type(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    name_ukr = models.CharField(max_length=100, blank=True, null=True)
    description_ukr = models.CharField(max_length=255, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s / %s' % (self.name, self.name_ukr)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["name"]    


# Size catalog
class Size(models.Model):
    name = models.CharField(max_length=100)
    width = models.IntegerField() 
    hight = models.IntegerField()
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]    


# Country table (Country)
class Country(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]    


class Bank(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]    


# list of currency
class Currency(models.Model):
    ids = models.CharField("code", max_length=50)
    ids_char = models.CharField("code", unique=True, max_length=5) #поле скорочена назва валюти
    name = models.CharField("currency name", max_length=50)
    country = models.ForeignKey(Country)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.ids_char)

    class Meta:
        ordering = ["ids"]    


# exchange rate
class Exchange(models.Model):
    date = models.DateTimeField()
    currency = models.ForeignKey(Currency)    
    value = models.DecimalField("money", max_digits=5, decimal_places=2)
    
    def __unicode__(self):
        return self.currency

    class Meta:
        ordering = ["date"]    


# list of manufectures 
class Manufacturer(models.Model):
    name = models.CharField(max_length=100)
    www = models.URLField(verify_exists=False, blank=True, null=True)
    logo = models.ImageField(upload_to = 'media/upload/', blank=True, null=True)
    country = models.ForeignKey(Country, null=True)
    description = models.TextField(blank=True, null=True)    
    
    def natural_key(self):
        return (self.id, self.name)
        
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ["name"]    


class Photo(models.Model):
    url = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)
    #goo_url = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'%s' % self.url

    class Meta:
        ordering = ["date", "description"]    


# Main table 
class Catalog(models.Model):
    ids = models.CharField("code", unique=True, max_length=50)
    dealer_code = models.CharField("dealer code", max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255)
    manufacturer = models.ForeignKey(Manufacturer)
    type = models.ForeignKey(Type, related_name='type')
    size = models.ForeignKey(Size, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)    
    photo = models.FileField(upload_to = 'media/upload/catalog/%Y/%m/%d', blank=True, null=True)
    photo_url = models.ManyToManyField(Photo, blank=True)
    year = models.IntegerField(blank=True, null=True)
    sale_to = models.DateField(auto_now_add=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField()
    last_price = models.FloatField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    currency = models.ForeignKey(Currency)
    sale = models.FloatField()
    country = models.ForeignKey(Country, null=True)
    count = models.IntegerField()
    length = models.FloatField(blank=True, null=True)
    last_update = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    user_update = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=255)
    locality = models.CharField("locality", blank=True, null=True, max_length=50)
    show = models.BooleanField(default=False, verbose_name="Статус відображення")
    
    def __unicode__(self):
        return "[%s] %s - %s" % (self.ids, self.manufacturer, self.name)

    class Meta:
        ordering = ["type"]    


# Frame Size
class FrameSize(models.Model):
    name = models.CharField(max_length=100)
    cm = models.FloatField() 
    inch = models.FloatField()
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["inch","name"]    


# --- види грошових надходжень
class CashType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name",]    
    

# postach Dealer (Ukraine)
class Dealer(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
#    brand = models.ManyToManyFields(Manufacturer)
    www = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ["name"]    


# postach Dealer manager (Ukraine)
class DealerManager(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    description = models.TextField()
    phone = models.CharField(max_length=100)
    company = models.ForeignKey(Dealer)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["company", "name"]    


# Dealer invoice (Ukraine)
class DealerInvoice(models.Model):
    origin_id = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=False)
    company = models.ForeignKey(Dealer)
    manager = models.ForeignKey(DealerManager, blank = True, null = True)
    price = models.FloatField()
    currency = models.ForeignKey(Currency)
    file = models.CharField(max_length=255)
    received = models.BooleanField(default=False, verbose_name="Товар отримано?")
    payment = models.BooleanField(default=False, verbose_name="Оплачено?")
    description = models.TextField(blank = True, null = True)
            
    def __unicode__(self):
        return "%s - %s - %s [%s %s]" % (self.origin_id, self.company, self.manager, self.price, self.currency) 

    class Meta:
        ordering = ["payment", "company", "manager", "date"]    


#inventory 
class InventoryList(models.Model):
    catalog = models.ForeignKey(Catalog)
    count = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now_add=False, blank = True, null = True)
    description = models.TextField(blank = True, null = True)
    user = user = models.ForeignKey(User, blank=False, null=False)
    real_count = models.IntegerField()
    check_all = models.BooleanField(default=False, verbose_name="Загальна кількість?")
    chk_del = models.BooleanField(default=False, verbose_name="Мітка на видалення")
            
    def __unicode__(self):
        return "[%s] - %s (%s) ***%s***" % (self.date, self.count, self.description, self.user) 

    class Meta:
        ordering = ["date", "catalog", "count"]    


class InvoiceComponentList(models.Model):
    invoice = models.ForeignKey(DealerInvoice)
    catalog = models.ForeignKey(Catalog)
    count = models.IntegerField()
    price = models.FloatField()
    currency = models.ForeignKey(Currency)
    date = models.DateField(auto_now_add=False)
    rcount = models.IntegerField(blank = True, null = True)
    description = models.TextField(blank = True, null = True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
            
    def __unicode__(self):
        return "%s - %s" % (self.invoice, self.catalog) 

    class Meta:
        ordering = ["invoice", "catalog", "price", "date"]    


# Dealer payment (Ukraine)
class DealerPayment(models.Model):
    dealer_invoice = models.ForeignKey(DealerInvoice)
    invoice_number = models.CharField(max_length=255, null = True)
    date = models.DateField(auto_now_add=True)
    bank = models.ForeignKey(Bank)
    price = models.FloatField()
    currency = models.ForeignKey(Currency)
    letter = models.BooleanField(default=False, verbose_name="Лист відправлено?")
    description = models.TextField(blank = True, null = True)
            
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["date", "invoice_number"]    


#Client database
class Client(models.Model):
    name = models.CharField(max_length=255)
    forumname = models.CharField(max_length=255)
    country = models.ForeignKey(Country)
    city = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    phone1 = models.CharField(max_length=100, blank = True, null = True)
    sale = models.IntegerField("how many percent for sale", default=0)
    summ = models.FloatField()
    birthday = models.DateField(auto_now_add=False, blank = True, null = True)
    sale_on = models.BooleanField(default=True, verbose_name="Знижка включена")
    description = models.TextField(blank = True, null = True)
    
    def __unicode__(self):
        return "%s - [%s]" % (self.name, self.forumname)

    class Meta:
        ordering = ["name"]    

#клієнтські борги
class ClientDebts(models.Model):
    client = models.ForeignKey(Client)
    date = models.DateTimeField()
    price = models.FloatField()
    cash = models.BooleanField(default=False, verbose_name="Каса?")
    description = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)    
    
    def __unicode__(self):
        return "[%s] - %s (%s) %" % (self.date, self.client, self.description)

    class Meta:
        ordering = ["client", "date"]    

#клієнтські проплати
class ClientCredits(models.Model):
    client = models.ForeignKey(Client)
    date = models.DateTimeField()
    price = models.FloatField()
    cash_type = models.ForeignKey(CashType, blank=True, null=True, on_delete=models.SET_NULL) 
    description = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return "[%s] - %s" % (self.client, self.description)

    class Meta:
        ordering = ["client", "date"]    


class ClientInvoice(models.Model):
    client = models.ForeignKey(Client)
    catalog = models.ForeignKey(Catalog)
    count = models.FloatField() #IntegerField()
    price = models.FloatField(blank = True, null = True)
    sum = models.FloatField()
    currency = models.ForeignKey(Currency)
    sale = models.IntegerField(blank = True, null = True, validators=[ MaxValueValidator(100), MinValueValidator(0) ]) 
    pay = models.FloatField(blank = True, null = True)    
#    date = models.DateField(auto_now_add=False)
    date = models.DateTimeField(auto_now_add = False)    
    description = models.TextField(blank = True, null = True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    chk_del = models.BooleanField(default=False, verbose_name="Мітка на видалення")    
            
    def __unicode__(self):
        return "%s - %s шт." % (self.catalog.name, self.count) 
        #return self.origin_id 

    class Meta:
        ordering = ["client", "catalog", "date"]    


class ClientOrder(models.Model):
    client = models.ForeignKey(Client)
    catalog = models.ForeignKey(Catalog, blank=True, null=True)
    description = models.TextField(blank = True, null = True)    
    count = models.IntegerField()
    price = models.FloatField(blank = True, null = True)
    sum = models.FloatField()
    currency = models.ForeignKey(Currency)
    pay = models.FloatField(default = 0, blank = True, null = True)    
    date = models.DateTimeField(auto_now_add = False)    
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)    
    status = models.BooleanField(default=False, verbose_name="Статус?")
    credit = models.ForeignKey(ClientCredits, blank=True, null=True)
            
    def __unicode__(self):
        return "%s (%s) - %s шт." % (self.catalog, self.description, self.count) 
        #return self.origin_id 

    class Meta:
        ordering = ["status", "-date", "client"]    


#my costs (Затрати)
class CostType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]    


class Costs(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    cost_type = models.ForeignKey(CostType)
    price = models.FloatField()
    description = models.TextField()

    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["date"]


#Bicycle type table
class Bicycle_Type(models.Model):
    type = models.CharField(max_length=255) #adult, kids, mtb, road, hybrid
    description = models.TextField(blank=True, null=True)

#    def natural_key(self):
#        return (self.id, self.type)

    def __unicode__(self):
        return self.type

    class Meta:
        ordering = ["type"]    


#Bicycle wheel size table
class Wheel_Size(models.Model):
    type = models.CharField(max_length=255) #20, 24, 26, 27.5, 29, 29+
    description = models.TextField(blank=True, null=True)
    iso = models.CharField(max_length=255) #559, 622, 630 ... (mm)

#    def natural_key(self):
#        return (self.id, self.type)

    def __unicode__(self):
        return self.type

    class Meta:
        ordering = ["type"]    


# Bicycle table (Bicycle)
class Bicycle(models.Model):
    model = models.CharField(max_length=255)
    type = models.ForeignKey(Bicycle_Type) #adult, kids, mtb, road, hybrid
    brand = models.ForeignKey(Manufacturer)
    year = models.DateField(blank = True, null=True)
    color = models.CharField(max_length=255)
    wheel_size = models.ForeignKey(Wheel_Size, blank=True, null=True) #20, 24, 26, 27.5, 29, 29+
    #sizes = models.CharField(max_length=255)    
    sizes = models.CommaSeparatedIntegerField(max_length=10)
    photo = models.ImageField(upload_to = 'media/upload/', max_length=255, blank=True, null=True)
    photo_url = models.ManyToManyField(Photo, blank=True)
    weight = models.FloatField()
    #PositiveIntegerField()
    price = models.FloatField()
    currency = models.ForeignKey(Currency)
    sale = models.FloatField(default = 0, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        #return u'Велосипед %s. Ціна %s грн.' % (self.model, self.brand)
        return u'Велосипед %s. Модель %s. %s (%s)' % (self.brand, self.model, self.year.year, self.color)
        #return u'Велосипед %s. Ціна %d грн.' % (self.model, self.price)
        
    class Meta:
        ordering = ["brand", "year", "type", "model", "price"]    
       
        
# Bicycle in store (BicycleStore)
class Bicycle_Store(models.Model):
    model = models.ForeignKey(Bicycle, blank = True, null = True)
    serial_number = models.CharField(max_length=50)
    size = models.ForeignKey(FrameSize, blank = True, null = True)
    price = models.FloatField()
    currency = models.ForeignKey(Currency)
    count = models.PositiveIntegerField()
    realization = models.BooleanField()
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        #return self.model
        return u'%s [%s]' % (self.model, self.serial_number)

    class Meta:
        ordering = ["model"]
        
            
# Bicycle sale to client
class Bicycle_Sale(models.Model):
    model = models.ForeignKey(Bicycle_Store)
    client = models.ForeignKey(Client)
    price = models.FloatField()
    currency = models.ForeignKey(Currency)
    sale = models.IntegerField()
    date = models.DateField(auto_now_add=False)
    service = models.BooleanField(default = False) 
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    sum = models.FloatField(blank=True, null=True)
    #debt = models.ForeignKey(ClientDebts, blank=True, null=True, on_delete=models.SET_NULL)
    debt = models.ForeignKey(ClientDebts, blank=True, null=True)
    
    def __unicode__(self):
        #return self.model
        return u'%s' % self.model

    class Meta:
        ordering = ["client", "model", "date"]

        
# Bicycle ORDER for client
class Bicycle_Order(models.Model):
    client = models.ForeignKey(Client)
    model = models.ForeignKey(Bicycle)
    size = models.CharField(max_length=50)
    price = models.FloatField()
    sale = models.IntegerField()
    prepay = models.FloatField()
    currency = models.ForeignKey(Currency)
    date = models.DateField(auto_now_add=True)
    done = models.BooleanField(default = False) 
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)    
    
    def __unicode__(self):
        #return self.model
        return u'%s -> %s' % (self.client ,self.model)

    class Meta:
        ordering = ["-date", "client", "model"]

            
class WorkGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    tabindex = models.IntegerField()
    
    def __unicode__(self):
        return u'%s -> %s' % (self.name, self.description)

    class Meta:
        ordering = ["name", "tabindex"]

     
class WorkType(models.Model):
    name = models.CharField(max_length=255)
    work_group = models.ForeignKey(WorkGroup)
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        #return u'Розділ %s. Робота: %s' % (self.work_group, self.name)
        return u'Робота: %s' % (self.name)
        #return self.name

    class Meta:
        ordering = ["work_group", "name"]
     
    
class WorkShop(models.Model):
    client = models.ForeignKey(Client)
    date = models.DateTimeField(auto_now_add=True)
    work_type = models.ForeignKey(WorkType)
    price = models.FloatField()
    pay = models.BooleanField(default = False, verbose_name="Оплачено?")
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.description

    class Meta:
        ordering = ["date", "client"]


class WorkStatus(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]

       
class PhoneStatus(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
       

class WorkTicket(models.Model):
    client = models.ForeignKey(Client)
    date = models.DateField()
    end_date = models.DateField()
    status = models.ForeignKey(WorkStatus)
    description = models.TextField(blank=True, null=True)
    phone_status = models.ForeignKey(PhoneStatus, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)    
    
    def __unicode__(self):
        return self.description

    class Meta:
        ordering = ["date", "status"]


class ShopDailySales(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    price = models.FloatField() #В касі на кінець дня
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=False, null=False)
    cash = models.FloatField() #Готівка
    tcash = models.FloatField() #Термінал
    ocash = models.FloatField() #Взято з каси
    
    def __unicode__(self):
        return "[%s] - %s" % self.date, self.price 

    class Meta:
        ordering = ["date", "price"]


# Bill table (nakladna)
#===============================================================================
# class Bill(models.Model):
#    ids = models.CharField("code", unique=True, max_length=50)
#    invoice_id = models.ForeignKey(DealerInvoice)
#    date = models.DateTimeField(auto_now_add=True)
#    product = models.ForeignKey(Catalog)
#    count = models.IntegerField("how many something", default=1)
#    price = models.FloatField(blank=True, null=True)
#    currency = models.ForeignKey(Currency)
#    description = models.CharField(max_length=255, blank=True, null=True)
#    
#    def __unicode__(self):
#        return self.name
# 
#    class Meta:
#        ordering = ["invoice_id"]    
#===============================================================================

class CheckPay(models.Model):
    check_num = models.IntegerField("mini-fp")
    cash = models.FloatField()
    term = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL) 
    description = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'%s / [%s / %s]' % (self.check_num, self.cash, self.term)

    class Meta:
        ordering = ["check_num"]    


# Check table (Check)
class Check(models.Model):
    #ids = models.CharField("code", unique=True, max_length=50)
    check_num = models.IntegerField("mini-fp")
    checkPay = models.ForeignKey(CheckPay, blank=True, null=True)
    client = models.ForeignKey(Client)
    date = models.DateTimeField(auto_now_add=True)
    catalog = models.ForeignKey(ClientInvoice, blank=True, null=True)
    bicycle = models.ForeignKey(Bicycle_Sale, blank=True, null=True)
    workshop = models.ForeignKey(WorkShop, blank=True, null=True)
    count = models.FloatField("how many something", default=1.00)
    discount = models.IntegerField("%", default=0)
    price = models.FloatField()
    cash_type = models.ForeignKey(CashType, blank=True, null=True, on_delete=models.SET_NULL) 
    description = models.CharField(max_length=255, blank=True, null=True)
    print_status = models.BooleanField(default=False)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)    
    
    def __unicode__(self):
        return self.catalog

    class Meta:
        ordering = ["date", "check_num"]    


class PreOrder(models.Model):
    date = models.DateField(auto_now_add=True)
    date_pay = models.DateField(auto_now_add=False)
    date_delivery = models.DateField()
    company = models.ForeignKey(Dealer)
    manager = models.ForeignKey(DealerManager, blank = True, null = True)
    price = models.FloatField()
    price_pay = models.FloatField()
    currency = models.ForeignKey(Currency)
    file = models.CharField(max_length=255)
    received = models.BooleanField(default=False, verbose_name="Товар отримано?")
    #payment = models.ForeignKey(DealerPayment, blank = True, null = True)
    payment = models.BooleanField(verbose_name="Оплачено?")
    description = models.TextField(blank = True, null = True)
            
    def __unicode__(self):
        return self.file 

    class Meta:
        ordering = ["company", "manager", "date"]    


class Discount(models.Model):
    name = models.CharField(max_length=255)
    manufacture_id = models.IntegerField()
    type_id = models.IntegerField() 
    date_start = models.DateField(auto_now_add=True)
    date_end = models.DateField(auto_now_add=False)
    sale = models.FloatField()
    #received = models.BooleanField(default=False, verbose_name="Товар отримано?")
    description = models.TextField(blank = True, null = True)
            
    def __unicode__(self):
        return self.file 

    class Meta:
        ordering = ["name", "sale", "date_end"]    


import datetime

class Rent(models.Model):
    catalog = models.ForeignKey(Catalog)    
    client = models.ForeignKey(Client)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateField(auto_now_add=False, default = datetime.date.today() + datetime.timedelta(days=3))
    count = models.IntegerField(default = 1)
    deposit = models.FloatField(default = 0, blank = True, null = True)
    status = models.BooleanField(default=False, verbose_name="Прокат?")
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank = True, null = True)
    cred = models.ForeignKey(ClientCredits, blank=True, null=True)
                
    def __unicode__(self):
        return self.catalog 

    class Meta:
        ordering = ["status", "-date_start", "date_end"]    
    
    
#--- Цінники ---
class ShopPrice(models.Model):
    catalog = models.ForeignKey(Catalog)
    scount = models.IntegerField(default = 1) # shop
    dcount = models.IntegerField(default = 0) # depository
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.count

    class Meta:
        ordering = ["catalog", "scount"]    


#--- Work day / Робочі дні ---
class WorkDay(models.Model):
    date = models.DateField()
    user = models.ForeignKey(User, blank=False, null=False)
    status = models.IntegerField(default = 0) # 0 - absant; 1 - present; 2 - half-time 
    description = models.TextField(blank = True, null = True)    
    
    def __unicode__(self):
        return u"[%s] - %s - (%s)" % self.date, self.user, self.description

    class Meta:
        ordering = ["date"]    


#--- message to Client  ---
class ClientMessage(models.Model):
    client = models.ForeignKey(Client, blank=False, null=False)
    msg = models.TextField(blank = True, null = True)
    status = models.BooleanField(default = False, verbose_name="Виконано?")
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, blank=False, null=False)
    ddate = models.DateTimeField(auto_now_add=False, blank=False, null=False)
    duser = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='duser')
    #duser = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return u'%s' % self.msg

    class Meta:
        ordering = ["client", "-date", "status"]
    

class ClientReturn(models.Model):
    client = models.ForeignKey(Client, blank=False, null=False)
    catalog = models.ForeignKey(Catalog)
    count = models.IntegerField(default = 0)
    sum = models.FloatField(default = 0, blank = True, null = True)
    buy_date = models.DateTimeField()
    buy_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='buy_user')
    msg = models.TextField(blank = True, null = True)
    date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    user = models.ForeignKey(User, blank=False, null=False)
    cash = models.BooleanField(blank=False, null=False, default = True)
    
    def __unicode__(self):
        return u'%s' % self.msg

    class Meta:
        ordering = ["-date", "client"]
    