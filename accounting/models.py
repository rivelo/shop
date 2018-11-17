# -*- coding: utf-8 -*-
from django.db import models
from django.forms import ModelForm
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Count, Sum
from django.db.models.aggregates import Avg
from datetime import datetime
from django.db.models import F

from urlparse import urlparse,parse_qs,urlunparse
from urllib import urlencode
import httplib

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
#    icon = models.ImageField(upload_to = 'upload/icon/', blank=True, null=True)
#    icon_select = models.ImageField(upload_to = 'upload/icon/', blank=True, null=True)
    
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
    #ukr_name = models.CharField(max_length=255)
    
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

#    def avg_currency(self):
#        self.filter(currency = self.currency).aggregate(average_val = Avg('value')) #annotate(avgval = Avg('value'))
#        return 
    
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
    www = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to = 'upload/brandlogo/', blank=True, null=True)
    country = models.ForeignKey(Country, null=True)
    description = models.TextField(blank=True, null=True)    
    
    def natural_key(self):
        return (self.id, self.name)
        
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ["name"]    


import os.path
import urllib2
from django.conf import settings

class Photo(models.Model):
    url = models.CharField(max_length=255)
    local = models.CharField(max_length=255, blank=True, null=True)
    www = models.URLField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)
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


# Main table 
class Catalog(models.Model):
    ids = models.CharField("code", unique=True, max_length=50)
    dealer_code = models.CharField("dealer code", max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255)
    manufacturer = models.ForeignKey(Manufacturer)
    type = models.ForeignKey(Type, related_name='type')
    size = models.ForeignKey(Size, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)    
    photo = models.FileField(upload_to = 'upload/catalog/%Y/', blank=True, null=True) # 'media/upload/catalog/%Y/%m/%d'
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
#    models.ManyToManyField() # field like sizechart, field to shoes
#    bike_style = models.ManyToManyField()  cyclocross, crosscountry, road, gravel ...
#    season = winter, summer, ...
    full_description = models.TextField(blank=True, null=True)
    youtube_url = models.ManyToManyField(YouTube, blank=True, null=True)
#    наявність у постачальника
    date = models.DateField(null=True, blank=True) #Строк придатності

    def get_saleprice(self):
        percent_sale = (100-self.sale)*0.01
        price = self.price * percent_sale
        return price

    def inv_price(self):
        usd = Currency.objects.get(pk=2)
        eur = Currency.objects.get(pk=4)
        uah = Currency.objects.get(pk=3)
        r = self.invoicecomponentlist_set.filter(price__gt = 0, currency = uah).values('currency').annotate(count_p=Count('currency'), sum_p=Sum('price'), count_s=Sum('count'))
        #r = self.invoicecomponentlist_set.filter(currency = eur).values('currency').annotate(count_p=Count('currency'), sum_p=Sum('price'))
        #r = self.invoicecomponentlist_set.filter(price__gt = 0, currency = usd).values('currency').annotate(count_p=Count('currency'), sum_p=Sum('price'))
        #r = self.invoicecomponentlist_set.filter(currency = uah).values('price', 'currency').annotate(sum_p=Sum('price'), count_p=Count('currency'))
        #values('price', 'currency')
        return r

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
            ic_count = ic_count + item.count
        if ic_count != 0:
            ua = sum / ic_count
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
            photos_list.append(self.photo)
        if self.photo_url:
            p_url = self.photo_url.all()
        for photo in p_url:
            if photo.local:
                photos_list.append(photo.local)
            if photo.url:
                photos_list.append(photo.url)
        if photos_list:
            return photos_list
        else:
            return False
            
        
    def _get_full_name(self):
        p = self.inv_price()
        cprice = p[0]['sum_p']/p[0]['count_s']
        if self.price < cprice:
            return "Ahtung!!!"
        return 'Price OK = ' + str(cprice)
    chk_price = property(_get_full_name) # Перевірка на правильність ціни

    
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

    def get_last_year_check(self):
        nday = 360
        cur_date = datetime.datetime.now()
        if (self.check_all == True) and ( self.date > cur_date-datetime.timedelta(days=int(nday)) ):
             return True

        return False 
            
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
    
    def __unicode__(self):
        return u"[%s] - %s (%s)" % (self.date, self.client, self.description)

    class Meta:
        unique_together = ["client", "date", "price", "cash", "description"]
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
#        cur_exchange = Exchange.objects.filter(currency__ids_char = self.currency.ids_char, date__month = month, date__year = year).aggregate(average_val = Avg('value'))['average_val']
        #cur_exchange2 = Exchange.objects.aggregate(average_val = Avg('value')) #annotate(avgval = Avg('value'))
#        if cur_exchange:
#            ua = self.catalog.price * cur_exchange
#        else:
#            ua = self.model.price * 1
        #ua = self.price * cur_exchange2['average_val'] #['value__avg']
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
            
    def __unicode__(self):
        return "%s (%s) - %s шт." % (self.catalog, self.description, self.count) 
        #return self.origin_id 

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


#Bicycle type table
class Bicycle_Type(models.Model):
    type = models.CharField(max_length=255) #adult, kids, mtb, road, hybrid
    ukr_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    level = models.IntegerField(default = 0, blank = True, null = True)
    parent_id = models.ForeignKey("self", blank=True, null = True, default=None)
    status = models.BooleanField(default = True, blank=True)

    def bike_count(self):
        res = self.bicycle_set.all().order_by('pk').aggregate(bike_sum = Count('pk'))
        return res['bike_sum']
    
    def subtype_count(self):
        res = self.bicycle_type_set.all().order_by('pk').aggregate(bike_sum = Count('pk'))
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


# Bicycle table (Bicycle)
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
    internet = models.BooleanField(default=False,)
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
        
    @property
    def photo_count(self):
        return self.photo_url.count()        

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
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

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

#    def get_photos(self):
#        return self.model.photo_set.all()

    def get_saleprice(self):
        percent_sale = (100-self.model.sale)*0.01
        price = self.model.price * percent_sale
        return price

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
    #debt = models.ForeignKey(ClientDebts, blank=True, null=True, on_delete=models.SET_NULL)
    debt = models.ForeignKey(ClientDebts, blank=True, null=True)

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

    def work_count(self):
        r = WorkShop.objects.filter(work_type = self).aggregate(work_count_sum = Count('pk'), work_sum=Sum('price'))#.latest('date')
        #res = r.price + self.cash - self.price
        return r #int(round(res, 0))

    def get_sale_price(self):
        r = self.price/100 * (100 - self.sale)
        base = 5
        return int(base * round(float(r)/base)) 

    def sum_depend_work(self):
        r = WorkType.objects.filter(dependence_work = self).aggregate(depend_sum=Sum('price'))
        return r 
    
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
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    
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
    phone_date = models.DateTimeField(blank=True, null=True)
    phone_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='p_user') 
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

    def day_sale(self):
        r = ShopDailySales.objects.filter(date__lt = self.date).latest('date')
        res = r.price + self.cash - self.price
        return int(round(res, 0))
    
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
    payment = models.BooleanField(default=False, verbose_name="Оплачено?")
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
    