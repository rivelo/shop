# -*- coding: utf-8 -*-
from django.db import models
from django.forms import ModelForm
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Count, Sum, Max
from django.db.models.aggregates import Avg
#from datetime import datetime
import datetime
from django.db.models import F

from urlparse import urlparse,parse_qs,urlunparse
from urllib import urlencode
import httplib
import os.path
import urllib2
from django.conf import settings
from _mysql import NULL
from django.db.models import Q
from django.utils.translation.trans_real import catalog
from __builtin__ import True
from django.template.defaultfilters import default
from datetime import date
#from audioop import reverse
#from Scripts.pilprint import description
from django.urls import reverse
from pyexpat import model
#from ctypes.test.test_pep3118 import s_bool


# Group Type = Group for Component category 
class GroupType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    name_ukr = models.CharField(max_length=100, blank=True, null=True)
    description_ukr = models.CharField(max_length=255, blank=True, null=True)
#   icon = models.ImageField(upload_to = 'upload/icon/', blank=True, null=True)
    
    def __unicode__(self):
        return u'%s / %s' % (self.name, self.name_ukr)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["name"]    


class Schedules(models.Model):
    name = models.CharField(max_length = 255, blank = True, null = True)
    start_week_day = models.PositiveSmallIntegerField(default = 1) 
    end_week_day = models.PositiveSmallIntegerField(default = 7)
    start_time = models.TimeField(default = datetime.time(10, 00, 00))
    end_time = models.TimeField(default = datetime.time(19, 00, 00))
    start_date = models.DateField(auto_now_add = False)
    end_date =  models.DateField()
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return u'%s : [%s - %s] - (%s - %s)' % (self.name, self.start_date, self.end_date, self.start_time, self.end_time)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["start_date", "start_week_day"]    


class Shop(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100, blank = False, null = False)
    phone1 = models.CharField(max_length=100, blank = True, null = True)
    phone2 = models.CharField(max_length=100, blank = True, null = True)
    email = models.EmailField(blank = True, null = True)
    web_site = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=255, blank = True, null = True)
    map_point = models.TextField(blank = True, null = True)
    ip_addr = models.GenericIPAddressField(protocol='IPv4', blank = True, null = True)
    status = models.BooleanField(default = True) # Work status
    show = models.BooleanField(default = True) # Show status in SHOPs list
#    shop_pay_cash = models.ManyToManyField(CashType, blank = True, related_name='Shop_Cash_Pay')
#    shop_pay_term = models.ManyToManyField(CashType, blank = True, related_name='Shop_Term_Pay')
    casa_server_ip =  models.GenericIPAddressField(protocol='IPv4', blank = True, null = True)
    casa_server_port = models.PositiveSmallIntegerField(default = 8123, null=True)
    casa_hash = models.CharField(max_length=255, blank=True, null=True)
# checkBox connect
    XLICENSEKEY = models.CharField(max_length=255, blank=True, null=True)
    PIN_CODE = models.CharField(max_length=255, blank=True, null=True)
    work_schedule = models.ManyToManyField(Schedules, blank=True) 
    user_list = models.ManyToManyField(User, blank=True)
    description = models.CharField(max_length=255, blank=True)
    #color = models.CharField(max_length=50, blank=True, , related_name='color (hex value) to show shop in table')
    #letter =  models.CharField(max_length=50, blank=True,)

 
    def get_deb_cred_in_date(self, year, month, day):
        ndate = datetime.date(int(year), int(month), int(day))
        cashtype_list = self.cashtype_set.all()
#        type_cash = cashtype_list.filter(pay_status='True', cash='True') 
#        type_term = cashtype_list.filter(pay_status='True', term='True')
        deb = ClientDebts.objects.filter(date__year=ndate.year, date__month=ndate.month, date__day=ndate.day, shop=self).order_by('date')
        cred = ClientCredits.objects.filter(date__year=ndate.year, date__month=ndate.month, date__day=ndate.day, cash_type__in = cashtype_list).order_by('date')
        res_dict = {}
        res_dict['deb'] = deb
        res_dict['cred'] = cred
        return res_dict


    def get_cashtype(self):
        return self.cashtype_set.all().filter(pay_status='True', cash='True')
    
    def get_termtype(self):
        return self.cashtype_set.all().filter(pay_status='True', term='True')

    def shop_cash_sum_by_day(self):
        cashtype_list = self.cashtype_set.all()
        type_cash = cashtype_list.filter(pay_status='True', cash='True') 
        type_term = cashtype_list.filter(pay_status='True', term='True')

        ndate = datetime.datetime.now()
            
        deb = ClientDebts.objects.filter(date__year=ndate.year, date__month=ndate.month, date__day=ndate.day, shop = self)#.order_by()
        cred = ClientCredits.objects.filter(date__year=ndate.year, date__month=ndate.month, date__day=ndate.day)#.order_by()
        cashCred = cred.filter(cash_type__in = type_cash).aggregate(suma=Sum("price")) # Cash
        termCred = cred.filter(cash_type__in = type_term).aggregate(suma=Sum("price")) # Term
        cashDeb = deb.filter(cash='True').aggregate(suma=Sum("price"))

        res_dict = {}
        res_dict['cashCred'] = cashCred.get('suma') or 0
        res_dict['termCred'] = termCred.get('suma') or 0
        res_dict['cashDeb'] = cashDeb.get('suma') or 0
        return res_dict

    def __unicode__(self):
        return u'%s' % (self.name)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["name", "address"]    


#class CashbackRanking(models.Model):
    #name = models.CharField(max_length=100, verbose_name="Назва рейтингу знижки")
    #percent = models.
    #sum = models.
    #ranking = models.PositiveSmallIntegerField(blank=True, default = 0)


#class FOP(models.Model):
#    FOP =
#    IBAN = 
#    bank_data = 
 

# --- види грошових надходжень
class CashType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва для типу оплати")
    description = models.TextField(blank=True, null=True)
    pay_status = models.BooleanField(default = False, verbose_name="Платіжний тип. Враховується в оплатах")
    cash = models.BooleanField(default = False, verbose_name="Готівка")
    term = models.BooleanField(default = False, verbose_name="Термінали або будь-який екваєринг. Враховується у касовому обліку.")
    shop = models.ForeignKey(Shop, blank=True, null=True, on_delete=models.SET_NULL)
    #def get_sum_by_day(): 

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name",]    

    
    
from django.utils.text import slugify
# Type = Component category 
class Type(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    name_ukr = models.CharField(max_length=100, blank=True, null=True)
    description_ukr = models.CharField(max_length=255, blank=True, null=True)
    bike_order = models.PositiveSmallIntegerField(blank=True, default = 0)
    group = models.ForeignKey(GroupType, blank=True, null=True)
    synonym = models.CharField(max_length=255, blank=True, null=True)
    synonym_ukr = models.CharField(max_length=255, blank=True, null=True)
    ico_status = models.BooleanField(default=False, verbose_name="Наявність іконки")
    # одиниці вимірювання чи коефіцієнт
#    ranking = models.FloatField()
#    icon = models.ImageField(upload_to = 'upload/icon/', blank=True, null=True)
#    icon_select = models.ImageField(upload_to = 'upload/icon/', blank=True, null=True)

    def get_icon_name(self, status=True):
        dirpath = settings.ICON_DIR
        if status == True:
            return (dirpath + slugify(self.name) + '-gr.png')
        else:
            return (dirpath + slugify(self.name) + '-bl.png')

    def get_discount(self):
        max_sale = None
        curdate = datetime.date.today()
        dateDiscount = Discount.objects.filter(date_start__lte = curdate, date_end__gte = curdate, type_id = self.pk).order_by("-sale")
        if dateDiscount.exists():
            pass
            #max_sale = dateDiscount.aggregate(msale = Max('sale'))
            #max_sale = dateDiscount.annotate(max_s = Max('name'))
            return dateDiscount
        else:
           return 0
    
    def __unicode__(self):
        return u'%s / %s' % (self.name, self.name_ukr)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["name"]    


#Bicycle type table
class Bicycle_Type(models.Model):
    type = models.CharField(max_length=255) #adult, kids, mtb, road, hybrid
    ukr_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    level = models.IntegerField(default = 0, blank = True, null = True)
    parent_id = models.ForeignKey("self", blank=True, null = True, default=None)
    status = models.BooleanField(default = True, blank=True)

    # Bikes in Store allTime
    def bike_count(self):
 #       all_bike = self.bicycle_set.all()
#        res = self.bicycle_set.all().aggregate(bike_sum = Count('pk')) 
        inlist = []
        inlist.append(self.pk)
#        for i in all_bike:
#            print ">> bike[%s] =" % self.type 
#            print "bike = " + str(i.id)
        bs_list = Bicycle_Store.objects.filter(model__type__pk__in = inlist)
        res = bs_list.aggregate(bike_sum = Count('pk'))
        return res['bike_sum']
    
    # Bikes in Store Now
    def subtype_count(self):
        inlist = []
        inlist.append(self.pk)
        bs_list = Bicycle_Store.objects.filter(count__gt = 0, model__type__pk__in = inlist)
        res = bs_list.aggregate(bike_sum = Count('pk'))
        #res = self.bicycle_type_set.filter().aggregate(bike_sum = Count('pk'))
        return res['bike_sum']

    def subtype_list(self):
        res = self.bicycle_type_set.all()
        return res

    def subtype_storebike(self):
        res = self.bicycle_type_set.all().values_list('pk')
        bs = Bicycle_Store.objects.filter(count__gt = 0, model__type__pk__in = res).order_by('model__brand')
        return bs

    def storebike(self):
        inlist = []
        inlist.append(self.pk)
        bs = Bicycle_Store.objects.filter(count__gt = 0, model__type__pk__in = inlist).order_by('model__brand')
        return bs

    def __unicode__(self):
        return u'%s' % self.type

    class Meta:
        ordering = ["type"]    


# Size catalog
class Size(models.Model):
    name = models.CharField(max_length=100)
    width = models.IntegerField() 
    hight = models.IntegerField()
    #length = models.IntegerField(default = 0, blank = True, null = True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]    


# Country table (Country)
class Country(models.Model):
    name = models.CharField(max_length=255)
    ukr_name = models.CharField(max_length=255, blank = True, null = True)
    
    
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
    #symbol
    country = models.ForeignKey(Country)

#    def avg_currency(self):
#        self.filter(currency = self.currency).aggregate(average_val = Avg('value')) #annotate(avgval = Avg('value'))
#        return 
    def short_str(self):
        return u"%s" % (self.ids_char)
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.ids_char)

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


class Discount(models.Model):
    name = models.CharField(max_length=255)
    manufacture_id = models.IntegerField(blank = True, null = True)
    type_id = models.IntegerField(blank = True, null = True) 
    date_start = models.DateField(auto_now_add = False)
    date_end = models.DateField(auto_now_add = False)
    sale = models.FloatField()
    description = models.TextField(blank = True, null = True)
            
    def get_manufacture(self):
        res = Manufacturer.objects.filter(pk = self.manufacture_id)
        if res.exists():
            return res[0]
        else:
            return None

    def get_type(self):
        res = Type.objects.filter(pk = self.type_id)
        if res.exists():
            return res[0]
        else:
            return None
    
    def __unicode__(self):
        return u'%s [%s-%s]. Знижка - %s%s' % (self.name, self.date_start, self.date_end, int(self.sale), '%') 

    class Meta:
        ordering = ["name", "sale", "date_start", "date_end"]    


# list of manufectures 
class Manufacturer(models.Model):
    name = models.CharField(max_length=100)
    www = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to = 'upload/brandlogo/', blank=True, null=True)
    country = models.ForeignKey(Country, null=True)
    description = models.TextField(blank=True, null=True)    
    bikecompany = models.BooleanField(default = False, blank = True, verbose_name="Компанія яка виготовляє велосипеди?")
    component = models.BooleanField(default = False, blank = True, verbose_name="Компанія яка виготовляє компоненти?")

    def get_discount(self):
        max_sale = None
        curdate = datetime.date.today()
        dateDiscount = Discount.objects.filter(date_start__lte = curdate, date_end__gte = curdate, manufacture_id = self.pk).order_by("-sale")
        if dateDiscount.exists():
            pass
            return dateDiscount
        else:
           return 0

    #===========================================================================
    # def get_discount(self):
    #     max_sale = None
    #     curdate = datetime.date.today()
    #     dateDiscount = Discount.objects.filter(date_start__lte = curdate, date_end__gte = curdate, manufacture_id = self.pk).order_by("-sale")
    #     if dateDiscount.exists():
    #         max_sale = dateDiscount.aggregate(Max('sale'))
    #     else:
    #        return 0
    #     return (max_sale, dateDiscount[0])         
    #===========================================================================
    
    def natural_key(self):
        return (self.id, self.name)
        
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ["name"]    


class Photo(models.Model):
    url = models.CharField(max_length=255)
    local = models.CharField(max_length=255, blank=True, null=True)
    www = models.URLField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)
    check_del = models.BooleanField(default = False, blank = True, verbose_name="Перевірити перед видаленням?")
    #goo_url = models.CharField(max_length=255)

    def image_local_exists(self):
        path = self.url
#        domain = urlparse(path).hostname
        file_path = settings.MEDIA_ROOT        
        if self.local and os.path.isfile(file_path.split('\media')[0] + self.local):
            return True
        else:
            if self.url <> "":
                try:
                    url_obj = urllib2.urlopen(self.url)
                    return True
                except:
                    pass
                    #return False
            if self.www <> "":
                try:
                    url_obj = urllib2.urlopen(self.url)
                    return True
                except:
                    return False
        return False

    def catalog_show(self):
        cat_list = self.catalog_set.all()
        str = ''
        for cat in cat_list:
            str = str + "["+cat.ids+"] " + cat.name + "<br>"
        return str

    def catalog_show_simple(self):
        return self.catalog_set.all()
    
    def __unicode__(self):
        return u'%s %s' % (self.url, self.local) 

    class Meta:
        ordering = ["date", "description"]    


class YouTube(models.Model):
    url = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)

    def youtube_hash(self):
        #qs = self.youtube_url
        try:
            qs = self.url
            pars = parse_qs(urlparse(qs).query)
            if pars:
                return pars['v'][0]
            else:
                return qs.split('/')[3]
        except:
            return 'youtube url not found'
    
    def __unicode__(self):
        return u'%s' % self.url

    class Meta:
        ordering = ["date", "description"]    



class Season(models.Model):
    name = models.CharField(max_length = 255, )
    value = models.CharField(max_length = 255, blank=True, null=True)
    icon = models.CharField(max_length = 255, blank=True, null=True)
    description = models.CharField(max_length = 255, blank=True, null=True)
        
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ["pk", "name"]    


class CatalogAttribute(models.Model):
    name = models.CharField(max_length = 255, )
    value = models.CharField(max_length = 255, blank=True, null=True)
    type = models.ManyToManyField(Type, blank = True) # Type have this Attribute
    icon = models.CharField(max_length = 255, blank=True, null=True)
    description = models.CharField(max_length = 255, blank=True, null=True)
    created_date = models.DateTimeField("Дата створення", null=True, blank=True)
    #updated_date = models.DateTimeField("Дата оновлення", auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)
    updated_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def all_values(self):
        res_val = CatalogAttributeValue.objects.filter(attr_id = self.pk)
        return res_val


    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ["pk", "name"]    


class CatalogAttributeValue(models.Model):
    attr_id = models.ForeignKey(CatalogAttribute)
    value = models.CharField(max_length = 255, blank=True, null=True)
    value_float = models.FloatField(blank=True, null=True)
    icon = models.CharField(max_length = 255, blank=True, null=True)
    description = models.CharField(max_length = 255, blank=True, null=True)
    created_date = models.DateTimeField(u"Дата створення", null=True, blank=True)
    updated_date = models.DateTimeField(u"Дата оновлення", auto_now_add=True, null=True, blank=True)
    updated_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def all_items(self):
        res_val = Catalog.objects.filter(attributes = self.pk)
        return res_val

    def get_text_value(self):
        tval = self.value#.encode('utf8')
        tname = self.attr_id.name#.encode('utf8')
        return [tval, tname] 
    
    def __unicode__(self):
        return u'%s - %s / %s' % (self.attr_id, self.value, self.value_float)

    class Meta:
        ordering = ["attr_id", "value", "value_float"]    


# Main table 
class Catalog(models.Model):
    ids = models.CharField("code", unique=True, max_length=50)
    dealer_code = models.CharField("dealer code", max_length=50, blank=True, null=True)
    manufacture_article = models.CharField("manufacture code(article)", max_length=100, blank=True, null=True)
    barcode_upc = models.CharField("barcode_upc", max_length=12, blank=True, null=True)
    barcode_ean = models.CharField("barcode_EAN", max_length=13, blank=True, null=True)
    barcode = models.CharField("barcode other", max_length=128, blank=True, null=True)
    name = models.CharField(max_length=255)
    manufacturer = models.ForeignKey(Manufacturer)
    type = models.ForeignKey(Type, related_name='type')
    size = models.ForeignKey(Size, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)    
    photo = models.FileField(upload_to = 'upload/catalog/%Y/', blank=True, null=True) # 'media/upload/catalog/%Y/%m/%d'
    photo_url = models.ManyToManyField(Photo, blank=True)
    year = models.IntegerField(u'Модельний рік', blank=True, null=True)
    sale_to = models.DateField(auto_now_add=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField()
    last_price = models.FloatField(blank=True, null=True)
    currency = models.ForeignKey(Currency)
    sale = models.FloatField()
    country = models.ForeignKey(Country, null=True, verbose_name = "Країна виробник")
    count = models.IntegerField(u"Кількість в магазинах")
    length = models.FloatField(u"Довжина (для товарів які продаються на метри)", blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    created_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='created_user')
    last_update = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    user_update = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='updated_user')
    description = models.CharField(u"Примітки для себе", max_length=255, blank=True, null=True)
    locality = models.CharField("locality", blank=True, null=True, max_length=50)
    show = models.BooleanField(default=False, verbose_name=u"Статус відображення")
    bike_style = models.ManyToManyField(Bicycle_Type, blank=True) # cyclocross, crosscountry, road, gravel, enduro, downhill, city...
    season = models.ManyToManyField(Season, blank = True) #    season = winter, summer, ...
    attributes = models.ManyToManyField(CatalogAttributeValue, blank = True) #    models.ManyToManyField() # field like sizechart, field to shoes

    full_description = models.TextField(u"Опис товару для Web-сторінки", blank=True, null=True)
    youtube_url = models.ManyToManyField(YouTube, blank=True)
#    наявність у постачальника
    date = models.DateField(u"Строк придатності", null=True, blank=True) #Строк придатності
    url_web_site = models.CharField(max_length=255, null=True, blank=True, verbose_name="Посилання на офіційний сайт")
    mistake = models.CharField(max_length=255, null=True, blank=True, verbose_name="Помилка в заповненні картки товару")
    mistake_status = models.BooleanField(default=False, verbose_name="Статус помилки")
    #search_history
    change_history = models.TextField(blank=True, null=True, verbose_name="History of changes on item Catalog ")
    rating = models.FloatField(blank=True, null=True)   
    #одиниці виміру
    #коефіцієнт для системи Сі

    def get_discount(self):
        curdate = datetime.date.today()
#        dateDiscount = Discount.objects.filter(date_start__lte = curdate, date_end__gte = curdate, type_id = self.type.pk)
        #dateDiscount = Discount.objects.filter(date_start__lte = curdate, date_end__gte = curdate, manufacture_id = self.manufacturer.pk)
        dateDiscount = Discount.objects.filter( date_start__lte = curdate, date_end__gte = curdate )
        dateDiscount = dateDiscount.filter( Q(manufacture_id = self.manufacturer.pk) | Q(type_id = self.type.pk) )
#        print "QUERY set = " + str(dateDiscount)
        try:
            pdiscount = dateDiscount[0].sale
            percent_sale = (100-pdiscount)*0.01
            price = self.price * percent_sale
        except:
            return 0
        return (price, pdiscount, dateDiscount[0].name)

    def get_discount_item(self):
        curdate = datetime.date.today()
        dateDiscount = Discount.objects.filter(date_start__lte = curdate, date_end__gte = curdate, manufacture_id = self.manufacturer.pk)
        if dateDiscount.exists():
            return dateDiscount[0]
        else:
            dateDiscount = Discount.objects.filter(date_start__lte = curdate, date_end__gte = curdate, type_id = self.type.pk)
            if dateDiscount.exists():
                return dateDiscount[0]
            else:
                return None

    def get_saleprice(self):
        percent_sale = (100-self.sale)*0.01
        price = self.price * percent_sale
        return price

    def client_price(self):
        usd = Currency.objects.get(pk=2)
        eur = Currency.objects.get(pk=4)
        uah = Currency.objects.get(pk=3)
        #r = self.clientinvoice_set.filter(pay__gt = 0, currency = uah).values('currency').annotate(count_p=Count('currency'), sum_p=Sum('pay'))
        #r = self.invoicecomponentlist_set.filter(currency = eur).values('currency').annotate(count_p=Count('currency'), sum_p=Sum('price'))
        #r = self.invoicecomponentlist_set.filter(price__gt = 0, currency = usd).values('currency').annotate(count_p=Count('currency'), sum_p=Sum('price'))
        r = self.clientinvoice_set.filter(currency = uah).values('currency').annotate(sum_p=Sum('sum'), count_p=Count('currency'), count_s=Sum('count'))
        #values('price', 'currency')
        return r

    def invoice_price(self): #UA price
        percent = 0
        profit = 0
        dn = datetime.datetime.now()
        month = dn.month
        year = dn.year
        ua = 0
        cc = self.invoicecomponentlist_set.filter(price__gt = 0) #.aggregate(isum = Sum('price'), )
        if not cc:
            return (0, 0)
        #ic_count = cc.count() #aggregate(icount = Count('price'))['icount']
        ic_count = 0
        sum = 0
        for item in cc:
            sum = sum + item.get_uaprice() * item.count
#            print "ITEM UA ["+ str(item.catalog) +"] = " + str(item.get_uaprice())
            ic_count = ic_count + item.count
        if ic_count != 0:
            ua = sum / ic_count
#            print "UA ["+ str(item.catalog) +"] = " + str(item.get_uaprice())
        if (self.currency.ids_char == 'UAH'):
            percent_sale = (100-self.sale)*0.01
            profit = self.price * percent_sale - ua 
            percent = (self.price * percent_sale) / (ua / 100) - 100
        #return cur_exchange1
        return (ua, profit, round(percent))

    def get_clientinvoice_count(self):
        cc = self.clientinvoice_set.filter().aggregate(cicount = Sum('count'))
        return cc['cicount']

    def get_invoice_count(self):
        cc = self.invoicecomponentlist_set.filter().aggregate(icount = Sum('count'))
        return cc['icount']
    # Розрахунок реальної кількості товару в магазині
    def get_realshop_count(self):
        ci = self.clientinvoice_set.filter().aggregate(cicount = Sum('count'))
        ic = self.invoicecomponentlist_set.filter().aggregate(icount = Sum('count'))
        res = int(ic['icount'] or 0) - int(ci['cicount'] or 0)
        return res

    def get_cur_invent(self):
        nday = 360
        cur_date = datetime.datetime.now()
        inv_list = self.inventorylist_set.filter(date__gt = cur_date-datetime.timedelta(days=int(nday)), real_count = F('count')).order_by('-date')
        #inv_list = self.inventorylist_set.filter(date__gt = cur_date-datetime.timedelta(days=int(nday)), check_all = True, real_count = F('count')).order_by('-date')
        #if (self.check_all == True) and ( self.date > cur_date-datetime.timedelta(days=int(nday)) ):
        return inv_list

    def new_arrival(self):
        count = 0
        days = 0
        nday = 14
        cur_date = datetime.datetime.now()
        dtdelta = cur_date-datetime.timedelta(days=int(nday))
        icl = self.invoicecomponentlist_set.filter(date__gt = dtdelta, rcount = None).aggregate(icount = Sum('count'), adate = Avg('date'))
        count = icl['icount']
        if icl and count > 0:
            res = cur_date - datetime.datetime.strptime(str(icl['adate']).split('.')[0], "%Y%m%d") 
            days = 5 - res.days
            if days <= 1:
                return "через (%s) день має приїхати - %s шт." % (days, count)
            else:
                return "через 1-%s дні має приїхати - %s шт." % (days, count)
        return False

    def get_photos(self):
        photos_list = []
        if self.photo:
            photos_list.append("/media/" + str(self.photo))
        if self.photo_url:
            p_url = self.photo_url.all()
        for photo in p_url:
            if photo.local:
                photos_list.append(photo.local)
            if photo.url and not photo.local:
                photos_list.append(photo.url)
        if photos_list:
            return photos_list
        else:
            return False

    def get_storage_box(self):
        list = StorageBox.objects.filter(catalog = self)
        return list

    def get_storage_box_sum_by_count(self):
        list = StorageBox.objects.filter(catalog = self).aggregate(sum_count = Sum('count'))
        return list

    def get_storage_box_list_to_html(self):
        list = StorageBox.objects.filter(catalog = self).values_list('box_name__name', 'count', 'count_real')
        res_list = []
        for i in list:
            box_name = u"%s - %s з %s шт."  % (i[0], i[1], i[2])
            res_list.append(box_name)
        return res_list

    def _get_all_code(self):
        data = 'ids: %s;\n  dealer_code: %s; barcode: %s; barcode_upc: %s; barcode_ean: %s; manufacture_article:%s;'  %  (self.ids, self.dealer_code, self.barcode, self.barcode_upc, self.barcode_ean, self.manufacture_article)
        code_list = (self.ids, self.dealer_code, self.barcode, self.barcode_upc, self.barcode_ean, self.manufacture_article)
        arr = []
        for i in code_list:
#            print "I = %s" % i
            if (i == None) or (i == u''):
                pass
            else:
                arr.append(i)
#        print "\nGET all Code - " +  str(arr) #str(code_list)
        return arr
    get_code = property(_get_all_code) # return list of all Catalog code 

    def _get_code_w_name(self):
        code_str = "[ " + " ".join(self._get_all_code()) + " ] "
        name_str = self.name
        res_str = code_str + name_str
        return res_str
    get_code_name = property(_get_code_w_name)

    def json_barcode(self):
        data = {'ids': self.ids,
                'dealer_code': self.dealer_code,
                'barcode': self.barcode,
                'barcode_upc' : self.barcode_upc,
                'barcode_ean' : self.barcode_ean,
                'manufacture_article': self.manufacture_article,
                'name': self.name,
                'weight': self.weight,
                'description': self.description,
                'mistake_status': self.mistake_status,
                'mistake': self.mistake
            }
        return data

    def chk_barcode(self, value):
        res = ''
        dres = {}
        dres['f_model'] = None
        code_list = (self.ids, self.dealer_code, self.barcode, self.barcode_upc, self.barcode_ean, self.manufacture_article)
        if value in code_list:
#            print "CHECK barcode =  True" 
            res = u"[%s] Даний код вже додано до товару" % value
            dres['msg'] = res
            dres['url'] = reverse("catalog_edit", kwargs={"id": self.pk}) #'/catalog/edit/' + str(self.pk) 
            dres['status'] = False
            dres['f_model'] = None 
#            print "\nQuerySet = " + str(Catalog.objects.filter(pk=self.pk).only('pk', 'ids', 'name', 'dealer_code'))
        else:
#            print "CHECK barcode =  False"
            #ids_obj = Catalog.objects.filter(ids = value)
            #dcode_obj = Catalog.objects.filter(dealer_code = value)
            chk_obj = Catalog.objects.filter(Q(ids=value) | Q(dealer_code=value) | Q(barcode=value) | Q(barcode_ean=value) | Q(barcode_upc=value) | Q(manufacture_article=value)).only('pk', 'ids', 'name', 'dealer_code', 'barcode')#.exclude(pk=self.pk)
#            print "Chk OBJ = " + str(chk_obj[0].dealer_code)
#            print "OBJ = " + str(list(chk_obj)) #.values_list('pk', 'ids', 'name', 'dealer_code'))
            list_o = chk_obj.values('pk', 'ids', 'name', 'dealer_code', 'barcode')
#            print "OBJ list = " + str(list_o)
            if chk_obj:
                dres['f_model'] = list(chk_obj) #, flat=True)
                dres['msg'] = "Існує інший товар з таким кодом"
                dres['url'] =  None #reverse("cat_set_attr") #, kwargs={"id": self.pk}) #'/catalog/edit/'
                dres['status'] = False
 #               for item in chk_obj:
 #                   print "Item = %s \n" % item.pk
 #                   print "Item ids = %s \n" % item.ids
 #                   print "Item name = %s \n" % item.dealer_code
                return dres
            
            if value.isdigit() == True:
                if len(value) == 12:
#                    print ("\nUPC barcode %s\n" % self.barcode_upc)
                    if self.barcode_upc == None or self.barcode_upc == '':
#                        print ("\nUPC barcode is None\n")
                        self.barcode_upc = value
                        res = u"Додано UPC barcode - %s " % value
                        dres['status'] = True
                    else:
                        res = u"UPC barcode [%s] існує в даного товару. Перезаписати його на новий [%s]? " % (self.barcode_upc, value)
                        dres['status'] = False
                        dres['url'] = '/catalog/edit/' + str(self.pk)
                elif len(value) == 13:
 #                   print ("\nEAN barcode\n")
                    if self.barcode_ean == None or self.barcode_ean == '':
                        self.barcode_ean = value
#                        print ("\nEAN barcode is None\n")
                        res = u"Додано EAN barcode - %s " % value
                        dres['status'] = True
                    else:
                        res = u"EAN barcode [%s] існує в даного товару. Перезаписати його на новий [%s]?" % (self.barcode_ean, value)
                        dres['status'] = False
                        dres['url'] = reverse("catalog_edit", kwargs={"id": self.pk}) #'/catalog/edit/' + str(self.pk)
                else:
#                    print ("\nEAN barcode\n")
                    if self.barcode == None or self.barcode == '':
                        self.barcode = value
#                        print ("\nBarcode is None\n")
                        res = u"Додано [%s] в поле barcode" % value
                        dres['status'] = True
                    else:
                        res = u"Поле barcode [%s] існує в даного товару. Перезаписати його на новий [%s]?" % (self.barcode, value)
                        dres['status'] = False
                        dres['url'] = '/catalog/edit/' + str(self.pk)
            else:
                res = u"Введені дані [%s] не є стандартним штрихкодом. Введіть ці дані вручну якщо вони вірні!? " % (value)
                dres['status'] = False                 
                dres['url'] = reverse("catalog_edit", kwargs={"id": self.pk})
            dres['msg'] = res
        self.save()
        return dres

    def inv_price(self):
        r = self.invoicecomponentlist_set.filter(price__gt = 0)
        l = len(r)
        sum = 0
        for item in r:
#            print "\nInvPrice UA =  %s" % item.get_uaprice()
            sum = sum + item.get_uaprice()
        #r = self.invoicecomponentlist_set.filter(currency = uah).values('price', 'currency').annotate(sum_p=Sum('price'), count_p=Count('currency'))
        try:
            res = sum / l
        except:
            res = 0
        return res
        
    def _get_chk_price(self):
        p = self.inv_price()
        if p == 0:
            color = "text-primary"
            return ("Товару не надходило або в надходженнях ціна 0 грн!", color)
        ua_s  = self.invoice_price()
#        print "\nFULL name Prop - %s \n" % p
#        print "\nUA seredn = " + str(ua_s) #[2]) + " --- " +str(ua_s)
#        cprice = p[0]['sum_p']/p[0]['count_s']
        #cprice = self.inv_price()
#        print ("Price = %s - s_Price = %s; with Sale 15 = %s; with Sale 25 = %s; with Sale 35 = %s\n" % (self.get_saleprice(), p, str(self.price*0.85), str(self.price*0.75), str(self.price*0.65) ))
        color = "text-success"
        if ( (self.get_saleprice() <= p) or (p >= (self.price * 0.85)) ):            
            color = "text-danger"
            return ("Ahtung!!!", color)
        if (p >= (self.price * 0.75)) and  (p < (self.price * 0.85)):
            color = "text-warning"
        if (p >= (self.price * 0.65)) and (p < (self.price * 0.75)):
            color="text-info"
        return ('Price OK! ', color) #+ str(cprice)
    chk_price = property(_get_chk_price) # Перевірка на правильність ціни

    # Get all attributes
    def get_attribute_values(self):
        res = []
        attr = self.attributes.all() 
        for i in attr:
            (a_val, a_name) = i.get_text_value()
            hh = { 'attr_name': a_name, 'value': a_val, 'id': i.id}
            res.append(hh)
        return (res)
    
    def __unicode__(self):
        return u"[%s] %s - %s" % (self.ids, self.manufacturer, self.name)

    class Meta:
        ordering = ["type"]    


# Frame Size
class FrameSize(models.Model):
    name = models.CharField(max_length=100)
    cm = models.FloatField() 
    inch = models.FloatField()
    letter = models.CharField(max_length=25, blank=True, null=True, help_text = "Please enter LETTER of frame size")
    description = models.CharField(blank=True, null=True, help_text = "Please enter description for this Frame Size", max_length=255)
    rider_height_min = models.PositiveSmallIntegerField(help_text="Rider MIN height (cm)", default=0)
    rider_height_max = models.PositiveSmallIntegerField(help_text="Rider MAX height (cm)", default=0)
 
# Geometry
    seattube = models.IntegerField("Seattube size in mm", default=0, blank=True)
    seattube_angle = models.FloatField("Seat tube angle in degree", default=0, blank=True)
    ett_toptube = models.IntegerField("Frame ETT in mm", default=0, blank=True)
    standover = models.IntegerField("how many milimiters on frame standover", default=0, blank=True)
#    BB DROP = 
    headtube = models.IntegerField("Frame HEADtube in mm", default=0, blank=True)
    headtube_angle = models.FloatField("HEADtube angle (degree)", default=0, blank=True)
#    REACH = 
#    FORK LENGTH
#    STACK = 
    wheelbase = models.PositiveIntegerField("Wheelbase size in mm", default=0, blank=True)
    #user_update = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
#    brand =  
#    model = models.ManyToManyField( , blank=True)

    def rider_height_str(self):
        str_res = ''
        if self.rider_height_min == 0 and self.rider_height_max == 0:
            str_res = ''
        else:
            str_res = "[%s - %s cm]" % (self.rider_height_min, self.rider_height_max) 
        return str_res
    
    def letter_str(self):
        str_res = '' 
        if self.letter:
            str_res = self.letter
        elif (self.cm == 0 and self.inch == 0):
            str_res = '%s' % (self.name, )
        elif (self.letter == '' or self.letter == None) and (self.cm != 0 or self.inch != 0):
            str_res = '[%s"] - %s см' % (self.inch, self.cm)
        return str_res
    
    def __unicode__(self):
        return '%s - %s [ %s cm -  %s " ]' % (self.name, self.letter, self.cm, self.inch, )

    class Meta:
        ordering = ["name", "inch", "cm", "letter"]    


# postach Dealer (Ukraine)
class Dealer(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True, null=True)
    brand_list = models.ManyToManyField(Manufacturer, blank=True)
    www = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ["name"]    


# postach Dealer manager (Ukraine)
class DealerManager(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(Dealer)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["company", "name"]    



class ListManager(models.Manager):
#    def get_queryset(self):
#        return super(MaleManager, self).get_queryset().filter(reg_event__sex=1).count()

    def get_year_list(self):
        #list = DealerInvoice.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
        return super(ListManager, self).get_queryset().filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')

#    def get_male_byyear(self, year):
#        return super(MaleManager, self).get_queryset().filter(reg_event__sex=1, reg_event__event__date__year = year).count()

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
    objects = models.Manager() # The default manager.
    list_objects = ListManager() # The specific manager.
    
    def check_recived_invoice(self):
        list = self.invoicecomponentlist_set.all()
        return list

    def get_year_list(self):
#        list = DealerInvoice.objects.values('date__year').order_by('date__year').annotate(count=Count('date__year'))
        list = DealerInvoice.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
#         Order.objects.filter().extra({'month':"Extract(month from created)"}).values_list('month').annotate(Count('id'))
        return list 

    def chk_invoice_items(self):
        status = True
        i_list = InvoiceComponentList.objects.filter(invoice = self.pk)
        for item in i_list:
            if item.check_count() == False:
                status = False
        return status
            
    def __unicode__(self):
        return "%s - %s - %s [%s %s]" % (self.origin_id, self.company, self.manager, self.price, self.currency) 

    class Meta:
        ordering = ["payment", "company", "manager", "date"]    


# ---------   inventory -----------------
 
class BoxName(models.Model):
    name = models.CharField(max_length=255)
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин")
    user = models.ForeignKey(User, blank=False, null=False)
    mark_delete = models.BooleanField(default = False, verbose_name="Мітка на видалення")
    description = models.CharField(max_length=255, blank = True, null = True)    
    
    def parse_name_by_rack(self):
        ns = self.name
        r_num = int(ns.split('.')[1].split('r')[1])
        return r_num

    def parse_name_by_shelf(self):
        ns = self.name
        s_num = int(ns.split('.')[2].split('s')[1])
        return s_num

    def parse_name_by_box(self):
        ns = self.name
        b_num = int(ns.split('.')[3].split('b')[1])
        return b_num

    def get_count_sum(self):
        res_sum = StorageBox.objects.filter(box_name = self).count()
        return res_sum 
    
    def __unicode__(self):
        return u'%s (%s) - [%s]' % (self.name, self.description, self.shop)

    class Meta:
        ordering = ['-pk', 'shop', 'name']
        
 
class InventoryList(models.Model):
    catalog = models.ForeignKey(Catalog)
    count = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True) # create date
    edit_date = models.DateTimeField(auto_now_add=False, blank = True, null = True)
    description = models.TextField(blank = True, null = True)
    user = user = models.ForeignKey(User, blank=False, null=False)
    real_count = models.IntegerField()
    check_all = models.BooleanField(default=False, verbose_name="Загальна кількість?")
    chk_del = models.BooleanField(default=False, verbose_name="Мітка на видалення")
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин")
    box_id = models.ForeignKey(BoxName, blank=True, null=True, verbose_name="Місце знаходження")


    def save(self, **kwargs):
        #super().save(**kwargs)  # Call the "real" save() method.
        update_fields = kwargs.get("update_fields")
        update_fields = ["count"]
        if "count" in update_fields:
            if self.pk :
                obj = InventoryList.objects.values('count').get(pk=self.pk)
                sbox = StorageBox.objects.filter(catalog = self.catalog, box_name = self.box_id)
                if obj['count'] != self.count and sbox.count() > 0:
                    cc = int(self.count) - int(obj['count'])
#                    print "\nSBOX count diff - %s\n" % (cc)
                    #iobj = StorageBox.objects.get(pk = sbox[0].pk)
                    iobj = sbox[0]
                    iobj.count = iobj.count + cc
                    dnow = datetime.datetime.now()
                    if iobj.history:
                        iobj.history = iobj.history + "\n[%s] Change COUNT; Inventory id = %s; count = %s in %s" % (dnow, self.pk, iobj.count, self.catalog.get_realshop_count())
                    else:
                        iobj.history = "[%s] Change COUNT; Inventory id = %s; count = %s in %s" % (dnow, self.pk, iobj.count, self.catalog.get_realshop_count())
                    iobj.save()
        super(InventoryList, self).save(**kwargs)  # Call the "real" save() method.

    def delete(self, **kwargs):
        sbox = StorageBox.objects.filter(catalog = self.catalog, box_name = self.box_id)
        if sbox.count() > 0:
            iobj = sbox[0]
            iobj.count = iobj.count - self.count
            dnow = datetime.datetime.now()
            if iobj.history:
                iobj.history = iobj.history + "\n[%s] DELETE Inventory id = %s; count = %s in %s" % (dnow, self.pk, iobj.count, self.catalog.get_realshop_count())
            else:
                iobj.history = "[%s] DELETE Inventory id = %s; count = %s in %s" % (dnow, self.pk, iobj.count, self.catalog.get_realshop_count())
            iobj.save()
        super(InventoryList, self).delete(**kwargs)

    def get_last_year_check(self):
        nday = 360
        cur_date = datetime.datetime.now()
        if (self.check_all == True) and ( self.date > cur_date-datetime.timedelta(days=int(nday)) ):
             return True
        return False 

    def get_count_sum_by_year(self, year):
        sum = InventoryList.objects.filter(date__year = year).aggregate(count_sum = Sum('count'))
        return sum  

    def get_count_sum_by_cur_year(self):
        year = self.date.year
        sum = InventoryList.objects.filter(catalog = self.catalog, date__year = year).aggregate(count_sum = Sum('count'))
        return sum  

    def get_sale_count_by_cur_year(self):
        year = self.date.year
        sum = ClientInvoice.objects.filter(catalog = self.catalog, date__year = year).aggregate(count_sum = Sum('count'))        
        return sum

    def get_count_in_box(self):
        b_id = self.box_id
        sum = StorageBox.objects.filter(catalog = self.catalog, box_name = b_id).aggregate(count_sum = Sum('count'))
        return sum

    def get_count_in_all_boxes(self):
        sum = StorageBox.objects.filter(catalog = self.catalog)
        #print ""
        sum = sum.aggregate(count_sum = Sum('count'))
        return sum

    def get_all_boxes(self):
        sum = StorageBox.objects.filter(catalog = self.catalog)
#        sum = sum.aggregate(count_sum = Sum('count'))
        return sum

            
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
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин") 
    #storage_box = models.ManyToManyField(StorageBox, blank = True) 
            
    def get_uaprice(self, sdate=None):
        if sdate == None:
        #dn = self.date #
            dn = datetime.datetime.now()
        else:
            dn = sdate
            #dn = datetime.datetime.now()
        month = dn.month
        year = dn.year
        cur_exchange = Exchange.objects.filter(currency__ids_char = self.currency.ids_char, date__month = month, date__year = year).aggregate(average_val = Avg('value'))['average_val']
        if cur_exchange:
            ua = self.price * cur_exchange
        else:
            ua = self.price * 1
        return ua
    
    def ci_sum(self):
        ci = ClientInvoice.objects.filter(catalog = self.catalog).aggregate(Count('pk'), csum = Sum('sum'))
        return (ci['csum'], ci['pk__count'])

    def check_count(self):
        if self.count == self.rcount:
            return True
        else:
            return False
            
    def __unicode__(self):
        return u"%s - %s" % (self.invoice, self.catalog) 

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
    forumname = models.CharField(max_length=255, blank = True, null = True)
    country = models.ForeignKey(Country)
    city = models.CharField(max_length=255)
    email = models.CharField(max_length=100, blank = True, null = True)
    phone = models.CharField(max_length=100)
    phone1 = models.CharField(max_length=100, blank = True, null = True)
    sale = models.IntegerField("how many percent for sale", default=0)
    summ = models.FloatField()
    birthday = models.DateField(auto_now_add=False, blank = True, null = True)
    sale_on = models.BooleanField(default=True, verbose_name="Знижка включена")
    description = models.TextField(blank = True, null = True)
    reg_date = models.DateField(auto_now_add=True, blank = True, null = True)
    reg_shop = models.ForeignKey(Shop, blank=True, null=True)
    reg_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    #cashback = models.FloatField(default=0)
    #cashback_out_date = models.DateField(blank = True, null = True)
    #bicycle_service = 

    def show_str_phone1(self):
        str = self.phone[0:3] + '-' + self.phone[3:6] + '-' + self.phone[6:8]  + '-' + self.phone[8:]
        return str 

    def show_str_phone2(self):
        str = ''
        if self.phone1:
            str = self.phone1[0:3] + '-' + self.phone1[3:6] + '-' + self.phone1[6:8]  + '-' + self.phone1[8:]
        return str 

    def check_rent(self):
        if self.rent_set.filter(status = False):
            return True
        return False 
    
    def show_rent_html(self):
        str_list = []
        list = self.rent_set.filter(status = False)
        for item in list:
            str_list.append( item.catalog.get_code_name )
        return str_list

    def check_workticket(self):
        list = self.workticket_set.all()
        names = ["Ремонтується", "Виконано невидано", "На зберіганні", "Прийнято"]
        s_list = WorkStatus.objects.filter(name__in = names)
        status = False
        for t in list:
            if t.status in s_list:
                status = True
        return status

    def list_order_items(self):
        list = self.clientorder_set.filter(status = False)
        return list
    
    def __unicode__(self):
        return u"%s - [%s]" % (self.name, self.forumname)

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
    shop = models.ForeignKey(Shop, blank=True, null=True)    
    
    def __unicode__(self):
        return u"[%s] - %s (%s)" % (self.date, self.client, self.description)

    class Meta:
#        unique_together = ["client", "date", "price", "cash", "description"]
        ordering = ["client", "date"]    


#клієнтські проплати
class ClientCredits(models.Model):
    client = models.ForeignKey(Client)
    date = models.DateTimeField()
    price = models.FloatField()
    cash_type = models.ForeignKey(CashType, blank=True, null=True, on_delete=models.SET_NULL) 
    description = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    shop = models.ForeignKey(Shop, blank=True, null=True)

#old function
    def get_daily_pay_shop1(self):
        curdate = datetime.date.today()
        daySum = ClientCredits.objects.filter(date__year = curdate.year, date__month = curdate.month, date__day = curdate.day) #, date__gte = curdate)
        pay_lst = settings.SHOP1_PAY
        cash_list = daySum.filter(cash_type__pk__in = pay_lst)
        cashtype_sum_day = cash_list.values('cash_type__pk', 'cash_type__name').annotate(cash_sum=Sum('price'), cash_count=Count('price'))
        return [cash_list, cashtype_sum_day]
#old function
    def get_daily_pay_shop2(self):
        curdate = datetime.date.today()
        daySum = ClientCredits.objects.filter(date__year = curdate.year, date__month = curdate.month, date__day = curdate.day) #, date__gte = curdate)
        pay_lst = settings.SHOP2_PAY
        cash_list = daySum.filter(cash_type__pk__in = pay_lst)
        cashtype_sum_day = cash_list.values('cash_type__pk', 'cash_type__name').annotate(cash_sum=Sum('price'), cash_count=Count('price'))
        return [cash_list, cashtype_sum_day]
#old function
    def get_daily_term_shop1(self):
        curdate = datetime.date.today()
        daySum = ClientCredits.objects.filter(date__year = curdate.year, date__month = curdate.month, date__day = curdate.day) #, date__gte = curdate)
        pay_lst = settings.SHOP1_PAY_TERM
        print "\nPAY list 1 = " + str(pay_lst) + "\n"
        #cashtype_lst = CashType.objects.filter(pk__in = pay_lst)
        cash_list = daySum.filter(cash_type__pk__in = pay_lst)
        #cash_list = daySum.filter(cash_type__in = cashtype_lst)
        cashtype_sum_day = cash_list.values('cash_type__pk', 'cash_type__name').annotate(cash_sum=Sum('price'), cash_count=Count('price'))
        term_sum = cash_list.aggregate(all_sum = Sum('price'))
        return [cash_list, cashtype_sum_day, term_sum['all_sum']]
#old function
    def get_daily_term_shop2(self):
        curdate = datetime.date.today()
        daySum = ClientCredits.objects.filter(date__year = curdate.year, date__month = curdate.month, date__day = curdate.day) #, date__gte = curdate)
        pay_lst = settings.SHOP2_PAY_TERM
        print "\nPAY list 2 = " + str(pay_lst) + "\n"
        #cashtype_lst = CashType.objects.filter(pk__in = pay_lst)
        cash_list = daySum.filter(cash_type__pk__in = pay_lst)
        #cash_list = daySum.filter(cash_type__in = cashtype_lst)
        cashtype_sum_day = cash_list.values('cash_type__pk', 'cash_type__name').annotate(cash_sum=Sum('price'), cash_count=Count('price'))
        term_sum = cash_list.aggregate(all_sum = Sum('price'))        
        return [cash_list, cashtype_sum_day, term_sum['all_sum']]


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
#    pay_status = models.BooleanField(default = False)
    date = models.DateTimeField(auto_now_add = False)
#    date_update = models.DateTimeField(auto_now_add = False, blank=True, null=True)    
    description = models.TextField(blank = True, null = True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
#    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_create')
#    user_update = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_update')
    chk_del = models.BooleanField(default=False, verbose_name="Мітка на видалення")    
    shop = models.ForeignKey(Shop, blank=True, null=True)
    #storage_box = models.ManyToManyField(StorageBox, blank = True)   

    def update_sale(self):
        if (self.catalog.sale == 0) and (self.client.sale > self.catalog.sale):
            self.sale = self.client.sale
            self.sum = float(self.count) * ((1-(float(self.client.sale)/100.0)) * float(self.price))
            self.save()
        if (self.catalog.sale <> 0):
            self.sale = self.catalog.sale
            self.sum = self.count * ((1-(self.catalog.sale/100.0)) * self.price)
            self.save()
        return True

#its wrong check becouse math in float val not equal to pay field 
    def check_pay(self):
        sum = self.price * self.count * (100 - self.sale)*0.01
        if self.pay == sum :
            return True
        else:
            return False
        
    def check_payment(self):
        if self.sum == self.pay:
            return True
        else:
            return False

    def get_profit(self):
        profit = 0
        dn = self.date
        month = dn.month
        year = dn.year
        ua = 0
        cc = self.catalog.invoicecomponentlist_set.filter(price__gt = 0) #.aggregate(isum = Sum('price'), )
        if not cc:
            return (0, 0)
        #ic_count = cc.count() #aggregate(icount = Count('price'))['icount']
        ic_count = 0
        sum = 0
        for item in cc:
            sum = sum + item.get_uaprice(self.date) * item.count
            ic_count = ic_count + item.count
        if ic_count != 0:
            ua = sum / ic_count
        if (self.currency.ids_char == 'UAH'):
            try:
                percent_sale = (100-self.sale)*0.01
            except:
                percent_sale = (100-0)*0.01
                self.sale = 0
                self.save()
            profit = self.price * percent_sale * self.count - ua * self.count 
        #return cur_exchange1
        return (ua, profit)

    def get_client_profit(self):
        try:
            res = (self.price * self.count) * (self.sale/100.0)
        except:
            res = (self.price * self.count) * (0/100.0)
            
            self.sale = 0
            self.save()
        return res 
    
    def get_sale_price(self):
        return self.price * (100 - self.sale)*0.01

    def get_ci_sbox(self):
        res = ClientInvoiceStorageBox.objects.filter(cinvoice = self)
        res_list = []
        for i in res:
            try:
                st = u"Місце: %s - %s шт." % (i.sbox.box_name.name, i.count)
            except:
                st = u"Місце: Видалене!" 
            res_list.append(st)
        return res_list

    def save(self, **kwargs):
        update_fields = kwargs.get("update_fields")
        update_fields = ["count"]
        if "count" in update_fields:
            if self.pk :
                obj = ClientInvoice.objects.values('count').get(pk=self.pk)
                cat = Catalog.objects.get(pk = self.catalog.pk)
                if obj['count'] != self.count :
                    cc = int(self.count) - int(obj['count'])
                    cat.count = cat.count - cc
                    cat.save()
            else:
                cat = Catalog.objects.get(pk = self.catalog.pk)
                cc = int(self.count)
                cat.count = cat.count - cc
                cat.save()
                
        super(ClientInvoice, self).save(**kwargs)  # Call the "real" save() method.
 
    def delete(self, **kwargs):
        ci_sbox = ClientInvoiceStorageBox.objects.filter(cinvoice = self.pk)
        for i in ci_sbox:
            i.delete()
        cat = Catalog.objects.get(pk = self.catalog.pk)
        cat.count = cat.count - self.count
        cat.save() 
        super(ClientInvoice, self).delete(**kwargs)
                
    def __unicode__(self):
        return u"%s - %s шт." % (self.catalog.name, self.count) 
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
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин") 

    def get_item_name(self):
        res = ""
        if self.catalog:
            res = res + self.catalog.get_code_name
            #res = "Code "
        if self.description:
            res = res + self.description.encode('utf8')
        return res
            
    def __unicode__(self):
        return "%s (%s) - %s шт." % (self.catalog, self.description, self.count) 

    class Meta:
        ordering = ["status", "-date", "client"]    


#my costs (Затрати)
class CostType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def cost_list(self):
        res = self.costs.all().order_by('-date')[:10]
        return res

    def cost_list_sum(self):
        res = self.costs.all().aggregate(cost_sum = Sum('price'))
        return res['cost_sum']
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]    


class Costs(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    cost_type = models.ForeignKey(CostType, related_name='costs', default=3)
    price = models.FloatField()
    description = models.TextField()

    def __unicode__(self):
        #return self.name
        return u"[%s] (%s) - %s грн." % (self.date, self.description, self.price) 

    class Meta:
        ordering = ["date"]




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


#Bicycle parts table
class Bicycle_Parts(models.Model):
    name = models.CharField(max_length=255, blank=True)
    catalog = models.ForeignKey(Catalog, null=True, blank=True)
    type = models.ForeignKey(Type) #frame, bar, wheel ...
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'[%s] %s / %s' % (self.type, self.name, self.catalog)

    class Meta:
        ordering = ["type__bike_order"]    


# Bicycle model table (Bicycle)
class Bicycle(models.Model):
    model = models.CharField(max_length=255)
    type = models.ForeignKey(Bicycle_Type) #adult, kids, mtb, road, hybrid
    brand = models.ForeignKey(Manufacturer)
    year = models.DateField(blank = True, null=True)
    color = models.CharField(max_length=255)
    wheel_size = models.ForeignKey(Wheel_Size, blank=True, null=True) #20, 24, 26, 27.5, 29, 29+
#    sizes = models.CommaSeparatedIntegerField(max_length=10)
    sizes = models.ManyToManyField(FrameSize, blank=True)
    photo = models.ImageField(upload_to = 'upload/bicycle/', max_length=255, blank=True, null=True)
    photo_url = models.ManyToManyField(Photo, blank=True)
    offsite_url = models.URLField(blank=True, null=True)
    weight = models.FloatField()
    price = models.FloatField()
    currency = models.ForeignKey(Currency)
    sale = models.FloatField(default = 0, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    warranty = models.PositiveIntegerField(default = 12, blank=True)
    warranty_frame = models.PositiveIntegerField(default = 12)
    geometry = models.ImageField(upload_to = 'upload/bicycle/geometry/', max_length=255, blank=True, null=True)
    internet = models.BooleanField(default=False)
    youtube_url = models.ManyToManyField(YouTube, blank=True)
    bikeparts = models.ManyToManyField(Bicycle_Parts, blank=True)# name, catalog, part_type, order_num,  )
    rating = models.IntegerField(default = 0)
    country_made = models.ForeignKey(Country, null=True) 

    def youtube_val(self):
        res = []
        #qs = self.youtube_url.all()
        qs = self.youtube_url.all()
        try:
            qs = self.youtube_url.all()
#            q = qs.all()
            for i in qs:
                pars = parse_qs(urlparse(i.url).query)
                if pars:
                    res.append(pars['v'][0])
                else:
                    res.append(i.url.split('/')[3])
               #res.append(i.url.split('?v=')[1])
            return res 
            #return qs #self.youtube_url.split('/') #[3]
        except:
            return 'test None'

    def get_saleprice(self):
        percent_sale = (100-self.sale)*0.01
        price = self.price * percent_sale
        return price
        
    @property
    def photo_count(self):
        return self.photo_url.count()        

    def get_simple_name(self):
        return u'Велосипед %s. Модель %s. (%s)' % (self.brand, self.model, self.color)

    def __unicode__(self):
        #return u'Велосипед %s. Ціна %s грн.' % (self.model, self.brand)
        return u'Велосипед %s. Модель %s. %s (%s)' % (self.brand, self.model, self.year.year, self.color)
        
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
    realization = models.BooleanField(default=False,)
    date = models.DateField(auto_now_add=True) # create date
    description = models.TextField(blank=True, null=True)
    #invoice = models.CharField(max_length=255, blank = True, null = True)
    #dealer_id = models.CharField(max_length=60, blank = True, null = True)
    #status = models.BooleanField(default=False)  #box shop 
    #user_assembly = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин") 
    #checked date = models.DateField(auto_now_add=True) # Shop checked date
    #user_check_state = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    #user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def get_profit(self):
        profit = 0
        dn = datetime.datetime.now()
        month = dn.month
        year = dn.year
        cur_exchange = Exchange.objects.filter(currency__ids_char = self.currency.ids_char, date__month = month, date__year = year).aggregate(average_val = Avg('value'))['average_val']
        #cur_exchange2 = Exchange.objects.aggregate(average_val = Avg('value')) #annotate(avgval = Avg('value'))
        if cur_exchange:
            ua = self.price * cur_exchange
        else:
            ua = self.price * 1
        #ua = self.price * cur_exchange2['average_val'] #['value__avg']
        if (self.model.currency.ids_char == 'UAH'):
            percent_sale = (100-self.model.sale)*0.01
            profit = self.model.price * percent_sale - ua
        #return cur_exchange1
        return (cur_exchange, profit)

    def get_uaprice(self):
        dn = datetime.datetime.now()
        month = dn.month
        year = dn.year
        cur_exchange = Exchange.objects.filter(currency__ids_char = self.currency.ids_char, date__month = month, date__year = year).aggregate(average_val = Avg('value'))['average_val']
        #cur_exchange2 = Exchange.objects.aggregate(average_val = Avg('value')) #annotate(avgval = Avg('value'))
        if cur_exchange:
            ua = self.price * cur_exchange
        else:
            ua = self.price * 1
        return ua

    def get_saleprice(self):
        percent_sale = (100-self.model.sale)*0.01
        price = self.model.price * percent_sale
        return price

    def get_pb_chast3(self):
        chast = 0
        uaprice = self.get_uaprice()
        if self.model.sale == 0:
            chast = self.model.price / 3.0
        if self.model.sale > 0:
            pb_commission = self.get_saleprice() * (0.955 - 0.05)
            if pb_commission > uaprice:
                chast = self.get_saleprice() / 3.0
        return chast 

    def get_pb_chast4(self):
        chast = 0
        commission = 0
        uaprice = self.get_uaprice()
        if self.model.sale == 0:
            chast = self.model.price / 4.0
        if self.model.sale > 0:
            pb_commission = self.get_saleprice() * (0.935 - 0.05)
            if pb_commission > uaprice:
                chast = self.get_saleprice() / 4.0
        commission = self.get_saleprice() * (0.065)                 
        return (chast, commission) 

#    def get_photos(self):
#        return self.model.photo_set.all()

    def get_client(self):
        bsale = self.bicycle_sale_set.all()
        return bsale
    
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
    debt = models.ForeignKey(ClientDebts, blank=True, null=True)
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин") 

    def get_profit(self):
        profit = 0
        dn = self.date
        month = dn.month
        year = dn.year
        cur_exchange = Exchange.objects.filter(currency__ids_char = self.model.currency.ids_char, date__month = month, date__year = year).aggregate(average_val = Avg('value'))['average_val']
        #cur_exchange2 = Exchange.objects.aggregate(average_val = Avg('value')) #annotate(avgval = Avg('value'))
        if cur_exchange:
            ua = self.model.price * cur_exchange
        else:
            ua = self.model.price * 1
        #ua = self.price * cur_exchange2['average_val'] #['value__avg']
        if (self.currency.ids_char == 'UAH'):
            percent_sale = (100-self.sale)*0.01
            profit = self.price * percent_sale - ua
        #return cur_exchange1
        return (cur_exchange, profit)

    def get_uaprice(self):
        dn = self.date
        month = dn.month
        year = dn.year
        cur_exchange = Exchange.objects.filter(currency__ids_char = self.model.currency.ids_char, date__month = month, date__year = year).aggregate(average_val = Avg('value'))['average_val']
        #cur_exchange2 = Exchange.objects.aggregate(average_val = Avg('value')) #annotate(avgval = Avg('value'))
        if cur_exchange:
            ua = self.model.price * cur_exchange
        else:
            ua = self.model.price * 1
        return ua

    
    def __unicode__(self):
        #return self.model
        return u'%s' % (self.model)

    class Meta:
        ordering = ["-date", "client", "model", ]

        
# Bicycle ORDER for client
class Bicycle_Order(models.Model):
    client = models.ForeignKey(Client)
    model = models.ForeignKey(Bicycle)
    size = models.CharField(max_length=50)
    price = models.FloatField(default = 0)
    sale = models.IntegerField(default = 0)
    prepay = models.FloatField(default = 0)
    currency = models.ForeignKey(Currency)
    date = models.DateField(auto_now_add=True)
    done = models.BooleanField(default = False) 
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин")    

    #def convert_to_ua(self):
    
    def __unicode__(self):
        #return self.model
        return u'%s -> %s' % (self.client ,self.model)

    class Meta:
        ordering = ["-date", "client", "model"]

 
#Bicycle storage type table
class Storage_Type(models.Model):
    type = models.CharField(max_length=255) #adult, kids, mtb, road, hybrid
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)
 
    def __unicode__(self):
        return self.type
 
    class Meta:
        ordering = ["type"]    
 
 
class Bicycle_Storage(models.Model):
    client = models.ForeignKey(Client)
    model = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=150, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    wheel_size = models.ForeignKey(Wheel_Size, blank=True, null=True) #20, 24, 26, 27.5, 29, 29+
    biketype = models.ForeignKey(Bicycle_Type) #adult, kids, mtb, road, hybrid
    service = models.BooleanField(default = False)
    washing = models.BooleanField(default = False)
    type = models.ForeignKey(Storage_Type) #full time / 1,2 riding time / 1 month
    serial_number = models.CharField(max_length=50)
#    photo = models.ImageField(upload_to = 'media/upload/bicycle/storage/', max_length=255, blank=True, null=True)
#    album = models.models.ManyToManyField(Photo, blank=True) #ForeignKey(Bicycle_Client_Album, verbose_name=u'альбом', related_name='photos')
    date_in = models.DateField(auto_now_add=True)
    date_out = models.DateField(auto_now_add=True)
    done = models.BooleanField(default = False)
    date = models.DateTimeField(auto_now_add=True, editable=False)
    price = models.FloatField(blank=True, null=True)
    currency = models.ForeignKey(Currency, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)    
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин")  

    def __unicode__(self):
        return u'%s -> %s [%s]' % (self.client ,self.model, self.serial_number)
 
    def get_photos(self):
        return self.bicycle_photo_set.all()
 
    class Meta:
        ordering = ["client"]    


class Bicycle_Photo(models.Model):
    bicycle = models.ForeignKey(Bicycle_Storage, verbose_name=u'альбом')
    title = models.CharField(u'назва', max_length=200, blank=True, default='')
    image = models.ImageField(u'зображення', upload_to='upload/bicycle/storage/')    
    #image = files_widget.ImageField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s [%s]' % (self.bicycle.model, self.bicycle.serial_number)
 
    class Meta:
        ordering = ["bicycle"]    


class PhoneStatus(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]

            
class WorkGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    tabindex = models.IntegerField()

    def work_ingroup_count(self):
        r = WorkType.objects.filter(work_group = self).aggregate(work_count_sum = Count('pk'))
        #res = r.price + self.cash - self.price
        return r #int(round(res, 0))
    
    def __unicode__(self):
        return u'%s >>> %s' % (self.name, self.description)

    class Meta:
        ordering = ["name", "tabindex"]

     
class WorkType(models.Model):
    name = models.CharField(max_length=255)
    work_group = models.ForeignKey(WorkGroup)
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)
    disable = models.BooleanField(default = False, verbose_name="Відображення")
    component_type = models.ManyToManyField(Type, blank=True)
    dependence_work = models.ManyToManyField("self", blank=True)
    block = models.BooleanField(default = False, verbose_name="Блок/обєднання робіт")
    plus = models.BooleanField(default = False, verbose_name="Сума+")
    sale = models.FloatField(default = 0, blank=True, null=True)
    #timer = models.Datetime
    #user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def work_count(self):
        r = WorkShop.objects.filter(work_type = self).aggregate(work_count_sum = Count('pk'), work_sum=Sum('price'))#.latest('date')
        #res = r.price + self.cash - self.price
        return r #int(round(res, 0))

    def get_sale_price(self):
        #r = int(self.price or 1)/100 * (100 - int (self.sale or 1))
        r = int(self.price or 1)/100.0 * (100 - int(self.sale))
        base = 5
        return int(base * round(float(r)/base))

    def sum_depend_work(self):
        r = WorkType.objects.filter(dependence_work = self).aggregate(depend_sum=Sum('price'))
        return r 

    def d_json(self):
        return {
            'id': self.pk,
            'name': self.name,
            'price': self.price
            }

    def to_json(self):
        return {
            'id' : self.pk,
            'name' : self.name,
            'work_group': self.work_group.id,
            'price': self.price,
            'description': self.description,
            'disable': self.disable,
            'block': self.block,
            'plus': self.plus,
            'sale': self.sale,
            'dependence_work': ( [j.d_json() for j in self.dependence_work.all()] ) 
        }
    
    def __unicode__(self):
        #return u'Розділ %s. Робота: %s' % (self.work_group, self.name)
        return u'Робота: %s' % (self.name)
        #return self.name

    class Meta:
        ordering = ["work_group", "name"]


class WorkStatus(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
#    color = models.CharField(max_length=50, blank = True, null = True)
#    disable = models.BooleanField()
#    show_cur_month = models.BooleanField()
#    order = models.PositiveIntegerField(default = 0, verbose_name="Порядок сортування статусів. 0 - не сортувати")
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class WorkTicket(models.Model):
    client = models.ForeignKey(Client)
    date = models.DateField()
    end_date = models.DateField()
    status = models.ForeignKey(WorkStatus)
    phone_date = models.DateTimeField(blank=True, null=True)
    phone_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='p_user') 
    description = models.TextField(blank=True, null=True)
    phone_status = models.ForeignKey(PhoneStatus, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    estimate_time = models.PositiveIntegerField(default = 0, verbose_name="Прогнозований час в ГОДИНАХ") # Hours
    history = models.TextField(blank=True, null=True)
    bicycle = models.CharField(max_length=255, blank=True, null=True)
    bike_part_type = models.ForeignKey(Type, blank=True, null=True) 
#    bike_part = models.CharField(max_length=255, blank=True, null=True)
    #change_status_dateTime =
    #user_work 
    shop = models.ForeignKey(Shop, blank=True, null=True)

    def save(self, *args, **kwargs):
        str_history = ""
        if self.pk is not None:
            str_history = WorkTicket.objects.get(pk = self.pk)
            #print "\nHistory = " +  str(self.history.to_python(value))
        #str_history = self.history 
#        self.history = str_history.history + "<br>[" + str(self.user) + "] - [" + str(self.date) + "] - " +  self.status.name + "\n" 
        super(WorkTicket, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return u"[%s] Велосипед: %s - %s [%s] (%s)" % (self.date, self.bicycle, self.description, self.status, self.client) 
#        return "[%s](%s) Велосипед: %s - %s [%s] (%s)" % (self.date, self.user, self.bicycle, self.description, self.status, self.client)

    class Meta:
        ordering = ["date", "status"]
     
    
class WorkShop(models.Model):
    client = models.ForeignKey(Client)
    date = models.DateTimeField(auto_now_add=True)
    work_type = models.ForeignKey(WorkType)
    price = models.FloatField()
    pay = models.BooleanField(default = False, verbose_name="Оплачено?")
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин")  
    time = models.PositiveIntegerField(default = 0, verbose_name='Витрачено часу. (Хвилини)')
    ticket = models.ForeignKey(WorkTicket, blank = True, null = True, verbose_name = 'Заявка до якої відноситься робота')
    #bike = 
    #x price

    def check_depence_category(self):
        if self.work_type.component_type.exists():
            return True
        else:
            return False
    
    def __unicode__(self):
        return self.description

    class Meta:
        ordering = ["date", "client"]



class ShopDailySales(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    price = models.FloatField() #В касі на кінець дня
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=False, null=False)
    cash = models.FloatField(verbose_name = 'Готівка') #Готівка
    tcash = models.FloatField(verbose_name = 'Термінал') #Термінал
    ocash = models.FloatField(verbose_name = 'Видано з каси') #Взято з каси
    shop = models.ForeignKey(Shop, blank=True, null=True)
    #history
    #

    def day_sale(self):
        r = ShopDailySales.objects.filter(date__lt = self.date, shop = self.shop).latest('date')
        res = r.price + self.cash - self.price
        return int(round(res, 0))
    
    def __unicode__(self):
        return "[%s] - %s" % (self.date, self.price) 

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
    shop = models.ForeignKey(Shop, blank=True, null=True)
    #UID
    #url_dps
    #print_status
    #fiskal =
    
    def __unicode__(self):
        return u'%s / [%s / %s]' % (self.check_num, self.cash, self.term)

    class Meta:
        ordering = ["check_num"]    


# Check table (Check)
class Check(models.Model):
    #ids = models.CharField("code", unique=True, max_length=50)
    check_num = models.IntegerField("mini-fp")
    checkPay = models.ForeignKey(CheckPay, blank=True, null=True,  on_delete=models.CASCADE)
    client = models.ForeignKey(Client) #, on_delete=models.SET_NULL)
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
        return u'[%s] %s %s' % (self.check_num, self.catalog, self.bicycle)

    class Meta:
        ordering = ["date", "check_num"]    


#class Check_Registration(models.Model):
#    pass
#    class Meta:

# ----------  Perspective future function -------------------- 
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
    payment = models.BooleanField(default=False, verbose_name="Оплачено?")
    description = models.TextField(blank = True, null = True)
            
    def __unicode__(self):
        return self.file 

    class Meta:
        ordering = ["company", "manager", "date"]    


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
    shop_giving = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин видав", related_name='shop_give')
    shop_return = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин прийняв", related_name='shop_retun')
    user_return = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='ureturn')
                
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
    
    def del_zero(self):
        print "DELETE zero " + catalog.get_realshop_count()
        if catalog.get_realshop_count == 0:
            print "Catalog delete = " + str(catalog)
            #self.delete()    
        return True

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
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин") 
    
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
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name="Магазин") 
    
    def __unicode__(self):
        return u'%s' % self.msg

    class Meta:
        ordering = ["-date", "client"]


 
class StorageBox(models.Model):
    catalog = models.ForeignKey(Catalog)
    box_name = models.ForeignKey(BoxName, blank=True, null=True)
    count = models.IntegerField(default = 0, blank=True, null=True) #FloatField()
    count_real = models.IntegerField(default = 0, blank=True, null=True) #IntegerField()
    count_last = models.IntegerField(default = 0, blank=True, null=True) #IntegerField()
    shop = models.ForeignKey(Shop, blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add = False, blank=False, null=False)    
    date_update = models.DateTimeField(auto_now_add = False, blank=False, null=False)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_create')
    user_update = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_update')
    mark_del = models.BooleanField(default=False, verbose_name="Мітка на видалення")    
    history = models.TextField(blank = True, null = True)
    description = models.CharField(max_length=255, blank = True, null = True)   
#    price = models.FloatField(blank = True, null = True)
#    sale = models.IntegerField(blank = True, null = True, validators=[ MaxValueValidator(100), MinValueValidator(0) ]) 

    def diff_count_color(self):
        status = ""
        if self.count == self.count_real:
            status = "badge-success"
        if self.count != self.count_real:
            status = "badge-warning"
        if self.count > self.count_real:
            status = "badge-danger"
        return status  

    def count_zero_html(self):
        cssclass = ''
        if self.count == 0:
            cssclass = 'zero_class'
        return cssclass

    def get_storage_name(self):
        return u"%s - %s" % (self.box_name, self.description)

    def get_storage_boxes_name(self):
        s_boxes = {'box_name': self.box_name.name, 'box_id': self.box_name.id, 'box_desc': self.box_name.description, 'count': self.count, 'box_shop': self.box_name.shop.name, 'shop': self.shop.name, 'sb_desc': self.description, 's_box_id': self.id}
        return s_boxes

    
    def get_ci_sb(self):
        res = self.clientinvoicestoragebox_set.all()
#        res = self.clientinvoicestoragebox_set.filter(cinvoice = ci)
#        print "\nRES get_ci_sb = %s\n" % res
        return res

    def get_ci_sb_by_cinv(self, ci):
#        res = self.clientinvoicestoragebox_set.all()
        res = self.clientinvoicestoragebox_set.filter(cinvoice = ci)
#        print "\nRES get_ci_sb = %s\n" % res
        return res
         
    def __unicode__(self):
        return u'[%s] %s - %s з %s шт.' % (self.box_name, self.catalog, self.count, self.count_real)
 
    class Meta:
        ordering = ["-date_create", "box_name", "catalog"]


#===============================================================================
# class StorageBoxTransfer(models.Model):
#     sbox_from = models.ForeignKey(StorageBox, blank=True, null=True, on_delete = models.SET_NULL)
#     to_box = models.ForeignKey(BoxName, blank=True, null=True)
#     count = models.IntegerField(default = 0, blank=True, null=True) #FloatField()
#     count_real = models.IntegerField(default = 0, blank=True, null=True) #IntegerField()
#     count_last = models.IntegerField(default = 0, blank=True, null=True) #IntegerField()
#     
#     user_create = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL,)# related_name='u_create_cl')
# #    user_accept = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='u_accept_cl')
#     date_create = models.DateTimeField(blank=True, null=True)
#     date_accept = models.DateTimeField(blank=True, null=True)
# 
# 
#     def __unicode__(self):
#         return u'[%s] %s - %s з %s шт.' % (self.box_name, self.catalog, self.count, self.count_real)
#  
#     class Meta:
#         ordering = ["-date_create",] # "box_from", "box_to", "catalog"]
#===============================================================================
    

 
class ClientInvoiceStorageBox(models.Model):
    sbox = models.ForeignKey(StorageBox, blank=True, null=True, on_delete = models.SET_NULL)
    cinvoice = models.ForeignKey(ClientInvoice, on_delete = models.CASCADE)
    count = models.IntegerField()
#    date_create = models.DateTimeField(auto_now_add = False, blank=False, null=False) 
    user_create = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='u_create_cl')
    user_accept = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='u_accept_cl')
    date_create = models.DateTimeField(blank=True, null=True)
    date_accept = models.DateTimeField(blank=True, null=True)

    def set_count(self, count, date, user):
        self.count = count
        self.date_accept = date
        self.user_accept = user
        self.save()
        return True
      
    def save(self, **kwargs):
        #super().save(**kwargs)  # Call the "real" save() method.
        update_fields = kwargs.get("update_fields")
        update_fields = ["count"]
        if "count" in update_fields:
            if self.pk :
                obj = ClientInvoiceStorageBox.objects.values('count').get(pk=self.pk)
#                sbox = StorageBox.objects.filter(catalog = self.sbox.catalog, box_name = self.sbox.box_name)
                sbox = StorageBox.objects.filter(pk = self.sbox.pk)
                if obj['count'] != self.count and sbox.count() > 0:
                    cc = int(self.count) - int(obj['count'])
#                    print "\nSBOX count diff = %s\n" % (cc)
                    #iobj = StorageBox.objects.get(pk = sbox[0].pk)
                    iobj = sbox[0]
                    iobj.count_last = iobj.count
                    iobj.count = iobj.count + cc
                    dnow = datetime.datetime.now()
                    iobj.date_update = dnow
                    
                    if iobj.history:
                        iobj.history = iobj.history + "\n[%s] Change COUNT; Client Invoice id = %s; count = %s in %s; diff = %s" % (dnow, self.pk, iobj.count, self.sbox.catalog.get_realshop_count(), cc)
                    else:
                        iobj.history = "[%s] Change COUNT; Client Invoice id = %s; count = %s in %s; diff = %s" % (dnow, self.pk, iobj.count, self.sbox.catalog.get_realshop_count(), cc)
                    iobj.save()
                    res_save = super(ClientInvoiceStorageBox, self).save(**kwargs)  # Call the "real" save() method.
            else:
#                print "\n>> Create new CI_StorageBox <<x\n"
                res_save = super(ClientInvoiceStorageBox, self).save(**kwargs)  # Call the "real" save() method.
#                print "\nSELF ID = %s \n" % self.pk
                sbox = StorageBox.objects.filter(pk = self.sbox.pk)
                cc = int(self.count)
                iobj = sbox[0]
                iobj.count_last = iobj.count
                iobj.count = iobj.count - cc
                dnow = datetime.datetime.now()
                iobj.date_update = dnow
                if iobj.history:
                    iobj.history = iobj.history + "\n[%s] Change COUNT; Client Invoice id = %s; count = %s in %s; diff = -%s" % (dnow, self.pk, iobj.count, self.sbox.catalog.get_realshop_count(), cc)
                else:
                    iobj.history = "[%s] Change COUNT; Client Invoice id = %s; count = %s in %s; diff = -%s" % (dnow, self.pk, iobj.count, self.sbox.catalog.get_realshop_count(), cc)
                iobj.save()
                
        

    def delete(self, **kwargs):
        sbox = StorageBox.objects.get(pk = self.sbox.pk)
        sbox.count = sbox.count + self.count
        dnow = datetime.datetime.now()
        if sbox.history:
            sbox.history = sbox.history + "\n[%s] DELETE Client Invoice Storage Box id = %s; count = %s; Count SUM = %s" % (dnow, self.pk, self.count, self.sbox.catalog.get_realshop_count())
        else:
            sbox.history = "[%s] DELETE Client Invoice Storage Box id = %s; count = %s; Count SUM = %s" % (dnow, self.pk, sbox.count, self.sbox.catalog.get_realshop_count())
        sbox.save()
        super(ClientInvoiceStorageBox, self).delete(**kwargs)

 
    def __unicode__(self):
        return u'[%s] %s' % (self.sbox, self.cinvoice)
  
    class Meta:
        ordering = ["-date_create", "sbox", ]
     
          

#===============================================================================
# class StorageBoxLog(models.Model):
#     catalog = models.ForeignKey(Catalog)
# 
#     box = models.ForeignKey(StorageBox, blank = True, null = True, on_delete = models.SET_NULL)
#     add = models.ForeignKey(InvoiceComponentList, blank = True, null = True, on_delete = models.CASCADE)
#     remove = models.ForeignKey(ClientInvoice, blank = True, null = True, on_delete = models.CASCADE)
#     count = models.IntegerField()
#     user_create = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
# 
# 
# class StorageBoxTransition(models.Model):
#     sbox_from = models.ForeignKey(StorageBox, related_name='box_from')
#     sbox_to = models.ForeignKey(StorageBox, blank=True, null=True, related_name='box_send', on_delete=models.SET_NULL)
#     box_to = models.ForeignKey(BoxName, blank = True, null = True, on_delete = models.SET_NULL)
#     count_from = models.IntegerField()
#     count_to = models.IntegerField()
#     shop_to = models.ForeignKey(Shop, blank=True, null=True)
#     user_create = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_send')
#     user_accept = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_accept')
#     date_create = models.DateTimeField(auto_now_add = False, blank=True, null=True)
#     date_accept = models.DateTimeField(auto_now_add = False, blank=True, null=True)
# 
#     def __unicode__(self):
#         return u'%s >> %s / %s з %s шт.' % (self.sbox_from.box_name, self.sbox_to.box_name, self.catalog, self.count, self.sbox_from.count_real)
#  
#     class Meta:
#         ordering = ["-date_create", "sbox_from", "user_create"]
#===============================================================================
