# -*- coding: utf-8 -*-
from django.db.models import Q
from django.db.models import F
from django.db import connection
from django.db.models import Sum, Count, Max, Avg
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear

from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.http import HttpResponse, Http404 
from django.http import JsonResponse
from django.http import QueryDict

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.core.urlresolvers import resolve

from django.shortcuts import render_to_response, redirect, render

from django.contrib.auth.models import Group
from django.contrib import auth

from django.template import RequestContext

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.utils.text import slugify

from django.urls import reverse

from models import Manufacturer, Country, Type, Currency, Bicycle_Type, Bicycle,  FrameSize, Bicycle_Store, Bicycle_Sale, Bicycle_Order, Bicycle_Storage, Bicycle_Photo, Storage_Type, Bicycle_Parts
from models import Catalog, Client, ClientDebts, ClientCredits, ClientInvoice, ClientOrder, ClientMessage, ClientReturn, InventoryList
from models import Dealer, DealerManager, DealerManager, DealerPayment, DealerInvoice, InvoiceComponentList, Bank, Exchange, PreOrder, CashType, Discount, Shop
from models import WorkGroup, WorkType, WorkShop, WorkStatus, WorkTicket, CostType, Costs, ShopDailySales, Rent, ShopPrice, Photo, WorkDay, Check, CheckPay, PhoneStatus, YouTube
from models import CatalogAttributeValue, CatalogAttribute, BoxName, StorageBox, ClientInvoiceStorageBox 

from forms import CatalogForm, ClientForm, ClientDebtsForm, ClientCreditsForm, ClientInvoiceForm, ClientOrderForm, ClientEditForm, BoxNameForm, BoxNameEditForm, InventoryListForm
from forms import ManufacturerForm, CountryForm, CurencyForm, CategoryForm, BicycleTypeForm, BicycleForm, BicycleFrameSizeForm, BicycleStoreForm, BicycleSaleForm, BicycleOrderForm, BicycleStorage_Form, StorageType_Form
from forms import DealerManagerForm, DealerForm, DealerPaymentForm, DealerInvoiceForm, InvoiceComponentListForm, BankForm, ExchangeForm, PreOrderForm, InvoiceComponentForm, CashTypeForm, DiscountForm 
from forms import WorkGroupForm, WorkTypeForm, WorkShopForm, WorkStatusForm, WorkTicketForm, CostTypeForm, CostsForm, ShopDailySalesForm, RentForm, WorkDayForm, ImportDealerInvoiceForm, ImportPriceForm, PhoneStatusForm, WorkShopFormset, SalaryForm
  
import datetime
import calendar
import codecs
import csv
import re
import math
import simplejson, json
import pytils_ua
import urllib
import StringIO, requests, os

from PIL import Image
from urlparse import urlsplit
from _mysql import NULL
from django.template.context_processors import request


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    date = datetime.datetime.now()
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR'],
        'shop_name': get_shop_from_ip(request.META['REMOTE_ADDR']),
#        'shop_name': get_shop_from_ip('192.168.1.1'),
#        'shop_name': get_shop_from_ip('10.0.0.1'),
        'year_now': date.year,
        'month_now': date.month,
        'day_now': date.day,
        'local_server': settings.LOCAL_TEST_SERVER,
    }

# CHANGE MONTH in datetime
def add_months(date, months):
    new_date = None
    month = date.month + months - 1
    year = date.year + (month / 12)
    month = (month % 12) + 1
    day = date.day
    day = 1
    while (day > 0):
        try:
            new_date = date.replace(year=year, month=month, day=day)
            break
        except:
            day = day - 1    
    return new_date


def sub_months(date, months):
    new_date = None
    month = (date.month - months) - 1
    #month = (date.month - months + 12) - 1
    year = date.year - abs(month / 12 )#/ date.month)
    #year = date.year - (date.month + months) / 12
    month = (month % 12) + 1
    day = date.day
    day = 1
    while (day > 0):
        try:
            new_date = date.replace(year=year, month=month, day=day)
            break
        except:
            day = day - 1    
    return new_date
# end - CHANGE MONTH in datetime

@csrf_exempt
def login(request):
    message = "AJAX"
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('user'):
                user = request.POST.get('user')
            if POST.has_key('password'):
                password = request.POST.get('password')
            user = auth.authenticate(username=user, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponse(simplejson.dumps({'response': message, 'result': 'success'}))
            else:
                return HttpResponse(simplejson.dumps({'response': message, 'result': 'error'}))
        
    username = request.POST['username']
    password = request.POST['password']
    next = request.POST['next']
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Правильный пароль и пользователь "активен"
        auth.login(request, user)
        # Перенаправление на "правильную" страницу
        if next:
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect("/.")            
    else:
        # Отображение страницы с ошибкой
        
            #return HttpResponse(simplejson.dumps(TheStory), content_type="application/json")
        if next:
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect("/.")            

@csrf_exempt
def logout(request):
    auth.logout(request)
    next_page = request.POST['next_page']
    return HttpResponseRedirect("/")

    
def auth_group(user, group):
    if user.groups.filter(name=group).exists():
        return True
    return False
    #return True if user.groups.filter(name=group) else False

#check from SETTING file
def check_ip(ip_addr):
    ip = '.'.join(ip_addr.split('.')[0:3])
    #request.META['REMOTE_ADDR']
    dict_shop  = settings.SHOPS
    for shop in dict_shop.keys():
        if dict_shop[shop] == ip:
            return shop
    else:
        return "----"

#check from DB table
def get_shop_from_ip(ip_addr):
    ip = '.'.join(ip_addr.split('.')[0:3])
    dict_shop = Shop.objects.filter( ip_addr__contains = ip )
#    print "\nIP = " + str(ip) + " >>>>> dict_shop" + str(dict_shop) 
    if dict_shop.first():
        return dict_shop.first()
    else:
        return Shop()
        #return "----"


def get_shop_from_request(request):
    ip_addr = request.META['REMOTE_ADDR']
    ip = '.'.join(ip_addr.split('.')[0:3])
    dict_shop = Shop.objects.filter( ip_addr__contains = ip )
    if dict_shop.first():
        return dict_shop.first()
    else:
        context = {'weblink': 'error_message.html', 'mtext': 'Магазин не ідентифікований у таблиці магазинів', }
        context.update(custom_proc(request))
        list_res = (request, 'index.html', context)
        return list_res
        #return render(request, 'index.html', context)


def current_url(request):
    return request.get_full_path()


# old function
def search(request):
    query = request.GET.get('q', '')
    if query:
        qset = (
            Q(name__icontains=query)
        )
        results = Manufacturer.objects.filter(qset).distinct()
    else:
        results = []
    return render_to_response("search.html", {
        "results": results,
        "query": query
    })


from django.views.generic import ListView

class PhoneStatusListView(ListView):
    model = PhoneStatus
    
#    template_name = 'index.html'
#    context_object_name = 'latest_question_list'

#    def get_queryset(self):
#        """Return the last five published questions."""
#        return Coutry.objects.order_by('-name')[:10]




def del_logging(obj):
    file_name = 'test_log'
    log_path = settings.MEDIA_ROOT + 'logs/' + file_name + '.log'
    log_file = open(log_path, 'a')
    log_file.write("%s >>> DELETE FROM TABLE %s WHERE id = %s \n" % (str(datetime.datetime.now()), obj._meta.verbose_name, obj.id) )
        
    for f in obj._meta.fields:
        log_file.write("Key = " + f.name + " - ") # field name
        s = "Value = %s" % f.value_from_object(obj) + "\n"
        log_file.write(s.encode('utf-8'))
        #log_file.write("Value = %s" % f.value_from_object(obj).encode('cp1251') + "\n") # field value
            
    #log_file.write("DELETE FROM TABLE " + table_name + obj.name)
    log_file.close()



def send_shop_mail(request, mto, w, subject='Наявний товар'):
    from_email = 'rivelo@ukr.net' #'rivelo@ymail.com' 
    to = mto
    text_content = 'www.rivelo.com.ua'
    html_content = w.content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return True #render_to_response("index.html", {'success_data': "Лист відправлено на пошту" + to}, context_instance=RequestContext(request, processors=[custom_proc]))

#old function
#===============================================================================
# def prev_url(request):
#     #referer = request.META.get('HTTP_REFERER', None)
#     referer = request.META['HTTP_REFERER']
#     if referer is None:
#         pass
#          # do something here
#     try:
#         #redirect_to = urlsplit(referer, 'http', False)[2]
#         redirect_to = refer
#     except IndexError:
#         pass
#          # do another thing here
#     return redirect_to
#===============================================================================


#----- Main Page -------------------
def main_page(request):
    if request.user.is_authenticated():
        category_list = Type.objects.filter(ico_status = True)
        context = {"cat_list": category_list, "weblink": 'index_.html'}
        context.update(custom_proc(request))
        return render(request, 'index.html', context) 
    else:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу. Авторизуйтеся або зверніться до адміністратора.', }
        #context = {"weblink": 'top.html'}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)


# ------------ Country -----------------
def country_add(request):
    a = Country()
    current_url = request.get_full_path()
    if request.method == 'POST':
        form = CountryForm(request.POST, instance=a)
        if form.is_valid():
            name = form.cleaned_data['name']
            Country(name=name).save()
            return HttpResponseRedirect('/country/view/')
    else:
        form = CountryForm(instance = a)
    return render_to_response('index.html', {'form': form, 'weblink': 'country.html', 'next': current_url}, context_instance=RequestContext(request, processors=[custom_proc]))


def country_del(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/country/view/')
    obj = Country.objects.get(id=id)
    del_logging(obj)
    obj.delete() 
    return HttpResponseRedirect('/country/view/')


def country_edit(request, id):
    a = Country.objects.get(pk=id)
    current_url = request.get_full_path()
    if request.method == 'POST':
        form = CountryForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/country/view/')
    else:
        form = CountryForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'country.html', 'next': current_url}, context_instance=RequestContext(request, processors=[custom_proc]))


def country_list(request):
    current_url = request.get_full_path()
    list = Country.objects.all()
    #return render_to_response('country_list.html', {'countries': list})
    context = {'countries': list, 'weblink': 'country_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


# ----------------- Bank --------------------

def bank_add(request):
    a = Bank()
    if request.method == 'POST':
        form = BankForm(request.POST, instance=a)
        if form.is_valid():
            name = form.cleaned_data['name']
            Bank(name=name).save()
            return HttpResponseRedirect('/bank/view/')
    else:
        form = BankForm(instance=a)
    #return render_to_response('bank.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'bank.html', 'text': 'Додати новий банк', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bank_edit(request, id):
    a = Bank.objects.get(pk=id)
    if request.method == 'POST':
        form = BankForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/bank/view/')
    else:
        form = BankForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'bank.html', 'text': 'Редагувати банк', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bank_del(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/bank/view/')
    obj = Bank.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bank/view/')
    

def bank_list(request):
    list = Bank.objects.all()
    #return render_to_response('bank_list.html', {'banks': list})
    return render_to_response('index.html', {'banks': list, 'weblink': 'bank_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


#--- cash type ---
@csrf_exempt
def cashtype_list(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            list = CashType.objects.all().values_list('id', 'name')
            
            dictionary = {}
            for el in list:
                str = unicode(el[1])
                dictionary[el[0]] = str
            dictionary['selected'] = request.POST['sel']
            json = simplejson.dumps(dictionary)
            return HttpResponse(json, content_type='application/json')            

    list = CashType.objects.all()
    context = {'list': list, 'weblink': 'cashtype_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def cashtype_add(request):
    a = CashType()
    if request.method == 'POST':
        form = CashTypeForm(request.POST, instance=a)
        if form.is_valid():
#            name = form.cleaned_data['name']
#            description = form.cleaned_data['description']
#            CashType(name=name, description=description).save()
            form.save()
            return HttpResponseRedirect('/cashtype/view/')
    else:
        form = CashTypeForm(instance=a)
    context = {'form': form, 'weblink': 'cashtype.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def cashtype_del(request, id):
    if auth_group(request.user, "admin") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для видалення/редагування ', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)    
#    if auth_group(request.user, 'admin')==False:
#        return HttpResponseRedirect('/cashtype/view/')
    obj = CashType.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/cashtype/view/')

@csrf_exempt
def cashtype_edit(request, id):
    a = CashType.objects.get(pk=id)
    if request.method == 'POST':
        form = CashTypeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/cashtype/view/')
    else:
        form = CashTypeForm(instance=a)
    context = {'form': form, 'weblink': 'cashtype.html', }
    context.update(custom_proc(request))        
    return render(request, 'index.html', context)

# ----------- Bicycle --------------
@csrf_exempt
def bicycle_type_add(request):
    a = Bicycle_Type()
    if request.method == 'POST':
        form = BicycleTypeForm(request.POST, instance=a)
        if form.is_valid():
            type = form.cleaned_data['type']
            description = form.cleaned_data['description']
            Bicycle_Type(type=type, description=description).save()
            return HttpResponseRedirect('/bicycle-type/view/')
    else:
        form = BicycleTypeForm(instance=a)
    #return render_to_response('bicycle_type.html', {'form': form})
    context = {'form': form, 'weblink': 'bicycle_type.html', }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def bicycle_type_edit(request, id):
    a = Bicycle_Type.objects.get(pk=id)
    if request.method == 'POST':
        form = BicycleTypeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/bicycle-type/view/')
    else:
        form = BicycleTypeForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_type.html', 'text': 'Редагувати тип', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_type_del(request, id):
    if auth_group(request.user, 'admin') == False:
        return HttpResponseRedirect('/bicycle-type/view/')
    obj = Bicycle_Type.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle-type/view/')


def bicycle_type_list(request):
    list = Bicycle_Type.objects.all()
    context = {'types': list, 'weblink': 'bicycle_type_list.html', }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_framesize_add(request):
    a = FrameSize()
    if request.method == 'POST':
        form = BicycleFrameSizeForm(request.POST, instance=a)
        if form.is_valid():
#            name = form.cleaned_data['name']
#            cm = form.cleaned_data['cm']
#            inch = form.cleaned_data['inch']
            #FrameSize(name=name, cm=cm, inch=inch).save()
            form.save()
            return HttpResponseRedirect('/bicycle-framesize/view/')
    else:
        form = BicycleFrameSizeForm(instance=a)
    context = {'form': form, 'weblink': 'bicycle_framesize.html', 'text': 'Створення нового розміру рами'}
    context.update(custom_proc(request))   
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_framesize_edit(request, id):
    a = FrameSize.objects.get(pk=id)
    if request.method == 'POST':
        form = BicycleFrameSizeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/bicycle-framesize/view/')
    else:
        form = BicycleFrameSizeForm(instance=a)
    context = {'form': form, 'weblink': 'bicycle_framesize.html', 'text': 'Розмір рами (редагування)'} 
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def bicycle_framesize_del(request, id):
    if auth_group(request.user, 'admin') == False:
        #return HttpResponseRedirect('/bicycle-framesize/view/')
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для видалення. Авторизуйтеся або зверніться до адміністратора.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    obj = FrameSize.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle-framesize/view/')


def bicycle_framesize_list(request):
    list = FrameSize.objects.all()
    #return render_to_response('bicycle_framesize_list.html', {'framesizes': list.values_list()})
    context = {'framesizes': list, 'weblink': 'bicycle_framesize_list.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def framesize_lookup(request):
    data = None
    if request.is_ajax():
#        print "\n>>> AJAX WORK AJAX <<<" + str(data) 
        if request.method == "POST":
            if request.POST.has_key(u'query'):
                value = request.POST[u'query']
                if len(value) > 2:
                    model_results = FrameSize.objects.filter(Q(name__icontains = value) | Q(description__icontains = value)).order_by('name', 'letter')
    #                data = serializers.serialize("json", model_results, fields = ('id', 'name', 'cm', 'inch', 'letter') )
                else:
                    model_results = Type.objects.all().order_by('name')
#                    data = serializers.serialize("json", model_results, fields = ('id', 'name', 'cm', 'inch', 'letter') )
            if request.POST.has_key(u'id'):
                value = request.POST[u'id']
#                print "\n>>> WORK - ID <<<" + str(data) + " | " + str(value)
                model_results = FrameSize.objects.filter( Q(pk = value) ).order_by('name')
                #data = serializers.serialize("json", model_results, fields = ('id', 'name_ukr', 'name') )
    data = serializers.serialize("json", model_results, fields = ('id', 'name', 'cm', 'inch', 'letter') )                
    return HttpResponse(data)         


def processUploadedImage(file, dir=''): 
#    img = Image.open(file) 
#    downsampleUploadedimage(img) 
#    stampUploadedImage(img) 
#    img.save(file, "JPEG") 
    upload_suffix = 'upload/' + dir + file.name
    upload_path = settings.MEDIA_ROOT + 'upload/' + file.name
        
    destination = open(settings.MEDIA_ROOT + 'upload/'+ dir + file.name, 'wb+')
    #destination = open('/media/upload/'+file.name, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()        
    return upload_suffix

#===============================================================================
# 
# def image_view(request):
#     a = Bicycle()
#     if request.method == 'POST':
#         form = BicycleForm(request.POST, instance=a)
#         if form.is_valid():
# #            name = form.cleaned_data['name']
# #            cm = form.cleaned_data['cm']
# #            inch = form.cleaned_data['inch']
#             Bicycle(name=name, cm=cm, inch=inch).save()
#     
#             return HttpResponseRedirect('/bicycle/view/list/')
#     else:
#         form = BicycleForm(instance=a)
#     
#     items = Bicycle.objects.all()
#     return render_to_response('bicycle.html', {'bicycles':items, 'form': form})
# 
# 
# def multiuploader(request):
#     if request.method == 'POST':
#         if request.FILES == None:
#             return HttpResponseBadRequest('Must have files attached!')
# 
#         #getting file data for farther manipulations
#         file = request.FILES[u'files[]']
#         wrapped_file = UploadedFile(file)
#         filename = wrapped_file.name
#         file_size = wrapped_file.file.size
# 
#         #writing file manually into model
#         #because we don't need form of any type.
#         image = Bicycle()
#         image.title=str(filename)
#         image.photo=file
#         image.save()
# 
#         #getting url for photo deletion
#         file_delete_url = '/delete/'
#         
#         #getting file url here
#         file_url = '/'
# 
#         #getting thumbnail url using sorl-thumbnail
#         im = get_thumbnail(image, "80x80", quality=50)
#         thumb_url = im.url
# 
#         #generating json response array
#         result = []
#         result.append({"name":filename, 
#                        "size":file_size, 
#                        "url":file_url, 
#                        "thumbnail_url":thumb_url,
#                        "delete_url":file_delete_url+str(image.pk)+'/', 
#                        "delete_type":"POST",})
#         response_data = simplejson.dumps(result)
#         return HttpResponse(response_data, mimetype='application/json')
#     else: #GET
#         return render_to_response('bicycle.html', 
#                                   {'static_url':settings.MEDIA_URL,
#                                    'open_tv':u'{{',
#                                    'close_tv':u'}}'}, 
#                                   )
#         
# 
# def multiuploader_delete(request, pk):
#     if request.method == 'POST':
#         image = get_object_or_404(Bicycle, pk=pk)
#         image.delete()
#         return HttpResponse(str(pk))
#     else:
#         return HttpResponseBadRequest('Only POST accepted')
#     
#===============================================================================

def bicycle_part_add(request):
    if (auth_group(request.user, 'seller') or auth_group(request.user, 'admin')) == False:
        response = JsonResponse({'error': "У вас не вистачає повноважень або ви не авторизувались в системі"})
        return response
    a = None
    bp = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if (POST.has_key('s_cat_id') or POST.has_key('s_name')) and POST.has_key('s_type') and POST.has_key('id'):                
                bid = request.POST['id']
                cat_id = None
                if POST.has_key('s_cat_id'):
                    cat_id = request.POST['s_cat_id']
                s_name = request.POST['s_name']
                s_type = request.POST['s_type']
                s_desc = request.POST['s_desc']
                d = {}
                if s_name or cat_id:
                    try:
                        bp_name = None
                        a = Bicycle.objects.get(pk = bid)
                        if s_name:
                            bp_name = s_name
                            bp = Bicycle_Parts.objects.filter(type = s_type).get(name = bp_name)
                        print "OBJECT = " + str(bp_name) + "CAT id = " + str(cat_id)
                        if cat_id:
                            bp_name = cat_id
                            bp = Bicycle_Parts.objects.filter(type = s_type).get(catalog = bp_name)
                        print "OBJECT = " + str(bp_name)
                        #    bp = Bicycle_Parts.objects.filter(type = s_type).get(catalog = bp_name)
                        a.bikeparts.add(bp)
                        a.save()
                        d['pk'] = bp.pk
                        d['cat'] = str(bp.catalog)
                        d['type'] = str(bp.type)
                        d['status'] = True
                        d['msg'] = 'Такий компонент вже існує.'
                        d['error'] = 'Такий компонент вже існує. Вибрати його?'
                    except Bicycle_Parts.DoesNotExist:
                        print "CAT = " + str(cat_id)
                        catalog = None
                        type = None
                        if s_type:
                            type = Type.objects.get(pk = s_type)
                        else:
                            d['status'] = False
                        if cat_id:
                            catalog = Catalog.objects.get(pk = cat_id)
                            bp = Bicycle_Parts.objects.create(name = s_name, catalog = catalog, type = type, description = s_desc)
                            d['status'] = True
                        else:
                            catalog = Catalog
                            bp = Bicycle_Parts.objects.create(name = s_name, type = type, description = s_desc)
                            d['status'] = True
                            
                        #bp = Bicycle_Parts.objects.create(name = s_name, catalog = catalog, type = type, description = s_desc)
                        a.bikeparts.add(bp)
                        a.save()
                        #d['status'] = True
                        d['pk'] = bp.pk
                        d['cat'] = str(bp.catalog)
                        d['type'] = str(bp.type)
                        d['desc'] = bp.description
                    except Bicycle.DoesNotExist:
                        d['status'] = False
                        d['error'] = "такого велосипеду не існує"
                    except Bicycle_Parts.MultipleObjectsReturned:
                        d['status'] = False
                        d['error'] = "Таких компонентів є більше ніж один. Видаліть дублікати."
            else:
                response = JsonResponse({'error': "Невірні параметри запиту"})
                return response
    
            response = JsonResponse(d)
            return response            
    
@csrf_exempt
def bicycle_add(request):
    if (auth_group(request.user, 'seller') or auth_group(request.user, 'admin')) == False:
        return HttpResponseRedirect('/bicycle/view/')
#    a = Bicycle()    
    if request.method == 'POST':
#        form = BicycleForm(request.POST, request.FILES, instance=a)
        form = BicycleForm(request.POST, request.FILES)        
        if form.is_valid():
            model = form.cleaned_data['model']
            type = form.cleaned_data['type']
            brand = form.cleaned_data['brand']
            color = form.cleaned_data['color']
            year = form.cleaned_data['year']
            weight = form.cleaned_data['weight']
#            sizes = form.cleaned_data['sizes']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            description = form.cleaned_data['description']
            sale = form.cleaned_data['sale']
            offsite_url = form.cleaned_data['offsite_url']
            photo = form.cleaned_data['photo']  
            wheel_size = form.cleaned_data['wheel_size']
            country_made = form.cleaned_data['country_made']
            rating = form.cleaned_data['rating']
            warranty = form.cleaned_data['warranty']
            geometry = form.cleaned_data['geometry']
            country_made = form.cleaned_data['country_made']
            internet = form.cleaned_data['internet']
                      
            folder = year.year
            upload_path_p = ''
            if photo == None:
                upload_path_p = None
            if isinstance(photo, InMemoryUploadedFile):
                upload_path_p = processUploadedImage(photo, 'bicycle/'+str(folder)+'/') 
                #a.photo=upload_path_p
            gfolder = year.year
            upload_path_g = ''
            if geometry == None:
                upload_path_g = None
            if isinstance(geometry, InMemoryUploadedFile):
                upload_path_g = processUploadedImage(geometry, 'geometry/'+str(gfolder)+'/')
                
            Bicycle(model = model, type=type, brand = brand, color = color, photo=upload_path_p, weight = weight, wheel_size = wheel_size, price = price, currency = currency, internet = internet, country_made = country_made, warranty = warranty, geometry = upload_path_g, offsite_url=offsite_url, description=description, year=year, sale=sale).save()
#            form.save() #_m2m()
            return HttpResponseRedirect('/bicycle/view/')
            #return HttpResponseRedirect(bicycle.get_absolute_url())
    else:
#        form = BicycleForm(instance=a)
        form = BicycleForm()        

    context = {'form': form, 'weblink': 'bicycle.html', 'text': 'Велосипед з каталогу (створення)'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_edit(request, id):
    if (auth_group(request.user, 'seller') or auth_group(request.user, 'admin')) == False:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))
        #return HttpResponseRedirect('/bicycle/view/')
    a = Bicycle.objects.get(pk=id)
    url_youtube = None
    if request.method == 'POST':
        form = BicycleForm(request.POST, request.FILES, instance=a)
        if form.is_valid():
            year = form.cleaned_data['year']
            photo = form.cleaned_data['photo']            
            #url_youtube = form.cleaned_data['upload_youtube']
            folder = year.year
            upload_path_p = ''
            if photo == None:
                upload_path_p = None
            if isinstance(photo, InMemoryUploadedFile):
                upload_path_p = processUploadedImage(photo, 'bicycle/'+str(folder)+'/') 
                a.photo=upload_path_p
                a.save()
            form.save()
            if request.POST.has_key('upload_youtube'):
                url_youtube = request.POST.get('upload_youtube')
                if url_youtube :
                    try:
                        y = YouTube.objects.get(url = url_youtube)
                        a.youtube_url.add(y)
                        a.save()
                    except YouTube.DoesNotExist:
                        add_tube = YouTube.objects.create(url = url_youtube, user = request.user)
                        a.youtube_url.add(add_tube)
                        a.save()
                         
            return HttpResponseRedirect('/bicycle/view/')
    else:
        form = BicycleForm(instance=a)
    context = {'form': form, 'weblink': 'bicycle.html', 'text': 'Велосипед з каталогу (редагування)'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def bicycle_del(request, id):
    if auth_group(request.user, 'admin') == False:
        return HttpResponseRedirect('/bicycle/view/')
    obj = Bicycle.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle/view/')


def bike_photo_url_add(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id') and POST.has_key('url'):
                pid = request.POST.get('id')
                p_url = request.POST.get('url')
                
                if Photo.objects.filter(url = p_url):
                    p = Photo.objects.get(url = p_url)
                    bike = Bicycle.objects.get(id = pid)
                    bike.photo_url.add(p)
                    bike.save()
                    return HttpResponse("This photo is present. Таке фото вже існує", content_type="text/plain;charset=UTF-8;")
                
                bp = Photo(url = p_url, date = datetime.datetime.now(), user = request.user, description="")
                bp.save()
                bike = Bicycle.objects.get(id = pid)
                bike.photo_url.add(bp)
                bike.save()
    search = "ok"
    return HttpResponse(search, content_type="text/plain;charset=UTF-8")


def bicycle_list(request, year=None, brand=None, percent=None):
    #yyy = None
    if year == None:
        now = datetime.datetime.now()
        year = now.year
    if brand == None:
        list = Bicycle.objects.filter(year__year=year)
    else:
        list = Bicycle.objects.filter(year__year=year, brand=brand)
        if percent!=None:
            Bicycle.objects.filter(year__year=year, brand=brand).update(sale=percent)
    bike_company = Bicycle.objects.filter(year__year=year).values('brand', 'brand__name').annotate(num_company=Count('model')).order_by('num_company')
    #bike_year = Bicycle.objects.values('year').annotate(n_year=Count('year__year'))
    bike_year = Bicycle.objects.filter().extra({'yyear':"Extract(year from year)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('yyear')
    #return render_to_response('bicycle_list.html', {'bicycles': list.values_list()})
    context = {'bicycles': list, 'year': year, 'b_company': bike_company, 'byear': bike_year, 'sale': percent, 'weblink': 'bicycle_list.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def bicycle_photo(request, id):
    obj = Bicycle.objects.get(id=id)
    #return render_to_response('bicycle_list.html', {'bicycles': list.values_list()})
    context = {'bicycle': obj, 'weblink': 'bicycle_photo.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_store_add(request, id=None):
    bike = None
    if id != None:
        bike = Bicycle.objects.get(id=id)
        
    if request.method == 'POST':
        form = BicycleStoreForm(request.POST)
        if form.is_valid():
            model = form.cleaned_data['model']
            serial_number = form.cleaned_data['serial_number']
            size = form.cleaned_data['size']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            description = form.cleaned_data['description']
            realization = form.cleaned_data['realization']
            count = form.cleaned_data['count']
            date = form.cleaned_data['date']
            Bicycle_Store(model = model, serial_number=serial_number, size = size, price = price, currency = currency, description=description, realization=realization, count=count, date=date).save()
            return HttpResponseRedirect('/bicycle-store/view/')
    else:
        if bike != None:
            form = BicycleStoreForm(initial={'model': bike.id, 'count': '1'})
        else:
            form = BicycleStoreForm()
    #return render_to_response('bicycle_store.html', {'form': form})
    #return render_to_response('index.html', {'form': form, 'bike': bike, 'weblink': 'bicycle_store.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    context = {'form': form, 'bike': bike, 'weblink': 'bicycle_store.html', }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_store_edit(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id'):
                id = request.POST.get('id')
                p = request.POST.get('serial')
                obj = Bicycle_Store.objects.get(pk = id)
                obj.serial_number = p
                obj.save() 
                c = Bicycle_Store.objects.filter(pk = id).values_list('serial_number', flat=True)
                #c = "ajax work"
                return HttpResponse(c)
            else:
                return HttpResponse("Ajax dont work ")
    
    a = Bicycle_Store.objects.get(pk=id)
    start_ins = Bicycle_Store.objects.get(pk=id)
    if request.method == 'POST':
        form = BicycleStoreForm(request.POST, instance=a)
        print ("\nFORM PRE valid!")
        print ("\nPrice = %s; Currency = %s" % (a.price, a.currency))
        if form.is_valid():
            print ("\nFORM - SAVE")
            print ("\nFORM price = %s" % form.fields['price'])
            if auth_group(request.user, "admin") == False:
                serial_number = form.cleaned_data['serial_number']
                size = form.cleaned_data['size']
                description = form.cleaned_data['description']
                shop = form.cleaned_data['shop']
                price = form.cleaned_data['price']
                a.serial_number = serial_number
                a.size = size
                a.description = description
                a.shop = shop
                a.price = start_ins.price
                a.currency = start_ins.currency
                a.count = start_ins.count
                print ("\n>> Price = %s; Currency = %s <<\n" % (start_ins.price, start_ins.currency))
                a.save()
            else:
                form.save()
#            count = form.cleaned_data['count']
            return HttpResponseRedirect('/bicycle-store/view/')
    else:
        form = BicycleStoreForm(instance=a)

    #if auth_group(request.user, "admin") == False:
    if auth_group(request.user, "seller") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для редагування ', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
                
    context = {'form': form, 'weblink': 'bicycle_store.html', 'text': 'Редагувати тип', 'bikeStore' : a }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def bicycle_store_del(request, id):
    if request.user.has_perm('accounting.delete_bicycle_store') == False:
        return HttpResponseRedirect('/.')
    obj = Bicycle_Store.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle-store/view/seller/')


def bicycle_store_list(request, id=None, all=False, shop=None):
    list = None
    shopId = None
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    try:
        shopId = Shop.objects.get(pk = id)
    except:
        shopId = shopN
    if all==True:
        list = Bicycle_Store.objects.all()
    else:
        list = Bicycle_Store.objects.filter(count=1) #.values('model__model', 'model__sale', 'model__year', 'model__brand__name', 'model__price', 'model__color', 'model__id', 'size__name', 'size__cm', 'size__inch', 'model__type__type', 'serial_number', 'size', 'price', 'currency', 'count', 'description', 'date', 'id')
    if shop == None:
        id = shopN.pk
    if id <> None:
        list = list.filter(shop = shopId.pk)
    price_summ = 0
    bike_summ = 0
    price_profit_summ = 0
    for item in list:
        price_profit_summ = price_profit_summ + item.get_profit()[1] #item['price'] * item['count']
        price_summ = price_summ + item.get_uaprice() 
    bike_sum = list.count()
    context = {'bicycles': list, 'weblink': 'bicycle_store_list.html', 'price_summ': price_summ, 'price_profit_summ':price_profit_summ, 'bike_summ': bike_summ, 'shopName': shopId, 'shopAll': shop}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def bicycle_store_list_by_seller(request, all=False, size='all', year='all', brand='all', html=False):
    list = None
    if all==True:
        if brand == 'all':
            list = Bicycle_Store.objects.all()
        else:
            list = Bicycle_Store.objects.filter(count=1, model__brand=brand)
    else:
        if size == 'all':
            if year == 'all':
                list = Bicycle_Store.objects.filter(count=1)
            else:
                list = Bicycle_Store.objects.filter(count=1, model__year__year=year)
        else:
            if year == 'all':
                list = Bicycle_Store.objects.filter(count=1, size=size)
            else:
                list = Bicycle_Store.objects.filter(count=1, model__year__year=year, size=size)
            #list = Bicycle_Store.objects.filter(count=1, size=size)
    price_summ = 0
    real_summ = 0
    bike_summ = 0
    for item in list:
        if item.count != 0:
            price_summ = price_summ + item.price * item.count 
        real_summ = real_summ + item.realization
        bike_summ = bike_summ + item.count
#    frames = FrameSize.objects.all()
#    bike_company = Bicycle_Store.objects.filter(count=1).values('model__brand', 'model__brand__name').annotate(num_company=Count('count'))
#'sizes': frames, 'b_company': bike_company,
    context = {'bicycles': list, 'weblink': 'bicycle_store_list_by_seller.html', 'price_summ': price_summ, 'real_summ': real_summ, 'bike_summ': bike_summ,  'html': html,}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def bicycle_store_simple_list(request):
    list = Bicycle_Store.objects.filter(count=1)
    context = {'bicycles': list, 'weblink': 'bicycle_store_simplelist.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)    


def bicycle_store_search(request):
    context = {'weblink': 'frame_search.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def bicycle_store_search_result(request, all=False):
    list = None
    serial = request.GET['serial_number']
    if all==True:
        list = Bicycle_Store.objects.all()
    else:
        list = Bicycle_Store.objects.filter(serial_number__icontains=serial)
    price_summ = 0
    real_summ = 0
    bike_summ = 0
    for item in list:
        if item.count != 0:
            price_summ = price_summ + item.price * item.count 
        real_summ = real_summ + item.realization
        bike_summ = bike_summ + item.count
    context = {'bicycles': list, 'weblink': 'bicycle_store_list_by_seller.html', 'price_summ': price_summ, 'real_summ': real_summ, 'bike_summ': bike_summ, }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_store_price(request, pprint=False):
    if request.method == 'POST':    
        checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
        list_id = []
        for id in checkbox_list:
            list_id.append( int(id.replace('checkbox_', '')) )
        list = Bicycle_Store.objects.filter(id__in = list_id)
    else: 
        list = Bicycle_Store.objects.filter(count=1)
    if pprint:
        context = {'bicycles': list, 'view':False}
        return render(request, 'bicycle_shop_price_list.html', context)
    context = {'bicycles': list, 'weblink': 'bicycle_shop_price_list.html', 'view':True, }
    context.update(custom_proc(request))    
    return render(request, 'index.html', context)


def bicycle_store_price_print(request):
    list = Bicycle_Store.objects.filter(count=1)
    return render_to_response('bicycle_shop_price_list.html', {'bicycles': list, 'view':False})


def store_report_bysize(request, id):
    list = Bicycle_Store.objects.filter(size = id, count = 1)
    frame = FrameSize.objects.get(id=id)
    frame_str = u"Розмір рами " + frame.name
    frames = FrameSize.objects.all()
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_store_list.html', 'text': frame_str, 'sizes': frames, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

    
def store_report_bytype(request, id):
    list = Bicycle_Store.objects.filter(model__type__exact=id, count__gt=0)
    if bool(list) == False:
        type = Bicycle_Type.objects.get(id = id)
        s = "Велосипедів <b>" + str(type.type) + "</b> типу в наявності не має"
        return HttpResponse(s) 
    type = list[0].model.type.type
    text = u"Тип велосипеду: " + type
    if auth_group(request.user, 'admin'):
        context = {'bicycles': list, 'weblink': 'bicycle_store_list.html', 'text': text, }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    context = {'bicycles': list, 'weblink': 'bicycle_store_list_by_seller.html', 'text': text, 'html': True}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_sale_add(request, id=None):
    if not request.user.is_authenticated():
        context = {'weblink': 'error_message.html', 'mtext': 'Авторизуйтесь щоб виконати дану функцію', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    bike = None
    serial_number = ''
    if id != None:
        bike = Bicycle_Store.objects.get(id=id)
        serial_number = bike.serial_number
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])        
    if request.method == 'POST':
        form = BicycleSaleForm(request.POST, initial={'currency': 3, 'date': datetime.date.today(), 'shop': shopN })
        if form.is_valid():
            model = form.cleaned_data['model']
            client = form.cleaned_data['client']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            sale = form.cleaned_data['sale']
            sum = form.cleaned_data['sum']
            date = form.cleaned_data['date']
            service = form.cleaned_data['service']
            description = form.cleaned_data['description']
            shop = form.cleaned_data['shop']
            user = request.user            
            bs = Bicycle_Sale(model = model, client=client, price = price, currency = currency, sale=sale, date=date, service=service, description=description, user=user, sum=sum, shop=shop)
            bs.save()
            
            update_bicycle = Bicycle_Store.objects.get(id=model.id)
            if update_bicycle.count != 0: 
                update_bicycle.count = update_bicycle.count - 1 
            #update_bicycle.count - 1
            update_bicycle.save()
            
            update_client = Client.objects.get(id=client.id)
            update_client.summ = update_client.summ + price
            if update_client.sale < 5:
                update_client.sale = 5 
            update_client.save()
            
            cdeb_price = price * (1 - sale/100.0)
            cdeb = ClientDebts(client=client, date=datetime.datetime.now(), price=cdeb_price, description=""+str(model), user=user)
            cdeb.save()
            bs.debt = cdeb
            bs.save()
            redirect = "/client/result/search/?id="+str(client.id)
            return HttpResponseRedirect(redirect)
    else:
        
        if bike != None:
            form = BicycleSaleForm(initial={'model': bike.id, 'price': bike.model.price, 'currency': bike.model.currency.id, 'sale': bike.model.sale, 'date': datetime.date.today(), 'shop': shopN })
        else:
            form = BicycleSaleForm(initial={'currency': 3, 'shop': shopN})
            
    context = {'form': form, 'weblink': 'bicycle_sale.html', 'serial_number': serial_number, 'bike_id': bike.id, 'text': 'Продаж велосипеду', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_sale_edit(request, id):
    a = Bicycle_Sale.objects.get(pk=id)
    user = None             
    if request.user.is_authenticated():
        user = request.user
    else:
        return HttpResponse("<h2>Для виконання операції редагування авторизуйтесь</h2>")
    
    if request.method == 'POST':
        form = BicycleSaleForm(request.POST, instance=a, bike_id=a.model.model.id)
        #form = BicycleSaleForm(request.POST, instance=a)
        if form.is_valid():
            model = form.cleaned_data['model']
            client = form.cleaned_data['client']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            sale = form.cleaned_data['sale']
            date = form.cleaned_data['date']
            service = form.cleaned_data['service']
            description = form.cleaned_data['description']
            sum = form.cleaned_data['sum']
            shop = form.cleaned_data['shop']
            form.save()
            
            cdeb_price = price * (1 - sale/100.0)
            try:
                cdeb = ClientDebts.objects.get(pk=a.debt.id)
                cdeb.price=cdeb_price
                cdeb.description=""+str(model)
                cdeb.user=user
                cdeb.save()
            except:
                pass

            return HttpResponseRedirect('/bicycle/sale/view/')
    else:
        form = BicycleSaleForm(instance=a, bike_id=a.model.model.id)
        
    serial_number = a.model.serial_number
    bike_id = a.id
    context = {'form': form, 'weblink': 'bicycle_sale.html', 'text': 'Редагувати проданий велосипед', 'serial_number': serial_number, 'bike_id': bike_id}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def bicycle_sale_del(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse("<h2>Для видалення потрібні права адміністратора </h2>")    
    obj = Bicycle_Sale.objects.get(id=id)
    del_logging(obj)
    update_client = Client.objects.get(id=obj.client.id)
    update_client.summ = update_client.summ - obj.price 
    update_client.save()
    update_storebike = Bicycle_Store.objects.get(id=obj.model.id)
    update_storebike.count = update_storebike.count + 1
    update_storebike.save()
    try:
        update_debt = ClientDebts.objects.get(id=obj.debt.id)
        update_debt.delete()
    except:
        pass
    obj.delete()
    return HttpResponseRedirect('/bicycle/sale/view/')


def bicycle_sale_list(request, year=False, month=False, id=None):
    list = None
    if (year != '') & (month == False):
        list = Bicycle_Sale.objects.filter(date__year=year).order_by('model__model__brand', 'date')
    if (year==False) & (month==False):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        #list = Bicycle_Sale.objects.all().order_by('date')
        if (id != None):
            #list = Bicycle_Sale.objects.filter(pk = id).order_by('date')
            list = Bicycle_Sale.objects.filter(model__id = id).order_by('date')
        else:
            list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
    if (year != False) & (month != False) & (id == None):
        list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
#    header_bike = Bicycle_Sale.objects.filter().extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('date')
    header_bike = Bicycle_Sale.objects.annotate(year=ExtractYear('date')).values('year').annotate(pk_count = Count('pk')).order_by('year')  
    psum = 0
    price_summ = 0
    profit_summ = 0
    service_summ = 0
    for item in list:
        #price_summ = price_summ + item.price
        price_summ = price_summ + item.price * ((100-item.sale)*0.01)
        profit_summ = profit_summ + item.get_profit()[1]
        if item.sum:
            psum = psum + item.sum
        if item.service == False:
            service_summ =  service_summ + 1
    context = {'bicycles': list, 'weblink': 'bicycle_sale_list.html', 'header_links':header_bike, 'price_summ':price_summ, 'profit_summ':profit_summ, 'pay_sum':psum, 'service_summ':service_summ, 'month': month, 'year':year, }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


#Bicycle sale list for all (WORK VERSION)
def bicycle_sale_list_by_brand(request, year=False, month=False, id=None, all=False):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")   
    list = None
    year = year
    month = month
    brand = None
    brand_count = None
    if (year==False) & (month==False):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
    if all == True:
        list = Bicycle_Sale.objects.filter(model__model__brand=id).order_by('date')
    else:
        if (month == False) & (id <> None):
            list = Bicycle_Sale.objects.filter(model__model__brand=id, date__year=year).order_by('date')
            brand = list[0].model.model.brand.name
#            list = Bicycle_Sale.objects.filter(model__model__brand=id).order_by('date')
        if (year != False) & (month != False) & (id == None):
            list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
        if (year != False) & (month != False) & (id <> None):
            list = Bicycle_Sale.objects.filter(model__model__brand=id, date__year=year, date__month=month).order_by('date')
#            list = Bicycle_Sale.objects.filter(model__id = id).order_by('date')
            brand = list[0].model.model.brand.name
        if (month == False) & (id == None):
            list = Bicycle_Sale.objects.filter(date__year=year).order_by('date')
    if id == None:
        brand_count = list.values('model__model__brand__name', 'model__model__brand').annotate(total=Count('model__model__brand')).order_by('total') #order_by('model__model__brand__name')
    #header_bike = Bicycle_Sale.objects.filter().extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('date')
    header_bike = Bicycle_Sale.objects.annotate(year=ExtractYear('date')).values('year').annotate(pk_count = Count('pk')).order_by('year')       
    #header_bike = Bicycle_Sale.objects.annotate(year = Q('date__year')).values('year').annotate(pk_count = Count('pk')).order_by('year')
    price_summ = 0
    price_summ_full = 0
    price_opt = 0
    price_opt_dol = 0
    price_opt_eur = 0
    profit_summ = 0
    service_summ = 0
    for item in list:
        #price_summ = price_summ + item.price
        price_summ = price_summ + item.price * ((100-item.sale)*0.01)
        price_summ_full = price_summ_full + item.price
        if item.model.currency.ids_char == 'UAH':
            price_opt = price_opt + item.model.price
        if item.model.currency.ids_char == 'USD':
            price_opt_dol = price_opt_dol + item.model.price
        if item.model.currency.ids_char == 'EUR':    
            price_opt_eur = price_opt_eur + item.model.price
#        print "\nCURRENCY BIKE = " + str(item.model.currency.ids_char)
        profit_summ = profit_summ + item.get_profit()[1]
        if item.service == False:
            service_summ =  service_summ + 1
    context = {'bicycles': list, 'weblink': 'bicycle_sale_list.html', 'price_summ':int(price_summ), 'price_summ_full': int(price_summ_full), 'header_links':header_bike, 'brand_count': brand_count, 'price_opt': price_opt, 'price_opt_eur': price_opt_eur, 'price_opt_dol': price_opt_dol, 'profit_summ':profit_summ, 'service_summ':service_summ, 'year':year, 'month': month, 'brand':brand}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def bicycle_sale_service(request, id=None):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")

    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                b_id = request.POST.get( 'id' )
                bserv = request.POST.get( 'value' )
                list = Bicycle_Sale.objects.get(id=b_id)
                if (bserv == "1"):
                    message = "Пройдено"
                    list.service = True
                    list.save()
                else:
                    message = "Не пройдено"
                    list.service = False
                    list.save()
                    
                return HttpResponse(message, content_type="text/plain;charset=UTF-8")
    else:
        message = "Error"
        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")


def sale_post_bike(token, bike, cash_pay=0, card_pay=0):
    goods = []
    payments = []
    ci = []
    ci.append(bike)
    bike_name = ""
    bike_name = u'Велосипед '+ bike.model.model.brand.name +u'. Модель '+ bike.model.model.model +'. '+str(bike.model.model.year.year)+' ('+bike.model.model.color+')'
    full_price = 0
    
    for inv in ci:
        ci_dic = {}
        price =  "%.2f" % inv.price
        print "\n PRICE = " + str(int(inv.price*100)) + "\n"
#        count = "%.3f" % inv.count
        discount = inv.sale

        gkey = {
        "code": '77'+str(bike.model.pk),
#        "name": inv.catalog.name[:40], #.encode('cp1251'),
        "name": bike_name,
        #"barcode": str(inv.catalog.ids), # "1112222111",
        "excise_barcode": "",
#        "header": "HeaderString",
#        "footer": "FooterTitle",
        "price": str(int(inv.price*100)),#"12200",
        #"uktzed": ""
        } 
        quantity =  "1000"   # one bike #
        discounts =  [ {
            "type": "DISCOUNT",
            "mode": "PERCENT",
            "value": str(discount) }
        ]
        
        ci_dic.update({'good': gkey})
        if discount <> 0:
            ci_dic.update({'discounts': discounts})
        ci_dic.update({'is_return': 'false'})
        ci_dic.update({'quantity': str(int(quantity))})
        ci_dic.update({"is_winnings_payout": "true",})
        goods.append(ci_dic)

        full_price = int(inv.price*100)*((100-discount)*0.01)
        print "\nFull price = " + str(full_price)
        print "\n CASH PAY = " + str(cash_pay) + "\n"
        #cash_round = round(float(cash_pay), 1)
        cash_round = int(math.ceil(round(float(cash_pay), 1)*100))
        card_round = int(round(float(card_pay)*100))
        print "\n CASH ROUND = " + str(cash_round) + "\n"
        print "\n CARD PAY = " + str(int(round(float(card_pay)*100))) + "\n"
        print "\nMATH  = " + str(full_price - card_round - cash_round) + "\n"
        if (full_price - card_round - cash_round) <> 0:
           cash_round = cash_round + 10 
        
        cash = {
        "type": "CASH",
        "value": str(cash_round),
        }
        cashless = {
        "type": "CASHLESS",
        "value": str(card_round), 
        "bank_name": "PrivatBank",
        "terminal": "Verifone",
        "acquirer_and_seller": "ecquirer007",
        #"receipt_no": "BANK_no"
        }
        if cash_pay <> '0':
            payments.append(cash)
        
        if card_pay <> '0':
            payments.append(cashless)
     
    url = "https://api.checkbox.ua/api/v1/receipts/sell"
    data_work = {
    "cashier_name": "RiveloName",
    "departament": "RiveloShop",
    "goods":  goods,
    "delivery": {
    },
#    "discounts": [],
    "bonuses": [],
    "payments": payments,      
    "rounding": "true",
    "header": "Вас вітає веломагазин-майстерня Rivelo!",
    "footer": "До зустрічі на дорогах і стежках України.",
    "stock_code": "string_Bottom",
    "technical_return": "false",
    "context": {
        "additionalProp1": "string_1",
        "additionalProp2": "string_2",
        "additionalProp3": "string_3"
    },
    "is_pawnshop": "false",
    "custom": {
        }
    
    }
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain', 
        'Authorization': token
        }  
    
    jsonString = json.dumps(data_work, indent=4)
    print "\nJSON : \n" + jsonString + "\n"
    
    r = requests.post(url, data=json.dumps(data_work), headers=headers)
    resp_str = json.dumps(r.json(), indent=4)
    print "CREATE Payment: " + resp_str + "\n"
    #print "Balance After: " + str(r.json()['shift']['balance']['balance']/100.0) + "\n"
    return r


def save_chek2db_bike(cash, term, bike, shop, request, desc=''):
    ci = []
    ci.append(bike)
    res = Check.objects.aggregate(max_count=Max('check_num'))
    chkPay = CheckPay(check_num = res['max_count'] + 1, cash = cash, term = term, description='checkbox_id='+desc+";")
    chkPay.user = request.user
    chkPay.save()
                    
    for inv in ci:
        check = Check(check_num=res['max_count'] + 1)
        checkPay = chkPay
        check.client = inv.client #Client.objects.get(id=client.id)
        #check.catalog = inv #ClientInvoice.objects.get(pk=inv)
        check.bicycle = inv #ClientInvoice.objects.get(pk=inv)
        check.description = "Продаж велосипеду. "
        check.checkPay = checkPay
        
        if ((float(cash) > 0) and (float(term) > 0)):
            check.description = check.description + " Готівка / Термінал"
        if (cash == '0'):
            check.description = check.description + " Термінал"
        if (term == '0'):
            check.description = check.description + " Готівка"
                        
        #check.count = inv.count
        check.count = 1 #bike count
        check.discount = inv.sale
        t = 1
        if cash >= term:
            if shop == 1:
                t = 1
            if shop == 2:
                t = 10
            check.price = inv.sum #m_val
        else: 
            if shop == 1:
                t = 9 # PUMB = 9 / PB = 2
            if shop == 2:
                t = 2 # PUMB = 9 / PB = 2

            check.price = term 
        check.cash_type = CashType.objects.get(id = t)
        check.print_status = False
        check.user = request.user
        check.save()
    return            


@csrf_exempt
def bicycle_sale_check_add(request, id):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    message = ''
    count = None
    URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    cmd = 'open_port;1;115200;'
    PARAMS = {'address':URL, 'cmd': cmd, 
              'hash': settings.MINI_HASH_1, 
              'user': request.user.username,
             }
    
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                b_id = request.POST.get( 'id' )
                m_val = request.POST.get( 'm_value' )
                t_val = request.POST.get( 't_value' )
                term_number =  request.POST.get( 'term' )

                bs = Bicycle_Sale.objects.get(id=id)
                chk_list = Check.objects.filter(bicycle = bs.id)
                if chk_list.count()>0:
                    message = "Даний чек вже існує"
                    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")                    
                
                #CheckBox casa
                if term_number == '2':
#                    URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"
                    token = post_casa_token()
                    resp = sale_post_bike(token, bs, cash_pay = m_val, card_pay = t_val)
                    if resp.status_code == 201:
#                        print "\nSTATUS RESPONCE - " + str(resp.status_code) + "\n"
                        #save_chek2db(m_val, t_val, ci, 2, request, desc=str(resp.json()['id']))
                        save_chek2db_bike(m_val, t_val, bs, 2, request, desc=str(resp.json()['id']))
                        message = "" + str(resp.json()['id'])
                    else:
                        message = "CHECKBOX - Error\n" + str(resp.text.encode('utf-8'))
                    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
#                    return 
                else:
#                    base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
#                    data =  {"cmd": "open"}
#                    url = base + urllib.urlencode(data)
                    #===========================================================
                    # try:
                    #     page = urllib.urlopen(url).read()
                    # except:
                    #     message = "Сервер" + settings.HTTP_MINI_SERVER_IP + " не відповідає"
                    #     return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
                    #===========================================================
                    try:
                        resp_open = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = "cashier_registration;1;0"
                        resp_registration = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = 'open_receipt;0' # відкрити чек
                        resp_registration = requests.post(url = URL, data = PARAMS)
                    except:
                        message = "Сервер "+settings.HTTP_MINI_SERVER_IP+" не відповідає"
                        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")

                    save_chek2db_bike(m_val, t_val, bs, 1, request)
####
                    #===========================================================
                    # res = Check.objects.aggregate(max_count=Max('check_num'))
                    # chkPay = CheckPay(check_num = res['max_count'] + 1, cash = m_val, term = t_val)
                    # chkPay.save()
                    # 
                    # res = Check.objects.aggregate(max_count=Max('check_num'))
                    # check = Check(check_num=res['max_count'] + 1)
                    # check.checkPay = chkPay
                    # check.client = bs.client #Client.objects.get(id=client.id)
                    # check.bicycle = bs #ClientInvoice.objects.get(pk=inv)
                    # check.description = "Продаж велосипеду"
                    # check.count = 1
                    # check.discount = bs.sale
                    # t = 1
                    # if m_val >= t_val:
                    #     t = 1
                    #     check.price = m_val
                    # else: 
                    #     t = 2
                    #     check.price = t_val 
                    # check.cash_type = CashType.objects.get(id = t)
                    # check.print_status = False
                    # check.user = request.user
                    # check.save()    
                    #===========================================================
###
                    price =  "%.2f" % bs.price
                    count = "%.3f" % 1
                    discount = bs.sale
                    #bike_s = 'Велосипед '+ bs.model.model.brand.name.encode('utf8') +'. Модель '+ bs.model.model.model.encode('utf8') +'. '+str(bs.model.model.year.year)+' ('+bs.model.model.color.encode('utf8')+')'
                    bike_s = u'Велосипед '+ bs.model.model.brand.name +u'. Модель '+ bs.model.model.model +'. '+str(bs.model.model.year.year)+' ('+bs.model.model.color+')'
                    #bike_s = bs.model.model.model[:40].encode('utf8')
                    #data =  {"cmd": "add_plu", "id":'77'+str(bs.model.pk), "cname":bike_s, "price":price, "count": count, "discount": discount}
                    
                    PARAMS['cmd'] = 'add_plu;'+'77'+str(bs.model.pk)+";0;0;0;1;1;1;"+price+";0;"+bike_s[:40].encode('cp1251')+";"+count+";"
                    resp = requests.post(url = URL, data = PARAMS)
                    PARAMS['cmd'] = 'sale_plu;0;0;0;1;'+'77'+str(bs.model.pk)+";"
                    resp = requests.post(url = URL, data = PARAMS)
                    PARAMS['cmd'] = 'discount_surcharge;1;0;1;'+"%.2f" % discount+";"
                    resp = requests.post(url = URL, data = PARAMS)


                    if m_val >= t_val:
                        if float(t_val) == 0:
                            PARAMS['cmd'] = "pay;"+"0;0;"
                            resp = requests.post(url = URL, data = PARAMS)
                        else:
                            PARAMS['cmd'] = "pay;0;"+"%.2f" % float(m_val)+";"
                            resp = requests.post(url = URL, data = PARAMS)
                            PARAMS['cmd'] = "pay;2;"+"%.2f" % float(t_val)+";"
                            print "PARAM = " + PARAMS['cmd']
                            resp = requests.post(url = URL, data = PARAMS)
                    else:
                        if float(m_val) == 0:
                            PARAMS['cmd'] = "pay;"+"2;0;"
                            resp = requests.post(url = URL, data = PARAMS)
                        else:
                            PARAMS['cmd'] = "pay;2;"+"%.2f" % float(t_val)+";"
                            resp = requests.post(url = URL, data = PARAMS)
                            PARAMS['cmd'] = "pay;0;"+"%.2f" % float(m_val)+";"
                            resp = requests.post(url = URL, data = PARAMS)
                    
                    PARAMS['cmd'] = 'close_port;'
                    resp_close = requests.post(url = URL, data = PARAMS)

                message = "Виконано"
                return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
    else:
        message = "Error"
        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")



def bicycle_sale_check(request, id=None, param=None):
    printed = False
    chk_pay = []
    list = Bicycle_Sale.objects.get(id=id)
    text = pytils_ua.numeral.in_words((100-int(list.sale))*0.01*int(list.price))
    month = pytils_ua.dt.ru_strftime(u"%d %B %Y", list.date, inflected=True)
    chk_list = Check.objects.filter(bicycle = list.id)
    if chk_list.count()>0:
        chk_num = chk_list[0].check_num
        printed = True
        chk_pay.append(chk_list[0].checkPay)
    else:
        chk_num = list.id
    w = render_to_response('bicycle_sale_check.html', {'bicycle': list, 'month':month, 'str_number':text, 'chk_num':chk_num, 'printed': printed})
    if param == 'print':
        return w
    if param == 'email':
        if request.user.is_authenticated() == False:
            return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
        if list.client.email == '':
            return HttpResponse("<h2>Введіть поштову адресу покупця</h2>")
        
        subject, from_email, to, to_copy = 'Товарний чек від веломагазину Rivelo', 'rivelo@ymail.com', list.client.email, 'rivelo@ukr.net'
        text_content = 'Доброго дня! Ваш чек на велосипед.'
        html_content = w.content
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to, to_copy])
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            return HttpResponse("<h2>Чек відправлено!</h2>")
        except:
            return HttpResponse("<h2>Сталася помилка при відправленні. Перевірте з'єднання до інтернету.</h2>")
    context = {'bicycle': list, 'month':month, 'chk_num':chk_num, 'str_number':text, 'weblink': 'bicycle_sale_check.html', 'print':'True', 'printed': printed, 'checkPay': chk_pay,}
    context.update(custom_proc(request))
    return render(request, 'index.html', context) 


def bicycle_sale_search_by_name(request):
    context = {'weblink': 'bicycle_sale_search_by_name.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def bsale_search_by_name_result(request, all=False):
    list = None
    name = request.GET['model_name']
    if all==True:
        list = Bicycle_Sale.objects.all()
    else:
        list = Bicycle_Sale.objects.filter(model__model__model__icontains = name)
    price_summ = 0
    real_summ = 0
    bike_summ = 0
    price_summ_full = 0
    for item in list:
        price_summ = price_summ + item.price 
        price_summ_full = price_summ_full + item.price
    context = {'bicycles': list, 'weblink': 'bicycle_sale_list.html', 'price_summ': price_summ, 'price_summ_full': int(price_summ_full), }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def bicycle_tradein_return(request, id):
    if auth_group(request.user, 'admin') == False:
        return HttpResponse('Дана дія доступна лише адміністратору', content_type="text/plain;charset=UTF-8;")
    bs = None
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR']) 
    dnow = datetime.datetime.now()
    try: 
        bs = Bicycle_Sale.objects.get(pk = id);
        bikeinStore = bs.model
        bikeinStore.realization = True 
        bikeinStore.count = 1
        bikeinStore.description = u"Trade in ("+ dnow.strftime("%d.%m.%Y") +u"). Last sale ("+ bs.date.strftime("%d/%m/%Y") +u") - " + str(bs.sum) + u" грн." 
        bikeinStore.shop = shopN  
#        bikeinStore.currency = Currency.objects.get(id=3)
#        bikeinStore.price = 
        bikeinStore.save() 
    except:
        return HttpResponse('Велосипеду не знайдено або вже виконані якісь інші дії з даним продажем', content_type="text/plain;charset=UTF-8;")
    if re.search("\\n$", bs.description) == None:
        bs.description = bs.description + "\n"
    bs.description = bs.description + u"Trade in ("+ dnow.strftime("%d.%m.%Y") +u")" 
    bs.sum = 0
    bs.save()
    return HttpResponseRedirect('')
        

def bicycle_sale_report(request):
    if auth_group(request.user, 'admin') == False:
        return HttpResponseRedirect('/')
#    query = "SELECT EXTRACT(year FROM date) as year, EXTRACT(month from date) as month, MONTHNAME(date) as month_name, COUNT(*) as bike_count, sum(price) as s_price FROM accounting_bicycle_sale GROUP BY year,month;"
    #sql2 = "SELECT sum(price) FROM accounting_clientdebts WHERE client_id = %s;"
    #user = id;
    list = None
    #===========================================================================
    # try:
    #     cursor = connection.cursor()
    #     cursor.execute(query)
    #     list = dictfetchall(cursor)
    #     #list = cursor.execute(sql1, )   
    # except TypeError:
    #     res = "Помилка"
    #===========================================================================
    list = Bicycle_Sale.objects.annotate(year=ExtractYear('date'), month=ExtractMonth('date')).values('year', 'month').annotate(suma=Sum("price"), bike_count=Count('pk')).order_by()
    sum = 0
    bike_sum = 0
    for month in list:
        sum = sum + month['suma']
        bike_sum = bike_sum + month['bike_count']
#        sum = sum + month['s_price']
#        bike_sum = bike_sum + month['bike_count']
    context = {'bicycles': list, 'all_sum': sum, 'bike_sum': bike_sum, 'weblink': 'bicycle_sale_report.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)



def bicycle_sale_report_by_brand(request):
    list = Bicycle_Sale.objects.values('model__model__brand__name', 'model__model__brand', 'model__model__brand__id').annotate(bcount=Count("model__model__model")).order_by('-bcount') #("model__model__brand")
    context = {'bicycles': list, 'weblink': 'bicycle_sale_report_bybrand.html', }
    context.update(custom_proc(request))    
    return render(request, 'index.html', context)    

@csrf_exempt
def bicycle_order_add(request):
    if auth_group(request.user, 'seller') == False:
        return HttpResponse('Для виконання дій авторизуйтесь', content_type="text/plain;charset=UTF-8;")
    a = Bicycle_Order(prepay=0, sale=0, currency=Currency.objects.get(id=3))
    if request.method == 'POST':
        form = BicycleOrderForm(request.POST, instance = a)
        if form.is_valid():
            cid = form.cleaned_data['client_id']
            client = Client.objects.get(pk = cid)
            mid = form.cleaned_data['model_id']
            model = Bicycle.objects.get(pk = mid)
            size = form.cleaned_data['size']
            price = form.cleaned_data['price']
            sale = form.cleaned_data['sale']
            prepay = form.cleaned_data['prepay']
            currency = form.cleaned_data['currency']
            date = form.cleaned_data['date']
            #done = form.cleaned_data['done']
            description = form.cleaned_data['description']
            user = None             
            cashtype = None
            if request.user.is_authenticated():
                user = request.user
              
            if request.POST.has_key('cash'):
                o_id = request.POST.get( 'cash' )            
                cashtype = CashType.objects.get(id = o_id)
                
            Bicycle_Order(client=client, model=model, size=size, price=price, sale=sale, currency=currency, date=date,  description=description, prepay=prepay, user=user).save()
            ClientCredits(client=client, date=date, price=prepay, description="Передоплата за "+str(model), user=user, cash_type=cashtype).save()                        
            return HttpResponseRedirect('/bicycle/order/view/')
    else:
        form = BicycleOrderForm(instance = a)
    
    context = {'form': form, 'weblink': 'bicycle_order.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html',  context)
    

def bicycle_order_list(request):
    #list = Bicycle_Order.objects.all().order_by("-date")
    list = Bicycle_Order.objects.all().order_by("-date").values('model__id', 'model__model', 'model__brand__name', 'model__year', 'model__color', 'model__type__type', 'client__id', 'client__name', 'client__forumname', 'size', 'price', 'prepay', 'sale', 'date', 'done', 'id', 'currency__name', 'description', 'user')
    context = {'order': list, 'weblink': 'bicycle_order_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)
    
@csrf_exempt
def bicycle_order_edit(request, id):
    a = Bicycle_Order.objects.get(pk=id)
    if request.method == 'POST':
        form = BicycleOrderForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/bicycle/order/view/')
    else:
        form = BicycleOrderForm(instance=a, initial={'client_id': a.client.pk, 'model_id': a.model.pk})
    context = {'form': form, 'weblink': 'bicycle_order.html'}
    return render(request, 'index.html', context)


def bicycle_order_del(request, id):
    obj = Bicycle_Order.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle/order/view/')    

@csrf_exempt
def bicycle_order_done(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('border_id'):
                o_id = request.POST.get( 'border_id' )
                obj = Bicycle_Order.objects.get(id = o_id)
                obj.done = not obj.done
                res = obj.done 
                obj.save()
                return HttpResponse(res, content_type="text/plain;charset=UTF-8;")
                #search = Bicycle_Order.objects.filter(id=o_id).values('done', 'description')
                #return HttpResponse(simplejson.dumps(list(search)), content_type="application/json")

    #            return HttpResponse(simplejson.dumps(list()), content_type="application/json")
    return HttpResponse("Помилка скрипта", content_type="text/plain;charset=UTF-8;")
    #return HttpResponseRedirect('/bicycle/order/view/')

# lookup bicycle price
def bicycle_lookup_ajax(request):
    search = None
    message = ""
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('store_id'):
                q = request.GET.get( 'store_id' )
                message = "It's AJAX!!!"
                search = Bicycle_Store.objects.filter(id=q).values('model__price', 'model__sale', 'serial_number')
            if GET.has_key('id'):
                q = request.GET.get( 'id' )
                message = "It's AJAX!!!"
                search = Bicycle.objects.filter(id=q).values('price', 'sale')
            
    else:
        message = "Error"
    #search = Bicycle.objects.filter(id=q).values('price', 'sale')
    return HttpResponse(simplejson.dumps(list(search)), content_type="application/json")

#def ValuesQuerySetToDict(vqs):
#    return [item for item in vqs]

@csrf_exempt
def bike_lookup(request):
    data = None
    cur_year = datetime.datetime.now().year
    if request.method == "POST":
        if request.POST.has_key(u'query'):
            value = request.POST[u'query']
            if len(value) > 2:
                model_results = Bicycle.objects.filter(year__gte=datetime.datetime(cur_year-2, 1, 1)).filter(Q(model__icontains = value) | Q(brand__name__icontains = value)).order_by('-year')
                data = serializers.serialize("json", model_results, fields = ('id', 'model', 'type', 'brand', 'color', 'price', 'year', 'sale')) #, use_natural_keys=False)
            else:
                data = []
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('bike_id'):
                q = request.POST['bike_id']
                search = Bicycle.objects.get(id=q)
                data = search.model
    else:
        message = "Error"
    return HttpResponse(data)                

@csrf_exempt
def bicycle_storage_type_add(request):
    if (auth_group(request.user, 'seller') or auth_group(request.user, 'admin')) == False:
        return HttpResponseRedirect('/bicycle/storage/type/view/')
    a = Storage_Type()    
    if request.method == 'POST':
#        form = BicycleForm(request.POST, request.FILES, instance=a)
        form = StorageType_Form(request.POST, request.FILES)        
        if form.is_valid():
            type = form.cleaned_data['type']
            price = form.cleaned_data['price'] 
            description = form.cleaned_data['description']
            
            Storage_Type(type=type, price = price, description=description).save()
            return HttpResponseRedirect('/bicycle/storage/type/view/')
            #return HttpResponseRedirect(bicycle.get_absolute_url())
    else:
#        form = BicycleForm(instance=a)
        form = StorageType_Form()        

    #return render_to_response('bicycle.html', {'form': form})
    return render(request, 'index.html', {'form': form, 'weblink': 'bicycle_storage.html', 'text': 'Вид зберігання'})


def bicycle_storage_type_list(request):
    #list = Bicycle_Order.objects.all().order_by("-date")
    list = Storage_Type.objects.all().order_by("id")
    context = {'list': list, 'weblink': 'storage_type_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


from django.contrib import messages
from django.shortcuts import  redirect
from django.utils.encoding import smart_str    

@csrf_exempt
def bicycle_storage_add(request):
    if (auth_group(request.user, 'seller') or auth_group(request.user, 'admin')) == False:
        return HttpResponseRedirect('/bicycle/storage/view/')
    #a = Bicycle_Storage()    
    if request.method == 'POST':
        #if request.FILES == None:
        images = request.FILES.getlist('file-input',[])            
        if len(images)<1:            
            return HttpResponse('Must have files attached!')
#        form = BicycleForm(request.POST, request.FILES, instance=a)
        form = BicycleStorage_Form(request.POST, request.FILES)        
        if form.is_valid():
            cid = form.cleaned_data['client']
#            client = Client.objects.get(pk = cid)
            model = form.cleaned_data['model']
            type = form.cleaned_data['type']
            color = form.cleaned_data['color']
            wheel_size = form.cleaned_data['wheel_size']
            size = form.cleaned_data['size']
            biketype = form.cleaned_data['biketype']
            serial_number = form.cleaned_data['serial_number']
            service = form.cleaned_data['service']
            washing = form.cleaned_data['washing']
            description = form.cleaned_data['description']
            date_in = form.cleaned_data['date_in']
            date_out = form.cleaned_data['date_out']
            done = form.cleaned_data['done']
            currency = form.cleaned_data['currency']
            price = form.cleaned_data['price']
#            photo = form.cleaned_data['photo']
            #===================================================================
            # folder = 'storage'            
            # if photo == None:
            #     upload_path = None
            # if isinstance(photo, InMemoryUploadedFile):
            #     upload_path = processUploadedImage(photo, 'bicycle/'+str(folder)+'/') 
            #===================================================================
           
#            bs = Bicycle_Storage(client=client, model = model, type=type, size=size, color = color, biketype=biketype, service = service, washing=washing, serial_number=serial_number, price = price, currency = currency, date_in=date_in, description=description).save()
            bs = Bicycle_Storage(client=cid, model = model, type=type, size=size, color = color, biketype=biketype, service = service, washing=washing, serial_number=serial_number, price = price, currency = currency, date_in=date_in, description=description, wheel_size=wheel_size)
            bs.save()
            #images = request.FILES.getlist('file-input',[])
            #bs_id = Bicycle_Storage.objects.get(pk = 14)
            for image in images:
                bs_id=bs
                try:
                    photo = Bicycle_Photo(bicycle = bs_id, image = image, user = request.user, date=bs.date, description=description)
                    photo.save()
                except Exception, e:
                    messages.error(request, smart_str(e)) 
                            
            #bp = Bicycle_Photo(bicycle = bs, user = request.user, description=description) 
            #bp.photo=upload_path
            #bp.save() 
            #Bicycle_Photo(title=title, description=description, www=www, image=upload_path, country=country).save()            
            return HttpResponseRedirect('/bicycle/storage/view/')
            #return HttpResponseRedirect(bicycle.get_absolute_url())
    else:
#        form = BicycleForm(instance=a)
        form = BicycleStorage_Form()        

    #return render_to_response('bicycle.html', {'form': form})
    context = {'form': form, 'weblink': 'bicycle_storage.html', 'text': 'Додати велосипед на зберігання'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def bicycle_storage_edit(request, id):
    a = Bicycle_Storage.objects.get(pk=id)
    images = request.FILES.getlist('file-input',[])
    #if request.method == 'GET' or len(images)<=1 or not is_valid:
    #if len(images)<=1:            
    #        return HttpResponse('Must have files attached!')
    if request.method == 'POST':
        form = BicycleStorage_Form(request.POST, request.FILES, instance=a)
        if form.is_valid():
            form.save()
            bs_id = a #Bicycle_Storage.objects.get(pk = 14)
            for image in images:
                bs_id = a
                try:
                    photo = Bicycle_Photo(bicycle = bs_id, image = image, user = request.user)
                    photo.save()
                except Exception, e:
                    messages.error(request, smart_str(e)) 
            
            return HttpResponseRedirect('/bicycle/storage/view/')
    else:
        form = BicycleStorage_Form(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_storage.html' , 'text': 'Додати велосипед на зберігання'}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_storage_list(request):
    #list = Bicycle_Order.objects.all().order_by("-date")
    list = Bicycle_Storage.objects.all().order_by("-date")
    context = {'list': list, 'weblink': 'bicycle_storage_list.html', 'next': current_url(request)}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def bicycle_storage_delete(request, id):
    obj = Bicycle_Storage.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle/storage/view/')



# --------------------Dealer company ------------------------
def dealer_add(request):
    a = Dealer()
    if request.method == 'POST':
        form = DealerForm(request.POST, instance = a)
        if form.is_valid():
            name = form.cleaned_data['name']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            street = form.cleaned_data['street']
            www = form.cleaned_data['www']
            description = form.cleaned_data['description']
            director = form.cleaned_data['director']
            Dealer(name=name, country=country, city=city, street=street, www=www, description=description, director=director).save()
            return HttpResponseRedirect('/dealer/view/')
    else:
        form = DealerForm(instance = a)
    #return render_to_response('dealer.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer.html'}, context_instance=RequestContext(request, processors=[custom_proc]))

@csrf_exempt
def dealer_edit(request, id):
    a = Dealer.objects.get(pk=id)
    if request.method == 'POST':
        form = DealerForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dealer/view/')
    else:
        form = DealerForm(instance=a)
    context = {'form': form, 'weblink': 'dealer.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

 
def dealer_del(request, id):
    obj = Dealer.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/dealer/view/')
 
 
def dealer_list(request):
    list = Dealer.objects.all()
    #return render_to_response('dealer_list.html', {'dealers': list.values_list()})
    context = {'dealers': list, 'weblink': 'dealer_list.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def dealer_manager_add(request):
    a = DealerManager()
    if request.method == 'POST':
        form = DealerManagerForm(request.POST, instance = a)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            company = form.cleaned_data['company']
            description = form.cleaned_data['description']
            DealerManager(name=name, email=email, phone=phone, company=company, description=description).save()
            return HttpResponseRedirect('/dealer-manager/view/')
    else:
        form = DealerManagerForm(instance = a)
    #return render_to_response('dealer-manager.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer-manager.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def dealer_manager_edit(request, id):
    a = DealerManager.objects.get(pk=id)
    if request.method == 'POST':
        form = DealerManagerForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dealer-manager/view/')
    else:
        form = DealerManagerForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer-manager.html'}, context_instance=RequestContext(request, processors=[custom_proc]))

 
def dealer_manager_del(request, id):
    obj = DealerManager.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/dealer-manager/view/')
 
 
def dealer_manager_list(request):
    list = DealerManager.objects.all().order_by('company')
    #return render_to_response('dealer-manager_list.html', {'dealer_managers': list.values_list()})
    return render_to_response('index.html', {'dealer_managers': list, 'weblink': 'dealer-manager_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def dealer_payment_add(request):
    a = DealerPayment()
    if request.method == 'POST':
        form = DealerPaymentForm(request.POST, instance = a)
        if form.is_valid():
            dealer_invoice = form.cleaned_data['dealer_invoice']
            invoice_number = form.cleaned_data['invoice_number']
            date = form.cleaned_data['date']
            bank = form.cleaned_data['bank']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            letter = form.cleaned_data['letter']
            desc = form.cleaned_data['description']

            if currency == dealer_invoice.currency:
                if dealer_invoice.price <= price:
                     obj = DealerInvoice.objects.get(id=dealer_invoice.id)
                     obj.payment = True
                     obj.save()
            else:
                if dealer_invoice.currency.id == 3:
                    exchange_dealer = 1
                    d = dealer_invoice.price
                else:
                    try:
                        exchange_dealer = Exchange.objects.get(date=datetime.date.today, currency=str(dealer_invoice.currency.id))
                    except Exchange.DoesNotExist:
                        now = datetime.date.today()
                        html = "<html><body>Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову.</body></html>" % now
                        return HttpResponse(html)

                    d = dealer_invoice.price * float(exchange_dealer.value)
                if currency.id == 3:
                    exchange_pay = 1
                    p = price
                else:
                    try:
                        exchange_pay = Exchange.objects.get(date=datetime.date.today, currency=str(currency.id))
                    except Exchange.DoesNotExist:
                        now = datetime.date.today()
                        html = "<html><body>Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову.</body></html>" % now
                        return HttpResponse(html)
                    
                    p = price * float(exchange_pay.value)
                if d <= p:
                     obj = DealerInvoice.objects.get(id=dealer_invoice.id)
                     obj.payment = True
                     #obj.save()
           
            DealerPayment(dealer_invoice=dealer_invoice, invoice_number=invoice_number, date=date, bank=bank, price=price, currency=currency, letter=letter, description=desc).save()
            return HttpResponseRedirect('/dealer/payment/view/')
    else:
        form = DealerPaymentForm(instance = a)
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer_payment.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

 
def dealer_payment_del(request, id):
    obj = DealerPayment.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/dealer/payment/view/')
 
 
def dealer_payment_list(request):
    list = DealerPayment.objects.all()
    return render_to_response('index.html', {'dealer_payment': list, 'weblink': 'dealer_payment_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))

@csrf_exempt
def dealer_invoice_add(request):
    a = DealerInvoice(date=datetime.date.today())
    if request.method == 'POST':
        form = DealerInvoiceForm(request.POST, instance = a)
        if form.is_valid():
            origin_id = form.cleaned_data['origin_id']
            date = form.cleaned_data['date']
            company = form.cleaned_data['company']
            manager = form.cleaned_data['manager']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            file = form.cleaned_data['file']
            received = form.cleaned_data['received']
            payment = form.cleaned_data['payment']
            description = form.cleaned_data['description']
            DealerInvoice(origin_id=origin_id, date=date, company=company, manager=manager, price=price, currency=currency, file=file, received=received, description=description, payment=payment).save()
            return HttpResponseRedirect('/dealer/invoice/view/')
    else:
        form = DealerInvoiceForm(instance = a)
    context = {'form': form, 'weblink': 'dealer_invoice.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def dealer_invoice_edit(request, id):
    a = DealerInvoice.objects.get(pk=id)
    if request.method == 'POST':
        form = DealerInvoiceForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            mmm = a.date.month
            yyy = a.date.year
            now = datetime.datetime.now()
            #m = now.month
            return HttpResponseRedirect('/dealer/invoice/year/'+str(yyy)+'/month/'+str(mmm)+'/view/')
    else:
        form = DealerInvoiceForm(instance=a)
    context = {'form': form, 'weblink': 'dealer_invoice.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

 
def dealer_invoice_del(request, id):
    obj = DealerInvoice.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/dealer/invoice/view/')
 
 
def dealer_invoice_list(request, id=False, pay='all', year=None):
    if id == False:
        if year :
            list = DealerInvoice.objects.filter(date__year = year)
        else:
            list = DealerInvoice.objects.all()
    else:
        if year :
            print "YEAR = " + str(year)
            list = DealerInvoice.objects.filter(company=id, date__year = year)
        else:
            list = DealerInvoice.objects.filter(company=id)
        if pay == 'paid':
            list = list.filter(company=id, payment=True)
        if pay == 'notpaid':
            list = list.filter(company=id, payment=False)
        if pay == 'sending':
            list = list.filter(company=id, received=False)
        if pay == 'all':
            list = list.filter(company=id)   

    now = datetime.datetime.now()
    year=now.year
            
    exchange = Exchange.objects.filter(date=datetime.date.today())
    try:
        exchange_d = Exchange.objects.get(date=datetime.date.today(), currency=2)
        exchange_e = Exchange.objects.get(date=datetime.date.today(), currency=4)
        summ = 0
        summ_debt = 0
        for e in list: 
        #DealerInvoice.objects.all():
            if e.currency.id == 2:
                summ = summ + (float(e.price) * float(exchange_d.value))
                if e.payment != True:
                    summ_debt = summ_debt + (float(e.price) * float(exchange_d.value))
            if e.currency.id == 4:
                summ = summ + (float(e.price) * float(exchange_e.value))
                if e.payment != True:
                    summ_debt = summ_debt + (float(e.price) * float(exchange_e.value))
            if e.currency.id == 3:
                summ = summ + e.price
                if e.payment != True:
                    summ_debt = summ_debt + e.price
                
        
    except Exchange.DoesNotExist:
        now = datetime.date.today()
        html = "<html><body>Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову.</body></html>" % now
        return HttpResponse(html)
         
        exchange_d = 0
        exchange_e = 0
    company_list = list.values("company", "company__name", "company__color").distinct().order_by("company__pk")        
    yearlist = DealerInvoice.list_objects.get_year_list()
    context = {'dealer_invoice': list, 'sel_company': id, 'sel_year': year, 'exchange': exchange, 'year_list' :yearlist, 'company_list': company_list, 'exchange_d': exchange_d, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'weblink': 'dealer_invoice_list.html', }
    context.update(custom_proc(request))        
    return render(request, 'index.html', context)


def dealer_invoice_list_month(request, year=False, month=False, pay='all'):
#    now = None
    list = None
    now = datetime.datetime.now()
    if month == False:
        month=now.month
    if year == False:
#        now = datetime.datetime.now()
        year=now.year
    if pay == 'paid':
            list = DealerInvoice.objects.filter(date__year=year, payment=True)
    if pay == 'notpaid':
            list = DealerInvoice.objects.filter(date__year=year, payment=False)
    if pay == 'sending':
            list = DealerInvoice.objects.filter(date__year=year, received=False)
    if pay == 'all':
            list = DealerInvoice.objects.filter(date__year=year, date__month=month)                        
    #list = DealerInvoice.objects.filter(date__year=year, date__month=month, payment=)
    exchange = Exchange.objects.filter(date = datetime.date.today())
    try:
        exchange_d = Exchange.objects.get(date=datetime.date.today(), currency=2)
        exchange_e = Exchange.objects.get(date=datetime.date.today(), currency=4)
        summ = 0
        summ_debt = 0
        #DealerInvoice.objects.filter(date__year=year, date__month=month):
        for e in list:
            if e.currency.id == 2:
                summ = summ + (float(e.price) * float(exchange_d.value))
                if e.payment != True:
                    summ_debt = summ_debt + (float(e.price) * float(exchange_d.value))
            if e.currency.id == 4:
                summ = summ + (float(e.price) * float(exchange_e.value))
                if e.payment != True:
                    summ_debt = summ_debt + (float(e.price) * float(exchange_e.value))
            if e.currency.id == 3:
                summ = summ + e.price
                if e.payment != True:
                    summ_debt = summ_debt + e.price
    except Exchange.DoesNotExist:
        html = "Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову" % now.strftime('%d-%m-%Y %H:%m')
        context = {'weblink': 'error_message.html', 'mtext': html}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
        exchange_d = 0
        exchange_e = 0
    company_list = list.values("company", "company__name", "company__color").distinct().order_by("company__pk")        
    yearlist = DealerInvoice.list_objects.get_year_list()
    context = {'dealer_invoice': list, 'exchange': exchange, 'exchange_d': exchange_d, 'year_list' :yearlist, 'company_list': company_list, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'sel_month':month, 'sel_year':year, 'weblink': 'dealer_invoice_list.html', 'next': current_url(request)}
    context.update(custom_proc(request))    
    return render(request, 'index.html', context)


def dealer_invoice_list_year(request, year=False, pay='all'):
    now = datetime.datetime.now()
    if year == False:
        year=now.year
    list = None
    if pay == 'paid':
            list = DealerInvoice.objects.filter(date__year=year, payment=True)
    if pay == 'notpaid':
            list = DealerInvoice.objects.filter(date__year=year, payment=False)
    if pay == 'sending':
            list = DealerInvoice.objects.filter(date__year=year, received=False)
    if pay == 'all':
            list = DealerInvoice.objects.filter(date__year=year)                        
    #list = DealerInvoice.objects.filter(date__year=year, date__month=month, payment=)
    exchange = Exchange.objects.filter(date=datetime.date.today)
    try:
        exchange_d = Exchange.objects.get(date=datetime.date.today, currency=2)
        exchange_e = Exchange.objects.get(date=datetime.date.today, currency=4)
        summ = 0
        summ_debt = 0
        #DealerInvoice.objects.filter(date__year=year, date__month=month):
        for e in list:
            if e.currency.id == 2:
                summ = summ + (float(e.price) * float(exchange_d.value))
                if e.payment != True:
                    summ_debt = summ_debt + (float(e.price) * float(exchange_d.value))
            if e.currency.id == 4:
                summ = summ + (float(e.price) * float(exchange_e.value))
                if e.payment != True:
                    summ_debt = summ_debt + (float(e.price) * float(exchange_e.value))
            if e.currency.id == 3:
                summ = summ + e.price
                if e.payment != True:
                    summ_debt = summ_debt + e.price
                    
    except Exchange.DoesNotExist:
        html = "Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову" % now.strftime('%d-%m-%Y %H:%m')
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': html, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        #exchange_d = 0
        #exchange_e = 0
    company_list = list.values("company", "company__name", "company__color").distinct().order_by("company__pk")
    yearlist = DealerInvoice.list_objects.get_year_list()
    return render_to_response('index.html', {'dealer_invoice': list, 'exchange': exchange, 'exchange_d': exchange_d, 'year_list' :yearlist, 'company_list': company_list, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'sel_year':year, 'weblink': 'dealer_invoice_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))



def dealer_invoice_search(request):
    #query = request.GET.get('q', '')
    context = {'weblink': 'dealer_invoice_search.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html',  context)


def dealer_invoice_search_result(request):
    list = None
    exchange = None
    if 'number' in request.GET and request.GET['number']:
         num = request.GET['number']
         list = DealerInvoice.objects.filter(origin_id__icontains = num)
     #list1 = DealerInvoice.objects.all()
    #return render_to_response('index.html', {'invoice_list': list, 'weblink': 'dealer_invoice_list_search.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    else:
        pass
    now = datetime.datetime.now()
    dnow = datetime.datetime.today()
    exchange = Exchange.objects.filter(date=datetime.date.today())
    try:
        exchange_d = Exchange.objects.get(date=datetime.date.today(), currency=2)
        exchange_e = Exchange.objects.get(date=datetime.date.today(), currency=4)
        summ = 0
        summ_debt = 0
        #DealerInvoice.objects.filter(date__year=year, date__month=month):
        for e in list:
            if e.currency.id == 2:
                summ = summ + (float(e.price) * float(exchange_d.value))
                if e.payment != True:
                    summ_debt = summ_debt + (float(e.price) * float(exchange_d.value))
            if e.currency.id == 4:
                summ = summ + (float(e.price) * float(exchange_e.value))
                if e.payment != True:
                    summ_debt = summ_debt + (float(e.price) * float(exchange_e.value))
            if e.currency.id == 3:
                summ = summ + e.price
                if e.payment != True:
                    summ_debt = summ_debt + e.price
                    
    except Exchange.DoesNotExist:
        html = "Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову" % dnow.strftime('%d-%m-%Y %H:%m')
        context = {'weblink': 'error_message.html', 'mtext': html, 'next': current_url(request)}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    company_list = list.values("company", "company__name", "company__color").distinct().order_by("company__pk")
    yearlist = DealerInvoice.list_objects.get_year_list()
    context = {'dealer_invoice': list, 'exchange': exchange, 'exchange_d': exchange_d, 'year_list' :yearlist, 'search_text': num, 'company_list': company_list, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'sel_year':now.year, 'weblink': 'dealer_invoice_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


@csrf_exempt
def dealer_invoice_set(request, id = None):
    if auth_group(request.user, 'admin')==False:
        #return HttpResponse('Error: У вас не має прав для редагування', content_type="text/plain;charset=UTF-8;charset=UTF-8")
        return HttpResponse(simplejson.dumps({'msg': 'Error: У вас не має прав для редагування'}), content_type="application/json")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):        
                id = request.POST.get('id')
                di_obj = DealerInvoice.objects.get(pk = id)
                di_obj.received = not (di_obj.received)
                di_obj.save()
                if di_obj.received:
                    status_msg = "Отримано"
                else:
                    status_msg = "В дорозі"
                #return HttpResponse('Ваш запит виконано', content_type="text/plain;charset=UTF-8;charset=UTF-8")
                return HttpResponse(simplejson.dumps({'status': di_obj.received, 'msg': status_msg}), content_type="application/json")
    else:
         di_obj = DealerInvoice.objects.get(pk = id)
         di_obj.received = not (di_obj.received)
         di_obj.save()
    return HttpResponseRedirect('/dealer/invoice/view/')
        #return HttpResponse('Ваш запит відхилено. Щось пішло не так', content_type="text/plain;charset=UTF-8;charset=UTF-8", status=401)
    #    return HttpResponse(simplejson.dumps({'msg':'Ваш запит відхилено. Щось пішло не так'}), content_type="application/json", status=401)


def invoice_new_item(request):
    date=datetime.date.today()
    start_date = datetime.date(date.year, 1, 1)
    end_date = datetime.date(date.year, 3, 31)    
    di = DealerInvoice.objects.filter(received = False).values_list("id", flat=True)
    nday = settings.NEW_INVOICE_SHOW_DAY #14
    list_comp = InvoiceComponentList.objects.filter(invoice__date__gt = date - datetime.timedelta(days=int(nday)), invoice__id__in = di).order_by("invoice__id")
    context = {'dinvoice_list': list_comp, 'weblink': 'dealer_invoice_new_item.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)  


def invoice_miss_stuff(request):
    date=datetime.date.today()
    start_date = datetime.date(date.year, 1, 1)
    end_date = datetime.date(date.year, 3, 31)    
    di = DealerInvoice.objects.filter(received = False).values_list("id", flat=True)
    nday = 180
    list_comp = InvoiceComponentList.objects.filter(invoice__date__gt = date - datetime.timedelta(days=int(nday)), invoice__id__in = di).exclude(rcount = F('count')).order_by("invoice__id")
    context = {'dinvoice_list': list_comp, 'weblink': 'dealer_invoice_new_item.html', }
    context.update(custom_proc(request))     
    return render(request, 'index.html', context)  
    
    

#-------------- InvoiceComponentList -----------------------
@csrf_exempt
def invoicecomponent_add(request, mid=None, cid=None, id=None):
#    company_list = Manufacturer.objects.all()
    price = 0
    ci_id = None
    if cid<>None:
        #a = InvoiceComponentList(date=datetime.date.today(), price=0, count=1, currency=Currency.objects.get(id=2), invoice=DealerInvoice.objects.get(id=187), catalog=Catalog.objects.get(id=cid))
        c = Catalog.objects.get(id=cid)        
        a = InvoiceComponentList(date=datetime.date.today(), price=0, count=1, currency=Currency.objects.get(id=2), invoice=DealerInvoice.objects.get(id=187), catalog = c)
        price = c.price
    else:    
        a = InvoiceComponentList(date=datetime.date.today(), price=0, count=1, currency=Currency.objects.get(id=2), invoice=DealerInvoice.objects.get(id=187))
    if id <> None:
        a = InvoiceComponentList.objects.get(pk = id)          
        cid = a.catalog.pk              
        ci_id = a.invoice.pk
    if request.method == 'POST':
        #form = InvoiceComponentListForm(request.POST, instance = a, test1=mid, catalog_id=cid)
        form = InvoiceComponentListForm(request.POST, instance = a, catalog_id=cid, ci_id = ci_id)
        if form.is_valid():
            invoice = form.cleaned_data['invoice']
            date = form.cleaned_data['date']
            catalog = form.cleaned_data['catalog']
            count = form.cleaned_data['count']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            description = form.cleaned_data['description']
            form.save()
            #InvoiceComponentList(date=date, invoice=invoice, catalog=catalog, price=price, currency=currency, count=count, description=description).save()
            
            cat = Catalog.objects.get(id = cid)
            cat.count = cat.count + count
            cat.save()
            return HttpResponseRedirect(reverse('serch-invoicecomponennts-by-id', args=[cat.pk]))
    else:
        form = InvoiceComponentListForm(instance = a, catalog_id=cid, ci_id = ci_id)
        #form = InvoiceComponentListForm(instance = a, test1=mid, catalog_id=cid)
#    return render_to_response('index.html', {'form': form, 'weblink': 'invoicecomponent.html', 'price_ua': price, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    context = {'form': form, 'weblink': 'invoicecomponent.html', 'price_ua': price}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def invoicecomponent_sales_list(request, mid=None, cid=None, month=None, all=None):
    company_name = '' 
    type_name = ''
    list = None # QuerySet
    id_list = []
    zsum = 0
    zcount = 0
    head_text = u'Повністю продані товари за останні %s місяців' % month
    head_text_array = []
    attr_ids_list = []
    list_res = None
    attr_ids_str = ""
#    all = False
    new_list = []
    years_range  = None
    sale_list = None
    curdate = datetime.datetime.now()
    sel_year = 0#= curdate.year
    url_name = None

    test_m = int(month)
#    add_m = add_months(curdate, test_m)
#    print "ADD month date = %s " % add_m
    sub_m = sub_months(curdate, test_m)
    print "SUB month date = %s " % sub_m

    if month:
        #dd = datetime.datetime(2024, 11, 1)
        sale_list = ClientInvoice.objects.filter(date__gte = sub_m)
        #sale_list = ClientInvoice.objects.filter(date__gte = dd)
    else:
        sale_list = ClientInvoice.objects.filter(date__month = curdate.month)
    list = InvoiceComponentList.objects.filter(catalog__clientinvoice__in = sale_list)
    if mid:
        if all == True:
            list = list.filter(catalog__manufacturer__id = mid)
        else:
            list = list.filter(catalog__manufacturer__id = mid).exclude(catalog__count__gt = 0)            
        company_name = Manufacturer.objects.get(id = mid)
        url_name = 'invoice-manufacture-by-year-all'
    if cid:
        if all == True:        
            list = list.filter(catalog__type__id = cid)
            head_text = u'Продані товари за останні %s місяців' % month
        else:
            head_text = u'Повністю продані товари за останні %s місяців' % month
            list = list.filter(catalog__type__id = cid).exclude(catalog__count__gt = 0)
            sale_list = sale_list.filter(catalog__type__id = cid)
        type_name = Type.objects.get(id=cid)
        url_name = 'invoice-category-by-year-all'
    
#    list_res_val = list.values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
    list_res = list.values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').annotate(sum_catalog=Sum('count')).order_by('catalog')
#    print "RES list wOut annotate - %s " % list_res_val.count() 
#    list_res = list_res_val.annotate(sum_catalog=Sum('count'))

    for item in list_res:
        id_list.append(item['catalog'])
    
    if auth_group(request.user, 'admin')==True:
        years_range = ClientInvoice.objects.filter(catalog__in=id_list).extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Sum('count')).order_by('yyear')

    sale_list = sale_list.filter(catalog__in=id_list).values('catalog', 'catalog__price').annotate(sum_catalog=Sum('count')).order_by('catalog')        
    cat_list = Catalog.objects.filter(pk__in=id_list).values('type__name_ukr', 'description', 'locality', 'id', 'manufacturer__id', 'manufacturer__name', 'photo_url', 'youtube_url', 'last_update', 'user_update__username')

    for element in list_res:
        element['balance']=element['sum_catalog']
        element['c_sale']=0
        for sale in sale_list:
            if element['catalog']==sale['catalog']:
                element['c_sale']=sale['sum_catalog']
                element['balance']=element['sum_catalog'] - element['c_sale']
        for cat in cat_list:
            if element['catalog']==cat['id']:
                element['manufacturer__id']=cat['manufacturer__id']
                element['manufacturer__name']=cat['manufacturer__name']
                element['locality']=cat['locality']
                element['type__name_ukr']=cat['type__name_ukr']
                element['description']=cat['description']
                element['photo_url']=cat['photo_url']
                element['youtube_url']=cat['youtube_url']
                element['last_update']=cat['last_update']
                element['user_update']=cat['user_update__username']
        
        if element['balance']!=0:
#            new_list.append(element)
            zsum = zsum + (element['balance'] * element['catalog__price'])
            zcount = zcount + element['balance']
            cat_obj = Catalog.objects.get(pk = element['catalog'])
            element['new_arrival'] = cat_obj.new_arrival()
            element['get_realshop_count'] = cat_obj.get_realshop_count()
            element['balance'] = cat_obj.get_realshop_count()
            element['get_discount'] = cat_obj.get_discount()
            element['invoice_price'] = cat_obj.invoice_price()
            element['box_name'] = cat_obj.get_storage_box_list_to_html()
#    print "RES list in return - %s " % list_res.count()
    cur_year = datetime.date.today().year
    #'qsearch_lookup' : mc_search,        
    vars = {'year_url_name': url_name, 'componentlist': list_res, 'zsum':zsum, 'zcount':zcount, 'company_name': company_name, 'company_id': mid, 'category_id': cid, 'category_name':type_name, 'years_range':years_range, 'cur_year': cur_year, 'select_year': sel_year, 'weblink': 'invoicecomponent_list.html', 'head_text': head_text, 'head_text_array': head_text_array, 'attr_ids_str': attr_ids_str}
    vars.update(custom_proc(request))
    return render(request, 'index.html', vars)



def invoicecomponent_list(request, mid=None, cid=None, isale=None, attr_id=None, attr_val_id=None, attr_val_ids=None, limit=0, focus=0, upday=0, sel_year=0, enddate=None, all=False, mc_search=False, by_id=None, url_name=None):
    #company_list = Manufacturer.objects.none()
    company_list = Manufacturer.objects.all().only('id', 'name')
    #type_list = Type.objects.none() 
    type_list = Type.objects.all()
    company_name = '' 
    cat_name = ''
    list = None # QuerySet
    id_list = []
    zsum = 0
    zcount = 0
    head_text = ''
    head_text_array = []
    attr_ids_list = []
    list_res = None
    attr_ids_str = ""
      
# Search by Name field    
    if 'name' in request.GET and request.GET['name']:
        name = request.GET['name'].strip()
        if len(name) <= 1:
            context = {'weblink': 'error_message.html', 'mtext': u'[%s] Введіть більше символів  для пошуку' % name, }
            context.update(custom_proc(request))
            return render(request, 'index.html', context)
        if name.isdigit() == True and (len(name) >= 12):
            id = name
#            list = InvoiceComponentList.objects.filter( Q(catalog__barcode__icontains=id) | Q(catalog__barcode_upc__icontains=id) | Q(catalog__barcode_ean__icontains=id) ).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')#.order_by('catalog__pk')            
            list = InvoiceComponentList.objects.filter( Q(catalog__barcode__icontains=id) | Q(catalog__barcode_upc__icontains=id) | Q(catalog__barcode_ean__icontains=id) )            
        else:
            list = InvoiceComponentList.objects.filter(catalog__name__icontains=name)        
            #list = InvoiceComponentList.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__dealer_code', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
# Search by Id field
    elif  'id' in request.GET and request.GET['id']:
        id = request.GET['id'].strip()
        if len(id) <= 1:
            context = {'weblink': 'error_message.html', 'mtext': u'[%s] Введіть більше символів  для пошуку' % id, }
            context.update(custom_proc(request))
            return render(request, 'index.html', context)
#        print ("Get id - OK | %s|" % id)
        if id.isdigit() == True and (len(id) >= 12):
#            print " is Barcode = %s" % id
            list = InvoiceComponentList.objects.filter( Q(catalog__barcode__icontains=id) | Q(catalog__barcode_upc__icontains=id) | Q(catalog__barcode_ean__icontains=id) )            
            #list = InvoiceComponentList.objects.filter( Q(catalog__barcode__icontains=id) | Q(catalog__barcode_upc__icontains=id) | Q(catalog__barcode_ean__icontains=id) ).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')#.order_by('catalog__pk')            
        try:
            # Parse QR code from item
            id_res = re.search(r"(?<=rivelo.com.ua/component/)[0-9]+", id.lower()).group()
            list = InvoiceComponentList.objects.filter(Q(catalog__id=id_res))            
#            list = InvoiceComponentList.objects.filter(Q(catalog__id=id_res)).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')            
        except:
            if not list:               
                list = InvoiceComponentList.objects.filter(Q(catalog__ids__icontains=id) | Q(catalog__dealer_code__icontains=id) | Q(catalog__manufacture_article__icontains=id) ).order_by('catalog__manufacturer')
#                list = InvoiceComponentList.objects.filter(Q(catalog__ids__icontains=id) | Q(catalog__dealer_code__icontains=id) | Q(catalog__manufacture_article__icontains=id) ).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').order_by('catalog__manufacturer')                
    if by_id:
        list = InvoiceComponentList.objects.filter(catalog__id = by_id)        
#        list = InvoiceComponentList.objects.filter(catalog__id = by_id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')        

    if list == None:
        list = InvoiceComponentList.objects.all()

    if mid:
        if all == True:
            list = list.filter(catalog__manufacturer__id=mid)
#            list = InvoiceComponentList.objects.filter(catalog__manufacturer__id=mid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')            
        else:
#            list = InvoiceComponentList.objects.filter(catalog__manufacturer__id=mid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').exclude(catalog__count = 0)
            list = list.filter(catalog__manufacturer__id=mid).exclude(catalog__count = 0)            
        company_name = Manufacturer.objects.get(id=mid)
    if cid:
        if all == True:        
            list = list.filter(catalog__type__id=cid)
            #list = InvoiceComponentList.objects.filter(catalog__type__id=cid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')            
        else:
            list = list.filter(catalog__type__id=cid).exclude(catalog__count = 0)
#            list = InvoiceComponentList.objects.filter(catalog__type__id=cid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').exclude(catalog__count = 0)            
        cat_name = type_list.get(id=cid)
    if attr_val_id:
        cav = CatalogAttributeValue.objects.filter(id = attr_val_id).values('value', 'value_float', 'attr_id__name')
        head_text = cav.first()['attr_id__name'] + ' >>> ' + cav.first()['value']
        if all == True:        
            list = list.filter(catalog__attributes__id=attr_val_id)
#            list = InvoiceComponentList.objects.filter(catalog__attributes__id=attr_val_id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')            
        else:
            list = list.filter(catalog__attributes__id=attr_val_id).exclude(catalog__count = 0)
#            list = InvoiceComponentList.objects.filter(catalog__attributes__id=attr_val_id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').exclude(catalog__count = 0)
    if attr_val_ids:
        f_str_ids = re.findall("[\+]\d+", attr_val_ids)
        for i in f_str_ids:
            attr_ids_list.append(i.split('+')[1])
        cav = CatalogAttributeValue.objects.filter(id__in = attr_ids_list).values('value', 'value_float', 'attr_id__name', 'pk')
        for i in cav:
            tmp_text = i['attr_id__name'] + ' >>> ' + i['value']
            head_text_array.append({'id': i['pk'], 'txt': tmp_text})
            attr_ids_str += "+" + str(i['pk'])
        for i in attr_ids_list:
            if all == True:        
                list = list.filter(catalog__attributes__id = i)
            #list = InvoiceComponentList.objects.filter(catalog__attributes__id__in = attr_ids_list).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')            
            else:
                list = list.filter(catalog__attributes__id = i).exclude(catalog__count = 0)
            #list = InvoiceComponentList.objects.filter(catalog__attributes__id__in = attr_ids_list).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').exclude(catalog__count = 0)
    if attr_id:
        ca = CatalogAttribute.objects.filter(id = attr_id).values('name')
        head_text = ca.first()['name']
        if all == True:        
            list = list.filter(catalog__attributes__attr_id=attr_id)
#            list = InvoiceComponentList.objects.filter(catalog__attributes__attr_id=attr_id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')            
        else:
            list = list.filter(catalog__attributes__attr_id=attr_id).exclude(catalog__count = 0)
#            list = InvoiceComponentList.objects.filter(catalog__attributes__attr_id=attr_id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').exclude(catalog__count = 0)            

    if isale == True:
        list = list.filter(catalog__sale__gt = 0)
#        list = InvoiceComponentList.objects.filter(catalog__sale__gt = 0).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
    if enddate == True:
        list = list.filter(catalog__date__isnull = False, catalog__count__gt = 0).order_by('-catalog__date')
#        list = InvoiceComponentList.objects.filter(catalog__date__isnull = False, catalog__count__gt = 0).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update', 'catalog__date').order_by('-catalog__date')        
    if upday != 0:
        curdate=datetime.datetime.today()
        update = curdate - datetime.timedelta(days=int(upday))
        list = list.filter(catalog__last_update__gt = update)
#        list = InvoiceComponentList.objects.filter(catalog__last_update__gt = update).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')        
        
#    list_res = list.values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')    
    list_res = list.values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
    if limit == 0:
        try:
            if enddate == True:
                list_res = list_res.annotate(sum_catalog=Sum('count')).order_by("catalog__date")
            else:
                list_res = list_res.annotate(sum_catalog=Sum('count')).order_by("catalog__type")
        except:
            list_res = InvoiceComponentList.objects.none()
    else:
        list_res = list_res.annotate(sum_catalog=Sum('count')).order_by("catalog__type")
#        list_res = list.values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__dealer_code', 'catalog__sale', 'catalog__count', 'catalog__type__id', 'catalog__description').order_by("catalog")
#        list_res = InvoiceComponentList.objects.all().values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__dealer_code', 'catalog__sale', 'catalog__count', 'catalog__type__id', 'catalog__description').annotate(sum_catalog=Sum('count')).order_by("catalog__type")        
#        list = InvoiceComponentList.objects.all().values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price', 'catalog__sale', 'catalog__count', 'catalog__type__id').annotate(sum_catalog=Sum('count')).order_by("catalog__type")
        list_res = list_res[:limit]


    for item in list_res:
        id_list.append(item['catalog'])

    new_list = []
    years_range  = None
    sale_list = None
    if auth_group(request.user, 'admin')==True:
        years_range = ClientInvoice.objects.filter(catalog__in=id_list).extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Sum('count')).order_by('yyear')
        #years_range = ClientInvoice.objects.filter(catalog__in=id_list).extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('yyear')
    if sel_year > 0:
        sale_list = ClientInvoice.objects.filter(catalog__in=id_list, date__year = sel_year).values('catalog', 'catalog__price').annotate(sum_catalog=Sum('count')).order_by('catalog')
        #years_range = ClientInvoice.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id'))
    else:
        sale_list = ClientInvoice.objects.filter(catalog__in=id_list).values('catalog', 'catalog__price').annotate(sum_catalog=Sum('count')).order_by('catalog')

    cat_list = Catalog.objects.filter(pk__in=id_list).values('type__name_ukr', 'description', 'locality', 'id', 'manufacturer__id', 'manufacturer__name', 'photo_url', 'youtube_url', 'last_update', 'user_update__username')        
#    arrive_list = Catalog.objects.filter(pk__in = id_list).new_arrival()
    for element in list_res:
        element['balance']=element['sum_catalog']
        element['c_sale']=0
        for sale in sale_list:
            if element['catalog']==sale['catalog']:
                element['c_sale']=sale['sum_catalog']
                element['balance']=element['sum_catalog'] - element['c_sale']
#                element['new_arrival'] = Catalog.objects.get(pk = element['catalog']).new_arrival()
#                element['invoice_price'] = Catalog.objects.get(pk = element['catalog']).invoice_price()
        for cat in cat_list:
            if element['catalog']==cat['id']:
                element['manufacturer__id']=cat['manufacturer__id']
#                element['manufacturer__name1']=cat['manufacturer__name']
                element['manufacturer__name']=cat['manufacturer__name']
                element['locality']=cat['locality']
                element['type__name_ukr']=cat['type__name_ukr']
                element['description']=cat['description']
                element['photo_url']=cat['photo_url']
                element['youtube_url']=cat['youtube_url']
                element['last_update']=cat['last_update']
                element['user_update']=cat['user_update__username']
        
        if element['balance']!=0:
            new_list.append(element)
            zsum = zsum + (element['balance'] * element['catalog__price'])
            zcount = zcount + element['balance']
            cat_obj = Catalog.objects.get(pk = element['catalog'])
            element['new_arrival'] = cat_obj.new_arrival()
            element['get_realshop_count'] = cat_obj.get_realshop_count()
            element['get_discount'] = cat_obj.get_discount()
            element['invoice_price'] = cat_obj.invoice_price()
            element['box_name'] = cat_obj.get_storage_box_list_to_html()
#            element['invoice_price'] = Catalog.objects.get(pk = element['catalog']).invoice_price()
#        if element['balance'] == 0:
#            print "Element = " + str(element)
    cur_year = datetime.date.today().year        
    #url_name = 'invoice-category-manufacture-by-year'
    vars = {'year_url_name': url_name, 'company_list': company_list, 'type_list': type_list, 'componentlist': list_res, 'zsum':zsum, 'zcount':zcount, 'company_name': company_name, 'company_id': mid, 'category_id': cid, 'category_name':cat_name, 'years_range':years_range, 'cur_year': cur_year, 'select_year': sel_year, 'weblink': 'invoicecomponent_list.html', 'focus': focus, 'qsearch_lookup' : mc_search, 'head_text': head_text, 'head_text_array': head_text_array, 'attr_ids_str': attr_ids_str}
    vars.update(custom_proc(request))
    return render(request, 'index.html', vars)


@csrf_exempt
def invoicecomponent_print(request):
    list = None
    id_list=[]
    map_id = []
    result_str = ''
    
    if 'ids' in request.POST and request.POST['ids']:
        id_list = request.POST['ids'].split(',')
#        map_id = map(int, id_list)
        list = Catalog.objects.filter(id__in = id_list).values('name', 'ids', 'manufacturer__name', 'price', 'sale', 'count', 'type__name').order_by('manufacturer')
    else:
        return HttpResponse("Не вибрано жодного товару", content_type="text/plain;charset=UTF-8;")
    response = HttpResponse()
#    result_str = u'Назва: '
#    response.write(u"<table>")
#    response.write(u"<tr> <td>Артикул</td> <td>Виробник</td> <td>Назва</td> <td>Ціна</td> <td>Знижка %</td> <td>Нова ціна</td> </tr>")
    for i in list:
#        response.write("<tr>")
        new_price = float(i['price']) / 100.0 * (100 - int(i['sale']))
 #       response.write("<td>"+ i['ids'] +"</td><td>"+ i['manufacturer__name'] +"</td><td>"+ i['name'] +"</td><td>" + str(i['price']) +u" грн.</td><td>"+ str(i['sale']) +"</td><td>"+ str(new_price) +u" грн.</td>")
        #response.write("<td>"+ i['ids'] +"</td><td>"+ i['name'] +"</td><td>" + i['ids'] +u" грн.</td><td>"+i['ids'] +"</td><td>") #+ str(new_price) +"</td>")
  #      response.write("</tr>")
        result_str = result_str + u'Товар: '
        result_str =  result_str + "[" + i['ids'] + "] ("  + i['manufacturer__name']+ ") " + i['name'] + "\n"
        if int(i['sale']) == 0:
            result_str = result_str + u"Ціна: " + str(i['price']) + u" грн. \n"
        else:
            result_str = result_str + u"Ціна: " + str(i['price']) + u" грн. \n"    
            result_str = result_str + u"Нова ціна: " + str(new_price) + u" грн. \n" 
        result_str = result_str + '\n'
    #response.write("</table>")
    response.write(result_str)
#    response = response.replace("<", "[")
#    response = response.replace(">", "]")
    return response


def invoicecomponent_manufacturer_html(request, mid):
    email = ""
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'admin')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('email'):        
                email = request.POST.get('email')
    list = Catalog.objects.filter(manufacturer__id=mid, count__gt=0).order_by('type__id')
    zcount = 0
    for elem in list:
        zcount = zcount + elem.count
    if mid == None:
        company_name = ""
    else:
        company_name = Manufacturer.objects.get(id=mid)
    w = render_to_response('component_list_by_manufacturer_html.html', {'componentlist': list, 'company_name': company_name, 'zcount': zcount})        
#    return render_to_response('index.html', {'componentlist': list, 'company_name': company_name, 'zcount': zcount, 'weblink': 'component_list_by_manufacturer_html.html'})
    send_shop_mail(request, email, w, 'Наявний товар')
    return HttpResponse('Ваш лист відправлено', content_type="ttext/plain;charset=UTF-8;")

# send Email all in shop by category
def invoicecomponent_category_html(request, mid): 
#    if auth_group(request.user, 'admin') == False:
#        return HttpResponseRedirect("/.")
    email = ""
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'admin')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('email'):        
                email = request.POST.get('email')
    list = Catalog.objects.filter(type__id=mid, count__gt=0).order_by('manufacturer__id')
    zcount = 0
    for elem in list:
        zcount = zcount + elem.count
    if mid == None:
        category = ""
    else:
        category = Type.objects.get(id=mid)
    w = render_to_response('component_list_by_type_html.html', {'componentlist': list, 'type_name': category, 'zcount': zcount})
#    w = render_to_response('index.html', {'componentlist': list, 'type_name': category, 'zcount': zcount, 'weblink': 'component_list_by_type_html.html'})
    send_shop_mail(request, email, w, 'Наявний товар')
    return HttpResponse('Ваш лист відправлено')
    #return render_to_response('index.html', {'componentlist': list, 'type_name': category, 'zcount': zcount, 'weblink': 'component_list_by_type_html.html'})


def invoicecomponent_sum(request):
    if auth_group(request.user, 'admin') == False:
        return HttpResponseRedirect("/.")
#    list = InvoiceComponentList.objects.all().aggregate(price_sum=Sum('catalog__price'))
    list = Catalog.objects.filter(count__gt=0).values('id', 'name', 'count', 'price').order_by("count")
    #.annotate(sum_catalog=Sum('count'))
    #aggregate(price_sum=Sum('count'))
    psum = 0
    scount = 0
    counter = 0
    for item in list:
        scount = scount + item['count']
        psum = psum + (item['price'] * item['count'])
        counter = counter + 1
    paginator = Paginator(list, 100)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        catalog = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        catalog = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        catalog = paginator.page(paginator.num_pages)
        
    return render(request, 'index.html', {'allpricesum':psum, 'countsum': scount, 'counter': counter, 'catalog': catalog, 'weblink': 'invoicecomponent_report.html', 'next': current_url(request)})


def invoicecomponent_del(request, id):
    obj = InvoiceComponentList.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    cat = Catalog.objects.get(id = obj.catalog.id)
    cat.count = cat.count - obj.count
    cat.save()
    return HttpResponseRedirect(reverse('serch-invoicecomponennts-by-id', args=[cat.pk]))

@csrf_exempt
def invoicecomponent_edit(request, id):
    a = InvoiceComponentList.objects.get(id=id)
    old_count = a.count
    cid = a.catalog.id
    if request.method == 'POST':
        #form = InvoiceComponentListForm(request.POST, instance=a)
        form = InvoiceComponentListForm(request.POST, instance=a, catalog_id=cid)
        if form.is_valid():
            invoice = form.cleaned_data['invoice']
            date = form.cleaned_data['date']
            catalog = form.cleaned_data['catalog']
            count = form.cleaned_data['count']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            description = form.cleaned_data['description']
            form.save()
            cat = Catalog.objects.get(id = cid)
            cat.count = cat.count + count - old_count
            cat.save()
            #return HttpResponseRedirect('/invoice/list/10/view/')
            return HttpResponseRedirect(reverse('serch-invoicecomponennts-by-id', args=[cat.pk]))
    else:
        form = InvoiceComponentListForm(instance=a, catalog_id=cid)
        #form = InvoiceComponentListForm(instance=a)
    context = {'form': form, 'weblink': 'invoicecomponent.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

# Сторінка для пошуку наявного товару в магазині за його кодом або назвою
def invoice_search(request):
    return render(request, 'index.html', {'weblink': 'invoice_search.html', 'next': current_url(request)})

# Пошук товару по назві і артикулу (стара функція)
#===============================================================================
# def invoice_search_result(request):
#     list = None
#     psum = 0
#     zsum = 0
#     scount = 0
#     zcount = 0
#     id_list = []
#     if 'name' in request.GET and request.GET['name']:
#         name = request.GET['name']
#         #list = Catalog.objects.filter(name__icontains = name).order_by('manufacturer') 
# #        list = InvoiceComponentList.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price', 'catalog__sale').annotate(sum_catalog=Sum('count'))
#         list = InvoiceComponentList.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__manufacturer__id', 'catalog__price', 'catalog__sale', 'catalog__description', 'catalog__type__id').annotate(sum_catalog=Sum('count'))        
#     elif  'id' in request.GET and request.GET['id']:
#         id = request.GET['id']
#         #list = InvoiceComponentList.objects.filter(catalog__ids__icontains=id)
# #        list = InvoiceComponentList.objects.filter(catalog__ids__icontains=id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__manufacturer__id', 'catalog__price', 'catalog__sale', 'catalog__description', 'catalog__type__id').annotate(sum_catalog=Sum('count')) 
#         list = InvoiceComponentList.objects.filter(Q(catalog__ids__icontains=id) | Q(catalog__dealer_code__icontains=id)).values('catalog').annotate(sum_catalog=Sum('count')).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__manufacturer__id', 'catalog__price', 'catalog__sale', 'catalog__description', 'catalog__type__id', 'sum_catalog', 'catalog__dealer_code')
# #        list = InvoiceComponentList.objects.filter(catalog__ids__icontains=id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__manufacturer__id', 'catalog__price', 'catalog__sale', 'catalog__type__id').annotate(sum_catalog=Sum('count'))        
#         #list = Catalog.objects.filter(ids__icontains = id).order_by('manufacturer')
# 
#     for item in list:
#         psum = psum + (item['catalog__price'] * item['sum_catalog'])
#         scount = scount + item['sum_catalog']
#         id_list.append(item['catalog'])
# #        list_sale = ClientInvoice.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price').annotate(sum_catalog=Sum('count'))
# #        list_sale = ClientInvoice.objects.filter(catalog__in=id_list).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price').annotate(sum_catalog=Sum('count'))
#     sale_list = ClientInvoice.objects.filter(catalog__in=id_list).values('catalog', 'catalog__price', 'catalog__type__name', 'catalog__type__id', 'catalog__locality').annotate(sum_catalog=Sum('count'))        
#     for element in list:
#         element['c_sale']=0
#         for sale in sale_list:
#             if element['catalog']==sale['catalog']:
#                 element['c_sale']=sale['sum_catalog']
#                 element['catalog__type__name'] = sale['catalog__type__name']                
#                 element['catalog__type__id'] = sale['catalog__type__id']
#                 element['catalog__locality'] = sale['catalog__locality']
#         if element.get('catalog__type__name') == None:
#             element['catalog__type__name'] = Catalog.objects.values('type__name').get(id=element['catalog'])['type__name']
#         element['balance']=element['sum_catalog'] - element['c_sale']                
#         zsum = zsum + ((element['sum_catalog'] - element['c_sale']) * element['catalog__price'])
#         zcount = zcount + (element['sum_catalog'] - element['c_sale'])
# #        return render_to_response('index.html', {'componentlist': list, 'salelist': list_sale, 'allpricesum':psum, 'zsum':zsum, 'zcount':zcount, 'countsum': scount, 'weblink': 'invoicecomponent_list_test.html'})
# 
#     category_list = Type.objects.filter(name_ukr__isnull=False).order_by('name_ukr')
#     company_list = Manufacturer.objects.all()
#     return render_to_response('index.html', {'company_list': company_list, 'category_list': category_list, 'componentlist': list, 'allpricesum':psum, 'zsum':zsum, 'zcount':zcount, 'countsum': scount, 'weblink': 'invoicecomponent_list_test.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
#     #return render_to_response('index.html', {'componentlist': list, 'allpricesum':psum, 'countsum': scount, 'weblink': 'invoicecomponent_list.html'})        
#===============================================================================


def invoice_report(request):
    #list = InvoiceComponentList.objects.all().order_by('-id')[:10]
    
    query = '''select accounting_invoicecomponentlist.id, count(*) as ccount, accounting_invoicecomponentlist.invoice_id as invoice, sum(accounting_invoicecomponentlist.price*accounting_invoicecomponentlist.count) as suma, accounting_dealerinvoice.origin_id
    from accounting_invoicecomponentlist left join accounting_dealerinvoice on accounting_dealerinvoice.id=invoice_id  
    group by accounting_invoicecomponentlist.invoice_id;'''
    company_list = None
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        company_list = dictfetchall(cursor)
        
    except TypeError:
        res = "Помилка"
    
    return render_to_response('index.html', {'list': list, 'company_list':company_list, 'weblink': 'invoice_component_report.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

# товар в накладній
def invoice_id_list(request, id=None, limit=0):
    list = None
    if limit == 0:
        list = InvoiceComponentList.objects.filter(invoice=id).order_by('-id')#.values('catalog__price', 'count', 'id', 'price', 'invoice__origin_id', 'invoice__company__name', 'invoice__manager__name', 'invoice__price', 'invoice__currency__ids_char' , 'catalog__ids', 'catalog__manufacturer', 'catalog__name', 'catalog__dealer_code', 'rcount', 'price', 'catalog__currency__name', 'date', 'description', 'user__username', 'currency__ids_char', 'catalog__id')
    else:
        list = InvoiceComponentList.objects.filter(invoice=id).order_by('-id')#.values('catalog__price', 'count', 'id', 'price', 'invoice__origin_id', 'invoice__company__name', 'invoice__manager__name', 'invoice__price', 'invoice__currency__ids_char' , 'catalog__ids', 'catalog__manufacturer', 'catalog__name', 'catalog__dealer_code', 'rcount', 'price', 'catalog__currency__name', 'date', 'description', 'user__username', 'currency__ids_char', 'catalog__id')[:limit]
    psum = 0
    optsum = 0
    scount = 0
    rcount = 0
    uaoptsum = 0
    status_delivery = False
    for item in list:
        psum = psum + (item.catalog.price * item.count)
        optsum = optsum + (item.price * item.count)
        uaoptsum = optsum + (item.get_uaprice() * item.count)
        scount = scount + item.count
        rcount = rcount + int(item.rcount or 0)
    if scount == rcount:
        status_delivery = True
    dinvoice = DealerInvoice.objects.get(id=id)    
    invoice_status_delivery =  dinvoice.received
    context = {'list': list, 'dinvoice':dinvoice, 'allpricesum':psum, 'alloptsum':optsum, 'ua_optsum':uaoptsum, 'countsum': scount, 'status_delivery': invoice_status_delivery, 'weblink': 'invoice_component_report.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def invoice_id_list_delete(request, id=None):
    list = None
    list = InvoiceComponentList.objects.filter(invoice=id).order_by('-id')#.values('catalog__price', 'count', 'id', 'price', 'invoice__origin_id', 'invoice__company__name', 'invoice__manager__name', 'invoice__price', 'invoice__currency__ids_char' , 'catalog__ids', 'catalog__manufacturer', 'catalog__name', 'catalog__dealer_code', 'rcount', 'price', 'catalog__currency__name', 'date', 'description', 'user__username', 'currency__ids_char', 'catalog__id')
    list.delete()
    dinvoice = DealerInvoice.objects.get(id=id)
    context = {'list': list, 'dinvoice':dinvoice,  'weblink': 'invoice_component_report.html',}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def invoice_cat_id_list(request, cid=None, limit=0):
    list = InvoiceComponentList.objects.filter(catalog=cid).order_by('-id') #.values('catalog__price', 'count', 'id', 'price', 'invoice__origin_id', 'invoice__company__name', 'invoice__manager__name', 'invoice__price', 'invoice__currency__ids_char' , 'catalog__ids', 'catalog__manufacturer', 'catalog__name', 'catalog__dealer_code', 'rcount', 'price', 'catalog__currency__name', 'date', 'description', 'user__username', 'currency__ids_char', 'catalog__id')
    psum = 0
    scount = 0
    optsum = 0
    for item in list:
#        psum = psum + (item['catalog__price'] * item['count'])
#        scount = scount + item['count']
        psum = psum + (item.catalog.price * item.count)
        scount = scount + item.count
        optsum = optsum + (item.get_uaprice() * item.count)
    context = {'list': list, 'allpricesum':psum, 'countsum': scount, 'alloptsum':optsum, 'weblink': 'invoice_component_report.html', }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def invoice_import_form(request):
    form = ImportDealerInvoiceForm()
    context = {'form': form, 'weblink': 'import_invoice.html',}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)    
    
@csrf_exempt
def invoice_import(request):
    invoice_reader = None
    ids_list = []
    add_list = []
    update_list = []
    error_list = []
    icl_list = []
    created_cat_list = []
    now = datetime.datetime.now()
    inv_number = None
    inv_number_form = ''
    recomended = False
    create_catalog = False

    if request.method == 'POST':
        form = ImportDealerInvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            recomended = form.cleaned_data['recomended']
            create_catalog = form.cleaned_data['create_catalog']
            inv_number_form = form.cleaned_data['invoice_number']
            inv_number_form = inv_number_form.replace(' ', '')
#            col_count = form.cleaned_data['col_count']
        else:
            return render_to_response('index.html', {'form': form, 'weblink': 'import_invoice.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))            

        csvfile = request.FILES['csv_file']
        dialect = csv.Sniffer().sniff(codecs.EncodedFile(csvfile, "utf-8").read(1024))
        csvfile.open()
        invoice_reader = csv.reader(codecs.EncodedFile(csvfile, "utf-8"), delimiter=';', dialect=dialect)

    name = 'id'
    w_file = open(settings.MEDIA_ROOT + 'csv/' + name + '_miss.csv', 'wb')
    spamwriter = csv.writer(w_file, delimiter=';', quotechar='|') #, quoting=csv.QUOTE_MINIMAL)
    for row in invoice_reader:
        cat = None
        id = None
        cur = None
        price_cur = None
        id = row[0]
        dealer_code = row[1]
        catalog_name = row[2]
        catalog_r_price = row[3].replace(' ', '')
        r_cur = row[4]
        inv_cat_count = int(row[5])
        catalog_price = row[6].replace(' ', '')
        p_cur = row[7]
        inv = None
        try:            
            if row[8] != '' and inv_number_form == '':
                inv_number = row[8]
                inv = DealerInvoice.objects.get(id = int(inv_number))
            elif row[8] == '' and inv_number_form != '':
                inv_number = inv_number_form
                inv = DealerInvoice.objects.get(id = int(inv_number))
            else:
                error_list.append('Накладну для товару ['+ id + '] ' + catalog_name +  ' не ВКАЗАНО!')
        except:
            error_list.append('Накладної для товару ['+ id + '] ' + catalog_name +  ' не знайдено')
        if len(row) >= 9:
            try:
                catalog_type_id = row[9]
                catalog_manufacture = row[10]
                catalog_country = row[11]
                catalog_color = row[12]
                description = row[13]
                photo = row[14]
            except:
                error_list.append('Для товару ['+ id + '] ' + catalog_name +'. ' + 'Щось не так в колонках №:  9, 10, 11, 12, 13, 14')
        try:
            cur = Currency.objects.get(id = r_cur)
            price_cur = Currency.objects.get(id = p_cur)
        except:
            error_list.append('Для товару ['+ id + '] ' + catalog_name +'. ' + 'Валюти з ID [' + r_cur + '] не існує')            
                  
        try:
            cat = Catalog.objects.get(Q(ids = id) | Q(dealer_code = id))
            ids_list.append(cat)
            if (float(catalog_price) > 0) and (recomended == True):
                cat.price = catalog_r_price 
                cat.currency = cur
            if (catalog_name and recomended == True):
                cat.name = catalog_name
            cat.count = cat.count + inv_cat_count
            cat.save()
            update_list.append(cat)
            if inv:
            #InvoiceComponentList(invoice = inv, catalog = cat, count = inv_cat_count, price= catalog_price, currency = c, date = now).save()
                icl = InvoiceComponentList.objects.create(invoice = inv, catalog = cat, count = inv_cat_count, price= catalog_price, currency = price_cur, date = now)
                icl_list.append(icl)
        except Catalog.DoesNotExist:
            error_list.append('Товару ['+ id + '] ' + catalog_name +  ' не знайдено!')
            add_list.append({'id': id, 'code': dealer_code, 'photo': photo, 'name': catalog_name, 'desc': description, 'price': catalog_r_price})
            if create_catalog == True:
                try:
                    m = None
                    m = Manufacturer.objects.get(id=catalog_manufacture)
                except:
                    error_list.append('Для товару ['+ id + '] ' + catalog_name +'. ' + 'Виробника з ID [' + catalog_manufacture + '] не існує') 
                try:
                    t = None
                    t = Type.objects.get(id=catalog_type_id)
                except:
                    error_list.append('Для товару ['+ id + '] ' + catalog_name +'. ' +'Такої категорії ID [' + catalog_type_id + '] не існує')
                try:
                    country = None
                    country = Country.objects.get(id=catalog_country)
                except:
                    error_list.append('Для товару ['+ id + '] ' + catalog_name +'. ' + 'Країни з ID [' + catalog_country + '] не існує')
#                new_cat = Catalog.objects.create(ids=id, dealer_code=dealer_code, name=catalog_name, manufacturer=m, type=t, year=datetime.datetime.now().year, color=catalog_color, price=catalog_r_price, currency=cur, sale=0, country=country, count = 0) #.save()                    
                try:
#                    if catalog_color == 0:
#                         catalog_color = ""
                    new_cat = Catalog.objects.create(ids=id, dealer_code=dealer_code, name=catalog_name, manufacturer=m, type=t, year=datetime.datetime.now().year, color=catalog_color, price=catalog_r_price, currency=cur, sale=0, country=country, count = 0, description="") #.save()
                    created_cat_list.append(new_cat)
                except:
                    pass
                    #error_list.append('Не вистачає полів (Категорія, Виробник, Країна) для товару ['+ id + '] ' + catalog_name +  ' не знайдено')
            spamwriter.writerow(row)

    #list = Catalog.objects.filter(ids__in = ids_list)
    #return render_to_response('index.html', {'catalog': list, 'weblink': 'invoice_catalog_import_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    context = {'update_list': update_list, 'add_list': add_list, 'weblink': 'invoice_catalog_import_list.html', 'error_list': error_list, 'created_cat_list': created_cat_list, 'icl_list': icl_list,}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)    


# --------------- Find Category or Manufacture (Ajax) and show LIST in html field---------
@csrf_exempt
def category_manufacture_lookup(request):
    data = None
    res = []
    if request.is_ajax():
#        print "\n>>> AJAX WORK AJAX <<<" + str(data) 
        if request.method == "POST":
            if request.POST.has_key(u'query'):
                value = request.POST[u'query']
                if len(value) >= 2:
                    model_results_type = Type.objects.filter(Q(name__icontains = value) | Q(name_ukr__icontains = value)).order_by('name')
#                    print ("LEN type %s " %  len(model_results_type))
                    if len(model_results_type):
#                        data1 = serializers.serialize("json", model_results_type, fields = ('id', 'name_ukr', 'name'))
                        for mod in model_results_type:
                            d_res = {}
                            d_res["id"] = mod.id
                            d_res["name"] = "%s - %s" % (mod.name, mod.name_ukr)
                            d_res["url"] = reverse('invoice-category-id-list', args=[mod.pk])
                            d_res["url_inv"] = reverse('inventory-by-type', args=[mod.pk])
                            res.append(d_res)
                            
                    model_results_manuf = Manufacturer.objects.filter(Q(name__icontains = value)).order_by('name')
#                    print ("LEN type %s " %  len(model_results_manuf))
                    if len(model_results_manuf):
#                        data2 = serializers.serialize("json", model_results_manuf, fields = ('id', 'name', 'www', ))
                        for mod in model_results_manuf:
                            d_res = {}
 #                           print ("Manufacture Name =  %s " %  (mod.name))
                            d_res["id"] = mod.id
                            d_res["name"] = ">> %s <<" % (mod.name.upper())
                            d_res["url"] = reverse('invoice-manufacture-id-list', args=[mod.pk])
                            d_res["url_inv"] = reverse('inventory-by-manufacturer', args=[mod.pk])
                            res.append(d_res)
                    #res = [data1, data2]
                    data = simplejson.dumps(res)
#                else:
#                    model_results = Type.objects.all().order_by('name')
#                    data = serializers.serialize("json", model_results, fields = ('id', 'name_ukr', 'name') )
 #   return HttpResponse(data)                
    return HttpResponse(data, content_type='application/json')    


def category_list(request):
    list = Type.objects.all()
    context = {'categories': list, 'weblink': 'category_list.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def category_get_list(request):
    list = Type.objects.all().values_list("id", "name", "name_ukr")
    dictionary = {}
    for el in list:
        str = unicode(el[1]) + " / " + unicode(el[2])
        dictionary[el[0]] = str
    #dictionary = dict(list)
    dictionary['selected'] = request.POST['sel']
    #json = simplejson.dumps(list) #{'aData': "None", 'id': pid, 'cname': c_name})
#    list = {'E':'Letter E','F':'Letter F','G':'Letter G', 'selected':'F'}
    json = simplejson.dumps(dictionary)
    return HttpResponse(json, content_type='application/json')

@csrf_exempt   
def category_lookup(request):
    data = None
    if request.is_ajax():
#        print "\n>>> AJAX WORK AJAX <<<" + str(data) 
        if request.method == "POST":
            if request.POST.has_key(u'query'):
                value = request.POST[u'query']

                if len(value) > 2:
                    model_results = Type.objects.filter(Q(name__icontains = value) | Q(name_ukr__icontains = value)).order_by('name')
                    data = serializers.serialize("json", model_results, fields = ('id', 'name_ukr', 'name') )
                else:
                    model_results = Type.objects.all().order_by('name')
                    data = serializers.serialize("json", model_results, fields = ('id', 'name_ukr', 'name') )
            if request.POST.has_key(u'id'):
                value = request.POST[u'id']
#                print "\n>>> WORK - ID <<<" + str(data) + " | " + str(value)
                model_results = Type.objects.filter( Q(pk = value) ).order_by('name')
                data = serializers.serialize("json", model_results, fields = ('id', 'name_ukr', 'name') )
    return HttpResponse(data)                

@csrf_exempt
def category_add(request):
    a = Type()
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance = a)
        if form.is_valid():
            form.save();
            return HttpResponseRedirect('/category/view/')
    else:
        form = CategoryForm(instance = a)
    return render(request, 'index.html', {'form': form, 'weblink': 'category.html'})

@csrf_exempt
def category_edit(request, id):
    a = Type.objects.get(pk=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/category/view/')
    else:
        form = CategoryForm(instance=a)
    context = {'form': form, 'weblink': 'category.html', 'text': 'Обмін валют (редагування)'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

def category_del(request, id):
    obj = Type.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/category/view/')    


def category_attr_list(request, show_attr=False):
    list = CatalogAttribute.objects.all()
    context = {'attr_list': list, 'weblink': 'category_attr_list.html'}
    context.update(custom_proc(request)) 
    context.update({'show_attr': show_attr})
    return render(request, 'index.html', context)


def category_attr_values_list(request, aid=None):
    list = None
    if aid :
        cattr_id = CatalogAttribute.objects.filter(pk = int(aid))
        list = CatalogAttributeValue.objects.filter(pk = aid)
    else:        
        list = CatalogAttributeValue.objects.all()
    context = {'attr_val_list': list, 'weblink': 'category_attr_values_list.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


# -------------- Currency and operations ----------------------
def curency_add(request):
    a = Currency()
    if request.method == 'POST':
        form = CurencyForm(request.POST, instance = a)
        if form.is_valid():
            ids = form.cleaned_data['ids']
            ids_char = form.cleaned_data['ids_char']
            name = form.cleaned_data['name']
            country_id = form.cleaned_data['country_id']
            Currency(ids=ids, ids_char=ids_char, name=name, country_id=country_id).save()
            return HttpResponseRedirect('/curency/view/')
    else:
        form = CurencyForm(instance = a)
    #return render_to_response('curency.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'curency.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def curency_list(request):
    list = Currency.objects.all()
    #return render_to_response('curency_list.html', {'currency': list.values()})
    return render_to_response('index.html', {'currency': list, 'weblink': 'curency_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def curency_del(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/curency/view/')    
    obj = Currency.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/curency/view/')

from bs4 import BeautifulSoup
import urllib2

def goverla_currency():
    url='https://goverla.ua/'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    soup = BeautifulSoup(the_page)
    usd = soup.find("div", {"id": "usd"})
    eur = soup.find("div", {"id": "eur"})
    soup_usd = BeautifulSoup(str(usd))
    soup_eur = BeautifulSoup(str(eur))
    try:
        c_usd = int(soup_usd.find("div", {'class' : 'gvrl-table-cell ask'}).string.split("-")[0])/100.0
    except:
        c_usd = 0
    try:
        c_eur = int(soup_eur.find("div", {'class' : 'gvrl-table-cell ask'}).string.split("-")[0])/100.0
    except:
        c_eur = 0
        
    return [c_usd, c_eur]


def pb_currency():
    EUR = 0
    USD = 0
    res = None
    #url='https://privatbank.ua/'
    url='https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
        the_page = response.read()
        res = json.loads(the_page)
    except:
        res = None
    #===========================================================================
    # soup = BeautifulSoup(the_page)
    # usd_b = soup.find("td", {"id": "USD_buy"})
    # eur_b = soup.find("td", {"id": "EUR_buy"})
    # usd_s = soup.find("td", {"id": "USD_sell"})
    # eur_s = soup.find("td", {"id": "EUR_sell"})
    #===========================================================================
    #===========================================================================
    # soup_usd_b = BeautifulSoup(str(usd_b))
    # soup_eur_b = BeautifulSoup(str(eur_b))
    # soup_usd_s = BeautifulSoup(str(usd_s))
    # soup_eur_s = BeautifulSoup(str(eur_s))
    #===========================================================================
    try:
        #c_usd = (float(str(soup_usd_b.string)) + float(str(soup_usd_s.string))) / 2
        USDb = res[1]['buy']
        USDs = res[1]['sale']
        c_usd = (float(USDb) + float(USDs)) / 2
        #c_usd = (float(str(soup_usd_b.string)) + float(str(soup_usd_s.string))) / 2
        #c_usd = (float(str(usd_b.string)) + float(str(usd_s.string))) / 2
    except:
        c_usd = 0
    try:
        EURb = res[0]['buy']
        EURs = res[0]['buy']
        c_eur = (float(EURb) + float(EURs)) / 2
    except:
        c_eur = 0
        
    return [c_usd, c_eur]

@csrf_exempt
def exchange_add(request):
    #cur = goverla_currency()
    cur = pb_currency()
    c_usd = cur[0]
    c_eur = cur[1]
        
    a = Exchange(date = datetime.datetime.now())
    if request.method == 'POST':
        form = ExchangeForm(request.POST, instance = a)
        if form.is_valid():
            date = form.cleaned_data['date']
            currency = form.cleaned_data['currency']
            value = form.cleaned_data['value']
            try:
                de = Exchange.objects.get(date = date, currency = currency.id)
                return HttpResponse("Такий курс вже існує, відредагуйте існуючий курс")
            except Exchange.DoesNotExist:
                Exchange(date=date, currency=currency, value=value).save()
                return HttpResponseRedirect('/exchange/view/')
    else:
        form = ExchangeForm(instance = a)
    context = {'form': form, 'eur': c_eur, 'usd': c_usd, 'weblink': 'exchange.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def exchange_list(request):
    cur = pb_currency()
    c_usd = cur[0]
    c_eur = cur[1]
    curdate = datetime.datetime.now()
    list = Exchange.objects.filter(date__month=curdate.month)
    context = {'exchange': list, 'eur': c_eur, 'usd': c_usd, 'weblink': 'exchange_list.html'} 
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def exchange_edit(request, id):
    a = Exchange.objects.get(pk=id)
    if request.method == 'POST':
        form = ExchangeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/exchange/view/')
    else:
        form = ExchangeForm(instance=a)
    context = {'form': form, 'weblink': 'exchange.html', 'text': 'Обмін валют (редагування)'}
    context.update(custom_proc(request))         
    return render(request, 'index.html', context)


def exchange_del(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/exchange/view/')        
    obj = Exchange.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/exchange/view/')



# -------- Catalog ---------------- 
@csrf_exempt
def manufacturer_add(request):
    a = Manufacturer()
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, request.FILES, instance=a)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            www = form.cleaned_data.get('www')
            country = form.cleaned_data.get('country')
            logo = form.cleaned_data.get('logo')
            if not logo:
                upload_path = ''
            else:
                upload_path = processUploadedImage(logo, 'manufecturer/') 
            #country = SelectFromModel(objects=Country.objects.all())
            Manufacturer(name=name, description=description, www=www, logo=upload_path, country=country).save()
            return HttpResponseRedirect('/manufacturer/view/')
    else:
        form = ManufacturerForm(instance=a)
    #return render_to_response('manufacturer.html', {'form': form})
    context = {'form': form, 'weblink': 'manufacturer.html', 'next': current_url(request)}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def manufacturer_edit(request, id):
    a = Manufacturer.objects.get(pk=id)
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, request.FILES, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/manufacturer/view/')
    else:
        form = ManufacturerForm(instance=a)
    context = {'form': form, 'weblink': 'manufacturer.html', 'text': 'Виробник (редагування)', 'next': current_url(request)}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def manufaturer_list(request):
    list = Manufacturer.objects.all()
    context = {'manufactures': list, 'weblink': 'manufacturer_list.html', }  
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def manufacturer_delete(request, id):
    if auth_group(request.user, "admin") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для редагування ', 'next': current_url(request)}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    obj = Manufacturer.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/manufacturer/view/')

@csrf_exempt
def manufacturer_lookup(request):
    data = []
    if request.method == "POST":
        if request.POST.has_key(u'query'):
            value = request.POST[u'query']
            if len(value) > 2:
                results = Manufacturer.objects.filter(name__icontains = value)
                #model_results = Client.objects.filter(Q(name__icontains = value) | Q(forumname__icontains = value))
                data = serializers.serialize("json", results, fields=('name','id', 'country', 'www'))
            else:
                data = []
        if request.POST.has_key(u'id'):
            value = request.POST[u'id']
            results = Manufacturer.objects.filter(id = value)
            data = serializers.serialize("json", results, fields=('name','id', 'country', 'www'))

    return HttpResponse(data)    


def catalog_import_form(request):
    if auth_group(request.user, 'seller')==False:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))    
    photo = False
    rec_price = False
    description = False
    name = False
    check_catalog_id = False
    add_list = []
    update_list = []
    ids_list = []
    created_cat_list = []
    error_list = []
    col_count = 3
    if request.method == 'POST':
        form = ImportPriceForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.cleaned_data['photo']
            rec_price = form.cleaned_data['recomended']
            description = form.cleaned_data['description']
            name = form.cleaned_data['name']
            check_catalog_id = form.cleaned_data['check_catalog_id']
            col_count = form.cleaned_data['col_count']
            if photo == True:
                print "PHOTO is True!!!"
            if check_catalog_id == True:
                print "Check ID is True!!!"
        else:
            return render_to_response('index.html', {'form': form, 'weblink': 'catalog_import.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))            

        csvfile = request.FILES['csv_file']
        dialect = csv.Sniffer().sniff(codecs.EncodedFile(csvfile, "utf-8").read(1024))
        csvfile.open()
        csv_file_reader = csv.reader(codecs.EncodedFile(csvfile, "utf-8"), delimiter=';', dialect=dialect)

        w_file = open(settings.MEDIA_ROOT + 'csv/miss_content.csv', 'wb')
        log_writer = csv.writer(w_file, delimiter=';', quotechar='|') #, quoting=csv.QUOTE_MINIMAL)

        for row in csv_file_reader:
            id = None
            code = None
            cat = None
            #print "\n ROW =  " + str(row) + '\n'
            if row[0] and row[0] <> '0':
                id = row[0]
            if row[1] and row[1] <> '0':            
                code = row[1]
            try:
                price = row[3]
                if (not id is None and not code is None):
                    cat = Catalog.objects.filter(Q(ids = id) | Q(dealer_code = id) | Q(ids = code) | Q(dealer_code = code)).first()
                if (not id is None) and (code is None):
                    try:
                        cat = Catalog.objects.get(Q(ids = id) | Q(dealer_code = id))
                    except:
                        pass
                if (not code is None) and (id is None):                
                    cat = Catalog.objects.filter(Q(ids = code) | Q(dealer_code = code)).first()
                if cat:
                    ids_list.append(cat)
                    if (price <> '0') and (rec_price == True): 
                        cat.last_price = cat.price
                        cat.price = row[3]
                        cat.currency = Currency.objects.get(id = row[4])
                        cat.last_update = datetime.datetime.now()
                        cat.user_update = User.objects.get(username='import')
                    if description:
                        cat.full_description = row[5]
                    if name:
                        cat.name = row[2]
                    cat.save()
                else:
                    if int(col_count) >= 10:
                        try:
                            m = None
                            m = Manufacturer.objects.get(id=row[8])
                        except:
                            error_list.append('Для товару ['+ row[0] + '] ' + row[2] +'. ' + 'Виробника з ID [' + row[8] + '] не існує') 
                        print "\n Manufacturer NAME = : " + m.name
                        try:
                            t = None
                            t = Type.objects.get(id=row[7])
                        except:
                            error_list.append('Для товару ['+ row[0] + '] ' + row[2] +'. ' +'Такої категорії ID [' + row[7] + '] не існує')
                        try:
                            c = None
                            c = Currency.objects.get(id = row[4])
                        except:
                            error_list.append('Для товару ['+ row[0] + '] ' + row[2] +'. ' + 'Валюти з ID [' + row[4] + '] не існує')
                        try:
                            country = None
                            country = Country.objects.get(id=row[9])
                        except:
                            error_list.append('Для товару ['+ row[0] + '] ' + row[2] +'. ' + 'Країни з ID [' + row[9] + '] не існує')
                                                                
                        new_cat = Catalog.objects.create(ids=row[0], dealer_code=row[1], name=row[2], manufacturer=m, type=t, year=datetime.datetime.now().year, color=row[10], price=row[3], currency=c, sale=0, country=country, count = 0) #.save()
                        print "CRATE CATALOG"
                        created_cat_list.append(new_cat)
#                print "\n ROW =  " + str(row) + '\n'
#                print "\n CATALOG =  " + str(cat) + '\n'
                update_list.append(row)
            except: # Catalog.DoesNotExist:
                print "\n EXCEPT \n"
                add_list.append({'id': id, 'code': code, 'photo': row[6], 'name': row[2], 'desc': row[5], 'price': row[3]});
                log_writer.writerow(row)
        return render_to_response('index.html', {'update_list': update_list, 'add_list': add_list, 'ids_list': ids_list, 'weblink': 'catalog_import_list.html', 'error_list': error_list, 'created_cat_list': created_cat_list,  'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        
    else:
        form = ImportPriceForm()
        return render_to_response('index.html', {'form': form, 'title': 'New Fuction', 'weblink': 'catalog_import.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    
#===============================================================================
#             if photo:
#                 try:
#                     old_file = directory  + row[6]
#                     directory_done = settings.MEDIA_ROOT + 'download/'
#                     s_name = cat.manufacturer.name
#                     new_folder = s_name.strip().replace(' ', '-').lower()
#                     new_file = directory_done + new_folder +'/'+ row[6]
#                     media_dir = new_file.replace(settings.MEDIA_ROOT, '/media/')
#                     if os.path.isfile(old_file):
# #                        print "File found = " + old_file
#                         ids_list.append({'cat_id': cat.ids, 'id': id, 'code': code, 'photo': row[6], 'photo_is': old_file})
#                         if not os.path.exists(directory_done + new_folder):
#                             os.makedirs(directory_done + new_folder)
#                         os.rename( old_file, new_file )
#                         chk_photo = Photo.objects.filter(local = media_dir)
#                         if chk_photo:
#                             cat.photo_url.add(chk_photo.first())
#                         else:
#                             addphoto = Photo(local = media_dir, date = datetime.datetime.now(), user = request.user, description="")
#                             addphoto.save()
#                             cat.photo_url.add(addphoto)
#                     else: 
#                         if not os.path.isfile(new_file):
# #                            print "File "+ new_file +" not exists"
#                             ids_list.append({'cat_id': cat.ids, 'id': id, 'code': code, 'photo': row[6], 'photo_is': 'File not Found'})
#                         else:   
# #                            print '*** file found in Download Folder - ' +  new_file
#                             chk_photo = Photo.objects.filter(local = media_dir)
#                             if chk_photo:
#                                 cat.photo_url.add(chk_photo.first())
#                             else:
#                                 addphoto = Photo(local = media_dir, date = datetime.datetime.now(), user = request.user, description="")
#                                 addphoto.save()
#                                 cat.photo_url.add(addphoto)
#                             ids_list.append({'cat_id': cat.ids, 'id': id, 'code': code, 'photo': row[6], 'photo_is': new_file})
#                     cat.save()
#                 except:
#                         im1 = Image.open(old_file)
#                         im2 = Image.open(new_file)
#                         if im1 == im2:
#                             os.remove(old_file)
#                         im1.close()
#                         im2.close()
#                 #cat.photo = row[6]
#===============================================================================    
#    form = ImportPriceForm()
#    return render_to_response('index.html', {'form': form, 'weblink': 'catalog_import.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    


#old function to import CSV file from disc
def catalog_import(request):
    if auth_group(request.user, 'seller')==False:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))    
    ids_list = []
#    if 'name' in request.GET and request.GET['name']:
#        name = request.GET['name']
    name = 'catalog'
    path = settings.MEDIA_ROOT + 'csv/' + name + '.csv'
    csvfile = open(path, 'rb')
    pricereader = csv.reader(csvfile, delimiter=';', quotechar='|')
    w_file = open(settings.MEDIA_ROOT + 'csv/catalog_miss.csv', 'wb')
    spamwriter = csv.writer(w_file, delimiter=';', quotechar='|') #, quoting=csv.QUOTE_MINIMAL)
    for row in pricereader:
        id = None
        #print row[0] + " - " + row[2]
        id = row[0]
        ids_list.append(row[0])
        try:
            cat = Catalog.objects.get(ids = id)
            if row[10]: 
                cat.type = Type.objects.get(id = row[3])
                cat.manufacturer = Manufacturer.objects.get(id = row[2])
                cat.price = row[10]
                cat.save()
            else:
                spamwriter.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
                    
        except Catalog.DoesNotExist:
            m = Manufacturer.objects.get(id=row[2])
            t = Type.objects.get(id=row[3])
            c = Currency.objects.get(id = row[11])
            country = Country.objects.get(id=row[5])                                        
            Catalog(ids=row[0], name=row[1], manufacturer=m, type=t, year=2015, color=row[4], price=row[10], currency=c, sale=0, country=country, count = 0).save()          
            spamwriter.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
        #return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")

    list = Catalog.objects.filter(ids__in = ids_list)
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_import_content(request):
    if auth_group(request.user, 'seller')==False:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))    
    directory = settings.MEDIA_ROOT + 'upload/photo/content/'
    csv_file_reader = None
    ids_list = []
    add_list = []
    update_list = []
    rec_price = False
    photo = None
    description = None
    name = None
    if request.method == 'POST':
        form = ImportPriceForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.cleaned_data['photo']
            rec_price = form.cleaned_data['recomended']
            description = form.cleaned_data['description']
            name = form.cleaned_data['name']
            if photo == True:
                print "PHOTO is True!!!"
#    if request.POST and request.FILES:
        csvfile = request.FILES['csv_file']
        dialect = csv.Sniffer().sniff(codecs.EncodedFile(csvfile, "utf-8").read(1024))
        csvfile.open()
        csv_file_reader = csv.reader(codecs.EncodedFile(csvfile, "utf-8"), delimiter=';', dialect=dialect)
        #rec_price = request.POST.get('recomended')
#        print "Recomended = " + str(rec_price)
    else:
        form = ImportPriceForm()
        return render_to_response('index.html', {'form': form, 'title': 'with Photo', 'weblink': 'catalog_import.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    
    
    w_file = open(settings.MEDIA_ROOT + 'csv/miss_content.csv', 'wb')
    log_writer = csv.writer(w_file, delimiter=';', quotechar='|') #, quoting=csv.QUOTE_MINIMAL)
    #reader = list(csv_file_reader)
#    lenCol = len(next(csv_file_reader))
#    print "Column = " + str(lenCol)
#    csvfile.seek(0)
    for row in csv_file_reader:
#        print "Column = " + str(len(row))
        id = None
        code = None
        cat = None
        if row[0] and row[0] <> '0':
            id = row[0]
        if row[1] and row[1] <> '0':            
            code = row[1]
        try:
            price = row[3]
            #if ((code <> '0') or (code <> '')) and ((id <> '0') or (id <> '')):
            if (not id is None and not code is None):
                cat = Catalog.objects.filter(Q(ids = id) | Q(dealer_code = id) | Q(ids = code) | Q(dealer_code = code)).first()
#                print "*** ids = " + str(id) + " | code = " + str(code)
#                print "Catalog code id==code = " + str(cat)
            #if (id <> '0') and ((code == '0') or (code == '')):
            if (not id is None) and (code is None):
                try:
                    cat = Catalog.objects.get(Q(ids = id) | Q(dealer_code = id))
#                    print "Catalog Id = " + str(cat)
                except:
#                    print "--PASS--"
                    pass
            #if (code <> '0') and ((id == '0') or (id == '')):
            if (not code is None) and (id is None):                
#                try:
                cat = Catalog.objects.filter(Q(ids = code) | Q(dealer_code = code)).first()
#                print "Catalog code = " + str(cat)
#                print "cat_ids = " + str( Catalog.objects.filter(Q(ids = code)) )
#                print "cat_code = " + str( Catalog.objects.filter(Q(dealer_code = code)) )
#                print "CODE = " + str(code) + " / ID = " + str(ids) 
 #               except:
 #                   pass
#            print "Catalog = " + str(cat)
            if cat:
                ids_list.append(cat)

            if (price <> '0') and (rec_price == True): 
                cat.last_price = cat.price
                cat.price = row[3]
                cat.currency = Currency.objects.get(id = row[4])
                cat.last_update = datetime.datetime.now()
                cat.user_update = User.objects.get(username='import')
                #cat.save()
            if photo:
                try:
                    old_file = directory  + row[6]
                    directory_done = settings.MEDIA_ROOT + 'download/'
                    s_name = cat.manufacturer.name
                    new_folder = s_name.strip().replace(' ', '-').lower()
                    new_file = directory_done + new_folder +'/'+ row[6]
                    media_dir = new_file.replace(settings.MEDIA_ROOT, '/media/')
                    if os.path.isfile(old_file):
#                        print "File found = " + old_file
                        ids_list.append({'cat_id': cat.ids, 'id': id, 'code': code, 'photo': row[6], 'photo_is': old_file})
                        if not os.path.exists(directory_done + new_folder):
                            os.makedirs(directory_done + new_folder)
                        os.rename( old_file, new_file )
                        chk_photo = Photo.objects.filter(local = media_dir)
                        if chk_photo:
                            cat.photo_url.add(chk_photo.first())
                        else:
                            addphoto = Photo(local = media_dir, date = datetime.datetime.now(), user = request.user, description="")
                            addphoto.save()
                            cat.photo_url.add(addphoto)
                    else: 
                        if not os.path.isfile(new_file):
#                            print "File "+ new_file +" not exists"
                            ids_list.append({'cat_id': cat.ids, 'id': id, 'code': code, 'photo': row[6], 'photo_is': 'File not Found'})
                        else:   
#                            print '*** file found in Download Folder - ' +  new_file
                            chk_photo = Photo.objects.filter(local = media_dir)
                            if chk_photo:
                                cat.photo_url.add(chk_photo.first())
                            else:
                                addphoto = Photo(local = media_dir, date = datetime.datetime.now(), user = request.user, description="")
                                addphoto.save()
                                cat.photo_url.add(addphoto)
                            ids_list.append({'cat_id': cat.ids, 'id': id, 'code': code, 'photo': row[6], 'photo_is': new_file})
                    cat.save()
                except:
                        im1 = Image.open(old_file)
                        im2 = Image.open(new_file)
                        if im1 == im2:
                            os.remove(old_file)
                        im1.close()
                        im2.close()
                #cat.photo = row[6]
                pass
            if description:
                cat.full_description = row[5]
            if name:
                cat.name = row[2]
            cat.save()
            update_list.append(row)

            try:
                m = Manufacturer.objects.get(id=row[8])
                t = Type.objects.get(id=row[7])
                c = Currency.objects.get(id = row[4])
                country = Country.objects.get(id=row[9])                                        
                Catalog(ids=row[0], dealer_code=row[1], name=row[2], manufacturer=m, type=t, year=datetime.datetime.now().year, color='', price=row[3], currency=c, sale=0, country=country, count = 0).save()
            except:
                pass
                            
        except: # Catalog.DoesNotExist:
            #add_list.append(row)
            pass

            add_list.append({'id': id, 'code': code, 'photo': row[6], 'name': row[2], 'desc': row[5], 'price': row[3]});
#            log_writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
            log_writer.writerow(row)
        
    #list = Catalog.objects.select_related('manufacturer', 'type', 'currency', 'country').filter(Q(ids__in = ids_list))
    return render_to_response('index.html', {'update_list': update_list, 'add_list': add_list, 'ids_list': ids_list, 'weblink': 'catalog_import_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
 
@csrf_exempt
def catalog_add(request):
    if auth_group(request.user, 'seller')==False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для редагування ', 'next': current_url(request)}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
#        return HttpResponse('Error: У вас не має прав для редагування')
    upload_path = ''
    if request.method == 'POST':
        form = CatalogForm(request.POST, request.FILES, request = request)
        if form.is_valid():
            ids = form.cleaned_data['ids']
            dealer_code = form.cleaned_data['dealer_code']
            name = form.cleaned_data['name']
            manufacturer = form.cleaned_data['manufacturer']
            type = form.cleaned_data['type']
            size = form.cleaned_data['size']
            weight = form.cleaned_data['weight']
            photo = form.cleaned_data['photo']
            year = form.cleaned_data['year']
            sale = form.cleaned_data['sale']
            sale_to = form.cleaned_data['sale_to']
            color = form.cleaned_data['color']
            country = form.cleaned_data['country']
            price = form.cleaned_data['price']
            count = form.cleaned_data['count']
            length = form.cleaned_data['length']
            currency = form.cleaned_data['currency']
            description = form.cleaned_data['description']
            if photo != None:               
                upload_path = processUploadedImage(photo, 'catalog/') 
            Catalog(ids=ids, dealer_code=dealer_code, name=name, manufacturer=manufacturer, type=type, size=size, weight=weight, year=year, sale=sale, sale_to=sale_to, color=color, description=description, photo=upload_path, country=country, price=price, currency=currency, count=count, length=length).save()
            return HttpResponseRedirect('/catalog/manufacture/' + str(manufacturer.id) + '/view/5')
    else:
        name = request.GET.get('name')
        ids = request.GET.get('ids')
        price = request.GET.get('price')
        dealer_code = request.GET.get('dealer_code')
        if dealer_code == 'None':
            dealer_code = '' 
        form = CatalogForm(request = request, initial={'ids': ids, 'name': name, 'price': price, 'dealer_code': dealer_code})
    context = {'form': form, 'weblink': 'catalog.html', 'next': current_url(request)}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

@csrf_exempt
def catalog_set(request):
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має прав для редагування')
 
    if request.is_ajax():
        if request.method == 'POST':
            POST = request.POST
            if POST.has_key('id') and POST.has_key('value') and auth_group(request.user, 'seller'):
                id = request.POST.get('id')
                d = request.POST.get('value')
                obj = Catalog.objects.get(id = id)
                obj.description = d
                obj.last_update = datetime.datetime.now()
                obj.user_update = request.user
                obj.save() 

                c = Catalog.objects.filter(id = id).values_list('description', flat=True)
                return HttpResponse(c)

            # ------------- Mark Mistake ---------------
            if POST.has_key('id') and POST.has_key('mistake'):
                pk = request.POST['id']                
                mistake = request.POST['mistake']
                if mistake == 'true':
                    mistake = True
                else:
                    mistake = False
                msgtext = request.POST['mistake_msg']
                obj = Catalog.objects.get(pk = pk)
                obj.mistake_status = mistake                                 
                obj.mistake = msgtext
                shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
                str_dt_now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                str_update = u"[%s] [%s] User [%s] mark mistake (%s) - [%s];\n" % (str_dt_now, shopN, request.user.username, msgtext, str(True)) 
                history = obj.change_history or ""
                obj.change_history = history + str_update
                obj.save() 
                d = {}
                d['status'] = True
                if mistake:
                    d['msg'] = 'Товар помічений для перевірки'
                else:
                    d['msg'] = 'Товар помічений як виправлений'
                response = JsonResponse(d)
                return response     

            if POST.has_key('id') and POST.has_key('locality') and auth_group(request.user, 'seller'):
                id = request.POST.get('id')                
                loc = request.POST.get('locality')
                obj = Catalog.objects.get(id = id)                                
                obj.locality = loc
                obj.save() 
                c = Catalog.objects.filter(id = id).values_list('locality', flat=True)
                return HttpResponse(c)
            
            if POST.has_key('id') and POST.has_key('price'):
                if auth_group(request.user, 'admin')==False:
                    d = {}
                    d['status'] = False
                    d['msg'] = 'Ви не має достаттньо повноважень для даної функції'
                    response = JsonResponse(d)
                    return response                
                id = request.POST.get('id')
                p = request.POST.get('price')
                obj = Catalog.objects.get(id = id)
                obj.last_price = obj.price
                obj.price = p
                obj.last_update = datetime.datetime.now()
                obj.user_update = request.user
                obj.save() 
#                c = Catalog.objects.filter(id = id).values('price', 'id')
                c = Catalog.objects.filter(id = id).values_list('price', flat=True)
#                print "\nV_list" + str(c)
                return HttpResponse(c)
            
            if POST.has_key('id') and POST.has_key('sale'):
                id = request.POST.get('id')                
                s = request.POST.get('sale')
                obj = Catalog.objects.get(id = id)                                
                obj.sale = s
                obj.last_update = datetime.datetime.now()
                obj.user_update = request.user
                obj.save()
                c = Catalog.objects.filter(id = id).values_list('sale', flat=True)
                return HttpResponse(c) 

            if POST.has_key('id') and POST.has_key('update_enddate'):
                pk = request.POST['id']                
                s = request.POST['update_enddate']
                obj = Catalog.objects.get(pk = pk)
                conv = datetime.datetime.strptime(s, '%d-%m-%Y').date()                                
                obj.date = conv
                obj.save() 
                d = {}
                d['status'] = True
                d['msg'] = 'Done'
                response = JsonResponse(d)
                return response                

            if POST.has_key('id') and POST.has_key('count'):
                d = {}
                if auth_group(request.user, 'admin')==False:
                    d['status'] = False
                    d['msg'] = 'Ви не має достаттньо повноважень для даної функції'
                    response = JsonResponse(d)
                    return response                
#                    return HttpResponse('Error: У вас не має прав для редагування')
                pk = request.POST['id']                
                count = request.POST['count']
                obj = Catalog.objects.get(pk = pk)
                obj.count = count
                obj.save() 
                d['status'] = True
                d['msg'] = 'Done'
                response = JsonResponse(d)
                return response                
              #  return HttpResponse(simplejson.dumps(list(c)))
    else :
           return HttpResponse('Error: Щось пішло не так')
    
@csrf_exempt
def catalog_edit(request, id=None):
    if auth_group(request.user, "seller") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для редагування. Авторизуйтесь на порталі або зверніться до адміністратора.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)    
    a = Catalog.objects.get(pk=id)
    if request.method == 'POST':
        form = CatalogForm(request.POST, request.FILES, instance=a, request = request)
        if form.is_valid():
#            if auth_group(request.user, "admin") == False:
#               return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для редагування ID товару', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
#            manufacturer = form.cleaned_data['manufacturer']
#            type = form.cleaned_data['type']
            a.last_update = datetime.datetime.now()
            a.user_update = request.user
            a.save()
            form.save()
            return catalog_list(request, id = id)
    else:
        form = CatalogForm(instance=a, request = request)
    context = {'form': form, 'weblink': 'catalog.html', 'cat_pk': id, 'catalog_obj': a.get_photos(), 'youtube_list': a.youtube_url.all()}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def catalog_list(request, id=None):
    list = None
    if id==None:
        list = Catalog.objects.all().order_by("-id")[:10]
    else:
        list = Catalog.objects.filter(id=id)
    context = {'catalog': list, 'weblink': 'catalog_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def catalog_same_list(request):
    list_ids = Catalog.objects.all().values_list('ids', 'dealer_code').order_by("-ids")
    space_list = []
    cat_ids = []
    for cat in list_ids:
         res = re.findall(r"\s\Z", cat[0])
         if res != []:
             space_list.append(cat[0].strip())
             c = Catalog.objects.get(ids = cat[0])
             c.ids = cat[0].strip()
             c.save()
             #cat_ids.append( Catalog.objects.filter(ids__icontains = cat[0].strip()).values_list('ids') )
             #cat_ids.append( Catalog.objects.filter(dealer_code__icontains = cat[0].strip()).values_list('ids') )
             
#    list = Catalog.objects.filter(ids__in = space_list)
    list = Catalog.objects.filter(ids__in = cat_ids)
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_discount_list(request):
    list = Catalog.objects.filter(sale__gt=0)[:100]
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_manufacture_list(request, id=None):
    company_list = Manufacturer.objects.all()
    #list = Catalog.objects.filter(manufacturer=id)[:10]
    if id<>None:
        list = Catalog.objects.filter(manufacturer=id).order_by("-id")
    else:
        list = Catalog.objects.filter(manufacturer=id).order_by("-id")
    #return render_to_response('catalog_list.html', {'catalog': list.values_list()})
    print_url = None
    if id:
        print_url = '/shop/price/company/'+ str(id) +'/view/'
    context = {'catalog': list, 'company_list': company_list, 'url': print_url, 'view': True, 'weblink': 'catalog_list.html', }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def catalog_part_list(request, id, num=5):
    list = Catalog.objects.filter(manufacturer=id).order_by("-id")[:num]
    #return render_to_response('catalog_list.html', {'catalog': list.values_list()})
    context = {'catalog': list, 'weblink': 'catalog_list.html',}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def catalog_manu_type_list(request, id, tid):
    list = Catalog.objects.filter(manufacturer=id, type=tid).order_by("-id")
    #return render_to_response('catalog_list.html', {'catalog': list.values_list()})
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html'})


def catalog_type_list(request, id):
    list = Catalog.objects.filter(type=id)
    #return render_to_response('catalog_list.html', {'catalog': list.values_list()})
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Помилка: У вас не достатньо прав для даної операції.')
    obj = Catalog.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/catalog/search/id/')


def catalog_search_id(request):
    context = {'weblink': 'catalog_search_id.html',}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def catalog_search_locality(request):
    context = {'weblink': 'catalog_search.html',}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def catalog_search_by_ids(request):
    ids = None
    cat_list = None
    resp_json = {} 
    if request.is_ajax():
        if request.method == 'POST':
            result = None
#            if auth_group(request.user, 'seller')==False:
#                return HttpResponse('Error: У вас не має прав для редагування', content_type="text/plain;charset=UTF-8;")
            POST = request.POST  
            if POST.has_key('ids'):
                ids = request.POST['ids']
                cat_list = Catalog.objects.filter(Q(ids__icontains = ids) | Q(dealer_code__icontains = ids)).order_by('manufacturer')
                
                if cat_list.count() == 1:
#                    sp = ShopPrice()
#                    sp.catalog = cat_list[0]
#                    sp.scount = 1
#                    sp.dcount = 1
#                    sp.user = request.user
#                    sp.save()
                    add_shop_price = ShopPrice.objects.create(catalog = cat_list[0], scount=1, dcount=1, user = request.user)
                    
                
                resp_json = list(cat_list.values('pk', 'name', 'ids', 'dealer_code', 'price', 'count', 'manufacturer__name', 'country__name'))
                return HttpResponse(simplejson.dumps(resp_json), content_type='application/json')
            else:
                return HttpResponse("Помилка! Параметр IDS не може бути пустим або відсутнім", content_type="text/plain;charset=UTF-8;")
    else:
        return HttpResponse("Помилка, цей запит не AJAX-овий", content_type="text/plain;charset=UTF-8;")


def catalog_search_result(request):
    list = None
    print_url = None
    if 'name' in request.GET and request.GET['name']:
        name = request.GET['name']
        list = Catalog.objects.filter(name__icontains = name).order_by('manufacturer')
        print_url = "/shop/price/bysearch_name/"+name+"/view/"
    elif 'id' in request.GET and request.GET['id']:
        id = request.GET['id']
        list = Catalog.objects.filter(Q(ids__icontains = id) | Q(dealer_code__icontains = id)).order_by('manufacturer')
        print_url = "/shop/price/bysearch_id/"+id+"/view/"
    elif 'locality' in request.GET and request.GET['locality']:
        local = request.GET['locality']
        list = Catalog.objects.filter(locality__icontains = local).order_by('locality')
    context = {'catalog': list, 'url':print_url, 'weblink': 'catalog_list.html',}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


@csrf_exempt
def catalog_lookup(request):
    # Default return list
    data = None
    data_res = None
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            # Ignore queries shorter than length 3
            if len(value) > 2:
                model_results = Catalog.objects.filter(name__icontains=value)
                data = serializers.serialize("json", model_results, fields=('name','id', 'ids', 'price'))
                data_res = data
        else:
            data = "request Error"
            data_res = data
    if request.is_ajax():
        if request.method == "POST":
            if request.POST.has_key(u'query') and request.POST.has_key(u'type'):
                value = request.POST[u'query']
                type_id = request.POST[u'type']

                if len(value) > 2:
                    model_results = Catalog.objects.filter(name__icontains=value, type = type_id)
                    data = serializers.serialize("json", model_results, fields=('name','id', 'ids', 'price'))
                    data_res = data
            if request.POST.has_key(u'name'):
                pass
    # JSON Read and Parse
    if request.method == "POST":
        rdict = QueryDict(request.body)
        sel_id = rdict.keys()#[0]
        req_dict = json.loads(request.body)
        if req_dict.has_key('pk'):
            pk = int(req_dict['pk'])
            value = req_dict['value']
            obj = Catalog.objects.get(id = pk)#.values('name','id', 'ids', 'dealer_code', 'price')
            res = obj.chk_barcode(value)
            #obj.barcode = value
            #obj.save()
#            data = serializers.serialize('json', [obj,])
            #===================================================================
            #data = serializers.serialize('json', res, many = True)
#            data = serializers.serialize('json', res['f_model'])
            # ndt = { 'msq': res['msg'],'url': res['url'], 'status': res['status'], }
            # print "\nNdata = %s;\n" % (ndt)
            # jdata = json.dumps(ndt)
            # data = jdata + data
            # print "Jdata = %s ;\n Ndata = %s;\n Data = %s;\n" % (jdata, ndt, data)
            #===================================================================
            if res['f_model']:
                res['f_model'] = serializers.serialize('json', res['f_model'])
            #data = json.dumps(res, skipkeys=True)
            data = simplejson.dumps(res)
            data_res = data
#        print "DICT = %s" % req_dict
        if req_dict.has_key('code_value'):
            code = req_dict['code_value']
            obj = Catalog.objects.filter(Q(ids__icontains=code) | Q(dealer_code__icontains=code) | Q(barcode__contains=code) | Q(barcode_ean__contains=code) | Q(barcode_upc__contains=code) | Q(manufacture_article__icontains=code))
#            print "\nOBJ = " + str(obj.count()) + "\n"
            res = serializers.serialize('json', obj)
#            data = simplejson.dumps(res)
            data_res = res
            if obj.count() == 0 :
                data = [{'error_msg': 'Error: Item not found!', 'error' : True , 'searchText': code}, ]  
                res = simplejson.dumps(data)
            if obj.count() > 10 :
                data = [{'error_msg': 'Знайдено понад 10 товарів з таким кодом, допишіть ще частину коду щоб зменшити список', 'error' : True , 'searchText': code}, ]  
                res = simplejson.dumps(data)
                data_res = res

    return HttpResponse(data_res, content_type='application/json')    


@csrf_exempt
def catalog_attr_lookup(request):
    data = None
    results = []
    model_results = None
    attr_val_array = None
    msg = ''
    if request.is_ajax():
        if request.method == "POST":
            if request.POST.has_key(u'query') and request.POST.has_key(u'type'):
                value = request.POST[u'query']
                type_id = request.POST[u'type'] #[5, 84]
                t_ids = Type.objects.filter(id__in = type_id.split(','))
                if len(value) >= 2:
                    #model_results = None
                    if value == u'всі' or value == u'all':
                        model_results = CatalogAttribute.objects.filter(type__in = t_ids)
                        attr_val_array = CatalogAttributeValue.objects.filter(attr_id__in = model_results).select_related('attr_id')
                    else:
                        model_results = CatalogAttribute.objects.filter(name__icontains=value, type__in = t_ids)
                        attr_val_array = CatalogAttributeValue.objects.filter(Q(value__icontains = value) | Q(attr_id__name__icontains = value), attr_id__type__in = t_ids).select_related('attr_id')
                    #attr_val_array = CatalogAttributeValue.objects.filter(attr_id__in = model_results).select_related('attr_id')
                    for i in attr_val_array:
                        results.append({'attr_id': i.attr_id.id, 'attr_name': i.attr_id.name, 'value': i.value, 'value_float': i.value_float, 'id': i.pk, 'description': i.description})
                    data = serializers.serialize("json", attr_val_array, fields=('value', 'value_float', 'description', 'attr_id.name', 'attr_id'))
            attr_name = "Not found"
            if model_results.first():
                attr_name = model_results.first().name
                msg = u'Ajax: Виконано!'
            else:
                msg = u"Параметрів для цього товару не знайдено"
            json = simplejson.dumps({'attr_name': attr_name, 'status': False, 'msg': msg, 'data': results})    
    return HttpResponse(json, content_type='application/json')


@csrf_exempt
def catalog_add_attr(request):
    data = None
    type_id = None
    cat_ids = None
    msg = u'Ajax: Запит виконано успішно'
    attr_name = "Not found"
    if request.is_ajax():
        if request.method == "POST":
            if request.POST.has_key(u'ids') and request.POST.has_key(u'attr_id'):
                attr_id = request.POST[u'attr_id']
                ids = request.POST[u'ids'] 
                cat_ids = Catalog.objects.filter(id__in = ids.split(','))
#                print "CAt = %s" % cat_ids.count()
                try:
                    type_id = CatalogAttributeValue.objects.get(id = int(attr_id))
                    for cat in cat_ids:
                        cat.attributes.add( type_id ) 
                except:
                    msg = u'Ajax: Щось пішло не так'
                data = serializers.serialize("json", cat_ids, fields=('id', 'name', 'ids', 'dealer_code'))
            
    json = simplejson.dumps({'attr_name': attr_name, 'status': True, 'msg': msg, 'data': data})
    return HttpResponse(json, content_type='application/json')
        

@csrf_exempt
def catalog_del_attr(request):
    data = None
    type_id = None
    cat_ids = None
    msg = u'Ajax: Запит виконано успішно'
    status = True
    
#     if auth_group(request.user, "admin") == False:
#         status = False
#         msg = 'У вас немає доступу для видалення'
#         json = simplejson.dumps({'status': status, 'msg': msg, 'data': data})    
#         return HttpResponse(json, content_type='application/json')
    
    if request.is_ajax():
        if request.method == "POST":
            # delete one attr in one catalog item
            if request.POST.has_key(u'c_attr_val_id') and request.POST.has_key(u'cat_id'):
                attr_id = request.POST[u'c_attr_val_id']
                cat_id = request.POST[u'cat_id']
                try:
                    catv = CatalogAttributeValue.objects.get(id = attr_id)
                    #cat = Catalog.objects.get(id = cat_id)
                    cat_ids = Catalog.objects.filter(id = cat_id)
                    cat_ids[0].attributes.remove( catv ) 
                except:
                    status = False
                    msg = u'Ajax: Щось пішло не так. Можливо товар або дана властивість вже не існує.'
                    
                data = serializers.serialize("json", cat_ids, fields=('id', 'name', 'ids', 'dealer_code'))
#            else:
#                msg = u'Помилка: параметр c_attr_val_id не знайдено!'
#                status = False
                
            # delete one attr in maby catalog items
            if request.POST.has_key(u'attr_val_id'):
                if auth_group(request.user, "admin") == False:
                    status = False
                    msg = 'У вас немає доступу для видалення'
                    json = simplejson.dumps({'status': status, 'msg': msg, 'data': data})    
                    return HttpResponse(json, content_type='application/json')
                attr_id = request.POST[u'attr_val_id']
                catv = CatalogAttributeValue.objects.filter(id__in = attr_id)
                cat_ids = Catalog.objects.filter(attributes__in = catv)
                try:
#                    type_id = CatalogAttributeValue.objects.get(id = int(attr_id))
                    for cat in cat_ids:
                        cat.attributes.remove( catv[0] ) 
                except:
                    msg = u'Ajax: Щось пішло не так'
                    
                data = serializers.serialize("json", cat_ids, fields=('id', 'name', 'ids', 'dealer_code'))
            else:
                #msg = u'Помилка: параметр attr_val_id не знайдено!'
                #status = False
                pass
                
    json = simplejson.dumps({'status': status, 'msg': msg, 'data': data})    
    return HttpResponse(json, content_type='application/json')


@csrf_exempt
def catalog_get_locality(request):
    sel_id = None
    if request.method == 'POST':
        sel_id = request.POST.get('sel_id')
    list = Catalog.objects.get(id=sel_id)#.values_list("id", "locality")
    return HttpResponse(unicode(list.locality), content_type='text')


# ------------- Clients -------------
@csrf_exempt
def client_add(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            forumname = form.cleaned_data['forumname']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            phone1 = form.cleaned_data['phone1']
            sale = form.cleaned_data['sale']
            summ = form.cleaned_data['summ']
            description = form.cleaned_data['description']
            birthday = form.cleaned_data['birthday']
            sale_on = form.cleaned_data['sale_on']
            user = None             
            if request.user.is_authenticated():
                user = request.user
            shopN = get_shop_from_request(request)
            a = Client(name=name, forumname=forumname, country=country, city=city, email=email, phone=phone, sale=sale, summ=summ, description=description, phone1=phone1, birthday=birthday, sale_on=sale_on, reg_user=user, reg_shop=shopN)
            a.save()
            #return HttpResponseRedirect('/client/view/')
            return HttpResponseRedirect('/client/result/search/?id=' + str(a.id))
    else:
        form = ClientForm()
    context = {'form': form, 'weblink': 'client.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def client_edit(request, id):
    a = Client.objects.get(pk=id)
    if request.method == 'POST':
        form = ClientEditForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            #return HttpResponseRedirect('/client/view/')
            return HttpResponseRedirect('/client/result/search/?id='+id)
    else:
        form = ClientEditForm(instance=a)
    context = {'form': form, 'weblink': 'client.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def client_join(request, id=None):
    #a = Client.objects.get(pk=id)
    if auth_group(request.user, "admin") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для редагування ', 'next': current_url(request)}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)

    if request.method == 'POST':
        POST = request.POST
        if POST.has_key('client_main') and POST.has_key('client_1'): # and POST.has_key('client_1'):
            main_id = request.POST.get('client_main')
            first_id = request.POST.get('client_1')
            if (main_id == first_id):
                return HttpResponse("ПОМИЛКА: Вибрано одного клієнта!!!")
            mc = Client.objects.get(pk=main_id)
            fc = Client.objects.get(pk=first_id)
            
            ClientDebts.objects.filter(client=fc).update(client=mc)
            ClientCredits.objects.filter(client=fc).update(client=mc)
            ClientInvoice.objects.filter(client=fc).update(client=mc)
            ClientOrder.objects.filter(client=fc).update(client=mc)
            Bicycle_Sale.objects.filter(client=fc).update(client=mc)
            Bicycle_Order.objects.filter(client=fc).update(client=mc)
            WorkShop.objects.filter(client=fc).update(client=mc)
            WorkTicket.objects.filter(client=fc).update(client=mc)
            #Check.objects.filter(client=fc).update(client=mc)
            Rent.objects.filter(client=fc).update(client=mc)
            ClientMessage.objects.filter(client=fc).update(client=mc)
            ClientReturn.objects.filter(client=fc).update(client=mc)
            
            fc.delete()
            return HttpResponseRedirect('/client/result/search/?id=' + main_id)
    context = {'weblink': 'client_join.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def client_balance_list(request):
#===============================================================================
#    query = '''select accounting_client.id as id, accounting_client.name as name, sum(accounting_clientcredits.price) as sum_cred, sum(accounting_clientdebts.price) as sum_deb    
#            from accounting_client left join accounting_clientcredits on accounting_client.id=accounting_clientcredits.client_id 
#            left join accounting_clientdebts on  accounting_client.id=accounting_clientdebts.client_id 
#            group by accounting_clientcredits.client_id, accounting_clientdebts.client_id;
#            '''
#                
#===============================================================================
    query = '''select accounting_client.id as id, accounting_client.name as name, sum(accounting_clientdebts.price) as sum_deb 
            from accounting_client 
            left join accounting_clientdebts on accounting_clientdebts.client_id=accounting_client.id 
            group by accounting_client.id order by accounting_client.id;
            '''
    query1 = '''select accounting_client.id as id, sum(accounting_clientcredits.price) as sum_cred 
            from accounting_client 
            left join accounting_clientcredits on accounting_clientcredits.client_id=accounting_client.id 
            group by accounting_client.id order by accounting_client.id;
            '''

    if auth_group(request.user, "admin") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу. Авторизуйтесь на порталі або звеніться до адміністратора.', 'next': current_url(request)}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)

    list = None
    list1 = None
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        list = dictfetchall(cursor)
        cursor1 = connection.cursor()
        cursor1.execute(query1)
        list1 = cursor1.fetchall()
    except TypeError:
        res = "Помилка"

    for item in list1:
        for key in list:
            if item[0]==key['id']:
                key['sum_cred']=item[1]
                try:
                    key['sum_cred'] = int(key['sum_cred'])
                except TypeError:
                    key['sum_cred'] = 0  # or whatever you want to do
                try:
                    key['sum_deb'] = int(key['sum_deb'])
                except TypeError:
                    key['sum_deb'] = 0
                key['minus']=key['sum_cred']-key['sum_deb']
    s_debt = 0
    s_cred = 0
    for key1 in list[:]:
        s_debt+=key1['sum_deb']
        s_cred+=key1['sum_cred']
        if (key1['sum_deb']==False) & (key1['sum_cred']==False):
            #key1['minus']=9999
            list.remove(key1)
    context = {'clients': list, 'sum_debt':s_debt, 'sum_cred':s_cred, 'weblink': 'client_balance_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)
            

def client_list(request):
    list = Client.objects.all().order_by("-pk")
    paginator = Paginator(list, 100)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    context = {'clients': contacts, 'weblink': 'client_list.html', }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def client_email_list(request):
    list = Client.objects.exclude(email = '')
    
    paginator = Paginator(list, 50)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    
    return render_to_response('index.html', {'clients': contacts, 'weblink': 'client_email_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/client/view/')
    obj = Client.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/client/view/')


def client_data(request, id):
    obj = Client.objects.get(id=id)
    context = {'client': obj, 'weblink': 'client_data.html', } 
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def clientdebts_add(request, id=None):
    shop_id = get_shop_from_ip(request.META['REMOTE_ADDR'])
    if request.method == 'POST':
        form = ClientDebtsForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            cash = form.cleaned_data['cash']
            shop = form.cleaned_data['shop']
            if request.user.is_authenticated():
                user = request.user
            ClientDebts(client=client, date=date, price=price, description=description, user=user, cash=cash, shop=shop).save()
            
            if id != None:
                return HttpResponseRedirect('/client/result/search/?id='+str(id))
            else:
                return HttpResponseRedirect('/clientdebts/view/')
    else:
        if id != None:
            form = ClientDebtsForm(initial={'client': id, 'date': datetime.datetime.now(), 'shop': shop_id})
        else:
            form = ClientDebtsForm()
    #return render_to_response('clientdebts.html', {'form': form})
    context = {'form': form, 'weblink': 'clientdebts.html',}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

@csrf_exempt
def clientdebts_edit(request, id):
    if auth_group(request.user, "admin") == False:
        return HttpResponseRedirect('/')
    a = ClientDebts.objects.get(pk=id)
    if request.method == 'POST':
        form = ClientDebtsForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
#===============================================================================
#            client = form.cleaned_data['client']
#            date = form.cleaned_data['date']
#            work_type = form.cleaned_data['work_type']
#            price = form.cleaned_data['price']
#            description = form.cleaned_data['description']
#            WorkShop(id=id, client=client, date=date, work_type=work_type, price=price, description=description).save()
#===============================================================================
            return HttpResponseRedirect('/clientdebts/view/')
    else:
        form = ClientDebtsForm(instance=a)
    context = {'form': form, 'weblink': 'client.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


#BORG
def clientdebts_list(request):
    #list = ClientDebts.objects.select_related().all()
    list = ClientDebts.objects.all().order_by("-id")
    
    paginator = Paginator(list, 50)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        debts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        debts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        debts = paginator.page(paginator.num_pages)
    context = {'clients': debts, 'weblink': 'clientdebts_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def clientdebts_delete(request, id):
    if auth_group(request.user, "admin") == False:
        return HttpResponseRedirect('/.')
    obj = ClientDebts.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def clientdebts_delete_all(request, client_id):
    if auth_group(request.user, "admin") == False:
        return HttpResponseRedirect('/.')
    obj = ClientDebts.objects.filter(client=client_id).delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@csrf_exempt
def clientcredits_add(request, id=None):
    shop_id = get_shop_from_ip(request.META['REMOTE_ADDR'])
    if request.method == 'POST':
        form = ClientCreditsForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            cash_type = form.cleaned_data['cash_type']
            shop = form.cleaned_data['shop']
            user = None             
            if request.user.is_authenticated():
                user = request.user
            ClientCredits(client=client, date=date, price=price, description=description, user=user, cash_type=cash_type, shop=shop).save()
            if id != None:
                return HttpResponseRedirect('/client/result/search/?id='+str(id))
            else:
                return HttpResponseRedirect('/clientcredits/view/')
    else:
        if id != None:
            cred = ClientCredits.objects.filter(client=id).aggregate(Sum('price'))
            deb = ClientDebts.objects.filter(client=id).aggregate(Sum('price'))
            #values('price').annotate(sum_deb=Sum('price'))
            if cred['price__sum'] == None:
                cred['price__sum'] = 0
            if deb['price__sum'] == None:
                deb['price__sum'] = 0
            borg = deb['price__sum'] - cred['price__sum']
            if borg <= 0:
                borg = 0
            form = ClientCreditsForm(initial={'client': id, 'date': datetime.datetime.now(), 'price': borg, 'description': "Закриття боргу ", 'shop': shop_id})
        else:
            form = ClientCreditsForm()
    #return render_to_response('clientcredits.html', {'form': form})
    context = {'form': form, 'weblink': 'clientcredits.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def clientcredits_list(request):
    list = ClientCredits.objects.all().order_by("-id")
    paginator = Paginator(list, 50)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        credits = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        credits = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        credits = paginator.page(paginator.num_pages)
    context = {'clients': credits, 'weblink': 'clientcredits_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def clientcredits_edit(request, id):
    if auth_group(request.user, "admin") == False:
#        return HttpResponseRedirect('/')
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для редагування ', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    a = ClientCredits.objects.get(pk=id)
    if request.method == 'POST':
        form = ClientCreditsForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/clientcredits/view/')
    else:
        form = ClientCreditsForm(instance=a)
    context = {'form': form, 'weblink': 'clientcredits.html', }
    context.update(custom_proc(request))         
    return render(request, 'index.html', context)

@csrf_exempt
def clientcredits_set(request):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id') and POST.has_key('value'):
                id = request.POST.get( 'id' )
                ct = request.POST.get( 'value' )
                r = ClientCredits.objects.get(id = id)
                cashtype = CashType.objects.get(id = ct)
                r.cash_type = cashtype
                r.save()
                search = ClientCredits.objects.filter(id = id).values('cash_type__name', 'cash_type__id')
                return HttpResponse(simplejson.dumps(list(search)))    
    

def clientcredits_delete(request, id):
    if auth_group(request.user, "admin") == False:
        return HttpResponseRedirect('/')
    obj = ClientCredits.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    #return HttpResponseRedirect('/clientcredits/view/')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
    #return HttpResponse('<script language="JavaScript">history.back();</script>')


def clientcredits_delete_all(request, client_id):
    if auth_group(request.user, "admin") == False:
        return HttpResponseRedirect('/')
    obj = ClientCredits.objects.filter(client=client_id).delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

#old function
def client_invoice_shorturl(request, cid=None):
    cat = Catalog.objects.get(id = cid)
    context = {'weblink': 'guestinvoice.html', 'cat': cat}
    return render(request, 'index.html', context)

@csrf_exempt
def client_invoice(request, cid=None, id=None, ciid=None):
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    cat = None
    a = None
    if not request.user.is_authenticated():
        context = {'weblink': 'guestinvoice.html', 'cat': cat}
        #custom_proc(request)
        return render(request, 'index.html', context)
    now = datetime.datetime.now()
    if (id):
        client = Client.objects.get(pk = id)
        a = ClientInvoice(client = client, date=datetime.datetime.today(), price=cat.price, sum=cat.price, sale=int(cat.sale), pay=0, count=1, currency=Currency.objects.get(id=3), catalog=cat, user = request.user)
    elif (cid):
        cat = Catalog.objects.get(id = cid)
        a = ClientInvoice(date=datetime.datetime.today(), price=cat.price, sum=cat.price, sale=int(Catalog.objects.get(id = cid).sale), pay=0, count=1, currency=Currency.objects.get(id=3), catalog=cat, user = request.user)
    elif (ciid):
        a = ClientInvoice.objects.get(pk = ciid)
        cat = Catalog.objects.get(id = a.catalog.id)
        cid = a.catalog.id
    else:
        a = ClientInvoice(date=datetime.datetime.today(), price=cat.price, sum=cat.price, sale=int(Catalog.objects.get(id = cid).sale), pay=0, count=1, currency=Currency.objects.get(id=3), catalog=cat, user = request.user)

    if (a.pay == a.sum) and ( auth_group(request.user, "admin") == False ):
        context = {'weblink': 'error_message.html', 'mtext': 'Даний товар вже продано і ви не можете його редагувати. Зробіть повернення!'}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
        
    if request.method == 'POST':
        form = ClientInvoiceForm(request.POST, instance = a, catalog_id=cid, request = request)
        if form.is_valid():
            client = form.cleaned_data['client']
            catalog = form.cleaned_data['catalog']
            count = form.cleaned_data['count']
            price = form.cleaned_data['price']
            sum = form.cleaned_data['sum']
            currency = form.cleaned_data['currency']
            sale = form.cleaned_data['sale']
            pay = form.cleaned_data['pay']
            date = form.cleaned_data['date']
            description = form.cleaned_data['description']
            clen = form.cleaned_data['length']
            shop = form.cleaned_data['shop']
#            sbox = form.cleaned_data['sbox_inv']
#            print "\nSBOX id = %s \n"  % sbox
            if request.POST.has_key('sbox_count[]') and request.POST.has_key('sbox_ids[]'):
                sbox_count = request.POST.get('sbox_count[]')
                sbox_ids = request.POST.get('sbox_ids[]')
                sbox_count = json.loads(sbox_count)
                sbox_ids = json.loads(sbox_ids)
                
#                print "\nSBOX count = %s \n"  % sbox_count
#                print "\nSBOX ids = %s \n"  % type(sbox_ids) 
                                                
            if (clen is not None) and (cat.type.pk == 13):
                description = description + '\nlength:' + str(clen)
                if cat.length is not None:
                    cat.length = cat.length + clen
                else:
                    cat.length = 0
            user_id = form.cleaned_data['user']
            if request.user.is_authenticated():
                user = user_id
            ci = a
            #ci = ClientInvoice(client=client, catalog=catalog, count=count, sum=sum, price=price, currency=currency, sale=sale, pay=pay, date=date, description=description, user=user, shop=shopN)
            ci.client = client
            ci.catalog=catalog
            ci.count=count
            ci.sum=sum
            ci.price=price
            ci.currency=currency
            ci.sale=sale
            ci.pay=pay
            ci.date=date
            ci.description=description 
            ci.user=user
            if auth_group(request.user, "admin") == True:
                ci.shop = shop
            else: 
                ci.shop=shopN
            
            ci.save()
            
            index = 0
            #sb_count = 0
#            print ("Sbox IDS (JSON) = %s \n" % sbox_ids)
#            print ("Sbox IDS count (JSON) = %s \n" % sbox_count)
            for box in sbox_ids:
                sb_count = 0
                sbox = StorageBox.objects.get(pk = sbox_ids[index])
                sb_count = sbox_count[index]
                if sb_count > 0:
                    obj_cisb = sbox.get_ci_sb_by_cinv(ci)
                    if obj_cisb:  
                        for i in obj_cisb: 
                            i.set_count(sb_count, now, user)
                    else:
                        ClientInvoiceStorageBox(sbox=sbox, cinvoice=ci, count=sb_count, date_create=now, user_create=user).save()
                index+=1
            
            if pay == sum:
                desc = catalog.name
                ct = CashType.objects.get(id=1)
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=ct)
                ccred.save()
                cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
                cdeb.save()

            return HttpResponseRedirect('/client/invoice/view/')
    else:
        form = ClientInvoiceForm(instance = a, catalog_id=cid, request = request)
        #form = ClientInvoiceForm(initial = { 'instance' : a, 'catalog_id' : cid, 'user': request.user})
    nday = 3
    nbox = cat.get_storage_box()
    b_len = False
    if cat.type.pk == 13:
        b_len = True
        
    clients_list = ClientInvoice.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client')).order_by('client__name') #'-client__id',

    cat_obj = cat.get_discount_item()
    context = {'form': form, 'weblink': 'clientinvoice.html', 'clients_list': clients_list, 'catalog_obj': cat, 'cat_sale':cat_obj, 'box_numbers': nbox, 'b_len': b_len, 'ci_obj': a}
    context.update(custom_proc(request))
    return render(request, 'index.html',  context)
#===============================================================================
# 
# @csrf_exempt
# def client_invoice_edit(request, id):
#     a = ClientInvoice.objects.get(id=id)
#     s_user = a.user
#     cat = Catalog.objects.get(id = a.catalog.id)
#     if not request.user.is_authenticated():
#         context = {'weblink': 'guestinvoice.html', 'cat': cat}
#         return render(request, 'index.html', context)
#     if (a.pay == a.sum) and ( auth_group(request.user, "admin") == False ):
#         context = {'weblink': 'error_message.html', 'mtext': 'Даний товар вже продано і ви не можете його редагувати'}
#         context.update(custom_proc(request))
#         return render(request, 'index.html', context)
#     
#     now = datetime.datetime.now()
#     old_count = a.count
#     cat_id = a.catalog.id
#     cat = Catalog.objects.get(id = cat_id)
#     if request.method == 'POST':
#         form = ClientInvoiceForm(request.POST, instance = a, catalog_id = cat_id, request = request)
#         if form.is_valid():
#             client = form.cleaned_data['client']
#             catalog = form.cleaned_data['catalog']
#             count = form.cleaned_data['count']
#             price = form.cleaned_data['price']
#             sum = form.cleaned_data['sum']
#             currency = form.cleaned_data['currency']
#             sale = form.cleaned_data['sale']
#             pay = form.cleaned_data['pay']
#             date = form.cleaned_data['date']
#             clen = form.cleaned_data['length']
#             shop = form.cleaned_data['shop']
#             user = form.cleaned_data['user']
#             description = form.cleaned_data['description']
#             if (clen is not None) and (cat.type.pk == 13):
#                 if a.description.find('length:')>=0:
#                     old_length = a.description.split('\n')[-1].split('length:')[1]
#                 if cat.length is not None:
#                     cat.length = cat.length - float(old_length) + float(clen)
#                 else:
#                     cat.length = 0 - float(old_length) + float(clen)
#                 description = description + '\nlength:' + str(clen)
#             cat.count = cat.count + (old_count - count)
#             cat.save()
# 
#             if (request.user.is_authenticated()) and (request.user.id == s_user.id):
#                 user = user
#             else:
#                 if auth_group(request.user, "admin") == True:
#                     user = user
#                 else:
#                     user = s_user
#             ClientInvoice(id=id, client=client, catalog=catalog, count=count, sum=sum, price=price, currency=currency, sale=sale, pay=pay, date=date, description=description, user=user, shop=shop).save()
# 
#             if pay == sum:
#                 desc = catalog.name
#                 ct = CashType.objects.get(id=1)
#                 ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=ct)
#                 ccred.save()
#                 cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
#                 cdeb.save()
#             
#             return HttpResponseRedirect('/client/invoice/view/')
#     else:
#         form = ClientInvoiceForm(instance = a, catalog_id = cat_id, request = request)
#     nday = 3 # користувачі за останні n-днів
#     dlen = None
#     nbox = cat.locality
#     b_len = False
#     if cat.type.pk == 13:
#         b_len = True
#         if a.description.find('length:')>=0:
#             dlen = a.description.split('\n')[-1].split(':')[1]
#     clients_list = ClientInvoice.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client')).order_by('client__id')
#     cat_obj = cat.get_discount_item()    
#     context = {'form': form, 'weblink': 'clientinvoice.html', 'clients_list': clients_list, 'catalog_obj': cat, 'cat_sale':cat_obj, 'box_number': nbox, 'b_len': b_len, 'desc_len':dlen,}
#     context.update(custom_proc(request))     
#     return render(request, 'index.html', context )
#===============================================================================

@csrf_exempt
def client_invoice_set(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування', content_type="text/plain;charset=UTF-8;")
            POST = request.POST  
            if POST.has_key('ids[]'):
                ids = request.POST.getlist('ids[]')
                if POST.has_key('client'):
                    client = request.POST['client']
                else:
                    client = False
                if POST.has_key('count'):
                    count = request.POST['count']
                
                ci_list = ClientInvoice.objects.filter(id__in = ids)
                for ci in ci_list:
                    if int(count) != 0:
                        ci.count = count
                        ci.sum = ci.price * int(count) * (1-ci.sale/100.0)
                    if client:
                        ci.client = Client.objects.get(id = client)
                        ci.update_sale()
                    ci.save()
                result = 'Виконано'
                return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
                
            return HttpResponse("Помилка", content_type="text/plain;charset=UTF-8;")


@csrf_exempt
def client_invoice_delete(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для видалення')
            POST = request.POST  
            if POST.has_key('ids[]'):
                ids = request.POST.getlist('ids[]')
                ci_list = ClientInvoice.objects.filter(id__in = ids)
                for ci in ci_list:
                    if ci.pay == ci.sum:
                        result = "Товар [" + str(ci.id) + "]" + str(ci.catalog) + "не можливо видалити. Його можливо тільки повернути!"
                        return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
                    else:
                        ci.delete()
                result = 'ok'
                return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
        else:
            result = 'Помилка запиту'
            return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
        
    obj = ClientInvoice.objects.get(id=id)
    cat = Catalog.objects.get(id = obj.catalog.id)
    if cat.type.pk == 13:
        if obj.description.find('length:')==0:
            old_length = obj.description.split('\n')[-1].split(':')[1]
            cat.length = cat.length - float(old_length)
    
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має прав для видалення')
    if (obj.pay == obj.sum) and auth_group(request.user, 'admin')==True:
        del_logging(obj)
        obj.delete()
        cat.count = cat.count + obj.count
        cat.save()
        return HttpResponseRedirect('/client/invoice/view/')
    if (obj.pay == obj.sum) and auth_group(request.user, 'admin')==False:
        return HttpResponse("Помилка: Даний товар можливо лише повернути")
    else:    
        del_logging(obj)
        obj.delete()
        cat.count = cat.count + obj.count
        cat.save()
    return HttpResponseRedirect('/client/invoice/view/')


def client_invoice_view(request, month=None, year=None, day=None, id=None, notpay=False, shop=None, client_id=None, all=None):
    # upd = ClientInvoice.objects.filter(sale = None).update(sale=0) # update recors with sale = 0
    show_month = month
    if year == None:
        year = datetime.datetime.now().year
    if month == None:
        month = datetime.datetime.now().month
        show_month = month 
    if day == None:
        day = datetime.datetime.now().day
#        list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date", "-id").values('id', 'client__id', 'client__name', 'sum', 'count', 'catalog__ids', 'catalog__name', 'price', 'currency__name', 'sale', 'pay', 'date', 'description', 'user__username', 'catalog__count', 'catalog__locality', 'catalog__pk', 'client__forumname')
        list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date", "-id")
    else:
        if day == 'all':
#            list = ClientInvoice.objects.filter(date__year=year, date__month=month).order_by("-date", "-id").values('id', 'client__id', 'client__name', 'sum', 'count', 'catalog__ids', 'catalog__name', 'price', 'currency__name', 'sale', 'pay', 'date', 'description', 'user__username', 'catalog__count', 'catalog__locality', 'catalog__pk', 'client__forumname')
            list = ClientInvoice.objects.filter(date__year=year, date__month=month).order_by("-date", "-id")            
        else:
#            list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date", "-id").values('id', 'client__id', 'client__name', 'sum', 'count', 'catalog__ids', 'catalog__name', 'price', 'currency__name', 'sale', 'pay', 'date', 'description', 'user__username', 'catalog__count', 'catalog__locality', 'catalog__pk', 'client__forumname')
            list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date", "-id")            
            day = int(day)
    psum = 0
    scount = 0
    sprofit = 0

    if client_id:
        list = list.filter(client = client_id)
    if client_id and all:
        list = ClientInvoice.objects.filter(date__year=year, client = client_id).order_by("-date", "-id")
        show_month = 'all'

    if (shop and shop <> '0'):
        list = list.filter(shop = shop)

    if notpay == True:    
        list = list.exclude(sum = F('pay'))
   
    for item in list:
#        scount = scount + item['count']
        psum = psum + item.sum
        scount = scount + item.count
        sprofit = sprofit + item.get_profit()[1]        
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    shops = Shop.objects.all()
    if shop == None:
        shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
        shop = shopN.id or 0
        if all != 'all':
            list = list.filter(shop = shop)
        
    paginator = Paginator(list, 15)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        cinvoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        cinvoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        cinvoices = paginator.page(paginator.num_pages)
        
#    context = {'sel_year':year, 'sel_month':int(month), 'month_days':days, 'sel_day':day, 'buycomponents': cinvoices, 'shops': shops, "shop": int(shop), 'sumall':psum, 'sum_profit':sprofit, 'countall':scount, 'weblink': 'clientinvoice_list.html', 'view': True,} 
    context = {'sel_year':year, 'sel_month':month, 'show_month': show_month, 'month_days':days, 'sel_day':day, 'buycomponents': cinvoices, 'shops': shops, "shop": int(shop), 'sumall':psum, 'sum_profit':sprofit, 'countall':scount, 'weblink': 'clientinvoice_list.html', 'view': True,}
    custom_dict = custom_proc(request)
    context.update(custom_dict)
    return render(request, 'index.html', context)


@csrf_exempt
def client_invoice_lookup(request, client_id):
    list = None
    client_invoice_sum = 0
    if request.is_ajax():
#        list = ClientInvoice.objects.filter(client=client_id).order_by("-date", "-id")
        list = ClientInvoice.objects.filter(client=client_id).values('date', 'catalog', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__name', 'count', 'price', 'sum', 'pay', 'currency__name').order_by("-date", "-id")
        for a in list:
            client_invoice_sum = client_invoice_sum + a['sum']

        #return HttpResponse("AJAX - TEST TAB for myTable")            
        return render_to_response('clientinvoice_ajax.html', {'invoice': list, 'client_invoice_sum': client_invoice_sum})
    #return HttpResponse("TEST TAB for myTable")
    
    list = ClientInvoice.objects.filter(client=client_id).values('date', 'catalog', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__name', 'count', 'price', 'sum', 'pay', 'currency__name').order_by("-date", "-id")
    return render_to_response('clientinvoice_ajax.html', {'invoice': list})


def client_invoice_id(request, id, notpay=False):
    list = ClientInvoice.objects.filter(catalog__id=id).order_by("-date", "-id") #.values('id', 'client__id', 'client__name', 'sum', 'count', 'catalog__ids', 'catalog__name', 'price', 'currency__name', 'sale', 'pay', 'date', 'description', 'user__username', 'catalog__count', 'catalog__locality', 'catalog__pk', 'client__forumname')
    psum = 0
    scount = 0
    sprofit = 0
    for item in list:
        psum = psum + item.sum
        scount = scount + item.count
        sprofit = sprofit + item.get_profit()[1]  

    if notpay == True:    
        list = list.exclude(sum = F('pay'))
    
    paginator = Paginator(list, 15)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        cinvoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        cinvoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        cinvoices = paginator.page(paginator.num_pages)
    context = {'buycomponents': cinvoices, 'sumall':psum, 'countall':scount, 'sum_profit':sprofit, 'weblink': 'clientinvoice_list.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def client_invoice_check(request, param=None):
    list_id = request.session['invoice_id']
    check_num = request.session['chk_num']
    ci = ClientInvoice.objects.filter(id__in=list_id)
    #-------- показ і відправка чеку на електронку ------
    client = ci[0].client
    #client = None 
    sum = ci.aggregate(Sum('sum'))
    sum = sum['sum__sum']
    text = pytils_ua.numeral.in_words(int(sum))
    month = pytils_ua.dt.ru_strftime(u"%d %B %Y", ci[0].date, inflected=True)
    
    w = render_to_response('client_invoice_sale_check.html', {'check_invoice': ci, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'check_num':check_num})
    if param == 'print':
        return w
    if param == 'email': 
        if client.email == '':
            return HttpResponse("Заповніть поле Email для відправки чеку")
        subject, from_email, to = 'Товарний чек від веломагазину Rivelo', 'rivelo@ukr.net', client.email
        text_content = 'www.rivelo.com.ua'
        html_content = w.content
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to, 'rivelo.shop@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponse("Лист з чеком успішно відправлено")        
    
    return w    
    #return HttpResponse("Ваши логин и пароль не соответствуют. Session = " + str(list_id))


def client_workshop_check(request, param=None):
    list_id = request.session['invoice_id']
    wk = WorkShop.objects.filter(id__in=list_id)
    client = wk[0].client
    desc = u"Роботи: "
    sum = 0
    #-------- показ і відправка чеку на електронку ------
    sum = wk.aggregate(Sum('price'))
    sum = sum['price__sum']
    text = pytils_ua.numeral.in_words(int(sum))
    month = pytils_ua.dt.ru_strftime(u"%d %B %Y", wk[0].date, inflected=True)
    context = {'check_invoice': wk, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'print':param, 'is_workshop': 'True', }
    context.update(custom_proc(request)) 
    w = render(request, 'client_invoice_sale_check.html', context)
#    w = render_to_response('client_invoice_sale_check.html', {'check_invoice': ci, 'month':month, 'sum': sum, 'client': client, 'str_number':text})
    if param == 'print':
        return w
    if param == 'email': 
        if client.email == '':
            return HttpResponse("Заповніть поле Email для відправки чеку")
        subject, from_email, to = 'Товарний чек від веломагазину Rivelo', 'rivelo@ymail.com', client.email
        text_content = 'www.rivelo.com.ua'
        html_content = w.content
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to, 'rivelo@ukr.net'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponse("Лист з чеком успішно відправлено")        
    
    return w    


def client_invioce_return_view(request, limit = None, shop=None):
    cr_list = None
    if limit != None:
        cr_list = ClientReturn.objects.all().order_by('-id')[:limit]
    else:
        cr_list = ClientReturn.objects.all()
    context = {'return_list': cr_list, 'weblink': 'ci_return_list.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context) 

@csrf_exempt
def client_invioce_return_add(request, id):
    ci = ClientInvoice.objects.get(id=id)
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    now = datetime.datetime.now()
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('msg') and POST.has_key('count'):
                msg = request.POST.get('msg')
                count = request.POST.get('count')
                cash = request.POST.get('cash')
                sum = ci.sum / ci.count * int(count)
                if int(count) > ci.count:
                    return HttpResponse("Error. Return count bigger then real", content_type="text/plain;charset=UTF-8;")
                res_count = ci.count - int(count)
                if res_count < 0:
                    count = ci.count
                    res_count = 0
                    sum = ci.sum / ci.count * int(count)
                if cash == "false":
                    cash = False
                    ClientCredits(client=ci.client, date=now, price=sum, description="Повернення/обмін: " + str(ci.catalog), cash_type=CashType.objects.get(name=u"Повернення"), user=request.user, shop=shopN).save()
                if cash == "true":
                    cash = True
                    ClientCredits(client=ci.client, date=now, price=sum, description="Повернення/обмін: " + str(ci.catalog), cash_type=CashType.objects.get(name=u"Повернення"), user=request.user, shop=shopN).save() 
                    ClientDebts(client=ci.client, date=now, price=sum, description="Повернення/обмін: " + str(ci.catalog), cash=True, user=request.user, shop=shopN).save() 
                cat = Catalog.objects.get(id = ci.catalog.id)
                cat.count = cat.count + int(count)
                cat.save() 
                ClientReturn(client = ci.client, catalog = ci.catalog, sum = sum, buy_date = ci.date, buy_user = ci.user, user = request.user, date=now, msg=msg, count=count, cash=cash).save()
                
                if res_count == 0:
                    ci.delete()
                else:
                    ci.count = res_count
                    if ci.sale <> 100:
                        ci.sum = res_count * ci.get_sale_price()
                    ci.pay = res_count * ci.get_sale_price()
                    ci.shop = shopN
                    ci.save()
    return HttpResponse("ok", content_type="text/plain;charset=UTF-8;")
 

def client_order_list(request):
    now = datetime.datetime.now()
    #list = ClientOrder.objects.filter(Q(status = False) | Q(date__year__gt = 2015))
    list = ClientOrder.objects.filter((Q(status = False)) | Q(date__gt=now-datetime.timedelta(days=360)))
    context = {'c_order': list, 'weblink': 'client_order_list.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)    

@csrf_exempt
def client_order_add(request, cid=None):
    #a = ClientOrder(date=datetime.datetime.today(), pay=0, count=1, currency=Currency.objects.get(id=3), catalog=Catalog.objects.all())
    a = ClientOrder(date=datetime.datetime.today(), pay=0, count=1, currency=Currency.objects.get(id=3))
    if request.method == 'POST':
        #form = ClientOrderForm(request.POST, instance = a, catalog_id=cid)
        form = ClientOrderForm(request.POST, instance = a)        
        if form.is_valid():
            client = form.cleaned_data['client']
#            catalog = form.cleaned_data['catalog']
#            arrray = catalog.split(":")
#            catalog = array[0]
            post = form.cleaned_data['post_id']
            catalog = None
            if post:
                catalog = Catalog.objects.get(id=post)
            description = form.cleaned_data['description']
            count = form.cleaned_data['count']
            price = form.cleaned_data['price']
            sum = form.cleaned_data['sum']
            currency = form.cleaned_data['currency']
            pay = form.cleaned_data['pay']
            date = form.cleaned_data['date']
            cash_type = form.cleaned_data['cash_type']
            user = None #form.cleaned_data['user_id']
            if request.user.is_authenticated():
                user = request.user
            if catalog:
                s = u"Аванс - " + catalog.name + "(" + description + ")"
            else:
                s = u"Аванс - " + description 
            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=pay, description=s, cash_type=cash_type, user=user)
            ccred.save()

            ClientOrder(client=client, catalog=catalog, count=count, sum=sum, price=price, currency=currency, pay=pay, date=date, description=description, user=user, credit=ccred).save()
            return HttpResponseRedirect('/client/order/view/')
    else:
        #form = ClientOrderForm(instance = a, catalog_id=cid)
        form = ClientOrderForm(instance = a)
    context = {'form': form, 'weblink': 'clientorder.html', 'next': current_url(request)}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def client_order_edit(request, id):
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('id'):
                q = request.GET.get( 'id' )
                r = ClientOrder.objects.get(id = id)
                r.status = not r.status
                r.save()
                search = ClientOrder.objects.filter(id = id).values('status')
                return HttpResponse(simplejson.dumps(list(search)))
    
    cash_type = CashType.objects.get(name=u"Готівка")
    
    a = ClientOrder.objects.get(pk=id)
    if request.method == 'POST':
        form = ClientOrderForm(request.POST, instance=a)

        if form.is_valid():
            pay = form.cleaned_data['pay']
            post = form.cleaned_data['post_id']
            cash_type = form.cleaned_data['cash_type']
            client = form.cleaned_data['client']
            catalog = None
            if post:
                catalog = Catalog.objects.get(id=post)
            form.save()
            a.catalog = catalog
            a.save()
            cred = ClientCredits.objects.get(id = a.credit.id)
            cred.client = client
            cred.price = pay
#            cred.cash_type = CashType.objects.get(name=u"Готівка")
            cred.cash_type = cash_type
            cred.save()
            return HttpResponseRedirect('/client/order/view/')
    else:
        if a.catalog:
            form = ClientOrderForm(instance=a, initial={'catalog' : a.catalog.pk, 'client': a.client.pk})
        else:
            form = ClientOrderForm(instance=a, initial={'client': a.client.pk})
    context = {'form': form, 'weblink': 'clientorder.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def client_order_delete(request, id):
    if auth_group(request.user, "admin") == False:
        return HttpResponseRedirect('/')
    obj = ClientOrder.objects.get(id=id)
    del_logging(obj)
    try:
        cred = ClientCredits.objects.get(id=obj.credit.id)
        del_logging(cred)
        cred.delete()
    except TypeError:
        res = "Помилка"
    obj.delete()
    return HttpResponseRedirect('/client/order/view/')
#    return HttpResponseRedirect(request.META['HTTP_REFERER'])


# Report sold components by month 
def client_invoice_report(request):
    if auth_group(request.user, "admin") == False:
        #return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу до даної сторінки!', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        return render(request, 'index.html', {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу до даної сторінки!'} )
    query = "SELECT EXTRACT(year FROM date) as year, EXTRACT(month from date) as month, MONTHNAME(date) as month_name, COUNT(*) as bike_count, sum(pay) as s_price FROM accounting_clientinvoice GROUP BY year,month;"
    #sql2 = "SELECT sum(price) FROM accounting_clientdebts WHERE client_id = %s;"
    #user = id;
    list = None
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        list = dictfetchall(cursor)
        #list = cursor.execute(sql1, )   
    except TypeError:
        res = "Помилка"
        
    sum = 0
    bike_sum = 0
    for month in list:
         sum = sum + month['s_price']
         bike_sum = bike_sum + month['bike_count']
    #list = Bicycle_Sale.objects.all().order_by('date')
    return render(request, 'index.html', {'bicycles': list, 'all_sum': sum, 'bike_sum': bike_sum, 'weblink': 'clientinvoice_sale_report.html', 'next': current_url(request)})


def client_search(request):
    #query = request.GET.get('q', '')
    context = {'weblink': 'client_search.html', 'next': current_url(request)}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


@csrf_exempt
def client_search_result(request):
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('name'):
                q = request.GET.get('name')
                c = Client.objects.filter(Q(name__icontains = q) | Q(forumname__icontains = q)).values('id','name', 'forumname')
#                res = Client.objects.filter(Q(name__icontains = q)).values_list('name', flat=True)
                return HttpResponse(simplejson.dumps(list(c)))

        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('phone'):
                q = request.POST.get('phone')
                c = Client.objects.filter(Q(phone__icontains = q) | Q(phone1__icontains = q)).values('id','name', 'forumname', 'phone', 'phone1')
#                res = Client.objects.filter(Q(name__icontains = q)).values_list('name', flat=True)
                return HttpResponse(simplejson.dumps(list(c)))
    
    username = request.GET['name']
    phone = request.GET['phone']
    city = request.GET['city']
    description = request.GET['description']
    cred = request.GET['cred']
    debt = request.GET['debt']
    client = None
    #clients = Client.objects.filter(name__icontains=username)
    if description:
        clients = Client.objects.filter(Q(description__icontains=description))
    if city:
        clients = Client.objects.filter(Q(city__icontains=city))
    if phone:
        clients = Client.objects.filter(Q(phone__icontains=phone) | Q(phone1__icontains=phone))
    if username:
        clients = Client.objects.filter(Q(name__icontains=username) | Q(forumname__icontains=username))
    if cred:
        clients = ClientCredits.objects.filter(Q(description__icontains=cred))
    if debt:
        clients = ClientCredits.objects.filter(Q(description__icontains=debt))

    if clients.count() == 1:
        return HttpResponseRedirect("/client/result/search/?id=" + str(clients[0].id))

    paginator = Paginator(clients, 50)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    if cred:
        return render_to_response('index.html', {'clients': contacts, 'weblink': 'clientcredits_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))        
    if debt:
        context = {'clients': contacts, 'weblink': 'clientdebts_list.html'}
        context.update(custom_proc(request))
        return render(request, 'index.html', context1)

    GET_params = request.GET.copy()  
    context = {'clients':contacts, 'weblink': 'client_list.html', 'c_count': clients.count(), 'GET_params':GET_params,}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


#----- Виписка клієнта -----
def client_result(request, tdelta = 30, id = None, email=False):
    now = datetime.datetime.now()
    user = None
    if request.GET.has_key('id'):
        user = request.GET['id']
    if id != None:
        user = id 
    sql1 = "SELECT sum(price) FROM accounting_clientcredits WHERE client_id = %s;"
    sql2 = "SELECT sum(price) FROM accounting_clientdebts WHERE client_id = %s;"
    try:
        cursor = connection.cursor()
        cursor.execute(sql1, [user])   
        credit= cursor.fetchone()
        cursor.execute(sql2, [user])
        debts = cursor.fetchone()
        if (credit[0] is None):
            credit = (0,)
        elif (debts[0] is None):
            debts = (0,)
        res = credit[0] - debts[0]
    except TypeError:
        res = "Такого клієнта не існує, або в нього не має заборгованостей"
    
    try:
        #client_name = Client.objects.values('name', 'forumname', 'id', 'phone', 'birthday', 'email').get(id=user)
        client_name = Client.objects.get(id=user)
    except ObjectDoesNotExist:
        client_name = ""
    
    credit_list = None
    cash_id = CashType.objects.get(id = 6) # Зарплата
    if auth_group(request.user, "admin") == False:
        #if str(request.user.username.encode('utf8')) == str(client_name['forumname'].encode('utf8')):
        if request.user.username == client_name.forumname.encode('utf8'):
        #if request.user.username == client_name['forumname'].encode('utf8'):            
            credit_list = ClientCredits.objects.filter(client=user, date__gt=now-datetime.timedelta(days=tdelta))
        else:    
            credit_list = ClientCredits.objects.filter(client=user, date__gt=now-datetime.timedelta(days=tdelta)).exclude(cash_type = cash_id)
    else: 
        credit_list = ClientCredits.objects.filter(client=user, date__gt=now-datetime.timedelta(days=tdelta))
    debt_list = ClientDebts.objects.filter(client=user, date__gt=now-datetime.timedelta(days=tdelta))
    client_invoice = ClientInvoice.objects.filter(Q(client=user) & (Q(pay__lt = F('sum')) | Q(date__gt=now-datetime.timedelta(days=tdelta))) ).order_by("-date", "-id")
     
    if client_invoice.count()>45 :
        tdelta = 6
        client_invoice = ClientInvoice.objects.filter(Q(client=user) & (Q(pay__lt = F('sum')) | Q(date__gt=now-datetime.timedelta(days=tdelta))) ).order_by("-date", "-id")
    client_invoice_sum = 0
    for a in client_invoice:
        client_invoice_sum = client_invoice_sum + a.sum

    client_workshop_sum = 0
    client_workshop = WorkShop.objects.filter(client=user).order_by("-date")
    for a in client_workshop:
        client_workshop_sum = client_workshop_sum + a.price
            
    b_bike = Bicycle_Sale.objects.filter(client=user).values('model__model__model', 'model__model__brand__name', 'model__serial_number', 'model__size__name', 'date', 'service', 'id')
    workshop_ticket = WorkTicket.objects.filter(client=user).values('id', 'date', 'description', 'status__name', 'phone_status__name', 'phone_user__username', 'phone_date', 'bike_part_type', 'bicycle', 'shop__name', 'user__username').order_by('-date')
    messages = ClientMessage.objects.filter(client=user).values('msg', 'status', 'date', 'user__username', 'id')
    status_msg = messages.values('status').filter(status=False).exists()
    rent = Rent.objects.filter(client=user)
    status_rent = rent.filter(status=False).exists()
    order = ClientOrder.objects.filter(client=user)
    status_order = order.filter(status=False).exists()
        
    isum = ClientInvoice.objects.filter(client=user).aggregate(Sum('sum'))
#    bsum = Bicycle_Sale.objects.filter(client=user).aggregate(Sum('sum'))
    client = Client.objects.get(id = user)
#    client.summ = float(isum['sum__sum'] or 0) + float(bsum['sum__sum'] or 0) + client_workshop_sum 
    client.summ = float(isum['sum__sum'] or 0) + client_workshop_sum
    
    sale_cat = [1,3,5,7,10]
    if (client.summ > settings.CLIENT_SALE_1) and (client.summ < settings.CLIENT_SALE_3):
        if client.sale < sale_cat[0] :
            client.sale = sale_cat[0]
    if (client.summ > settings.CLIENT_SALE_3) and (client.summ < settings.CLIENT_SALE_5):
        if client.sale < sale_cat[1] :
            client.sale = sale_cat[1]
    if (client.summ > settings.CLIENT_SALE_5) and (client.summ < settings.CLIENT_SALE_7):
        if client.sale < sale_cat[2] :
            client.sale = sale_cat[2]
    if (client.summ > settings.CLIENT_SALE_7) and (client.summ < settings.CLIENT_SALE_10):
        if client.sale < sale_cat[3] :
            client.sale = sale_cat[3]
    if (client.summ > settings.CLIENT_SALE_10):
        if client.sale < sale_cat[4] :
            client.sale = sale_cat[4]
    if client.sale_on == False:
    #if (client.id == 138) or (client.id == 1277):
        client.sale = 0
        
    if (client.id == 1257):
        client.sale = 100
    client.save()
    if email == True :
        context = {'clients': res, 'invoice': client_invoice, 'email': email, 'client_invoice_sum': client_invoice_sum, 'workshop': client_workshop, 'client_workshop_sum': client_workshop_sum, 'debt_list': debt_list, 'credit_list': credit_list, 'client_name': client_name, 'b_bike': b_bike, 'workshopTicket': workshop_ticket, 'messages': messages, 'status_msg':status_msg, 'status_rent':status_rent, 'status_order':status_order, 'tdelta': tdelta}
        return render(request, 'client_result.html', context)
    context = {'weblink': 'client_result.html', 'clients': res, 'invoice': client_invoice, 'email': email, 'client_invoice_sum': client_invoice_sum, 'workshop': client_workshop, 'client_workshop_sum': client_workshop_sum, 'debt_list': debt_list, 'credit_list': credit_list, 'client_name': client_name, 'b_bike': b_bike, 'workshopTicket': workshop_ticket, 'messages': messages, 'status_msg':status_msg, 'status_rent':status_rent, 'status_order':status_order, 'tdelta': tdelta}  
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def client_lookup(request):
    data = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            if len(value) > 2:
                model_results = Client.objects.filter(Q(name__icontains = value) | Q(forumname__icontains = value) | Q(phone__icontains = value) | Q(phone1__icontains = value))
                data = serializers.serialize("json", model_results, fields=('name','id', 'sale', 'forumname', 'phone'))
            else:
                data = []
    return HttpResponse(data)                


def client_lookup_by_id(request):
    data = None
    if request.method == "GET":                
        if request.GET.has_key(u'client_id'):
            value = request.GET[u'client_id']
            model_results = Client.objects.values('id', 'name', 'forumname').get(pk = value)
            data = simplejson.dumps(model_results)
    return HttpResponse(data)    


# --------------- WorkShop -----------------
@csrf_exempt
def workgroup_add(request):
    if auth_group(request.user, 'admin')==False:
        #return HttpResponse('Error: У вас не має доступу до даної дії. Можливо ви не авторизувались.')
        context = {'weblink': 'error_message.html', 'mtext': 'У вас не має доступу до даної дії. Можливо ви не є адміністратором?.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
   
    if request.method == 'POST':
        form = WorkGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            tabindex = form.cleaned_data['tabindex']
            WorkGroup(name = name, description = description, tabindex = tabindex).save()
            return HttpResponseRedirect('/workgroup/view/')
    else:
        form = WorkGroupForm()
    return render(request, 'index.html', {'form': form, 'weblink': 'workgroup.html'})


@csrf_exempt
def workgroup_edit(request, id):
    a = WorkGroup.objects.get(pk=id)
    if auth_group(request.user, 'admin')==False:
        msg_txt = u'У вас не має можливості редагувати групу - [ %s ]' % (a.name)
        context = {'weblink': 'error_message.html', 'mtext':  msg_txt}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    
    if request.method == 'POST':
        form = WorkGroupForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workgroup/view/')
    else:
        form = WorkGroupForm(instance=a)
    return render(request, 'index.html', {'form': form, 'weblink': 'workgroup.html', 'next': current_url(request)})


def workgroup_list(request, id=None):
    list = WorkGroup.objects.all().order_by("tabindex")
    context = {'workgroups': list, 'weblink': 'workgroup_list.html', 'next': current_url(request)}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def workgroup_delete(request, id):
    obj = WorkGroup.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workgroup/view/')


def worktype_add(request):
    if auth_group(request.user, 'admin')==False:
        #return HttpResponse('Error: У вас не має доступу до даної дії. Можливо ви не авторизувались.')
        context = {'weblink': 'error_message.html', 'mtext': 'У вас не має можливості додавати роботу. Можливо ви не є адміністратором?.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    
    if request.method == 'POST':
        form = WorkTypeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            work_group = form.cleaned_data['work_group']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            WorkType(name=name, work_group=work_group, price=price, description=description).save()
            return HttpResponseRedirect('/worktype/view/')
    else:
        form = WorkTypeForm()
    return render(request, 'index.html', {'form': form, 'weblink': 'worktype.html', 'add_edit_text': 'Створити', 'workID': None})


def worktype_edit(request, id):
    if auth_group(request.user, 'admin')==False:
        #return HttpResponse('Error: У вас не має доступу до даної дії. Можливо ви не авторизувались.')
        context = {'weblink': 'error_message.html', 'mtext': 'У вас не має можливості змінювати роботу.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    
    a = WorkType.objects.get(pk=id)
    if request.method == 'POST':
        form = WorkTypeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            #return HttpResponseRedirect('/worktype/view/')
            return HttpResponseRedirect('/worktype/view/group/'+ str(a.work_group.id))
    else:
        form = WorkTypeForm(instance=a)
    context = {'form': form, 'weblink': 'worktype.html', 'add_edit_text': 'Редагувати', 'workID': a}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def worktype_list(request, id=None):
    list = None
    if id != None:
        list = WorkType.objects.filter(work_group=id)
    else:
        list = WorkType.objects.all()
    worklist = WorkType.objects.all().order_by('work_group')
    component_type_list = Type.objects.all().order_by('group')
    context = {'worktypes': list, 'worklist': worklist, 'component_type_list':component_type_list, 'weblink': 'worktype_list.html', }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

#===============================================================================
# 
# def worktype_list(request):
#    list = WorkType.objects.all()
#    return render_to_response('index.html', {'worktypes': list, 'weblink': 'worktype_list.html'})
#===============================================================================
@csrf_exempt
def worktype_join(request, id1=None, id2=None, ids=None):
    if auth_group(request.user, 'admin')==False:
        #return HttpResponseRedirect('/')
        return HttpResponse('Error: У вас не має прав для обєднання')
    d = {}
    if (id1 == id2) and (id1 != None):
        return HttpResponse('Не має сенсу обєднувати роботу саму з собою')
    
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id1'):
                id1 = request.POST['id1']
                if id1 == '':
                    d['status'] = False
                    d['msg'] = 'Основна робота не вибрана'
                    response = JsonResponse(d)
                    return response
            if POST.has_key('id2'):
                id2 = request.POST['id2']
                if id2 == '':
                    d['status'] = False
                    d['msg'] = 'Виберіть роботу зі списку для обєднання'
                    response = JsonResponse(d)
                    return response
            if POST.has_key('ids'):
                ids = request.POST['ids'].split(',')
                try:
                    ids.remove(id1)
                except:
                    result = "Введіть правильний ID товару для обєднання"
                    return HttpResponse(result, content_type="text/plain;charset=UTF-8;;")

                for i in ids:
                    workshop = WorkShop.objects.filter(work_type = i).update(work_type = id1)
                    obj_del = WorkShop.objects.get(id = i)
                #obj_del.delete()
            workshop = WorkShop.objects.filter(work_type = id2).update(work_type = id1)
            obj_del = WorkType.objects.get(id = id2)
                
            d['status'] = True
            d['msg'] = 'Дані про роботу оновлено'
            response = JsonResponse(d)
#            result = "ok"
            return response #HttpResponse(result, content_type="text/plain;charset=UTF-8;")
    
    w1 = WorkType.objects.get(id=id1)
    w2 = WorkType.objects.get(id=id2)
    workshop = WorkShop.objects.filter(work_type = id2).update(work_type = id1)
    
    return HttpResponseRedirect( '/worktype/view/group/' + str(w1.work_group.id) )


def worktype_delete(request, id):
    obj = WorkType.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workgroup/view/')

@csrf_exempt
def worktype_depence_add(request):
    if request.is_ajax():
        if request.method == 'POST': 
            if request.POST.has_key('id') and request.POST.has_key('depence_id[]'):
                d = {}
                id = request.POST['id']                
                dep_ids = request.POST.getlist('depence_id[]')
                obj = WorkType.objects.get(pk = id)
                dw = WorkType.objects.filter(pk__in = dep_ids)
                dw_list = list(dw)
#                print "Depence = " + str(dw[0].pk)
                #obj.dependence_work.add(dw[0])
                obj.dependence_work.add(*dw_list)
                obj.save() 
                d['status'] = True
                d['msg'] = 'Done'
                d['work_list'] = list(dw.values('id', 'name', 'price'))
                response = JsonResponse(d)
                return response
            else:
                d['status'] = False
                d['msg'] = 'Парамтри не передано або вони невірні'
                response = JsonResponse(d)
                return response
    else:
        return HttpResponse('Error: Щось пішло не так під час запиту')     


def worktype_depence_component_add(request):
    if request.is_ajax():
        if request.method == 'POST': 
            if request.POST.has_key('id') and request.POST.has_key('comp_ids[]'):
                d = {}
                id = request.POST['id']                
                dep_ids = request.POST.getlist('comp_ids[]')
                obj = WorkType.objects.get(pk = id)
                dw = Type.objects.filter(pk__in = dep_ids)
                dw_list = list(dw)
#                print "Depence = " + str(dw[0].pk)
                #obj.dependence_work.add(dw[0])
                obj.component_type.add(*dw_list)
                obj.save() 
                d['status'] = True
                d['msg'] = 'Done'
                d['comp_list'] = list(dw.values('id', 'name'))
                response = JsonResponse(d)
                return response
            else:
                d['status'] = False
                d['msg'] = 'Парамтри не передано або вони невірні'
                response = JsonResponse(d)
                return response
                       
    else:
        return HttpResponse('Error: Щось пішло не так під час запиту')     
    
@csrf_exempt
def worktype_depence_delete(request):
    d = {}
    if (auth_group(request.user, 'seller')==False) or (auth_group(request.user, 'admin')==False):
        d['status'] = False 
        d['msg'] = 'Ви не має достаттньо повноважень для даної функції'
        response = JsonResponse(d)
        return response                
    if request.is_ajax():
        if request.method == 'POST': 
            if request.POST.has_key('id') and request.POST.has_key('del_work_id'):
                id = request.POST['id']                
                dep_work_id = request.POST['del_work_id']
                obj = WorkType.objects.get(pk = id)
                dw = WorkType.objects.get(pk = dep_work_id)
                obj.dependence_work.remove(dw)
                obj.save() 
                d['status'] = True
                d['msg'] = 'Done'
                response = JsonResponse(d)
                return response
            else:
                d['status'] = False
                d['msg'] = 'Парамтри не передано або вони невірні'
                response = JsonResponse(d)
                return response
    else:
        return HttpResponse('Error: Щось пішло не так під час запиту')     


def worktype_depence_component_delete(request):
    d = {}
    if request.is_ajax():
        if (auth_group(request.user, 'seller')==False): # or (auth_group(request.user, 'admin')==False):
            d['status'] = False
            d['msg'] = 'Ви не має достаттньо повноважень для даної функції'
            response = JsonResponse(d)
            return response                
        
        if request.method == 'POST': 
            if request.POST.has_key('id') and request.POST.has_key('del_component_id'):
                id = request.POST['id']                
                dep_comp_id = request.POST['del_component_id']
                obj = WorkType.objects.get(pk = id)
                dc = Type.objects.get(pk = dep_comp_id)
                obj.component_type.remove(dc)
                obj.save() 
                d['status'] = True
                d['msg'] = 'Done'
                response = JsonResponse(d)
                return response
            else:
                d['status'] = False
                d['msg'] = 'Парамтри не передано або вони невірні'
                response = JsonResponse(d)
                return response
    else:
        return HttpResponse('Error: Щось пішло не так під час запиту')     
    
@csrf_exempt
def workstatus_add(request):
    text = 'Створити новий статус роботи'
    if request.method == 'POST':
        form = WorkStatusForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            WorkStatus(name=name, description=description).save()
            return HttpResponseRedirect('/workstatus/view/')
    else:
        form = WorkStatusForm()
    context = {'form': form, 'text': text, 'weblink': 'workstatus.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def workstatus_edit(request, id):
    text = 'Редагувати статус виконання роботи'
    a = WorkStatus.objects.get(pk=id)
    if request.method == 'POST':
        form = WorkStatusForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workstatus/view/')
    else:
        form = WorkStatusForm(instance=a)
    context = {'form': form, 'text': text, 'weblink': 'workstatus.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def workstatus_list(request):
    search = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                q = request.POST.get( 'id' )
        search = dict ((o.pk, o.name) for o in WorkStatus.objects.all())
        return HttpResponse(simplejson.dumps(search), content_type="application/json")
    else:
        message = "Error"
    list = WorkStatus.objects.all()
    plist = PhoneStatus.objects.all()
    context = {'workstatus': list.values_list(), 'phonestatuslist': plist, 'weblink': 'workstatus_list.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def workstatus_delete(request, id):
    obj = WorkStatus.objects.get(id=id)
    del_logging(obj)
    if (auth_group(request.user, 'admin') == True):
        obj.delete()
    return HttpResponseRedirect('/workstatus/view/')

@csrf_exempt
def phonestatus_list(request):
    search = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                q = request.POST.get( 'id' )
        search = dict ((o.pk, o.name) for o in PhoneStatus.objects.all())
        return HttpResponse(simplejson.dumps(search), content_type="application/json")
    else:
        message = "Error"
        return message

@csrf_exempt
def phonestatus_add(request):
    text = 'Додати статус дзвінка'
    if request.method == 'POST':
        form = PhoneStatusForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            PhoneStatus(name=name, description=description).save()
            return HttpResponseRedirect('/')
    else:
        form = PhoneStatusForm()
    context = {'form': form, 'text': text, 'weblink': 'workstatus.html'} 
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def phonestatus_edit(request, id):
    text = 'Редагувати статус дзвінка'
    a = PhoneStatus.objects.get(pk=id)
    if request.method == 'POST':
        form = PhoneStatusForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workstatus/view/')
    else:
        form = PhoneStatusForm(instance=a)
    context = {'form': form, 'text': text, 'weblink': 'workstatus.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def phonestatus_delete(request, id):
    obj = PhoneStatus.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workstatus/view/')

@csrf_exempt
def workticket_add(request, id=None):
    client = None
    if id!=None:
        client = Client.objects.get(id=id)
    
    if request.method == 'POST':
        if client!=None:
            form = WorkTicketForm(request.POST, initial={'client': client.id, 'status': 1})
        else:
            form = WorkTicketForm(request.POST, initial={'status': 1})
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            end_date = form.cleaned_data['end_date']
            status = form.cleaned_data['status']
#            phone_status = form.cleaned_data['phone_status']
            description = form.cleaned_data['description']
            shop = form.cleaned_data['shop']
            estimate_time = form.cleaned_data['estimate_time']
            bicycle = form.cleaned_data['bicycle']
            bike_part_type = form.cleaned_data['bike_part_type'] 
            user = request.user
            if shop == None:
                shop = get_shop_from_ip(request.META['REMOTE_ADDR'])
                
            try:        
#                print "\n>>>> TRY WORK!!!"
                WorkTicket(client=client, date=date, end_date=end_date, status=status, description=description, user=user, shop=shop, estimate_time = estimate_time, bicycle = bicycle, bike_part_type = bike_part_type).save()
            except Exception as e:
                mtext = "Ви не залогувались на порталі. Увійдіть та спробуйте знову. <br>" + str(e) 
                context = {'weblink': 'error_message.html', 'mtext': mtext}
                return render(request, 'index.html', context)
            return HttpResponseRedirect('/workticket/view/')
        else:
            pass
#            print "\n>>>> Form not valid!!!"
    else:
        if client != None:
            form = WorkTicketForm(initial={'client': client.id, 'status': 1})
        else:
            form = WorkTicketForm(initial={'date': datetime.datetime.today(), 'status': 1, 'end_date': datetime.datetime.now()+datetime.timedelta(3)})
    context = {'form': form, 'weblink': 'workticket.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

@csrf_exempt
def workticket_edit(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id_w'):
                id = request.POST.get('id_w')
                p = request.POST.get('value')
                obj = WorkTicket.objects.get(pk = id)
                obj.status = WorkStatus.objects.get(pk = p)
                obj.end_date = datetime.date.today()
                obj.user = request.user
                hist = (obj.history or "")
                obj.history = hist +  "[" + str(request.user) + "] - [" + str(obj.date) + "] - " +  obj.status.name + " - change Ticket Status\n" 
                obj.save() 
                c = WorkTicket.objects.filter(pk = id).values_list('status__name', flat=True)
                return HttpResponse(c)
            if POST.has_key('id_wp'):
                id = request.POST.get('id_wp')
                p = request.POST.get('value')
                obj = WorkTicket.objects.get(pk = id)
                obj.phone_status = PhoneStatus.objects.get(pk = p)
                obj.phone_date = datetime.datetime.today()
                obj.phone_user = request.user
                obj.history = obj.history +  "[" + str(request.user) + "] - [" + str(obj.date) + "] - " +  obj.phone_status.name + " - change Phone Status\n" 
                obj.save() 
                c = WorkTicket.objects.filter(pk = id).values_list('phone_status__name', flat=True)
                return HttpResponse(c)
            if POST.has_key('desc_w'):
                id = request.POST.get('desc_w')
                desc = request.POST.get('value')
                obj = WorkTicket.objects.get(pk = id)
                desc = desc.replace('<br>', '\n')
                desc = desc.lstrip()
                desc = desc.rstrip()
                obj.description = re.sub('<[^<]+?>', '', desc)
                obj.user = request.user
                try:
                    obj.history = obj.history + "[" + str(request.user) + "] - [" + str(obj.date) + "] - " +  obj.status.name + " - change Description\n"
                except TypeError:
                    obj.history = "[" + str(request.user) + "] - [" + str(obj.date) + "] - " +  obj.status.name + " - change Description\n"
                obj.save() 
                c = WorkTicket.objects.filter(pk = id).values_list('description', flat=True)
                return HttpResponse(c)
            else:
                return HttpResponse("dont work ajax")
    
    a = WorkTicket.objects.get(pk=id)
    if request.method == 'POST':
        form = WorkTicketForm(request.POST, instance=a)
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            end_date = form.cleaned_data['end_date']
            status = form.cleaned_data['status']
#            phone_status = form.cleaned_data['phone_status']
            description = form.cleaned_data['description']
#            user = form.cleaned_data['user']
            shop = form.cleaned_data['shop']
            estimate_time = form.cleaned_data['estimate_time']
            bicycle = form.cleaned_data['bicycle']
            bike_part_type = form.cleaned_data['bike_part_type'] 

            if request.user.is_authenticated():
                user = request.user
#            print "\nSHOP = " + str(shop)
            if shop == None:
                shop = get_shop_from_ip(request.META['REMOTE_ADDR'])   
            history_wt = a #WorkTicket.objects.get(pk = id)
            history = ""
            if form.has_changed():
#                print ("\n>>> The following fields changed: %s" % ", ".join(form.changed_data))
                for field_name in form.changed_data:
#                    print "Field [%s] = %s" % (field_name, form.fields[field_name])
                    history = history + "Field name[%s] = %s;\n" %  (field_name, request.POST.get(field_name)) #form.fields[field_name])
                user_date_str = "[%s](%s)\n" % (date, user)
                try:
                    history = history_wt.history + user_date_str + history + "\n"
                except TypeError:
                    history = user_date_str + history + "\n"
                
            
            WorkTicket(id = id, client=client, history=history, date=date, end_date=end_date, status=status, description=description, user=user, shop=shop, estimate_time=estimate_time, bicycle=bicycle, bike_part_type=bike_part_type).save()
            return HttpResponseRedirect('/workticket/view/')
    else:
        form = WorkTicketForm(instance=a)
    context = {'form': form, 'weblink': 'workticket.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def workticket_list(request, year=None, month=None, all=False, status=None, shop=None):
    cur_year = datetime.datetime.now().year
    wy = WorkTicket.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('pk')).order_by('year') #annotate(year_count=Count('date__year'))
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    if shop:
        shopN = Shop.objects.filter(id = shop)
        shop = int(shop)
    else:
        try:
            shop = int(shopN.id)
        except:
            context = {'weblink': 'error_message.html', 'mtext': 'Не правильний id/ip магазину ' + str(request.META['REMOTE_ADDR']), }
            context.update(custom_proc(request))
            return render(request, 'index.html', context)
    
    list = None
    WTiketlist = None
    WTiketlist = WorkTicket.objects.filter(shop = shop)
    if shop == 0:
        WTiketlist = WorkTicket.objects.all()
    
    if month != None:
        list = WTiketlist.filter(date__year=year, date__month=month)
    if (year == None) and (month == None):
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        list = WTiketlist.filter(date__year=year, date__month=month)
    if all == True:
        list = WTiketlist.filter(date__year=cur_year)
    if status == '0':
        list = WTiketlist #filter(status__id__in=[status,1]) # All
    if int(status or 0) > 0:
        list = WTiketlist.filter(status__id= status)

    shops = Shop.objects.all()
    ws_list = WorkStatus.objects.all()
    context = {'workticket':list.order_by('-date'), 'sel_year': int(year), 'sel_month':int(month), 'status': int(status or 0), 'year_ticket': wy, 'weblink': 'workticket_list.html', 'shops': shops, 'wstatus_list': ws_list, 'shop' : shop} 
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def workticket_delete(request, id):
    obj = WorkTicket.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workticket/view/')

@csrf_exempt
def workshop_add(request, id=None, id_client=None):
    if request.user.is_authenticated():
        user = request.user
    else:
        context = {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}
        context.update(custom_proc(request)) 
        return render(request, 'index.html', context)
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    now = datetime.datetime.now()
    work = None
    wclient = None
    if id != None:
        work = WorkType.objects.get(id=id)
    if id_client!=None:
        wclient = Client.objects.get(id=id_client)
    if request.method == 'POST':
        form = WorkShopForm(request.POST, client_id=wclient, request = request)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workshop/view/')
    else:
        if work != None:
            form = WorkShopForm(initial={'work_type': work.id, 'price': work.get_sale_price, 'user': request.user, 'shop': shopN}, client_id=wclient, request = request)
        elif wclient != None:
            form = WorkShopForm(initial={'client': wclient.id, 'user': request.user, 'shop': shopN, }, client_id=wclient, request = request)
        else:        
            form = WorkShopForm(initial={'user': request.user, 'shop': shopN,  }, request = request)
    nday = 7
    try:
        wc_name = wclient.name
        wc_id = wclient.id
    except:
        wc_name = None
        wc_id = None
    clients_list = WorkShop.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client')).order_by('client_id')
    context = {'form': form, 'weblink': 'workshop.html', 'clients_list':clients_list, 'client_name': wc_name, 'client_id': wc_id, 'work': work, 'next': current_url(request)}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def workshop_add_formset(request):
    now = datetime.datetime.now()
    formset = formset = WorkShopFormset(None)
    if request.method == 'POST':
        formset = WorkShopFormset(request.POST)
        if formset.is_valid():
            for form in formset:
                # extract name from each form and save
                name = form.cleaned_data.get('name')
                # save book instance
                if name:
                    WorkShop(client=client, date=date, work_type=work_type, price=price, description=description, user=user).save()
            # once all books are saved, redirect to book list view
            return HttpResponseRedirect('/workshop/view/')
#===============================================================================
# '''        
#         form = WorkShopForm(request.POST)
#         if form.is_valid():
#             client = form.cleaned_data['client']
#             date = form.cleaned_data['date']
#             work_type = form.cleaned_data['work_type']
#             price = form.cleaned_data['price']
#             description = form.cleaned_data['description']
#             #pay = form.cleaned_data['pay']
#             user = form.cleaned_data['user']            
#             if request.user.is_authenticated():
#                 user = request.user
#             else:
#                 return HttpResponse('Error: У вас не має прав для редагування, або ви не Авторизувались на сайті')
#             WorkShop(client=client, date=date, work_type=work_type, price=price, description=description, user=user).save()
#             return HttpResponseRedirect('/workshop/view/')
# '''        
#===============================================================================
    nday = 7
    heading_message = 'Formset Demo'
    clients_list = WorkShop.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))        
    return render_to_response('index.html', { 'formset': formset, 'weblink': 'workshop_formset.html', 'clients_list':clients_list, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

@csrf_exempt
def workshop_edit(request, id):
    if not request.user.is_authenticated():    
        context = {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'},
        context.update(custom_proc(request)) 
        return render(request, 'index.html', context)
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    now = datetime.datetime.now()
    a = WorkShop.objects.get(pk=id)
    work = a.work_type
    owner = a.user
    old_p = a.price
    if (request.user <> owner) and (auth_group(request.user, 'admin') == False):
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не є влаником даної роботи або не залогувались на порталі. Робота створена користувачем - <b>' + str(owner)+ '</b>'}, context_instance=RequestContext(request, processors=[custom_proc]))             
    
    if request.method == 'POST':
        print "<<< POST >>>"
        form = WorkShopForm(request.POST, instance=a, wticket_id=a.ticket, request = request, client_id=a.client)
        if form.is_valid():
            print "VALID form!"
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            work_type = form.cleaned_data['work_type']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            pay = a.pay #form.cleaned_data['pay']
            #user = request.user 
            user = form.cleaned_data['user']
            shop = form.cleaned_data['shop']
            time = form.cleaned_data['time']
            ticket = form.cleaned_data['ticket']
            #hour = form.cleaned_data['hour']
            #time = int(time) + int(hour) * 60
            if shop == None:
                shop = shopN
                            
            WorkShop(id=id, client=client, date=date, work_type=work_type, price=price, description=description, user=user, pay = pay, shop=shop, time = time, ticket = ticket).save()                 
            return HttpResponseRedirect('/workshop/view/')
    else:
        form = WorkShopForm(instance=a, request = request, wticket_id=a.ticket, client_id=a.client, )
    nday = 7
    clients_list = WorkShop.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client')).order_by('client__id')
    context = {'form': form, 'weblink': 'workshop.html', 'clients_list':clients_list, 'client_name': a.client, 'work': work}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def workshop_list(request, year=None, month=None, day=None, shop=None):
    now = datetime.datetime.now()
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    if shop:
        shopN = Shop.objects.filter(id = shop)
        shop = int(shop)
    else:
        try:
            shop = int(shopN.id)
        except:
            context = {'weblink': 'error_message.html', 'mtext': 'Не правильний id/ip магазину ' + str(request.META['REMOTE_ADDR']), }
            context.update(custom_proc(request))
            return render(request, 'index.html', context)
    
    if year == None:
        year = now.year
    if month == None:
        month = now.month
    
    if day == None:
        day = now.day
        list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day, shop=shop).order_by("-date")
    else:
        if day == 'all':
            list = WorkShop.objects.filter(date__year=year, date__month=month, shop=shop).order_by("-date")
            day = 0
        else:
            list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day, shop=shop).order_by("-date")
    sum = 0 
    for item in list:
        sum = sum + item.price
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    shops = Shop.objects.all()
    context = {'workshop': list, 'summ':sum, 'sel_year':int(year), 'sel_month':int(month), 'sel_day':int(day), 'month_days': days, 'weblink': 'workshop_list.html', 'shops': shops, 'shop': shop}
    context.update(custom_proc(request))     
    return render(request, 'index.html', context)

@csrf_exempt
def workshop_delete(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                wid = request.POST.get( 'id' )
    if wid:
        id = wid 
    obj = WorkShop.objects.get(id=id)
    if (auth_group(request.user, 'admin') == True) or ((request.user == obj.user) and (obj.pay == False)):
        del_logging(obj)
        obj.delete()
        return HttpResponse("Роботу видалено", content_type="text/plain;charset=UTF-8;")
    else:
        return HttpResponse("Роботу не можливо видалити, можливо це не ваша робота, або ви не залогувались на портал", status=401)

@csrf_exempt
def workshop_set(request):
    wid = None
    price = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('w_id') and POST.has_key('price'):
                wid = POST.get( 'w_id' )
                price = POST.get( 'price' )
                print "Work ID = %s | Price = %s"  % (wid, price)
    
    obj = WorkShop.objects.get(id = wid)
    if (auth_group(request.user, 'admin') == True) or ((request.user == obj.user) and (obj.pay == False)):
#        del_logging(obj)
        num = float(price) / obj.price 
        obj.price = price
#        if len(obj.description) > 0 : 
        if obj.description :
            obj.description = obj.description + "\nx" + str(num)
        else:
            obj.description = "x" + str(num)
        obj.save()
#        obj.delete()
        #return HttpResponse("Ціну на роботу змінено", content_type="text/plain;charset=UTF-8;")
        return HttpResponse(simplejson.dumps({'data': {'status': True, 'price': price}, 'obj': (obj.client.name, obj.price, obj.pay, obj.description)}), content_type="application/json")
    else:
        err_msg = "Роботу не можливо редагувати, можливо це не ваша робота, або ви не залогувались на портал"
        return HttpResponse(simplejson.dumps({'data': {'status': False, 'price': price, 'msg': err_msg}, 'obj': (obj.client.name, obj.price, obj.pay, obj.description)}), content_type="application/json")
        #return HttpResponse("Роботу не можливо редагувати, можливо це не ваша робота, або ви не залогувались на портал", status=401)


# lookup workshop price
def worktype_ajax(request):
    search = None
    message = ""
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('id'):
                q = request.GET.get( 'id' )
                message = "It's AJAX!!!"
    else:
        message = "Error"
    search = WorkType.objects.filter(id=q).values('price', 'description')
    comp_depence = Type.objects.filter(worktype__pk = q).values('name', 'pk', 'name_ukr')  
    return HttpResponse(simplejson.dumps({'data': list(search), 'dep': list(comp_depence)}), content_type="application/json")

@csrf_exempt
def worktype_lookup(request):
    data = []
    if request.method == "POST":
        if request.POST.has_key(u'query'):
            value = request.POST[u'query']
            if len(value) > 2:
                results = WorkType.objects.filter(name__icontains = value, disable = False)
                #data = serializers.serialize("json", results, fields=('name', 'id', 'price', 'dependence_work', 'get_sale_price', 'sale', 'work_group', 'description', 'plus'))
                data = [i.to_json() for i in results]
                
            else:
                data = []
    return HttpResponse(json.dumps(data), content_type="application/json")        
#    return HttpResponse(data, content_type="application/json")    


def workshop_pricelist(request, pprint=False):
    list = WorkType.objects.all().values('name', 'price', 'sale', 'id', 'description', 'work_group', 'work_group__name', 'plus').order_by('work_group__tabindex')
    if pprint:
        context = {'work_list': list, 'pprint': True} 
        context.update(custom_proc(request))
        return render(request, 'workshop_pricelist.html', context)
    else:        
        context = {'work_list': list, 'weblink': 'workshop_pricelist.html', 'pprint': False}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)    

#------------- Shop operation --------------
@csrf_exempt
def shopdailysales_add(request, id=None):
    if auth_group(request.user, 'seller')==False:
        context = {'weblink': 'error_message.html', 'mtext': 'Помилка: У вас не має доступу до <<Денна каса за місяць>>. Можливо ви не авторизувались.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)            
    lastCasa = None
    now = datetime.datetime.now()
    shopN = None
    #shopN = get_shop_from_ip('192.168.1.55')
    if id != None :
        shopN = Shop.objects.get(id = id)
    else: 
        shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
        #shopN = get_shop_from_ip('192.168.1.7')
    sum_casa = shopN.shop_cash_sum_by_day()
    if request.method == 'POST':
        form = ShopDailySalesForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            cash = form.cleaned_data['cash']
            tcash = form.cleaned_data['tcash']
            ocash = form.cleaned_data['ocash']
            shop = form.cleaned_data['shop']
            if form.cleaned_data['user']:
                user = form.cleaned_data['user']
            else:
                user = request.user
            date = now
            if request.user.is_authenticated():
                user = request.user
            ShopDailySales(date=date, price=price, description=description, user = user, cash=cash, tcash=tcash, ocash=ocash, shop = shop).save()
            return HttpResponseRedirect('/shop/sale/view/')
    else:        
        unknown_client = Client.objects.get(id = settings.CLIENT_UNKNOWN)
#        print "USER - " + str(unknown_client.pk)
             
        deb = ClientDebts.objects.filter(date__year=now.year, date__month=now.month, date__day=now.day).order_by()
        cred = ClientCredits.objects.filter(date__year=now.year, date__month=now.month, date__day=now.day).order_by()
#        cash_credsum = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price"))
        #=======================================================================
        # try:
        #     cashCred = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price")).get(cash_type=1)['suma']
        # except ClientCredits.DoesNotExist:
        #     cashCred = 0
        # try:
        #     TcashCred = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price")).get(cash_type=9)['suma'] # PUMB
        # except ClientCredits.DoesNotExist:
        #     TcashCred = 0
        # try:
        #     cashDeb = deb.values('cash').annotate(suma=Sum("price")).get(cash='True')['suma']
        # except ClientDebts.DoesNotExist:
        #     cashDeb = 0
        #=======================================================================
        
        cashCred = sum_casa['cashCred'] 
        TcashCred = sum_casa['termCred']
        cashDeb = sum_casa['cashDeb']
        
        cashCred_sum = 0
        cashDeb_sum = 0
        try:
            cashCred_sum = cred.values('client').annotate(suma=Sum("price")).get(client = settings.CLIENT_UNKNOWN)['suma']
        except ClientCredits.DoesNotExist:
            cashCred_sum = 0
        try:
            cashDeb_sum = deb.values('client').annotate(suma=Sum("price")).get(client = settings.CLIENT_UNKNOWN)['suma'] #.filter(client = unknown_client).annotate(suma=Sum("price"))
        except ClientDebts.DoesNotExist:
            cashDeb_sum = 0

        unk_cash = cashCred_sum - cashDeb_sum

        ci_status = 0
        other_ci = 0
        try:
            ci_array = ClientInvoice.objects.filter(date__year=now.year, date__month=now.month, date__day=now.day)
            #ci_res = ClientInvoice.objects.filter(client = unknown_client, date__year=now.year, date__month=now.month, date__day=now.day)
            ci_res = ci_array.filter(client = unknown_client)
            for ci in ci_res: 
                if ci.check_payment() == False:
#                    print "FILTER ok!!!"
                    ci_status = ci_status + 1
            other_ci = ci_array.exclude(sum = F('pay'))
        except ClientInvoice.DoesNotExist:
            ci_status = 0

#        lastCasa = ShopDailySales.objects.latest('date')
        lastCasa = ShopDailySales.objects.filter(shop = shopN).latest('date')
        casa = cashCred - cashDeb
        form = ShopDailySalesForm(initial={'cash': casa, 'ocash': cashDeb, 'tcash':TcashCred, 'user': request.user, 'shop': shopN})
        
    syear = now.year
    smonth = now.month
    sday = now.day
    context = {'form': form, 'weblink': 'shop_daily_sales.html', 'lastcasa': lastCasa, 'ci_status': ci_status, 'other_ci':other_ci, 'unk_cash': unk_cash, 's_year': syear, 's_month': smonth, 's_day': sday, 'shopname': shopN }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def shopmonthlysales_view(request, year=None, month=None):
    if (month == None) or (year == None):
        now = datetime.datetime.now()
        year = now.year
        month = now.month
    if auth_group(request.user, 'admin') == False:
        return HttpResponseRedirect("/.")
    deb = ClientDebts.objects.filter(date__year=year, date__month=month ).extra(select={'year': "EXTRACT(year FROM date)", 'month': "EXTRACT(month from date)", 'day': "EXTRACT(day from date)"}).values('year', 'month', 'day').annotate(suma=Sum("price")).order_by()
#    cred = ClientCredits.objects.filter(Q(date__year=year), Q(date__month=month), Q(cash_type__name='Готівка') | Q(cash_type__name='Термінал ПУМБ') | Q(cash_type__name='Термінал pb.ua') | Q(cash_type=None) | Q(cash_type='Готівка Міцкевича')).extra(select={'year': "EXTRACT(year FROM date)", 'month': "EXTRACT(month from date)", 'day': "EXTRACT(day from date)"}).values('year', 'month', 'day').annotate(suma=Sum("price")).order_by()
    cred = ClientCredits.objects.filter(Q(date__year=year), Q(date__month=month), Q(cash_type__name='Готівка') | Q(cash_type__name='Термінал ПУМБ') | Q(cash_type__name='Термінал pb.ua') | Q(cash_type__name='Готівка Міцкевича') | Q(cash_type=None)).extra(select={'year': "EXTRACT(year FROM date)", 'month': "EXTRACT(month from date)", 'day': "EXTRACT(day from date)"}).values('year', 'month', 'day').annotate(suma=Sum("price")).order_by()
    year_list = ClientCredits.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('pk')).order_by('year')    
    sum_cred = 0
    sum_deb = 0
    
    for element in cred:
        element['cred']=0
        sum_cred = sum_cred + element['suma']
        for deb_element in deb:
            if (deb_element['year']==element['year']) and (deb_element['month']==element['month']) and (deb_element['day']==element['day']):
                element['deb']=deb_element['suma']
                sum_deb = sum_deb + deb_element['suma']
                #element['balance']=element['sum_catalog'] - element['c_sale']
    date_month = pytils_ua.dt.ru_strftime(u"%B %Y", datetime.datetime(int(year), int(month), 1), inflected=False)
    context = {'sum_cred': sum_cred, 'sum_deb': sum_deb, 'Cdeb': deb, 'Ccred':cred, 'date_month': date_month, 'sel_year': int(year), 'year_list':year_list, 'sel_month':int(month), 'l_month': xrange(1,13), 'weblink': 'shop_monthly_sales_view.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def shopdailysales_view(request, year, month, day, shop=0):
#    shopN = get_shop_from_ip('192.168.1.55')
#    shopN = get_shop_from_ip('10.0.0.1')
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    payments = shopN.get_deb_cred_in_date(year, month, day)
    cred = None
    cred = payments['cred']
    deb = payments['deb']   
    if auth_group(request.user, "admin") == True:
        cred = ClientCredits.objects.filter(date__year=year, date__month=month, date__day=day).order_by()
        deb = ClientDebts.objects.filter(date__year=year, date__month=month, date__day=day).order_by()
#    deb = ClientDebts.objects.filter(date__year=year, date__month=month, date__day=day).order_by()
    try:
        cash_credsum = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price")).order_by('cash_type')
        cashCred = cash_credsum.filter(cash_type__in = shopN.get_cashtype()).aggregate(suma=Sum("price"))# get(cash_type__pk = CASH)['suma']
    except ClientCredits.DoesNotExist:
        cashCred = 0
    try:
        cash_debsum = deb.values('cash').annotate(suma=Sum("price")).order_by('cash')
        cashDeb = cash_debsum.get(cash='True')['suma']        
    except ClientDebts.DoesNotExist:
        cashDeb = 0
#    casa = (cashCred.get('suma') or 0) - cashDeb
#    if custom_proc(request)['shop_name'] == 'shop2':
    casa = cashCred['suma']
    deb_sum = 0
    cred_sum = 0
    for c in cred:
        cred_sum = cred_sum + c.price
    for d in deb:    
        deb_sum = deb_sum + d.price
    sel_date = datetime.date(int(year), int(month), int(day))
    strdate = pytils_ua.dt.ru_strftime(u"%d %B %Y", sel_date, inflected=True)
    context = {'Cdeb': deb, 'Ccred':cred, 'date': strdate, 'sel_date': sel_date, 'd_sum': deb_sum, 'c_sum': cred_sum, 'cash_credsum': cash_credsum, 'cash_debsum':cash_debsum, 'casa':casa, 'shopName': shopN, 'weblink': 'shop_daily_sales_view.html'}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def shopdailysales_edit(request, id):
    if auth_group(request.user, "admin") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу для редагування. Зверніться до адміністратора.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)

    now = datetime.datetime.now()
    a = ShopDailySales.objects.get(pk=id)
    syear = a.date.year
    smonth = a.date.month
    sday = a.date.day   
    if request.method == 'POST':
        form = ShopDailySalesForm(request.POST, instance=a)
        if form.is_valid():
            date = form.cleaned_data['date']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            cash = form.cleaned_data['cash']
            tcash = form.cleaned_data['tcash']
            ocash = form.cleaned_data['ocash']
            ocash = form.cleaned_data['ocash']
            shop = form.cleaned_data['shop']
            #group = Group.objects.get(name='admin') 
#            if group not in request.user.groups.all():
#                date = now
            if request.user.is_authenticated():
                user = request.user

            ShopDailySales(pk=a.pk, date=a.date, price=price, description=description, user = user, cash=cash, tcash=tcash, ocash=ocash, shop = shop).save()
            return HttpResponseRedirect('/shop/sale/view/')
    else:
        form = ShopDailySalesForm(instance=a)
#    syear = now.year
#    smonth = now.month
#    sday = now.day   
    context = {'form': form, 'weblink': 'shop_daily_sales.html', 's_year': syear, 's_month': smonth, 's_day': sday,}
    context.update(custom_proc(request))     
    return render(request, 'index.html', context)


from django.utils import timezone
def shopdailysales_list(request, month=None, year=None, shop_id=None):    
    if auth_group(request.user, 'seller')==False:
        #return HttpResponse('Error: У вас не має доступу до даної дії. Можливо ви не авторизувались.')
        context = {'weblink': 'error_message.html', 'mtext': 'У вас не має доступу до даної дії. Можливо ви не авторизувались.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    shopN = None
    shoplist = None
    if shop_id == None:
        #shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
        shopN = get_shop_from_request(request)
        try:
            return render(shopN[0], shopN[1], shopN[2]) 
        except: #Shop.DoesNotExist:
            pass
    else:
        shopN = Shop.objects.get(pk = shop_id )
    
    if auth_group(request.user, 'admin')==True:
        shoplist = Shop.objects.all()
        
#    now = datetime.datetime.now()
    now = timezone.now()
    if month == None:
        month = now.month
    if year == None:
        year = now.year
    list = ShopDailySales.objects.filter(date__year=year, date__month=month, shop=shopN)
    total_sum = list.aggregate(total_cash=Sum('cash'), total_tcash=Sum('tcash'), total_price=Sum('price'), total_ocash=Sum('ocash'))
    context = {'shopsales': list, 'total_sum': total_sum, 'l_month': xrange(1,13), 'sel_month':int(month), 'weblink': 'shop_sales_list.html', 'shopName': shopN, 'shopID': shop_id, 'ShopList' : shoplist}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def shopdailysales_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має доступу до даної дії. Можливо ви не авторизувались.')
    obj = ShopDailySales.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/shop/sale/view/')



#Стара функція
def shop_price_old(request, mid, limit=0, pprint=False):
#    list = InvoiceComponentList.objects.filter(catalog__manufacturer__exact=id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale', 'catalog__country__name').annotate(sum_catalog=Sum('count'))
    #list = InvoiceComponentList.objects.filter(manufacturer = id)
    company = Manufacturer.objects.get(id=mid)
    company_list = Manufacturer.objects.all()
    url = '/shop/price/company/'+mid+'/print/'
    
    list = None
    id_list=[]
    psum = 0
    zsum = 0
    scount = 0
    zcount = 0
    
    if limit == 0:
        list = InvoiceComponentList.objects.filter(catalog__manufacturer__exact=mid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale').annotate(sum_catalog=Sum('count'))
    else:
        list = InvoiceComponentList.objects.filter(catalog__manufacturer__exact=mid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale').annotate(sum_catalog=Sum('count'))[:limit]

    for item in list:
        id_list.append(item['catalog'])
        item['balance']=item['sum_catalog']
        item['c_sale']=0
    new_list = []
    sale_list = ClientInvoice.objects.filter(catalog__in=id_list).values('catalog', 'catalog__price').annotate(sum_catalog=Sum('count'))        
    for element in list:
        #element['c_sale']=0
        
        for sale in sale_list:
            if element['catalog']==sale['catalog']:
                element['c_sale']=sale['sum_catalog']
                element['balance']=element['sum_catalog'] - element['c_sale']
            #else:
            #    element['balance']=element['sum_catalog'] 
        if element['balance']!=0:
            new_list.append(element)
       
#        return render_to_response('index.html', {'componentlist': list, 'salelist': list_sale, 'allpricesum':psum, 'zsum':zsum, 'zcount':zcount, 'countsum': scount, 'weblink': 'invoicecomponent_list_test.html'})
#    return render_to_response('index.html', {'company_list': company_list, 'company_name': company_name, 'componentlist': list, 'allpricesum':psum, 'zsum':zsum, 'zcount':zcount, 'countsum': scount, 'weblink': 'invoicecomponent_list_test.html'})
    if pprint:
        return render_to_response('price_list.html', {'catalog': new_list, 'company': company, 'company_list': company_list,})
    
    return render_to_response('index.html', {'catalog': new_list, 'company': company, 'company_list': company_list, 'weblink': 'price_list.html', 'view': True, 'link': url, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))



def shop_price(request, mid, limit=0, pprint=False):
#    list = InvoiceComponentList.objects.filter(catalog__manufacturer__exact=id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale', 'catalog__country__name').annotate(sum_catalog=Sum('count'))
    #list = InvoiceComponentList.objects.filter(manufacturer = id)
    list = Catalog.objects.filter(manufacturer = mid, count__gt=0).order_by("type")    
    company = Manufacturer.objects.get(id=mid)
    company_list = Manufacturer.objects.all()
    url = '/shop/price/company/'+mid+'/print/'
    
    if pprint:
        return render_to_response('price_list.html', {'catalog': list, 'company': company, 'company_list': company_list, 'request':request,})
    
    return render_to_response('index.html', {'catalog': list, 'company': company, 'company_list': company_list, 'weblink': 'price_list.html', 'view': True, 'link': url, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def shop_price_lastadd(request, id, pprint = False):
    url = '/shop/price/lastadded/'+id+'/print/'
    #list = InvoiceComponentList.objects.all().order_by("-id")[:id]
    list = Catalog.objects.filter(count__gt=0).order_by("-id")[:id]
    if pprint:
        return render_to_response('price_list.html', {'catalog': list, 'request':request,})
    return render_to_response('index.html', {'catalog': list, 'weblink': 'price_list.html', 'view': True, 'link': url, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def shop_price_bysearch_id(request, id):
    url = '/shop/price/bysearch_id/'+id+'/print/'
    list = Catalog.objects.filter(ids__icontains=id).order_by("-id")
    return render_to_response('index.html', {'catalog': list, 'weblink': 'price_list.html', 'view': True, 'link': url, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    

    
def shop_price_bysearch_id_print(request, id):
    list = Catalog.objects.filter(ids__icontains=id).order_by("-id")
    context = {'catalog': list, 'view': False, 'next': current_url(request)}
    context.update(custom_proc(request))
    return render(request, 'price_list.html', context)    


def shop_price_bysearch_name(request, id, pprint = False):
    url = '/shop/price/bysearch_name/'+id+'/print/'
    list = Catalog.objects.filter(name__icontains=id, count__gt=0).order_by("manufacturer","-id")
    if pprint:
        return render_to_response('price_list.html', {'catalog': list})
    return render_to_response('index.html', {'catalog': list, 'weblink': 'price_list.html', 'view': True, 'link': url, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    

@csrf_exempt
def shop_price_print_add(request, id=None):
    if request.is_ajax():
        if auth_group(request.user, 'seller')==False:
            return HttpResponse('Error: У вас не має прав для редагування')
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                q = request.POST.get( 'id' )
                s = 1 
                if POST.has_key('scount'):
                    s = request.POST.get( 'scount' )
                ids = q.split(',')
                if len(ids) > 1:
                    for i in ids:
                        cat = Catalog.objects.get(id = i)
                        if (cat.get_realshop_count() >= s) and (s > 1):
                            return  HttpResponse("Помилка.\nКількість цінників більша за кількість наявного товару.", content_type="text/plain;charset=UTF-8;")
                        sp = ShopPrice()
                        sp.catalog = cat
                        sp.scount = s
                        sp.dcount = 0
                        sp.user = request.user
                        sp.save()
                else:
                    cat = Catalog.objects.get(id=ids[0])
                    if (cat.get_realshop_count() >= s) and (s > 1):
                        return  HttpResponse("Помилка.\nКількість цінників більша за кількість наявного товару.", content_type="text/plain;charset=UTF-8;")
                    sp = ShopPrice()
                    sp.catalog = cat
                    sp.scount = s
                    sp.dcount = 0
                    sp.user = request.user
                    sp.save()
                return HttpResponse("Виконано.\nДодано цінник \n" + str(sp.catalog) + "\nЦіна - " + str(sp.catalog.price) + " грн.", content_type="text/plain;charset=UTF-8;")
    if request.method == 'POST':
        cat = Catalog.objects.get(id=id)
        sp = ShopPrice()
        sp.catalog = cat
        sp.scount = 1
        sp.dcount = 1
        sp.user = request.user
        sp.save()
    return HttpResponseRedirect('/shop/price/print/view/')

@csrf_exempt
def shop_price_print_add_invoice(request):
    if auth_group(request.user, 'seller')==False:
        return HttpResponse(simplejson.dumps({'msg': 'Error: У вас не має прав для редагування'}), content_type="application/json")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):        
                id = request.POST.get('id')
                di_obj = DealerInvoice.objects.get(pk = id)
                cat_list = di_obj.invoicecomponentlist_set.all()
#                print "Invoice list:"
                for obj in cat_list:
#                    print "Cat = " + str(obj.catalog)
                    sp = ShopPrice()
                    sp.catalog = obj.catalog
                    sp.scount = 1 # count of price
                    sp.dcount = 0
                    sp.user = request.user
                    sp.save()
                    
                status_msg = u"Цінники з накладної #" + str(di_obj.origin_id) + u" додані"
                #return HttpResponse('Ваш запит виконано', content_type="text/plain;charset=UTF-8;charset=UTF-8")
                return HttpResponse(simplejson.dumps({'status': di_obj.received, 'msg': status_msg}), content_type="application/json")
    else:
        return HttpResponse(simplejson.dumps({'msg':'Ваш запит відхилено. Щось пішло не так'}), content_type="application/json", status=401)


def remove_duplicated_ShopPrice_records(request):
    duplicates = ShopPrice.objects.values('catalog').annotate(catalog_count=Count('catalog'), cat_max_id = Max('pk')).filter(catalog_count__gt=1)
    for item in duplicates:
#        print "[" + str(item) + "] catalog - " + str(item['catalog']) 
        delitem = ShopPrice.objects.filter(catalog = item['catalog']).exclude(pk = item['cat_max_id'])
        delitem.delete()
    #list = ShopPrice.objects.all().order_by("-catalog__sale", "catalog", "user", "date", "catalog__manufacturer")
    #return render_to_response('index.html', {'weblink': 'mtable_pricelist.html', 'price_list': list}, context_instance=RequestContext(request, processors=[custom_proc]))
    return HttpResponseRedirect('/shop/price/print/list/')


def remove_zero_ShopPrice_records(request):
    list = ShopPrice.objects.all().order_by("user")
    for item in list:
        if item.catalog.get_realshop_count() == 0:
#            print 'REAL count = ' + str(item.catalog.get_realshop_count()) + " || Catalog - " + str(item.catalog)
            item.delete()
    #return shop_price_print_list(request)
    return HttpResponseRedirect('/shop/price/print/list/')


def shop_price_qrcode_print_view(request):
    list = ShopPrice.objects.all().order_by("user")
    return render_to_response('manual_qrcode_price_list.html', {'price_list': list, 'view': True}, context_instance=RequestContext(request, processors=[custom_proc]))    


def shop_price_print_list_add(request):
    if request.user.is_authenticated():
        user = request.user
    else:
        context = {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    by_user = False
    plist = None
    context = {'weblink': 'scan_many_barcode.html', 'price_list': plist, 'by_user' : by_user}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def shop_price_print_list(request, user_id = None, pprint=False):
    if request.user.is_authenticated():
        user = request.user
    else:
        context = {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}
        context.update(custom_proc(request)) 
        return render(request, 'index.html', context)
    list = None
    by_user = False
    if user_id :
        by_user = True
        list = ShopPrice.objects.filter(user = user_id).order_by("-catalog__sale", "catalog", "date", "catalog__manufacturer")
    else:    
        list = ShopPrice.objects.all().order_by("-catalog__sale", "catalog", "user", "date", "catalog__manufacturer")
    
    plist = None
    paginator = Paginator(list, 330)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        plist = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        plist = paginator.page(paginator.num_pages)
    if pprint:
        context = {'price_list': plist, 'view': True}
        return render(request, 'manual_price_list.html', context)
    context = {'weblink': 'mtable_pricelist.html', 'price_list': plist, 'by_user' : by_user}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)    
    
@csrf_exempt
def shop_price_print_delete_all(request, user_id = None):
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має прав для редагування')
    
    list = None
    if user_id:
        list = ShopPrice.objects.filter(user = user_id).delete()
    else:
        list = ShopPrice.objects.all().delete()
#    return render_to_response('index.html', {'weblink': 'manual_price_list.html', 'price_list': list}, context_instance=RequestContext(request, processors=[custom_proc]))
    return HttpResponseRedirect('/shop/price/print/list/')        

@csrf_exempt
def shop_price_print_delete(request, id=None, user_id = None):
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має прав для редагування')
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                q = request.POST.get( 'id' )
                obj = ShopPrice.objects.get(id=q)
                del_logging(obj)
                obj.delete()
                return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")
    else:
        try:
            obj = ShopPrice.objects.get(id=id)
            del_logging(obj)
            obj.delete()
        except:
            pass
        if user_id:
            try:
                list = ShopPrice.objects.filter(user = user_id).delete()
            except:
                pass
    return HttpResponseRedirect('/shop/price/print/list/')


def price_import_form(request):
    form = ImportPriceForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'import_price.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    


def price_import(request):
    pricereader = None
    ids_list = []
    now = datetime.datetime.now()
    rec_price = False
#    if 'name' in request.GET and request.GET['name']:
#        name = request.GET['name']
    if request.POST and request.FILES:
#    if request.FILES:
        csvfile = request.FILES['csv_file']
        dialect = csv.Sniffer().sniff(codecs.EncodedFile(csvfile, "utf-8").read(1024))
        csvfile.open()
        pricereader = csv.reader(codecs.EncodedFile(csvfile, "utf-8"), delimiter=';', dialect=dialect)
        rec_price = request.POST.get('recomended')
#===============================================================================
#    name = 'import'
#    path = settings.MEDIA_ROOT + 'csv/' + name + '.csv'
#    csvfile = open(path, 'rb')
#    pricereader = csv.reader(csvfile, delimiter=';', quotechar='|')
#===============================================================================
    w_file = open(settings.MEDIA_ROOT + 'csv/miss.csv', 'wb')
    spamwriter = csv.writer(w_file, delimiter=';', quotechar='|') #, quoting=csv.QUOTE_MINIMAL)
    for row in pricereader:
        id = None
        code = None
        cat = None
        #print row[0] + " - " + row[2]
        id = row[0]
        code = row[1]
                
        try:
            price = row[3]    

            if (code <> '0') and (id <> '0'):
#                print('CODE = ' + code + ' - ID ='+id)
                cat = Catalog.objects.filter(Q(ids = id) | Q(dealer_code = id) | Q(ids = code) | Q(dealer_code = code)).first()
                print ('ID + CODE = '+cat.ids)
                
            
            if (id <> '0'):
                try:
                    cat = Catalog.objects.get(Q(ids = id) | Q(dealer_code = id))
                    ids_list.append(cat.ids)
                except:
                    print ('ID = '+cat.ids)
                #    cat = Catalog.objects.get(dealer_code = id)
                #print('Catalog =  [' +id+ ']['+code+']# '+cat.ids+'|'+price)
                # заміна старого коду на новий
                #cat.dealer_code = id
                #cat.ids = code
                #cat.save()
                
            if (code <> '0'):
                print(' CODE  ['+code+']# '+row[3]+'')
                try:
                    cat = Catalog.objects.get(Q(ids = code) | Q(dealer_code = code))
                    ids_list.append(cat.ids)
                except:
                    #cat = Catalog.objects.get(ids = code)
                    print('CODE = ' + cat.ids)
#            if code != u'0':
                #cat.dealer_code = code
            if (price <> '0') and (rec_price == 'on'): 
                #print('Catalog =  [' +id+ ']['+code+']# '+cat.ids+'|'+price)
                cat.last_price = cat.price
                cat.price = row[3]
            #cat.dealer_code = row[1]
                cat.currency = Currency.objects.get(id = row[4])
                cat.last_update = datetime.datetime.now()
            #cat.user_update = request.user
                cat.user_update = User.objects.get(username='import')
 #           cat.description = row[5]
                cat.save()
            
            #spamwriter.writerow([row[0], row[1], row[2], row[3], row[4]],)
        except: # Catalog.DoesNotExist:
                      
            spamwriter.writerow([row[0], row[1], row[2], row[3], row[4]])
        #return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")
    list = Catalog.objects.select_related('manufacturer', 'type', 'currency', 'country').filter(Q(ids__in = ids_list))
    return render_to_response('index.html', {'catalog': list, 'post':rec_price,  'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    

#--------------------- MY Costs -------------------------
def costtype_add(request):
    if request.method == 'POST':
        form = CostTypeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            CostType(name=name, description=description).save()
            return HttpResponseRedirect('/cost/type/view/')
    else:
        form = CostTypeForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'costtype.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def costtype_list(request):
    list = CostType.objects.all()
    return render(request, 'index.html', {'costtypes': list, 'weblink': 'costtype_list.html', 'next': current_url(request)})


def costtype_delete(request, id):
    obj = CostType.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/cost/type/view/')

@csrf_exempt
def cost_add(request, id = None):
    cost = None
    if id != None: 
        cost = CostType(id=id)
        
    if request.method == 'POST':
        form = CostsForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            cost_type = form.cleaned_data['cost_type']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            Costs(date=date, cost_type=cost_type, price=price, description=description).save()
            return HttpResponseRedirect('/cost/view/')
    else:
        if cost != None:
            form = CostsForm(initial={'cost_type': cost.id})
        else:        
            form = CostsForm()
    context = {'form': form, 'weblink': 'cost.html',}
    context.update(custom_proc(request))             
    return render(request, 'index.html', context)


def cost_edit(request, id):
    a = Costs.objects.get(pk=id)
    if request.method == 'POST':
        form = CostsForm(request.POST, instance=a)
        if form.is_valid():
            date = form.cleaned_data['date']
            cost_type = form.cleaned_data['cost_type']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            Costs(id=id, date=date, cost_type=cost_type, price=price, description=description).save()            

#            form.save()
            return HttpResponseRedirect('/cost/view/')
    else:
        form = CostsForm(instance=a)
    context = {'form': form, 'weblink': 'cost.html', }
    context.update(custom_proc(request))         
    return render(request, 'index.html', context)


def cost_list(request, year=None, month=None):
    if auth_group(request.user, "admin") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу до даної функції', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    list = None
    if year != None and month == None:
        list = Costs.objects.filter(date__year=year)
    elif (year != None) and (month != None):
        list = Costs.objects.filter(date__year=year, date__month=month)
    elif year == None and month == None:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        list = Costs.objects.filter(date__year=year, date__month=month)
    else:
        list = Costs.objects.all().order_by("-date")
    #list = Costs.objects.filter(date__year=year, date__month=month)
    sum_price = list.aggregate(allsum = Sum('price'))
    year_list = Costs.objects.all().extra({'yyear':"Extract(year from date)"}).values('yyear').annotate(year_count = Count('pk')).order_by('yyear')
        
    paginator = Paginator(list, 25)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        pcost = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pcost = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pcost = paginator.page(paginator.num_pages)
#    if year == None:
#        year = datetime.datetime.now().year
#    if month == None:
#        month = datetime.datetime.now().month
#    if day == None:
#        day = datetime.datetime.now().day        
    sel_month = int(month or 0)
    sel_year = int(year or 0)
#    for i in year_list:
#        print "SEL = [%s][]" % sel_year
#        print "STR year - " + str(type(i['yyear'])) 
    context = {'weblink': 'cost_list.html', 'costs': pcost, 'summ': sum_price['allsum'], 'y_list' : year_list, 'sel_month': sel_month, 'sel_year': sel_year}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


def cost_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/cost/view/')
    obj = Costs.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/cost/view/')

@csrf_exempt
def salary_add(request, id=None):
    if request.user.is_authenticated():
        user = request.user
    else:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))
#        return HttpResponse('Error: У вас не має прав для редагування, або ви не Авторизувались на сайті')
    now = datetime.datetime.now()
    form = SalaryForm(initial={'user': user.pk})
    if request.method == 'POST':
        form = SalaryForm(request.POST)
#        print "POST is true"
        if form.is_valid():
#            print "FORM is true"
            cash_type = CashType.objects.get(id = 6)
            client = form.cleaned_data['client']
            #wclient = Client.objects.get(id=client)
            date = form.cleaned_data['date']
            cost_type = CostType.objects.get(id = 5) #form.cleaned_data['cost_type']
            description = form.cleaned_data['description']
            description_cost = u"Зарплата за " + description + u". " + client.name 
            price = form.cleaned_data['price']
            Costs(id=id, date=date, cost_type=cost_type, price=price, description = description_cost).save()
            ClientCredits(client=client, date=date, price=price, description= u"Зарплата за "+ description, user=user, cash_type = cash_type).save()
            
            #form.save()
            #WorkShop(client=client, date=date, work_type=work_type, price=price, description=description, user=user).save()
            return HttpResponseRedirect('/cost/view/')
    else:
        #print "FORM is false"
        form = SalaryForm(initial={'user': user.pk})

    context = {'form': form, 'weblink': 'salary.html', 'next': current_url(request)}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms.models import formset_factory


def formset_test(request, id):
    client = Client.objects.get(pk=id)
    
    ArticleFormSet = formset_factory(WorkShopForm, extra=1, can_delete=True)
    formset = ArticleFormSet(initial=[{'client': id, 'price': '1122'},])
    
    if request.method == 'POST':
        #formset = ArticleFormSet(request.POST, instance=client)
        formset = ArticleFormSet(request.POST)
        if formset.is_valid():
            #formset.save()
            for form in formset.forms:
                form.save()

            return HttpResponseRedirect('/workshop/view/')
    else:
        formset = ArticleFormSet(initial=[{'client': id, 'price': '1122'},{'client': id, 'price': '1122'},{'client': id, 'price': '1122'},])
        
    #return render_to_response("client_workshop.html", {"property_formset": formset, 'client': client})
    return render_to_response('index.html', {'property_formset': formset, 'client': client, 'weblink': 'client_workshop.html'})
    #return render_to_response("formset_test.html", {"formset": formset, 'client': client})


def inline_formset_test(request):
    #client = WorkShop.objects.get(pk=2)
    client = Client.objects.get(pk=2)
    WorkInlineFormSet = inlineformset_factory(Client, WorkShop, extra=1)
    
    if request.method == 'POST':
        #formset = ArticleFormSet(request.POST, instance=client)
        formset = WorkInlineFormSet(request.POST, instance=client)
        if formset.is_valid():
            #formset.save()
            for form in formset.forms:
                form.save()
            return HttpResponseRedirect('/workshop/view/')
    else:
        formset = WorkInlineFormSet(instance=client)
    return render_to_response("manage_client.html", {"property_formset": formset, 'client': client})
    #return render_to_response("formset_test.html", {"formset": formset, 'client': client})
    


def manage_works(request, author_id):
    client = WorkShop.objects.get(pk=author_id)
    MyFormSet = inlineformset_factory(Client, WorkShop, extra=1)
    if request.method == "POST":
        property_formset = MyFormSet(request.POST, request.FILES, instance=client)
        if property_formset.is_valid():
            for form in property_formset.forms:
                client = form.cleaned_data['client']
                #date = form.cleaned_data['date']
                work_type = form.cleaned_data['work_type']
                price = form.cleaned_data['price']
                description = form.cleaned_data['description']
                if form.id != None:
                    WorkShop(id=form.id, client=author_id, work_type=work_type, price=price, description=description).save()            
                else:
                    WorkShop(client=author_id, work_type=work_type, price=price, description=description).save()
#            property_formset.save()
#            property_formset = MyFormSet(instance=client)
            return HttpResponseRedirect('/workshop/view/')
            # Do something.
    else:
        property_formset = MyFormSet(instance=client)
    return render_to_response("formset_test.html", {"formset": property_formset,})        
#    return render_to_response("manage_client.html", {"property_formset": property_formset,})


def preorder_add(request):
    a = PreOrder(price=0, price_pay=0, date_pay=datetime.date.today(), date_delivery=datetime.date.today())
    if request.method == 'POST':
        form = PreOrderForm(request.POST, instance = a)
        if form.is_valid():
            date = form.cleaned_data['date']
            date_pay = form.cleaned_data['date_pay']
            date_delivery = form.cleaned_data['date_delivery']
            company = form.cleaned_data['company']
            manager = form.cleaned_data['manager']
            price = form.cleaned_data['price']
            price_pay = form.cleaned_data['price_pay']
            currency = form.cleaned_data['currency']
            file = form.cleaned_data['file']
            received = form.cleaned_data['received']
            description = form.cleaned_data['description']
            PreOrder(date=date, date_pay=date_pay, date_delivery=date_delivery, company=company, manager=manager, price=price, price_pay=price_pay, currency=currency, file=file, received=received, description=description).save()
            return HttpResponseRedirect('/preorder/view/')
    else:
        form = PreOrderForm(instance = a)
    return render_to_response('index.html', {'form': form, 'weblink': 'preorder.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def preorder_list(request):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/')
    list = PreOrder.objects.all()
    #return render_to_response('dealer_list.html', {'dealers': list.values_list()})
    return render_to_response('index.html', {'preorder1': list, 'weblink': 'preorder_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def preorder_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/preorder/view/')
    obj = PreOrder.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/preorder/view/')


def preorder_edit(request, id):
    a = PreOrder.objects.get(pk=id)
    if request.method == 'POST':
        form = PreOrderForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/preorder/view/')
    else:
        form = PreOrderForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'preorder.html'})


#--- workday ---
def workday_add(request):
    a = WorkDay(date=datetime.date.today())
    if request.method == 'POST':
        form = WorkDayForm(request.POST, instance = a)
        if form.is_valid():
            date = form.cleaned_data['date']
            user = form.cleaned_data['user']
            status = form.cleaned_data['status']
            description = form.cleaned_data['description']
            WorkDay(date=date, user=user, status=status, description=description).save()
            return HttpResponseRedirect('/workday/user/all/report/')
    else:
        form = WorkDayForm(instance = a)

    return render_to_response('index.html', {'form': form, 'weblink': 'workday.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    


def workday_list(request):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/')
    list = WorkDay.objects.all()
    return render_to_response('index.html', {'workdays': list, 'weblink': 'workday_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def workday_ajax(request):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('date'):
                d = request.POST.get( 'date' )
                w = WorkDay.objects.filter(date = d).values_list('user__username', 'status', 'description', 'id')
            if POST.has_key('cmonth'):
                m = request.POST.get( 'cmonth' )
                y = request.POST.get( 'cyear' )
                w = WorkDay.objects.filter(date__month = m, date__year = y).values_list('user__username', 'status', 'description', 'id')
            search = w    
                #search = Rent.objects.filter(id = id).values('status')
            return HttpResponse(simplejson.dumps(list(search)))



def workday_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/')
    obj = WorkDay.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workday/user/all/report/')

@csrf_exempt
def clientmessage_add(request):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('client'):
                c = request.POST.get( 'client' )
                m = request.POST.get( 'msg' )
                cl = Client.objects.get(id=c)
                if (request.user):
                    w = ClientMessage(client=cl, msg=m, status=False, date=datetime.date.today(), user=request.user, ddate=datetime.date.today()).save()    
                else:
                    return HttpResponse(simplejson.dumps(["Для додавання повідомлень потрібно зайти на сайт"]))
    
                search = ClientMessage.objects.filter(client = c).values('msg')
            return HttpResponse(simplejson.dumps(list(search)))

@csrf_exempt
def clientmessage_set(request, id=None):
    m = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('msg_id'):
                m = request.POST.get( 'msg_id' )
                c_msg = ClientMessage.objects.get(id=m)
                if (request.user):
                    c_msg.ddate = datetime.datetime.now()
                    c_msg.duser = request.user 
                    c_msg.status = not c_msg.status 
                    c_msg.save()
                else:
                    return HttpResponse(simplejson.dumps(["Для додавання повідомлень потрібно зайти на сайт"]))
    
            search = ClientMessage.objects.filter(id = m).values('msg')
        return HttpResponse(simplejson.dumps(list(search)))
    

def clientmessage_list(request):
    client_msg = ClientMessage.objects.all().order_by('date')
    context = {'msg_list': client_msg, 'weblink': 'client_msg_list.html'}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)            


def clientmessage_delete(request, id):
    obj = ClientMessage.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/clientmessage/list/')

@csrf_exempt
def payform(request):
    checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
    if bool(checkbox_list) == False:
        context = {'weblink': 'error_manyclients.html',}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    list_id = []
    for id in checkbox_list:
        list_id.append( int(id.replace('checkbox_', '')) )
    ci = ClientInvoice.objects.filter(id__in=list_id)
    client = ci[0].client
    desc = ""
    sum = 0
    bal = 0
    error_msg = None
    chk_list = None
    if Check.objects.filter(catalog__id__in = list_id):
        error_msg = "Дана позиція вже існує в чеку №:"
        chk_list = Check.objects.filter(catalog__id__in = list_id).values("check_num", "catalog__catalog__name")
#        for ichek in Check.objects.filter(catalog__id__in = list_id).values("check_num"):
#            url =  '<a href="/check/'+str(ichek['check_num'])+'/print/">['+str(ichek['check_num'])+'],</a>'
            #error_msg = error_msg + "["+str(ichek['check_num'])+"]"
        if auth_group(request.user, 'admin')==False:
            context = { 'weblink': 'error_manyclients.html', 'chk_list': chk_list, 'error_msg':error_msg, }
            context.update(custom_proc(request)) 
            return render(request, 'index.html', context)
        
    for inv in ci:
        if client!=inv.client:
            error_msg = "Вибрані позиції різних клієнтів"
            context = {'weblink': 'error_manyclients.html', 'error_msg':error_msg, }
            context.update(custom_proc(request))
            return render(request, 'index.html', context)
        if inv.check_payment() and ('send_check' not in request.POST):
            if (auth_group(request.user, 'admin') == False):
                error_msg = "Вибрані позиції вже оплачені"
                context = {'weblink': 'error_manyclients.html', 'error_msg':error_msg, }
                context.update(custom_proc(request))
                return render(request, 'index.html', context)
        
        client = inv.client
        #inv.pay = inv.sum
        desc = desc + inv.catalog.name + "; "
        sum = sum + inv.sum
    #-------- показ і відправка чеку на електронку ------
    if 'send_check' in request.POST:
#        if inv.check_pay() == False:
        if inv.check_payment() == False:
            if (auth_group(request.user, 'admin') == False):
                error_msg = "Вибрані позиції ще не оплачені і на них не можна друкувати фіскальний чек"
                context = {'weblink': 'error_manyclients.html', 'error_msg':error_msg, 'next': current_url(request)}
                context.update(custom_proc(request))
                return render(request, 'index.html',  context)
        
        text = pytils_ua.numeral.in_words(int(sum))
        month = pytils_ua.dt.ru_strftime(u"%d %B %Y", ci[0].date, inflected=True)
        request.session['invoice_id'] = list_id
        check_num = Check.objects.aggregate(Max('check_num'))['check_num__max']+1
        request.session['chk_num'] = check_num
        context = {'check_invoice': ci, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'check_num':check_num, 'weblink': 'client_invoice_sale_check.html', 'print': True, }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
     
    user = client.id
    if user == settings.CLIENT_UNKNOWN:
        bal = 0
    else:  
        sql1 = "SELECT sum(price) FROM accounting_clientcredits WHERE client_id = %s;"
        sql2 = "SELECT sum(price) FROM accounting_clientdebts WHERE client_id = %s;"
        #user = id;
        try:
            cursor = connection.cursor()
            cursor.execute(sql1, [user])   
            credit = cursor.fetchone()
    
            cursor.execute(sql2, [user])
            debts = cursor.fetchone()
    
            if (credit[0] is None):
                credit = (0,)
            elif (debts[0] is None):
                debts = (0,)
    
            res = credit[0] - debts[0]
            
        except TypeError:
            #res = "Такого клієнта не існує, або в нього не має заборгованостей"    
            res = 0
        bal = res
    url = '/client/result/search/?id=' + str(client.id)
    cmsg = ClientMessage.objects.filter(client__id=user)
    context = {'messages': cmsg,'checkbox': list_id, 'invoice': ci, 'summ': sum, 'balance':bal, 'client': client, 'chk_list': chk_list, 'error_msg':error_msg, 'weblink': 'payform.html', }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

@csrf_exempt
def workshop_payform(request):
    checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
    if bool(checkbox_list) == False:
        return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    list_id = []
    for id in checkbox_list:
        list_id.append( int(id.replace('checkbox_', '')) )
    wk = WorkShop.objects.filter(id__in=list_id)
    client = wk[0].client
    desc = u"Роботи: "
    sum = 0
    for inv in wk:
        if client!=inv.client:
            return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        client = inv.client
        #inv.pay = inv.sum
        desc = desc + inv.work_type.name + "; "
        sum = sum + inv.price
    #-------- показ і відправка чеку на електронку ------
    if 'send_check' in request.POST:
        text = pytils_ua.numeral.in_words(int(sum))
        month = pytils_ua.dt.ru_strftime(u"%d %B %Y", wk[0].date, inflected=True)
        request.session['invoice_id'] = list_id
        check_num = Check.objects.aggregate(Max('check_num'))['check_num__max'] + 1
        context = {'weblink': 'client_invoice_sale_check.html', 'check_invoice': wk, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'print':'True', 'is_workshop': 'True', 'check_num':check_num, }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)        

    user = client.id
    if user == 138:
        bal = 0
    else:
        try:
            debt = ClientDebts.objects.filter(client__id=user).aggregate(suma=Sum('price'))
            cred = ClientCredits.objects.filter(client__id=user).aggregate(suma=Sum('price'))
            res = cred['suma'] - debt['suma']
        except TypeError:
            #res = "Такого клієнта не існує, або в нього не має заборгованостей"    
            res = 0
        bal = res
    cmsg = ClientMessage.objects.filter(client__id=user)
    context = {'messages': cmsg,'checkbox': list_id, 'invoice': wk, 'summ': sum, 'balance':bal, 'client': client, 'weblink': 'payform.html', 'workshop':True}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)

@csrf_exempt
def dealer_payform(request):
    checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
    print "CHECK BOX = " + str(checkbox_list)
#    if bool(checkbox_list) == False:
#        return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    list_id = []
    for id in checkbox_list:
        list_id.append( int(id.replace('checkbox_', '')) )
        print "dealer ID = "  + id.replace('checkbox_', '')
    
    di_list = DealerInvoice.objects.filter(id__in = list_id)
    di_list.update(payment = True)
    
    icl = InvoiceComponentList.objects.filter(invoice__in = di_list)
    for i in icl: 
        #print "Count DIFF = " + str (i.check_count)
        if i.check_count() == False:
            print "FALSE - is REAL"
            print "INVOICE = " + str(i.invoice.id)
            DealerInvoice.objects.filter(id = i.invoice.id).update(payment = False)

    url = '/dealer/invoice/view/'
    return HttpResponseRedirect(url)
#    return render_to_response('index.html', {'weblink': 'payform_dealer.html', 'workshop':True}, context_instance=RequestContext(request, processors=[custom_proc]))

@csrf_exempt
def client_ws_payform(request):
    user = None            
    if request.user.is_authenticated():
        user = request.user
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    now = datetime.datetime.now()
    checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
    if bool(checkbox_list) == False:
        return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    list_id = []
    res = Check.objects.aggregate(max_count=Max('check_num'))
    for id in checkbox_list:
        list_id.append( int(id.replace('checkbox_', '')) )
    wk = WorkShop.objects.filter(id__in=list_id)
    client = wk[0].client
    desc = u"Роботи: "
    sum = 0

    URL = ""
    cash_id = None
    term_id = None
    shop_number = request.POST.get("shop")
    if int(shop_number) == 1:
        URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/?"
        cash_id = CashType.objects.get(id = 1) # готівка Каказька
        term_id = CashType.objects.get(id = 9) # термінал Кавказька
    if int(shop_number) == 2:
        URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/?"
        cash_id = CashType.objects.get(id = 10) # готівка Міцкевича
        term_id = CashType.objects.get(id = 2) # термінал Міцкевича
    
    for inv in wk:
        if client!=inv.client:
            return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        client = inv.client
        desc = desc + inv.work_type.name + "; "
        sum = sum + inv.price

# Без друку касового чеку
    print_check = request.POST.get("print_check", False)
    if print_check == False:
        if 'pay' in request.POST and request.POST['pay']:
            pay = request.POST['pay']
            #cash_type = CashType.objects.get(id = 1) # готівка
            if float(request.POST['pay']) != 0:
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_id, shop=shopN)
                ccred.save()
        if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
            pay = request.POST['pay_terminal']
            #cash_type = CashType.objects.get(id = 9) # термінал приват = 2; ПУМБ = 9
            if float(request.POST['pay_terminal']) != 0:
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=term_id, shop=shopN)
                ccred.save()

        ccred = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0, shop=shopN)
        ccred.save()
        for item in wk:
            item.pay = True
            #item.shop = shopN
            item.save()
        
        if client.id == settings.CLIENT_UNKNOWN:
            return HttpResponseRedirect('/workshop/view/')
         
        url = '/client/result/search/?id=' + str(client.id)
        return HttpResponseRedirect(url)
        
#--------- Begin section to send data to CASA ---------

    if (float(request.POST['pay']) != 0) or (float(request.POST['pay_terminal']) != 0):
        #base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
        data =  {"cmd": "get_status"}
        url = URL + urllib.urlencode(data)
        try:
            page = urllib.urlopen(url).read()
            #base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            data =  {"cmd": "open"}
            url = URL + urllib.urlencode(data)
            page = urllib.urlopen(url).read()
        except:
            return HttpResponse("Включіть комп'ютер з касовим апаратом")
    
    if (float(request.POST['pay']) == 0) and (float(request.POST['pay_terminal']) == 0):
        if client.id == settings.CLIENT_UNKNOWN:
            #return HttpResponseRedirect('/workshop/view/')
            return HttpResponse("Невідомому клієнту не можна додати борг")
        ccred = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0, shop=shopN)
        ccred.save()
        for item in wk:
            item.pay = True
            item.save()
        #base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
        data =  {"cmd": "close"}
        url = URL + urllib.urlencode(data)
        page = urllib.urlopen(url).read()
        url = '/client/result/search/?id=' + str(client.id)
        return HttpResponseRedirect(url)
           
    if 'pay' in request.POST and request.POST['pay']:
        pay = request.POST['pay']
        cash_type = CashType.objects.get(id = 1) # готівка
        if float(request.POST['pay']) != 0:
            ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_type, shop=shopN)
            ccred.save()
            
            res = Check.objects.aggregate(max_count=Max('check_num'))
            chkPay = CheckPay(check_num = res['max_count'] + 1, cash = pay, term = 0)
            chkPay.user = request.user
            chkPay.save()

            for inv in wk:
                check = Check(check_num=res['max_count'] + 1)
                check.client = client #Client.objects.get(id=client.id)
                check.checkPay = chkPay
                check.workshop = inv #ClientInvoice.objects.get(pk=inv)
                check.description = "Майстерня. Готівка."
                check.count = 1
                check.discount = 0
                check.price = inv.price
                check.cash_type = cash_id #CashType.objects.get(id = 1)
                check.print_status = False
                check.user = user
                check.save()
                price =  "%.2f" % inv.price
                count = "%.3f" % 1
                data =  {"cmd": "add_plu", "id":'99'+str(inv.work_type.pk), "cname":inv.work_type.name[:40].encode('utf8'), "price":price, "count": count, "discount": 0}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
                
            if (float(pay) >= sum):
                data =  {"cmd": "pay", "sum": 0, "mtype": 0}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
                #base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                data =  {"cmd": "close"}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()                
            else:
                data =  {"cmd": "pay", "sum": pay, "mtype": 0}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
                data =  {"cmd": "pay", "sum": 0, "mtype": 2}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
                #base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                data =  {"cmd": "close"}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
            
    if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
        pay = request.POST['pay_terminal']
        cash_type = term_id #CashType.objects.get(id = 9) # термінал приват = 2 / ПУМБ = 9
        if float(request.POST['pay_terminal']) != 0:
            ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_type, shop=shopN)
            ccred.save()
            res = Check.objects.aggregate(max_count=Max('check_num'))
            chkPay = CheckPay(check_num = res['max_count'] + 1, cash = 0, term = pay)
            chkPay.save()
            
            for inv in wk:
                check = Check(check_num=res['max_count'] + 1)
                check.client = client #Client.objects.get(id=client.id)
                check.checkPay = chkPay
                check.workshop = inv #ClientInvoice.objects.get(pk=inv)
                check.description = "Майстерня. Термінал."
                check.count = 1
                check.discount = 0
                check.price = inv.price
                check.cash_type = term_id #CashType.objects.get(id = 9)
                check.print_status = False
                check.user = user
                check.save()
                price =  "%.2f" % inv.price
                count = "%.3f" % 1
                data =  {"cmd": "add_plu", "id":'99'+str(inv.work_type.pk), "cname":inv.work_type.name[:40].encode('utf8'), "price":price, "count": count, "discount": 0}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
            
            if (float(pay) >= sum):
                data =  {"cmd": "pay", "sum": 0, "mtype": 2}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
            else:
                data =  {"cmd": "pay", "sum": pay, "mtype": 2}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
                data =  {"cmd": "pay", "sum": 0, "mtype": 0}
                url = URL + urllib.urlencode(data)
                page = urllib.urlopen(url).read()

    #base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
    data =  {"cmd": "close"}
    url = URL + urllib.urlencode(data)
    page = urllib.urlopen(url).read()

#----- End section to send data to CASA  
            
    ccred = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0, shop=shopN)
    ccred.save()
    for item in wk:
        item.pay = True
        item.save()

    if client.id == 138:
        return HttpResponseRedirect('/workshop/view/')
         
    url = '/client/result/search/?id=' + str(client.id)
    return HttpResponseRedirect(url)


@csrf_exempt
def client_payform(request):
    checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
    list_id = []
    user = None
    if request.user.is_authenticated():
        user = request.user
    else:
        error_msg = "Для даної дії потрібно авторизуватись!"
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    now = datetime.datetime.now()
    desc = ""
    count = None
    sum = 0
    client = None
    res = Check.objects.aggregate(max_count=Max('check_num'))
    check = None
    status = True
    URL = ""
    cash_id = None
    term_id = None
    shop_number = request.POST.get("shop")
    pay_status = request.POST.get("pay_status")
    if int(shop_number) == 1:
        URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
#        print "SERVER 1 - SEND request"
        cash_id = CashType.objects.get(id = 1) # готівка Каказька
        term_id = CashType.objects.get(id = 9) # термінал Кавказька
    if int(shop_number) == 2:
#        print "SERVER 2 - SEND request"
        URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"
        cash_id = CashType.objects.get(id = 10) # готівка Міцкевича
        term_id = CashType.objects.get(id = 2) # термінал Міцкевича
        
    cmd = 'open_port;1;115200;'
    PARAMS = {'address':URL, 'cmd': cmd, 
              'hash': settings.MINI_HASH_1, 
              'user': request.user.username,
              }
    
    if len(checkbox_list):
        for id in checkbox_list:
            list_id.append( int(id.replace('checkbox_', '')) )
        ci = ClientInvoice.objects.filter(id__in=list_id)
        client = ci[0].client
        for inv in ci:
            if inv.check_payment():
                if (auth_group(request.user, 'admin') == False):
                    error_msg = "Вибрані позиції вже оплачені!"
                    return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'error_msg':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
       
#--------- Begin section to send data to CASA ---------
        try: 
            print "\nURL = " + URL + "\n"
            print "PARAM:" + str(PARAMS) + "\n"
            if (int(shop_number) == 1) and (int(pay_status) == 1):
                print "\n**** IF Work ****\n"
                resp_open = requests.post(url = URL, data = PARAMS)
                print "Response: " + str(resp_open) + "\n"
        except:
            if auth_group(request.user, 'admin') == False:
                status = False
                return HttpResponse("Включіть комп'ютер з касовим апаратом", content_type="text/plain;charset=UTF-8;")
            else:
                status = False

        if (float(request.POST['pay']) == 0) and (float(request.POST['pay_terminal']) == 0):
            if (client.id == settings.CLIENT_UNKNOWN):
                return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': "Невідомий клієнт не може мати борг"}, context_instance=RequestContext(request, processors=[custom_proc]))

        for inv in ci:
            inv.pay = inv.sum
            desc = desc + inv.catalog.name + "; "
            sum = sum + inv.sum
            inv.shop = shopN
            inv.save()
            
        if pay_status == '0':
            print "ADD BORG!!! \n"
            
    else:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext':'Не вибрано жодного товару', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

# Без друку касового чеку
    print_check = request.POST.get("print_check", False)
    if print_check == False:
        if (float(request.POST['pay']) != 0) or (float(request.POST['pay_terminal']) != 0):
            if (client.id == settings.CLIENT_UNKNOWN):
#                print "CLIENT id = " + str(client.id) + " -- SUM = " + str(sum)
                if (float(request.POST['pay']) + float(request.POST['pay_terminal']) < sum):
                    return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': "Невідомий клієнт не може мати борг"}, context_instance=RequestContext(request, processors=[custom_proc]))
        
        if 'pay' in request.POST and request.POST['pay']:
            pay = request.POST['pay']
            if float(request.POST['pay']) != 0:
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_id, shop=shopN)
                ccred.save()
        if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
            pay = request.POST['pay_terminal']
            if float(request.POST['pay_terminal']) != 0:
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=term_id, shop=shopN)
                ccred.save()
   
        cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0, shop=shopN)
        cdeb.save()
        if client.id == settings.CLIENT_UNKNOWN:
            return HttpResponseRedirect('/client/invoice/view/')
        url = '/client/result/search/?id=' + str(client.id)
        return HttpResponseRedirect(url)

# Друк фіскального чеку
    if (float(request.POST['pay']) != 0) or (float(request.POST['pay_terminal']) != 0):
        if client.id == settings.CLIENT_UNKNOWN:
            if (float(request.POST['pay']) + float(request.POST['pay_terminal']) < sum):
                return HttpResponse("Невідомий клієнт не може мати борг", content_type="text/plain;charset=UTF-8;;");
        
        try:
            #print "Status checkbox = " + str(print_check)
            #resp_open = requests.post(url = URL, data = PARAMS)
            PARAMS['cmd'] = "cashier_registration;1;0"
            resp_registration = requests.post(url = URL, data = PARAMS)
            PARAMS['cmd'] = 'open_receipt;0' # відкрити чек
            resp_registration = requests.post(url = URL, data = PARAMS)
        except:
            message = "Сервер "+settings.HTTP_MINI_SERVER_IP+" не відповідає"
            return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
    
    if (float(request.POST['pay']) == 0) and (float(request.POST['pay_terminal']) == 0):
        if client.id == settings.CLIENT_UNKNOWN:
            return HttpResponse("Невідомий клієнт не може мати борг", content_type="text/plain;charset=UTF-8;;");
        cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0, shop=shopN)
        cdeb.save()
        if status == True:
            PARAMS['cmd'] = 'close_port;'
            resp_close = requests.post(url = URL, data = PARAMS)
            
        url = '/client/result/search/?id=' + str(client.id)
        return HttpResponseRedirect(url)
    
    if 'pay' in request.POST and request.POST['pay']:
        pay = request.POST['pay']
        #cash_type = CashType.objects.get(id = 1) # готівка
        if float(request.POST['pay']) != 0:
            ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_id)
            ccred.save()
            
            res = Check.objects.aggregate(max_count=Max('check_num'))
            chkPay = CheckPay(check_num = res['max_count'] + 1, cash = pay, term = 0)
            chkPay.user = request.user
            chkPay.save()

            for inv in ci:
                check = Check(check_num=res['max_count'] + 1)
                check.checkPay = chkPay
                check.client = client #Client.objects.get(id=client.id)
                check.catalog = inv #ClientInvoice.objects.get(pk=inv)
                check.description = "Готівка"
                check.count = inv.count
                check.discount = inv.sale
                check.price = inv.price
                check.cash_type = cash_id #CashType.objects.get(id = 1)
                check.print_status = False
                check.user = user
                check.save()
                price =  "%.2f" % inv.price
                count = "%.3f" % inv.count                
                discount = inv.sale
                
                if inv.catalog.length <> None:
                    PARAMS['cmd'] = 'add_plu;'+str(inv.catalog.pk)+";0;1;0;1;1;1;"+price+";0;"+inv.catalog.name[:40].encode('cp1251')+";"+count+";"
                    resp = requests.post(url = URL, data = PARAMS)
                else:
                    PARAMS['cmd'] = 'add_plu;'+str(inv.catalog.pk)+";0;0;0;1;1;1;"+price+";0;"+inv.catalog.name[:40].encode('cp1251')+";"+count+";"
                    resp = requests.post(url = URL, data = PARAMS)
                PARAMS['cmd'] = 'sale_plu;0;0;0;'+count+";"+str(inv.catalog.pk)+";"
                resp = requests.post(url = URL, data = PARAMS)
                PARAMS['cmd'] = 'discount_surcharge;1;0;1;'+"%.2f" % discount+";"
                resp = requests.post(url = URL, data = PARAMS)
                #PARAMS['cmd'] = 'cancel_receipt;'
                #resp = requests.post(url = URL, data = PARAMS)

            if (float(pay) >= sum):
                PARAMS['cmd'] = "pay;0;0;"
                resp = requests.post(url = URL, data = PARAMS)
            else:
                PARAMS['cmd'] = "pay;0;"+"%.2f" % float(pay)+";"
                resp = requests.post(url = URL, data = PARAMS)
                PARAMS['cmd'] = "pay;2;0;"
                resp = requests.post(url = URL, data = PARAMS)
        if float(pay) <> 0:
            PARAMS['cmd'] = 'close_port;'
            resp_close = requests.post(url = URL, data = PARAMS)

    if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
        pay = request.POST['pay_terminal']
        #cash_type = CashType.objects.get(id = 9) # термінал
        if float(request.POST['pay_terminal']) != 0:
            ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=term_id, shop=shopN)
            ccred.save()
            res = Check.objects.aggregate(max_count=Max('check_num'))
            chkPay = CheckPay(check_num = res['max_count'] + 1, cash = 0, term = pay)
            chkPay.save()

            for inv in ci:
                check = Check(check_num=res['max_count'] + 1)
                check.client = client #Client.objects.get(id=client.id)
                check.catalog = inv #ClientInvoice.objects.get(pk=inv)
                check.checkPay = chkPay
                check.description = "Картка"
                check.count = inv.count
                check.discount = inv.sale
                check.price = inv.price
                check.cash_type = term_id #CashType.objects.get(id = 9)
                check.print_status = False
                check.user = user
                check.save()
                price =  "%.2f" % inv.price
                count = "%.3f" % inv.count
                discount = inv.sale
                if inv.catalog.length <> None:
                    PARAMS['cmd'] = 'add_plu;'+str(inv.catalog.pk)+";0;1;0;1;1;1;"+price+";0;"+inv.catalog.name[:40].encode('cp1251')+";"+count+";"
                    resp = requests.post(url = URL, data = PARAMS)
                else:
                    PARAMS['cmd'] = 'add_plu;'+str(inv.catalog.pk)+";0;0;0;1;1;1;"+price+";0;"+inv.catalog.name[:40].encode('cp1251')+";"+count+";"
                    resp = requests.post(url = URL, data = PARAMS)
                PARAMS['cmd'] = 'sale_plu;0;0;0;'+count+";"+str(inv.catalog.pk)+";"
                resp = requests.post(url = URL, data = PARAMS)
                PARAMS['cmd'] = 'discount_surcharge;1;0;1;'+"%.2f" % discount+";"
                resp = requests.post(url = URL, data = PARAMS)
                #PARAMS['cmd'] = 'cancel_receipt;'
                #resp = requests.post(url = URL, data = PARAMS)

            if (float(pay) >= sum):                
                PARAMS['cmd'] = "pay;2;0;"
                resp = requests.post(url = URL, data = PARAMS)
            else:
                PARAMS['cmd'] = "pay;2;"+"%.2f" % float(pay)+";"
                resp = requests.post(url = URL, data = PARAMS)
                PARAMS['cmd'] = "pay;0;0;"
                resp = requests.post(url = URL, data = PARAMS)
 
        if float(pay) <> 0:
            PARAMS['cmd'] = 'close_port;'
            resp_close = requests.post(url = URL, data = PARAMS)
               
    cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0, shop=shopN)
    cdeb.save()
    if client.id == settings.CLIENT_UNKNOWN:
        return HttpResponseRedirect('/client/invoice/view/')
    url = '/client/result/search/?id=' + str(client.id)
    return HttpResponseRedirect(url)


def catalog_saleform(request):
    checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
    list_id = []
    for id in checkbox_list:
        list_id.append( int(id.replace('checkbox_', '')) )
    catalog = Catalog.objects.filter(id__in=list_id)
    
    if 'sale' in request.POST and request.POST['sale']:
        sale = request.POST['sale']
        if float(request.POST['sale']) <= 0:
            sale = 0
        for c in catalog:
            c.sale = sale
            c.save()
             
#===============================================================================
#    if 'pay' in request.POST and request.POST['pay']:
#        pay = request.POST['pay']
#        if float(request.POST['pay']) != 0:
#            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=pay, description=desc)
#            ccred.save()
#===============================================================================
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#    return HttpResponse("You pressed button SALE" + str(list_id))

from django.contrib.auth.models import User

def user_invoice_report(request, month=None, year=None, day=None, user_id=None):
    userid = None
    if user_id:
        user_id = user_id

    if request.user.is_authenticated() and user_id == None:
        user_id = request.user.id
    if user_id == None: #'0':
#        user_id = None
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу. Авторизуйтесь на порталі.', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
        
#    else:
#        user_id = None
    
    if year == None:
        year = datetime.datetime.now().year
    if month == None:
        month = datetime.datetime.now().month

    if day == None:
        day = datetime.datetime.now().day
        list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day, user__id=user_id).order_by("-date", "-id")
    else:
        if day == 'all':
            list = ClientInvoice.objects.filter(date__year=year, date__month=month, user__id=user_id).order_by("-date", "-id")
        else:
            list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day, user__id=user_id).order_by("-date", "-id")
            
    psum = 0
    scount = 0
    for item in list:
        psum = psum + item.sum
        scount = scount + item.count
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    
    paginator = Paginator(list, 25)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        cinvoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        cinvoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        cinvoices = paginator.page(paginator.num_pages)

    try:
        user = User.objects.get(id=user_id)
    except:
        user = None
    context = {'sel_user':user, 'sel_year':year, 'sel_month':month, 'sel_day':day, 'month_days':days, 'buycomponents': cinvoices, 'sumall':psum, 'sum_salary':psum*0.05, 'countall':scount, 'weblink': 'report_clientinvoice_byuser.html', 'view': True, }
    context.update(custom_proc(request))        
    return render(request, 'index.html', context)



def worktype_report(request, id, month=None, year=None, day=None,  limit=None):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/')    
    sel_day = None
    sel_month = None
    work_type = WorkType.objects.get(id=id)
    if year == None:
        year = datetime.datetime.now().year
    if month <> None:
        list = WorkShop.objects.filter(date__year=year, date__month=month, work_type__id=id).order_by("-date", "-id")
        sel_month = month
    if month == None:
        month = datetime.datetime.now().month
        sel_month = month
    if day == 'all':
        sel_month = None
        #day = datetime.datetime.now().day
        #list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day, work_type__id=id).order_by("-date", "-id")
        list = WorkShop.objects.filter(date__year=year, work_type__id=id).order_by("-date", "-id")
    if limit == 'all':
        list = WorkShop.objects.filter(work_type__id=id).order_by("-date", "-id")

    year_list = WorkShop.objects.filter(work_type__id=id).extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
    month_list = WorkShop.objects.filter(work_type__id=id).filter(date__year = year).extra({'month':"Extract(month from date)"}).values_list('month').annotate(Count('id')).order_by('month')

    psum = 0
    scount = 0
    for item in list:
        psum = psum + item.price
        scount = scount + 1
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    
    paginator = Paginator(list, 25)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        cinvoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        cinvoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        cinvoices = paginator.page(paginator.num_pages)
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    
    context = {'sel_user':user, 'sel_year':year, 'years': year_list, 'sel_month':sel_month, 'month_list':month_list, 'sel_day':sel_day, 'month_days':days, 'workshop': cinvoices, 'sumall':psum, 'countall':scount, 'work_type': work_type,  'weblink': 'report_worktype.html', 'view': True, 'next': current_url(request)}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)
    

def user_workshop_report(request,  month=None, year=None, day=None, user_id=None):
    if request.user.is_authenticated() and user_id == None:
        user_id = request.user.id
    
    if year == None:
        year = datetime.datetime.now().year
    if month == None:
        month = datetime.datetime.now().month
    if day == None:
        day = datetime.datetime.now().day
        list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day, user__id=user_id).order_by("-date", "-id")
    else:
        if day == 'all':
            list = WorkShop.objects.filter(date__year=year, date__month=month, user__id=user_id).order_by("-date", "-id")
        else:
            list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day, user__id=user_id).order_by("-date", "-id")
            
    psum = 0
    scount = 0
    for item in list:
        psum = psum + item.price
        scount = scount + 1
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    
    paginator = Paginator(list, 25)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        cinvoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        cinvoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        cinvoices = paginator.page(paginator.num_pages)

    user = User.objects.get(id=user_id)
    context = {'sel_user':user, 'sel_year':year, 'sel_month':month, 'sel_day':day, 'month_days':days, 'workshop': cinvoices, 'sumall':psum, 'sum_salary':psum*0.4, 'countall':scount, 'weblink': 'report_workshop_byuser.html', 'view': True,}
    context.update(custom_proc(request))         
    return render(request, 'index.html', context)


def all_user_salary_report(request, month=None, year=None, day=None, user_id=None):
    if auth_group(request.user, "admin") == False:
        context = {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу. Зверніться до адміністратора. ', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    
    qwsum = None
    res = None
    l = 0
    users = User.objects.filter(is_active = True).order_by('id')
   
    if year == None:
        year = datetime.datetime.now().year
    if month == None:
        month = datetime.datetime.now().month

    if day == None:
        day = datetime.datetime.now().day
        w_list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username',).annotate(total_price=Sum('price')).order_by('user')
        c_list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum')).order_by('user')
        b_list = Bicycle_Sale.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum')).order_by('user')
    else:
        if day == 'all':
            w_list = WorkShop.objects.filter(date__year=year, date__month=month).values('user', 'user__username', ).annotate(total_price=Sum('price')).order_by('user')
            c_list = ClientInvoice.objects.filter(date__year=year, date__month=month).values('user', 'user__username').annotate(total_price=Sum('sum')).order_by('user')
            b_list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).values('user', 'user__username').annotate(total_price=Sum('sum')).order_by('user')
            qwsum = WorkShop.objects.filter(date__year=year, date__month=month, user__in = users).values('user', 'user__username', 'user').annotate(total_price=Sum('price')).order_by('user')
            qcsum = ClientInvoice.objects.filter(date__year=year, date__month=month, user__in = users).values('user', 'user__username').annotate(total_price=Sum('sum')).order_by('user')
            qbsum = Bicycle_Sale.objects.filter(date__year=year, date__month=month, user__in = users).values('user', 'user__username').annotate(total_price=Sum('sum')).order_by('user')
            qbsum1 = Bicycle_Sale.objects.filter(date__year=year, date__month=month, user__in = users).exclude(user=4).aggregate(total_price=Sum('sum'))
            
            d = {}
            for u in users:
                t = []
                dic = {}
                t.append(qwsum.filter(user = u.id))
                dic['workshop'] = qwsum.filter(user = u.id)
                t.append(qcsum.filter(user = u.id))
                dic['client_inv'] = qcsum.filter(user = u.id)
                t.append(qbsum.filter(user = u.id))
                dic['bicycle'] =  qbsum.filter(user = u.id)
                if dic['workshop'].count() == 0 and dic['client_inv'].count() == 0 and dic['bicycle'].count() == 0:
                    #print 'EMPTY ' +  str(type(dic['workshop'])) + str(dic['client_inv']) + str(dic['bicycle'])
                    pass
                else:
                    #print 'DICT = ' + str(dic['workshop'].count()) + str(dic['client_inv'].count()) + str(dic['bicycle'].count())
                    d[u.id] = dic
            res = d
            l = len(res)
            try:
                qbsum1 = qbsum1['total_price'] * 0.05 / l
            except:
                qbsum1 = 0
        else:
            w_list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('price')).order_by('user')
            c_list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum')).order_by('user')
            b_list = Bicycle_Sale.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum')).order_by('user')
    bsum = 0
    csum = 0
    wsum = 0
    for b in b_list:
        bsum = bsum + (b['total_price'] or 0)
    for c in c_list:
        csum = csum + c['total_price']
    for w in w_list:
        wsum = wsum + w['total_price']
    #year_list = Bicycle_Sale.objects.filter().extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('date')
    year_list = Bicycle_Sale.objects.annotate(year=ExtractYear('date')).values('year').annotate(pk_count = Count('pk')).order_by('year') 
    #annotate(year=Extract('date','year')).values('year').annotate(total_bike=Count('year')).order_by('date')  #all().values('model', 'date').annotate(total_bike=Count('date')).order_by('date__year')
    context = {'sel_year': int(year), 'sel_month':int(month), 'workshop':w_list, 'cinvoice': c_list, 'bicycle_list':b_list, 'qwsum': qbsum1,  'll':l, 'res': res, 'bike_sum': bsum, 'c_sum': csum, 'w_sum': wsum, 'weblink': 'report_salary_all_user.html', 'year_list': year_list}
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

@csrf_exempt
def rent_add(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    else:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))
    a = Rent()
    if request.method == 'POST':
        form = RentForm(request.POST, instance = a)
        #form = RentForm(request.POST)
        if form.is_valid():
            catalog = form.cleaned_data['catalog']
            client = form.cleaned_data['client']
#            date_start = form.cleaned_data['date_start']
            date_start = datetime.datetime.now()
            date_end = form.cleaned_data['date_end']
#            count = form.cleaned_data['count']
            count = 1
            deposit = form.cleaned_data['deposit']
#            status = form.cleaned_data['status']
            status = False
            description = form.cleaned_data['description']
            user = None            
            if request.user.is_authenticated():
                user = request.user

            r = Rent(catalog=catalog, client=client, date_start=date_start, date_end=date_end, count=count, deposit=deposit, status=status, description=description, user=user)
            r.save()
            currency = form.cleaned_data['currency']
            cash_type = form.cleaned_data['cash_type']
#            cash_type = CashType.objects.get(id = currency.id) 
            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=deposit, description="Завдаток за прокат "+str(catalog), user=user, cash_type=cash_type)
#            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=deposit, description="Завдаток за прокат "+str(catalog), user=user, cash_type=currency.id)
            ccred.save()
            r.cred = ccred
            r.save()
            return HttpResponseRedirect('/rent/view/')
    else:
        form = RentForm(instance = a)
        #form = RentForm()
    context = {'form': form, 'weblink': 'rent.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)
    

def rent_edit(request, id):
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('id'):
                q = request.GET.get( 'id' )
                r = Rent.objects.get(id = id)
                if r.status == False:
                    cdeb = ClientDebts(client=r.client, date=datetime.datetime.now(), price=r.cred.price, description="Повернення завдатку за прокат "+str(r.catalog), user=request.user, cash=True)
                    cdeb.save()
                #r.deposit
                r.status = not r.status
                r.save()
                #search = Rent.objects.filter(id = id).values_list('status', flat=True)    
                search = Rent.objects.filter(id = id).values('status')
                return HttpResponse(simplejson.dumps(list(search)))
    
    a = Rent.objects.get(pk=id)
    if request.method == 'POST':
        form = RentForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            try:
                ccred = ClientCredits.objects.get(pk=a.cred.id)
                ccred.price = form.cleaned_data['deposit']
                ccred.cash_type = form.cleaned_data['cash_type']
                if request.user.is_authenticated():
                    user = request.user
                    ccred.user = user
                ccred.save()
            except:
                pass

            return HttpResponseRedirect('/rent/view/')
    else:
        form = RentForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'rent.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def rent_list(request):
    now = datetime.datetime.now()
    list = Rent.objects.filter((Q(status = False)) | Q(date_end__gt=now-datetime.timedelta(days=360)))
    context = {'rent': list, 'weblink': 'rent_list.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)    


def rent_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/preorder/view/')
    obj = Rent.objects.get(id=id)
    try:
        ccred = ClientCredits.objects.get(pk=obj.cred.id)
        ccred.delete()
    except:
        pass

    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/rent/view/')


def ajax_search1(request):
    if request.method == 'GET':  
        GET = request.GET  
        if GET.has_key('q'):
            q = request.GET.get( 'q' )
            search = Country.objects.all()
            results = search.filter(name__contains = q)
            matches = ""
            for result in results:
                matches = matches + "%s\n" % (result.name)
            return HttpResponse(matches, content_type="text/plain;charset=UTF-8;")

# search client in autocomplete field
def ajax_search(request):
    results = []
    search = None
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('term'):
                q = request.GET.get( 'term' )
#                search = Client.objects.filter(name__icontains = q).values_list('name', flat=True)
                search = Client.objects.filter(Q(name__icontains = q) | Q(forumname__icontains = q)).values_list('name', flat=True)
                #results = search.filter(name__icontains = q).values_list('name', flat=True)
                #for i in search:
                #    results.append(i)
    else:
        message = "Error"
    return HttpResponse(simplejson.dumps(list(search)))

       

def client_card_sendemail(request, id):
    client = id
    user = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('status'):
                user = request.POST.get('status')
    
#    list = Catalog.objects.filter(manufacturer = 28, count__gt=0).order_by("type")    
#    company = Manufacturer.objects.get(id=28)
#    company_list = Manufacturer.objects.all()
#    w = render_to_response('price_list.html', {'catalog': list, 'company': company, 'company_list': company_list,})
        cl = None   
        try:
            cl = Client.objects.get(id = client)#.values_list('email')
        except:
            return HttpResponse("Сталася помилка при відправленні. Не заповнено поле E-MAIL")
        w = client_result(request, 30, client, True)

#        if cl.email == None:
#            return HttpResponse("Сталася помилка при відправленні. Не заповнено поле E-MAIL")
        
        subject, from_email, to = 'Картка клієнта в магазині Rivelo', 'rivelo@ymail.com', cl.email
        text_content = 'This is an important message.'
#    html_content = '<p>This is an <strong>important</strong> message.</p>'
        html_content = w.content
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
    #msg.send()
#    send_mail('Rivelo shop', 'Here is the new message with you check.', 'rivelo@ymail.com', ['igor.panchuk@gmail.com'], fail_silently=False)
    #send_mail('subj - Test rivelo check', 'Here is the new message with you check.', 'rivelo@ymail.com', ['igor.panchuk@gmail.com'],)
    # Define these once; use them twice!
#    strFrom = 'rivelo@ymail.com'
#    strTo = 'rivelo@ukr.net'
#    send_mail('Товарний Чек - Test rivelo check', 'Here is the new message with you check.', 'rivelo@ymail.com', [strTo,],)
    #send_mail('subj - Test rivelo check', ‘message’, ‘from@mail.ru’, ‘rivelo@ymail.com’)        
    #return render_to_response('index.html', {'weblink': 'index.html'})
    
        try:
            msg.send()
            return HttpResponse("Лист відправлено на пошту " + to)
        except:
            return HttpResponse("Сталася помилка при відправленні. Перевірте з'єднання до інтернету або зверніться до адмністратора.")
    return None
#    return render_to_response("index.html", {"weblink": 'top.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


@csrf_exempt
def client_history_cred(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для перегляду')
            now = datetime.datetime.now()
            POST = request.POST  
            if POST.has_key('client_id') and POST.has_key('cred_day'):
                cid = request.POST['client_id']
                cmonth = request.POST['cred_month']
                cyear = request.POST['cred_year']
                cday = request.POST['cred_day']
                n_day = int(cday) - 30;
                p_cred_month = ClientCredits.objects.filter(client = cid, date__gt=now-datetime.timedelta(days=int(cday)), date__lt=now-datetime.timedelta(days=n_day)).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                #p_cred_month = ClientCredits.objects.filter(client = cid, date__month = cmonth, date__year = cyear).values('id', 'price', 'description', 'user', 'user__username', 'date')
                json = list(p_cred_month)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")
                
                #json = serializers.serialize('json', p_cred_month, fields=('id', 'date', 'price', 'description', 'user', 'user_username'))
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
        
            if 'clientId' in request.POST and request.POST['clientId']:
                clientId = request.POST['clientId']
#                cday = request.POST['cred_day']
#                n_day = int(cday) - 30;
                p_cred_month = None
                cash_id = CashType.objects.get(id = 6) # заробітна плата
                if auth_group(request.user, "admin") == False:
                    client_name = Client.objects.values('name', 'forumname', 'id', 'phone', 'birthday', 'email').get(id = clientId)
                    if str(request.user.username).lower() == str(client_name['forumname'].lower()):
#                        p_cred_month = ClientCredits.objects.filter(client = clientId, date__gt=now-datetime.timedelta(days=int(cday)), date__lt=now-datetime.timedelta(days=n_day)).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                        p_cred_month = ClientCredits.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')                        
                    else:
#                        p_cred_month = ClientCredits.objects.filter(client = clientId, date__gt=now-datetime.timedelta(days=int(cday)), date__lt=now-datetime.timedelta(days=n_day)).exclude(cash_type = cash_id).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                        p_cred_month = ClientCredits.objects.filter(client = clientId).exclude(cash_type = cash_id).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')                        
                else: 
#                    p_cred_month = ClientCredits.objects.filter(client = clientId, date__gt=now-datetime.timedelta(days=int(cday)), date__lt=now-datetime.timedelta(days=n_day)).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                    p_cred_month = ClientCredits.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')                
                #p_cred_month = ClientCredits.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                #p_cred_month = ClientCredits.objects.filter(client = cid, date__month = cmonth, date__year = cyear).values('id', 'price', 'description', 'user', 'user__username', 'date')
                json = list(p_cred_month)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")

                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    return HttpResponse(data_c, content_type='application/json')    


@csrf_exempt
def client_history_debt(request):
    data_c = None
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для перегляду')
            now = datetime.datetime.now()
            POST = request.POST  
            if POST.has_key('client_id') and POST.has_key('cred_day'):
                cid = request.POST['client_id']
                cday = request.POST['cred_day']
                n_day = int(cday) - 30;
                p_debt_month = ClientDebts.objects.filter(client = cid, date__gt=now-datetime.timedelta(days=int(cday)), date__lt=now-datetime.timedelta(days=n_day)).values('id', 'price', 'description', 'user', 'user__username', 'date')
                json = list(p_debt_month)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")

                return HttpResponse(simplejson.dumps(json), content_type='application/json')
                
                
            if 'clientId' in request.POST and request.POST['clientId']:
                clientId = request.POST['clientId']
                p_debt_month = ClientDebts.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date')
                #p_cred_month = ClientCredits.objects.filter(client = cid, date__month = cmonth, date__year = cyear).values('id', 'price', 'description', 'user', 'user__username', 'date')
                json = list(p_debt_month)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")

                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    return HttpResponse(data_c, content_type='application/json')    

@csrf_exempt
def client_history_invoice(request):
    now = datetime.datetime.now()
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для перегляду')
            POST = request.POST  
            if POST.has_key('client_id') and POST.has_key('day'):
                cid = request.POST['client_id']
                day = request.POST['day']
                nday = int(day)-30
                client_invoice = ClientInvoice.objects.filter(client=cid, date__gt=now-datetime.timedelta(days=int(day)), date__lt=now-datetime.timedelta(days=nday)).order_by("-date", "-id").values('id', 'catalog', 'catalog__name', 'catalog__ids', 'count', 'price', 'sum', 'currency', 'currency__name', 'pay', 'description', 'user', 'user__username', 'date')
                json = list(client_invoice) 
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")

                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    return HttpResponse()#result, content_type='application/json')


#===============================================================================
# def insertstory(request):
#     if 'TextStory' in request.POST and request.POST['TextStory']:
#         TheStory = request.POST['TextStory']
#     #return render_to_response('news_list.html')
#     search = Client.objects.filter(forumname__icontains = TheStory).values_list('name', flat=True)    
#     return HttpResponse(simplejson.dumps(list(search)))
#===============================================================================


def xhr_test(request):
    if request.is_ajax():
        price = 56 #Catalog.objects.get(id=448).value("price")
        message = "Hello AJAX; Price = " + str(price)
    else:
        message = "Hello"
#    if 'TextStory' in request.POST and request.POST['TextStory']:
#        TheStory = request.POST['TextStory']
    #return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
    return HttpResponse(simplejson.dumps({'response': message, 'result': 'success', 'param1':'Ти таки', 'param2':'натиснув його!'}), content_type='application/json')

# Rent function to get price of goods
def ajax_test(request):
    search = None
    message = ""
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('id'):
                q = request.GET.get( 'id' )
                message = "It's AJAX!!!"
    else:
        message = "Error"
    #search = Catalog.objects.filter(id=q).values_list('price', flat=True)
    search = Catalog.objects.filter(id=q).values('price', 'sale', 'name')
    
    #return HttpResponse(simplejson.dumps(response), content_type="application/json")#    return HttpResponse(simplejson.dumps(list(search)), content_type='application/json')
    return HttpResponse(simplejson.dumps(list(search)), content_type="application/json")
    #return HttpResponse(serialized_queryset, content_type='application/json')
#    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")


def ajax_price_print(request):
    search = None
    message = ""
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('id'):
                q = request.GET.get( 'id' )
                message = "It's AJAX!!!"
    else:
        message = "Error"
    search = "ok"
    #search = Catalog.objects.filter(id=q).values('price', 'sale', 'name')
    #return HttpResponse(simplejson.dumps(list(search)), content_type="application/json")
    return HttpResponse(search, content_type="text/plain;charset=UTF-8;")

@csrf_exempt
def invoice_new_edit(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id') and POST.has_key('rcount'):
                id = request.POST.get('id')
                p = request.POST.get('rcount')
                obj = InvoiceComponentList.objects.get(id = id)
                obj.user = request.user
                obj.rcount = p
                obj.shop = get_shop_from_ip(request.META['REMOTE_ADDR'])
                obj.save()
                c = InvoiceComponentList.objects.filter(id = id).values('rcount', 'user__username', 'id')
                #return HttpResponse(c, content_type='text/plain;charset=UTF-8;')
    results = {'value': c[0]['rcount'], 'user': c[0]['user__username'], 'id':c[0]['id']}
    json = simplejson.dumps(results)
    return HttpResponse(json, content_type='application/json')


@csrf_exempt
def invoice_sales_by_year(request):
    results = None
    year_count = []
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('catid'):
                cat_id = request.POST.get('catid')
                year_list = ClientInvoice.objects.filter(catalog__id = cat_id).extra({'year':"Extract(year from date)"}).values_list('year').annotate(Sum('count')).order_by('-year')
#    month_list = WorkShop.objects.filter(work_type__id=id).filter(date__year = year).extra({'month':"Extract(month from date)"}).values_list('month').annotate(Count('id')).order_by('month')                
#                print "Year list = %s" % year_list 
                for i in year_list:
                    year_count.append({'year': i[0], 'count': i[1] })
#                obj = InvoiceComponentList.objects.get(id = id)
#                obj.user = request.user
#                obj.shop = get_shop_from_ip(request.META['REMOTE_ADDR'])
 #               obj.save()
  #              c = InvoiceComponentList.objects.filter(id = id).values('rcount', 'user__username', 'id')
#    results = {'value': year_list[0], 'user': request.user, 'count': year_list[0]['count']}
                #y_list = serializers.serialize('json', year_list, fields=('year', 'count'))
                results = {'year_count': year_count, 'status': True}
    json = simplejson.dumps(results)
    #json = simplejson.dumps(year_list)
    return HttpResponse(json, content_type='application/json')

    
@csrf_exempt
def photo_url_add(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування', content_type="text/plain;charset=UTF-8;;")
            POST = request.POST  
            if POST.has_key('id') and POST.has_key('url'):
                pid = request.POST.get('id')
                p_url = request.POST.get('url')
                photo_select = Photo.objects.filter(url = p_url)
                if photo_select:
                    c = Catalog.objects.get(id = pid)
                    c.photo_url.add(photo_select[0])
                    c.save()
                    return HttpResponse("Таке фото вже існує / This photo is present", content_type="text/plain;charset=UTF-8;;")
                p1 = Photo(url = p_url, date = datetime.datetime.now(), user = request.user, description="")
                p1.save()
                c = Catalog.objects.get(id = pid)
                c.photo_url.add(p1)
                c.save()
    search = "ok"
    return HttpResponse(search, content_type="text/plain;charset=UTF-8;;")


def retrieve_image(url):
    response = requests.get(url)
    if response.status_code != 200:
        print "Error - " + response.status_code
    return StringIO.StringIO(response.content)


def save_photo_local(obj, url, d_url, file_path, filename):
    try:
        ri = retrieve_image(url)
        image = Image.open(ri)
#        print "Django FileName = " + d_url + filename
        #obj.local = filename
#        print "FileName = " + filename
        if os.path.isfile(file_path + filename):
#            print "isFile = True"
            obj.local = d_url + filename
            obj.save()
            tempfile = file_path + filename[:-4]+ "-"+ str(obj.pk) +filename[-4:]
#            print "Image OBJ = " + tempfile
            im1 = Image.open(file_path + filename)
            image.save(file_path + filename[:-4]+ "-"+ str(obj.pk) +filename[-4:], 'JPEG')
            #image.save('c:\svn\catalog\catalog\media/download/398292-305.jpg', 'JPEG')
            im2 = Image.open(tempfile)
#            print "image file = " + file_path + filename
            if im1 == im2: 
#                print "File is SAME/equal"
                os.remove(tempfile)
            else:
#                print "Save another file..."+ file_path + filename[:-4]+ "-"+ str(obj.pk) +filename[-4:]
                image.save(file_path + filename[:-4]+ "-"+ str(obj.pk) +filename[-4:], 'JPEG')
                obj.local = d_url + filename[:-4]+ "-"+ str(obj.pk) +filename[-4:]
                obj.save()
                pass
            return False
        else:
            image.save(file_path + filename, 'JPEG')
            obj.local = d_url + filename  
            obj.www = url
            obj.save()
#            print "File save = " + file_path +  filename
            return obj
    except:
        print "EXCEPT save_photo_local - " + filename
        pass
    return obj

@csrf_exempt
def photo_url_get(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
#            if auth_group(request.user, 'admin')==False:
#                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id'):
                cid = request.POST.get('id')
                cat = Catalog.objects.get(id = cid)
                photo_list = cat.get_photos()
                c_name = "[" + cat.ids + "] - " + cat.name
                try:
                    #json = simplejson.dumps({'aData': list(photo_list), 'id': cid, 'cname': c_name})
                    json = simplejson.dumps({'aData': photo_list, 'id': cid, 'cname': c_name})
                except:
                    json = simplejson.dumps({'aData': "None", 'id': cid, 'cname': c_name})
        return HttpResponse(json, content_type='application/json')
    else:
#        print "<< ELSE - WORK PHOTO ajax >>"
        #id = request.POST.get('id')
        obj = Photo.objects.get(pk = id)
        bset = obj.bicycle_set.all()
        cat_set = obj.catalog_set.all()
        str_cat = ''
        str_bike = ''
        for cat in cat_set:
            str_cat = str_cat + str(cat.pk) + "["+ str(cat.ids) +"] | " 
        for bike in bset:            
            str_bike = str_bike + str(bike.pk)
        
        status_cat = cat_set.exists()
        status_bike = bset.exists()
        
        o_url = ''
        if obj.url == "":
            o_url = obj.www
        if obj.www == None:
            o_url = obj.url
        else:
            o_url = obj.www
#        print "oURL = " + o_url
#        print "oWwww = " + str(obj.www)
#        print "obj_url = " + obj.url
#        print "olocal = " + (str(obj.local) or "")

        file_path = settings.MEDIA_ROOT + 'download/'
        filetype = ".jpg"
        media = settings.MEDIA_URL + 'download/'
#        print "file_path = " + file_path
        filename = ''
        dirname_glob = settings.PROJECT_DIR

        if (not status_cat) and (not status_bike):
            filename = "new-file-" + str(obj.pk)
        if (status_cat) and (not status_bike):
            filename = cat_set[0].ids
            filename = slugify(filename)
        if (not status_cat) and (status_bike):            
            filename = bset[0].id
            filename = slugify(filename)
#        print "File name = " + filename + filetype
#        print "Local path = " + dirname_glob[:-1]
        
        if obj.local == None or obj.local == '':
#            print "Locale = None"
            save_photo_local(obj, o_url, media, file_path, filename + filetype)            
#            return HttpResponse("Local NoneType")
            str_obj = "<img style='max-width:500px' src='" + str(o_url) + "'> <br>Photo = ["+ str(obj.date) +"] " + "<br>cat_id - " + str_cat + "<br> bike_id - " + str_bike + "<br>" + "url = " + obj.url + "<br>local = " + (str(obj.local) or "") + "  <br>  www = " + str(obj.www) + "<br> User = " + str(obj.user)
            return HttpResponse(str_obj)
        
#        print "Local path + obj = " + dirname_glob[:-1] + obj.local
        if (obj.local <> '') and (os.path.isfile(dirname_glob[:-1] + obj.local)):
            #print "File LOCAL exists = " + str(settings.MEDIA_ROOT + obj.local)
 #           print "File Local exists = " + dirname_glob[:-1] + obj.local
            #obj.local = ''
            #obj.save()
            str_obj = "<img style='max-width:500px' src='" + (str(obj.local) or "") + "'> <br>Photo = ["+ str(obj.date) +"] " + "<br>cat_id - " + str_cat + "<br> bike_id - " + str_bike + "<br>" + "url = " + obj.url + "<br>local = " + (str(obj.local) or "") + "  <br>  www = " + str(obj.www) + "<br> User = " + str(obj.user)
            return HttpResponse(str_obj)

        if ((obj.local <> '') and (not os.path.isfile(dirname_glob[:-1] + obj.local)) and (o_url <> '')):
#            print "Local var is False"
            save_photo_local(obj, o_url, media, file_path, filename + filetype)

 #       print "LAST return"
        str_obj = "<img style='max-width:500px' src='" + (str(obj.local) or "") + "'> <br>Photo = ["+ str(obj.date) +"] " + "<br>cat_id - " + str_cat + "<br> bike_id - " + str_bike + "<br>" + "url = " + obj.url + "<br>local = " + (str(obj.local) or "") + "  <br>  www = " + str(obj.www) + "<br> User = " + str(obj.user)
        #str_obj = "<img style='max-width:500px' src='"+ str(obj.local) or "" + "'><br>Photo = ["+ str(obj.date) +"] " + "<br>cat_id - " + str_cat + "<br> bike_id - " + str_bike + "<br>" + "url = " + str(obj.url) or "" + "<br>local = " + str(obj.local) or "" + "  <br>  www = " + str(obj.www) or ""  
        return HttpResponse(str_obj) 


def change_photo_url(obj_photo):
    obj = obj_photo 
    bset = obj.bicycle_set.all()
    cat_set = obj.catalog_set.all()
    str_cat = ''
    str_bike = ''
    status_cat = cat_set.exists()
    status_bike = bset.exists()
    o_url = ''
    if obj.url == "":
        o_url = obj.www
    if obj.www == None:
        o_url = obj.url
    else:
        o_url = obj.www
#    print "oURL = " + o_url

    file_path = settings.MEDIA_ROOT + 'download/'
    filetype = ".jpg"
    media = settings.MEDIA_URL + 'download/'
    #print "file_path = " + file_path
    filename = ''
    dirname_glob = settings.PROJECT_DIR

    if (not status_cat) and (not status_bike):
        filename = "new-file-" + str(obj.pk)
    if (status_cat) and (not status_bike):
        filename = cat_set[0].ids
        filename = slugify(filename)
    if (not status_cat) and (status_bike):            
        filename = bset[0].id
        filename = slugify(unicode(str(filename), "utf-8"))
    if obj.local == None or obj.local == '':
        print "Locale = None - [" + filename + filetype + ']' 
        save_photo_local(obj, o_url, media, file_path, filename + filetype)            
        return True

    if (obj.local <> '') and (os.path.isfile(dirname_glob[:-1] + obj.local)):
#        print "File Local exists = " + dirname_glob[:-1] + obj.local
        return True

    if ((obj.local <> '') and (not os.path.isfile(dirname_glob[:-1] + obj.local)) and (o_url <> '')):
#        print "Local var is False"
        save_photo_local(obj, o_url, media, file_path, filename + filetype)

#    print "LAST return"
    return True

@csrf_exempt
def photo_del_field(request):
    if auth_group(request.user, 'admin')==False:
        #return HttpResponse('Error: У вас не має прав для редагування')
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                pid = request.POST.get('id')
                try:
                    photo = Photo.objects.get(pk = pid)    
                    if POST.has_key('local'):
                        local = request.POST.get('local')
                        loc = photo.local
                        photo.local = ''
                        photo.save()
                        msg = 'Фото '+ str(loc) +' видалено'
                        json = simplejson.dumps({'status': True, 'msg': msg})
                        return HttpResponse(json, content_type='application/json')
                    if POST.has_key('www'):
                        www = request.POST.get('www')
                        www = photo.www
                        photo.www = None
                        photo.save()
                        msg = 'Фото '+ '['+str(photo.pk)+'] ' + str(www) +' видалено'
                        json = simplejson.dumps({'status': True, 'msg': msg})
                        return HttpResponse(json, content_type='application/json')
                    if POST.has_key('url'):
                        url = request.POST.get('url')
                        url = photo.url
                        photo.url = ''
                        photo.save()
                        msg = 'Фото '+'['+str(photo.pk)+'] ' + str(url) +' видалено'
                        json = simplejson.dumps({'status': True, 'msg': msg})
                        return HttpResponse(json, content_type='application/json')
                    
                except:
                    json = simplejson.dumps({'status': False, 'msg': u'Ajax: Photo get ERRROR'})
                    return HttpResponse(json, content_type='application/json')
    json = simplejson.dumps({'status': False, 'msg': u'Ajax: Щось пішло не так'})
    return HttpResponse(json, content_type='application/json')



def photo_list(request, show=2, page=1, limit=50, cat_id=None):
    list = None
    show = int(show)
#    print "PARAM id = " + str(show) + " Page = " + str(page)
    limit = int(limit)
    page = int(page)
    lim_a = (page * limit) - limit
    lim_b = page * limit 
     
    if show == 0: # Show all
        if page > 0:
            list = Photo.objects.exclude(catalog = None)[lim_a:lim_b]
        if page == 9999:
            list = Photo.objects.exclude(catalog = None).order_by('-date')[:limit]
        if page == 0:                
            list = Photo.objects.exclude(catalog = None)
        #list = Photo.objects.filter(catalog = None)
        text = "Show all record who join Catalog "
    if show == 1: # New record with Catalog connect
        if page > 0:
            list = Photo.objects.exclude((Q(www = '') | Q (www = None)) & Q(catalog = None))[lim_a:lim_b]
        if page == 9999:
            list = Photo.objects.exclude((Q(www = '') | Q (www = None)) & Q(catalog = None)).order_by('-date')[:limit]
    if show == 2: # New record with Catalog connect
        if page > 0:                
            list = Photo.objects.exclude( (Q(www = '') | Q (www = None)) )[lim_a:lim_b]
        if page == 9999:
            list = Photo.objects.exclude( (Q(www = '') | Q (www = None)) ).order_by('-date')[:limit]
        text = "New record with Catalog connect"
    if show == 3: # Show all who catalog in None
        if page > 0:
            list = Photo.objects.filter(catalog = None)[lim_a:lim_b]
        if page == 9999:
            list = Photo.objects.filter(catalog = None).order_by('-date')[:limit]
        text = "Show all who catalog in None"                                     
    if show == 4: # Show all who have URL field
        if page > 0:        
            list = Photo.objects.exclude( (Q(url = '') | Q (catalog = None)) )[lim_a:lim_b]
        if page == 9999:
            list = Photo.objects.exclude( (Q(url = '') | Q (catalog = None)) ).order_by('-date')[:limit]
        text = "Show all who have URL field empty"
    if show == 5: # Show catalog
        cat = Catalog.objects.get(id = cat_id)
        list = Photo.objects.filter(catalog = cat)
        #list = Photo.objects.filter(catalog = None)
        text = "Show all record who join Catalog - " + str(cat)

#    list = Photo.objects.filter((Q(www = '') | Q (www = None)) & Q(catalog = None)).values('user', 'date', 'url', 'catalog__name', 'catalog__id', 'catalog__ids', 'user__username', 'id', 'bicycle__model', 'bicycle', 'local', 'www').order_by('-date')
    for iphoto in list:
        psts = change_photo_url(iphoto)
#        print "[" + str(iphoto.pk) + "] - "+ str(psts) 
    context = {'weblink': 'photo_list.html', 'list': list, 'text': text, }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)


@csrf_exempt
def photo_url_delete(request, id=None):
    if auth_group(request.user, 'seller')==False:
        return HttpResponseRedirect('/catalog/photo/list/')
    obj = None
    if (id <> None):
        try:        
            obj = Photo.objects.get(pk = id)
            obj.delete()
        except:
            return HttpResponse("Дане фото вже видалене спробуйте інший ID")#, content_type="text/plain;charset=UTF-8;")
    try:
        if request.is_ajax():
            if request.method == 'POST':  
                POST = request.POST  
                if POST.has_key('id'):
                    wid = request.POST.get( 'id' )
            obj = Photo.objects.get(id = wid)
            del_logging(obj)
            obj.delete()
            return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")
        else: 
            obj = Photo.objects.get(id = id)
    except:
        pass

    return HttpResponseRedirect('/catalog/photo/list/')
    
@csrf_exempt
def catalog_set_type(request):
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має прав для редагування')
    q = request.POST.get('category_id')
    cid = request.POST.get('id')
    POST = request.POST
    if POST.has_key('ids'):
        cids = request.POST.get('ids')
        list_id = cids.split(',')
        t_catalog = Catalog.objects.filter(id__in = list_id) #.values_list('type__name')
        t_catalog.update(type = Type.objects.get(id = q))
        return HttpResponse('ok')
        #t_catalog.save()
    if POST.has_key('id'):
        t_catalog = Catalog.objects.get(id = cid) #.values_list('type__name')
        t_catalog.type = Type.objects.get(id = q) 
        t_catalog.save()
    cat = Catalog.objects.filter(id = cid).values('type__name', 'type__id')
    return HttpResponse(simplejson.dumps(list(cat)), content_type="application/json")
#    return HttpResponse(cat[0][0], content_type="text/plain;charset=UTF-8;")

@csrf_exempt
def bicycle_price_set(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'admin')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id') and POST.has_key('price'):
                id = request.POST.get('id')
                p = request.POST.get('price')
#                bike = Bicycle_Store.objects.get(id = id)
                
                obj = Bicycle.objects.get(id = id)
                obj.price = p
                obj.save() 

                c = Bicycle.objects.filter(id = id).values_list('price', flat=True)
                return HttpResponse(c)
    

            if POST.has_key('id') and POST.has_key('sale'):
                id = request.POST.get('id')
                p = request.POST.get('sale')
                obj = Bicycle.objects.get(id = id)
                obj.sale = p
                obj.save() 
                c = Bicycle.objects.filter(id = id).values_list('sale', flat=True)
                return HttpResponse(c)

@csrf_exempt
def boxname_search(request):
    if not request.user.is_authenticated():
        context = {'weblink': 'error_message.html', 'mtext': 'Авторизуйтесь щоб виконати дану функцію', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    ret_res = None
    POST = request.POST
    if request.method == 'POST':
        if POST.has_key('locality'):
            search = request.POST.get('locality')
            boxes = BoxName.objects.filter(Q(name__icontains = search) | Q(description__icontains = search))
            #ret_res = storage_boxes_list(request, boxname = search)
            ret_res = storage_boxes_list(request, boxes = boxes)
    #context = {"weblink": 'storage_box.html', }
#    context = {'weblink': 'error_message.html', 'mtext': 'Функція працює', }    
#    context.update(custom_proc(request))
#    return render(request, "index.html", context)
    return ret_res


# -------- old function ----------
def storage_box_list_old(request, boxname=None, pprint=False):
    if boxname:
        list = Catalog.objects.filter(locality = boxname)
    else:
        #list = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').order_by('locality')
        list = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').values('locality').annotate(icount = Count('locality')).order_by('locality')
        #boxlist = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').values('locality').annotate(icount=Count('locality')).order_by('locality')
    if pprint:
        return render(request, 'storage_box.html', {'boxes': list, 'pprint': True})
    cur_year = datetime.date.today().year
    context = {"weblink": 'storage_box.html', "boxes": list, 'pprint': False, 'cur_year': cur_year}
    context.update(custom_proc(request))
    return render(request, "index.html", context)


@csrf_exempt
def storagebox_edit(request, id=None):
    sb_description = None
    sb_last_count =None
    sb_real_count = None
    sb_last_count = None
    sb_count = None
    response_data = {}
    status = "Помилка"

    if not auth_group(request.user, 'admin'):
        response_data['description'] = "Авторизуйтесь щоб виконати дану функцію. Для виконання вам потрібна роль Адміністратора"
        return JsonResponse(response_data)
        
    
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('sbox_id'):
                sb_id = request.POST.get( 'sbox_id' )
            if POST.has_key('count'):
                sb_count = request.POST.get( 'count' )
            if POST.has_key('real_count'):
                sb_real_count = request.POST.get( 'real_count' )
            if POST.has_key('last_count'):
                sb_last_count = request.POST.get( 'last_count' )
            if POST.has_key('description'):
                sb_description = request.POST.get( 'description' )
                
    if sb_id:
        try:
            obj = StorageBox.objects.get(id=sb_id)
        except:
            response_data['description'] = "Сталась помилка. Такого запису не існує або щось пішло не так."
            return JsonResponse(response_data)

        dnow = datetime.datetime.now()
        diff_count = int(obj.count) - int(sb_count)
        diff_real = int(obj.count_real) - int(sb_real_count)
        diff_last = int(obj.count_last) - int(sb_last_count)
        hist_str = "[ %s ] COUNT changed: %s -> %s; Real COUNT: %s -> %s; Last COUNT: %s -> %s; DIFF: (%s; %s; %s) by user [%s]" % (str(dnow) , str(obj.count), str(sb_count), str(obj.count_real), str(sb_real_count), str(obj.count_last), str(sb_last_count), str(diff_count), str(diff_real), str(diff_last), str(request.user))  
        obj.count = sb_count
        obj.count_real = sb_real_count
        obj.count_last = sb_last_count
        obj.description = sb_description
        obj.date_update = dnow
        obj.user_update = request.user
        if obj.history:
            obj.history += hist_str.decode('utf-8') + "\n" #+ inv_str.decode('utf-8')
        else: 
            obj.history = hist_str.decode('utf-8') + "\n" #+ inv_str.decode('utf-8')
        obj.save()
        status = "Виконано"
        if diff_count != 0:
            response_data['count'] = obj.count
        elif diff_real != 0:
            response_data['real_count'] = obj.count_real
        elif diff_last != 0:
            response_data['last_count'] = obj.count_last
        response_data['description'] = hist_str
        response_data['status'] = status
        return JsonResponse(response_data)

    return HttpResponse("Запит оброблено без результату", content_type="text/plain;charset=UTF-8;")


@csrf_exempt
def storage_box_delete(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                bid = request.POST.get( 'id' )
    if bid:
        id = bid
    obj = StorageBox.objects.get(id=id)
    obj.delete()
    return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")
    #return HttpResponseRedirect('/workshop/view/')


def storage_box_delete_all(request, all=False):
    if all == True:
        obj = Catalog.objects.exclude(locality__exact='').update(locality='')
    else:
        obj = Catalog.objects.filter(count__lte = 0).update(locality='')
    
    return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")

#------------- Old function
@csrf_exempt
def storage_box_rename(request):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('old_name') and POST.has_key('new_name'):
                box_name = request.POST.get( 'old_name' )
                new_name = request.POST.get( 'new_name' )
                obj = Catalog.objects.filter(locality = box_name).update(locality=new_name)
#                obj.locality = ''
#                obj.save()
    return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")


def storage_boxes(request):
    boxlist = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').values('locality').annotate(icount=Count('locality')).order_by('locality')
    context = {"weblink": 'storage_boxes.html', "boxes": boxlist}
    context.update(custom_proc(request))
    return render(request, "index.html", context)    

@csrf_exempt
def storage_box_add(request):
    if not request.user.is_authenticated():
        context = {'weblink': 'error_message.html', 'mtext': 'Авторизуйтесь щоб виконати дану функцію', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)

    a = BoxName()
    userid = request.user
    shopid = get_shop_from_ip(request.META['REMOTE_ADDR'])
    if request.method == 'POST':
        form = BoxNameForm(request.POST)#, request = request)        
        if form.is_valid():
            name = form.cleaned_data['name']
            shop = form.cleaned_data['shop']
            user = form.cleaned_data['user']
            description = form.cleaned_data['description']
            mark_delete = form.cleaned_data['mark_delete']
            Nbox = BoxName(name=name, shop = shop, user=user, description=description, mark_delete=mark_delete)
            Nbox.save()
                            
            return HttpResponseRedirect( reverse('storage-boxes-list', ) )
    else:
        form = BoxNameForm(initial={'user': userid, 'shop': shopid})#, request = request)        
    context = {"weblink": 'storage_box_add.html', 'form': form, 'add_form': True}
    context.update(custom_proc(request))
    return render(request, "index.html", context)  


@csrf_exempt
def storage_box_edit(request, id):
    if not request.user.is_authenticated():
        context = {'weblink': 'error_message.html', 'mtext': 'Авторизуйтесь щоб виконати дану функцію', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)
    a = BoxName.objects.get(pk=id)
    if request.method == 'POST':
#        form = BicycleStorage_Form(request.POST, request.FILES, instance=a)
        form = BoxNameEditForm(request.POST, instance=a) #, request = request)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect( reverse('storage-boxes-list', ) )
    else:
        form = BoxNameEditForm(instance=a)#, request = request)
    context = {"weblink": 'storage_box_add.html', 'form': form, 'box_id': id}
    context.update(custom_proc(request))
    return render(request, "index.html", context)  


def storage_boxes_list(request, id=None, boxname=None, boxes=None):
    shopList = Shop.objects.filter(show = True)
    boxlist = None
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
#    shopN = get_shop_from_ip('192.168.1.1')
    if id:
        boxlist = BoxName.objects.filter(shop = id)
        shopN = Shop.objects.get(pk = id)
    if boxname:
        boxlist = BoxName.objects.filter(name__icontains = boxname)
    if not boxname and not id and not boxes:
        boxlist = BoxName.objects.filter(shop = shopN)
    if boxes:
        boxlist = boxes
        #boxlist = BoxName.objects.all()
    bname_list  = []
    try:
        tmp = ".".join(boxlist[0].name.split(".")[0:2])
        for boxn in boxlist.order_by("name"):
            btmp = ".".join(boxn.name.split(".")[0:2])
            if btmp != tmp:
                bname_list.append(btmp)
                tmp = btmp
    except:
        pass
    context = {"weblink": 'storage_boxes_list.html', "boxes": boxlist, 'shop_list': shopList, 's_shop_id': shopN, "bname_list": bname_list}
    context.update(custom_proc(request))
    return render(request, "index.html", context)  


def storage_box_list(request, id=None):
    shopList = Shop.objects.filter(show = True)
    boxname = BoxName.objects.get(pk = id)
    boxlist = None
    bs_stat = None
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    if id:
        boxlist = StorageBox.objects.filter(box_name = id, )
        bs_stat = False
    else:
        #boxlist = StorageBox.objects.filter(shop = shopN)
        boxlist = BoxName.objects.all()
        bs_stat = True
     
    context = {"weblink": 'storage_box_list.html', "box_list": boxlist, 'shop_list': shopList, 's_shop_id': shopN, 'boxname': boxname, 'box_or_storage': bs_stat}
    context.update(custom_proc(request))
    return render(request, "index.html", context)  


def storage_box_list_by_catalog(request, id):
    boxlist = StorageBox.objects.filter(catalog = id)
    boxname = BoxName.objects.filter(id__in = boxlist.values('box_name'))
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    cat_status = True
    cat_sel = Catalog.objects.get(id = id)
    context = {'weblink': 'storage_box_list.html', 'box_list': boxlist, 's_shop_id': shopN, 'boxname': boxname, 'catalog_boxes': cat_status, 'cat_sel': cat_sel}
    context.update(custom_proc(request))
    return render(request, "index.html", context)  


@csrf_exempt
def inventory_edit(request, id):
    if not auth_group(request.user, 'admin'):
        context = {'weblink': 'error_message.html', 'mtext': 'Авторизуйтесь щоб виконати дану функцію', }
        context.update(custom_proc(request))
        return render(request, 'index.html', context)

    a = InventoryList.objects.get(pk=id)
    if request.method == 'POST':
        form = InventoryListForm(request.POST, instance=a) 
        if form.is_valid():
            form.save()
            return HttpResponseRedirect( reverse('inventory-list', ) )
    else:
        form = InventoryListForm(instance=a)
    context = {"weblink": 'inventory.html', 'form': form, 'catalog': a.catalog}
    context.update(custom_proc(request))
    return render(request, "index.html", context)  


def inventory_list(request, shop_id=None, year=None, month=None, day=None):
    s_year = year
    s_month = month
    s_day = day
    list = None
    shopId = None
    day_list = None
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    shopList = Shop.objects.all()
    if (year == None):
        s_year = datetime.datetime.now().year
    else:
        s_year = year
    list = InventoryList.objects.filter(date__year = s_year)
    if (month != None):
        list = list.filter(date__month = month)
        day_list = InventoryList.objects.filter(date__year = s_year, date__month = month).extra({'day':"Extract(day from date)"}).values_list('day').annotate(Count('id')).order_by('day')        
    if (day != None):
        list = list.filter(date__day = day)
    if (year == None) and (month == None) and (day == None):
        s_month = datetime.datetime.now().month
        s_day = datetime.datetime.now().day
        list = list.filter(date__month = s_month, date__day = s_day)
        day_list = InventoryList.objects.filter(date__year = s_year, date__month = s_month).extra({'day':"Extract(day from date)"}).values_list('day').annotate(Count('id')).order_by('day')
        print "Shop LIST = %s " % shop_id
    if shop_id == None:
        shop_id = shopN
        shopId = shopList
    else:
        shopId = Shop.objects.filter(id = shop_id)
    #list = list.filter(date__month = s_month, date__day = s_day, shop__in = shopId)
    list = list.filter(shop__in = shopId)
    year_list = InventoryList.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
    month_list = InventoryList.objects.filter(date__year = s_year).extra({'month':"Extract(month from date)"}).values_list('month').annotate(Count('id')).order_by('month')
    context = {"weblink": 'inventory_list.html', "return_list": list, "year_list": year_list, 'month_list': month_list, 'day_list': day_list, 'sel_day': s_day, 'sel_month': s_month, 'sel_year': s_year, 'sel_shop': shop_id, 'shop_list': shopList}
    context.update(custom_proc(request))
    return render(request, "index.html", context)


def inventory_by_catalog_id(request, cat_id):
    c_id = None
    try:
        c_id = Catalog.objects.get(pk = cat_id)
        inv_list = InventoryList.objects.filter(catalog = c_id).order_by('-date')
        boxes = inv_list[0].get_all_boxes()
    except:
        res_str = u"Обліку для товару %s: %s не знайдено" % (cat_id, c_id)
        context = {'weblink': 'error_message.html', 'mtext': res_str}
        context.update(custom_proc(request))         
        return render(request, 'index.html', context)        
    
    
    context = {"weblink": 'inventory_by_catalog.html', "catalog": c_id, "inv_list": inv_list, 'boxes': boxes}
    context.update(custom_proc(request))    
    return render(request, 'index.html', context)


def inventory_catalog_type(request, type_id):
    type_obj = Type.objects.get(pk = type_id)
#    cat_list = Catalog.objects.filter(type = type_obj, count__gt = 0)
    all_cat = Catalog.objects.filter(type = type_obj) #, count__lte = 0)
    cat_ids = []
    for i in all_cat:
        box_sum_count = i.get_storage_box_sum_by_count()['sum_count']
        if (box_sum_count > 0) :
            cat_ids.append(i.pk)
        if ((box_sum_count == 0) or (not box_sum_count)) and (i.count > 0) :
            cat_ids.append(i.pk)
    cat_list = Catalog.objects.filter(pk__in = cat_ids).order_by("manufacturer")
           
    context = {"weblink": 'inventory_by_type.html', "catalog_list": cat_list, 'cattype': type_obj} #, "inv_list": inv_list, 'boxes': boxes}
    context.update(custom_proc(request))    
    return render(request, 'index.html', context)
    

def inventory_catalog_manufacturer(request, m_id):
    m_obj = Manufacturer.objects.get(pk = m_id)
    all_cat = Catalog.objects.filter(manufacturer = m_obj) #, count__lte = 0)
    cat_ids = []
    for i in all_cat:
        box_sum_count = i.get_storage_box_sum_by_count()['sum_count']
        if (box_sum_count > 0) :
            cat_ids.append(i.pk)
        if ((box_sum_count == 0) or (not box_sum_count)) and (i.count > 0) :
            cat_ids.append(i.pk)
    cat_list = Catalog.objects.filter(pk__in = cat_ids).order_by("type")
    
#    cat_list = Catalog.objects.filter(manufacturer = m_obj, count__gt = 0)    
    context = {"weblink": 'inventory_by_type.html', "catalog_list": cat_list, 'manufacturer': m_obj} 
    context.update(custom_proc(request))    
    return render(request, 'index.html', context)



def inventory_mistake(request, year=None, month=None, day=None):
    #im = InventoryList.objects.filter(check_all = True).annotate(dcount=Max('date')).order_by('date')
    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    #im = InventoryList.objects.filter(check_all = True, date__gt = year_ago).annotate(mdate=Max('date', distinct=True)).order_by('catalog__manufacturer', 'catalog__id').values('id', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'mdate', 'edit_date')
#    im = InventoryList.objects.filter(Q(date__gt = year_ago), ( (Q(real_count = F('count')) & Q(check_all = False)) | (Q(real_count__gt = F('count')) & Q(check_all = True)) | (Q(real_count__lt = F('count')) & Q(check_all = True)) )).annotate(mdate=Max('date', distinct=True)).order_by('-check_all', 'catalog__manufacturer', 'catalog__id').values('id', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'mdate', 'edit_date')
    im = InventoryList.objects.filter(Q(date__gt = year_ago), ( (Q(real_count__lt = F('count')) & Q(check_all = False)) | (Q(real_count__gt = F('count')) & Q(check_all = True)) | (Q(real_count__lt = F('count')) & Q(check_all = True)) )).order_by('-check_all', 'catalog__manufacturer', 'catalog__id')
    #list = im.filter(Q(real_count__lt = F('count')) | Q(real_count__gt = F('count')))#.values('id', 'catalog', )
    #list = im.exclude( Q(real_count = F('count')) & Q(check_all = True) ) 
    #list = im.exclude( check_all = True, real_count__gt = F('count'), real_count__lt = F('count'))
    list = im 
    #list = InventoryList.objects.filter(check_all = True, real_count__lt = F('count'))
    #return render_to_response("index.html", {"weblink": 'inventory_mistake_list.html', "return_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))
    year = datetime.date.today().year
    day_list = []
    title = "Помилки у підрахунках"
    year_list = InventoryList.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
    month_list = InventoryList.objects.filter(date__year = year).extra({'month':"Extract(month from date)"}).values_list('month').annotate(Count('id')).order_by('month')
    context = {"weblink": 'inventory_list.html', "return_list": list, "year_list": year_list, 'month_list': month_list, 'day_list': day_list, 'cur_year': year, 'cur_month': month, 'title_text': title}
    context.update(custom_proc(request))
    return render(request, "index.html", context)


def inventory_autocheck(request, year=None, month=None, day=None, update=False):
    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    im = InventoryList.objects.filter( Q(date__gt = year_ago), ((Q(real_count = F('count')) & Q(check_all = False))) ).annotate(mdate=Max('date', distinct=True)).order_by('catalog__id')
    if update == True:
        im.update(check_all=True)
    list = im.values('id', 'catalog__name', 'catalog__ids', 'catalog__id', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'edit_date')
    return render_to_response("index.html", {"weblink": 'inventory_mistake_list.html', "return_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))


def inventory_mistake_not_all(request, year=None, month=None, day=None):
    all_cat = Catalog.objects.filter(count__gt = 0)
    cat_ids = []
    for i in all_cat:
        box_sum_count = i.get_storage_box_sum_by_count()['sum_count']
        if (box_sum_count == 0) or (not box_sum_count) :
            cat_ids.append(i.pk)
            
    im = InventoryList.objects.filter(catalog__in = cat_ids)    
    
    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    exc_list =  InventoryList.objects.filter( Q(date__gt = year_ago) ) #, (Q(real_count = F('count')) & Q(check_all = True)) )
    #im = InventoryList.objects.filter(Q(date__gt = year_ago), ( (Q(real_count__gt = F('count')) & Q(check_all = False)) | (Q(real_count__lt = F('count')) & Q(check_all = False)) )).order_by('-check_all', 'catalog__manufacturer', 'catalog__id')
#    im = InventoryList.objects.filter(Q(date__gt = year_ago) & Q(real_count__lt = F('count')))        
    #list = im.exclude(catalog__id__in=[term.catalog.id for term in exc_list])
   
    list = im
    cat_count = all_cat.count()
    #list_count = im.count
    list_count = len(cat_ids)
    title = "Помилки у підрахунках (товари в яких не має місця)"
    paginator = Paginator(list, 100)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        inv_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        inv_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        inv_list = paginator.page(paginator.num_pages)
    year = datetime.date.today().year
    day_list = []
    year_list = InventoryList.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
    month_list = InventoryList.objects.filter(date__year = year).extra({'month':"Extract(month from date)"}).values_list('month').annotate(Count('id')).order_by('month')
    context = {"weblink": 'inventory_list.html', "return_list": inv_list, "year_list": year_list, 'month_list': month_list, 'day_list': day_list, 'cur_year': year, 'cur_month': month, 'title_text': title, 'list_count': list_count, 'cat_count': cat_count}
    context.update(custom_proc(request))
    return render(request, "index.html", context)


def inventory_mistake_not_found(request, year=None, month=None, day=None):
    all_cat = Catalog.objects.filter(count__gt = 0)
    cat_ids = []
    for i in all_cat:
        box_sum_count = i.get_storage_box_sum_by_count()['sum_count']
        if (box_sum_count == 0) or (not box_sum_count) :
#            print "BOX count = %s" % box_sum_count
            cat_ids.append(i.pk)

    cat_list = Catalog.objects.filter(pk__in = cat_ids).order_by('manufacturer')#[:100]

    paginator = Paginator(cat_list, 50)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        cat_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        cat_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        cat_list = paginator.page(paginator.num_pages)



    cat_count = all_cat.count()
    list_count = len(cat_ids)
    title = "Товари у яких не має місця"
    context = {"weblink": 'inventory_mistake_list.html', "cat_list": cat_list, 'title_text': title, 'list_count': list_count, 'cat_count': cat_count}
    context.update(custom_proc(request))
    return render(request, "index.html", context)


def inventory_search(request):
    res_str = "some Error"
    #context = {'weblink': 'error_message.html', 'mtext': res_str}
    context = {'weblink': 'inventory_search.html', 'mtext': res_str}
    context.update(custom_proc(request))         
    return render(request, 'index.html', context)        


def inventory_fix_catalog(request, cat_id=None, inv_id=None, update=False):
    if not request.user :
        print "User = " + str(request.user)
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))    
    cur_year = datetime.date.today().year
#    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    cfix = Catalog.objects.get(id = cat_id)
    realCount = cfix.get_realshop_count()
    ifix = InventoryList.objects.filter(catalog = cfix, date__year = cur_year)
    isum = ifix.filter(check_all = False, real_count = realCount).aggregate(csum = Sum('count'))
    maxDate = ifix.filter(check_all = False, real_count = realCount).aggregate(mdate = Max('date'))
    gt_max = None
    if maxDate['mdate']:
        gt_max = ifix.filter(date__gt = maxDate['mdate'])
        print "FILTER MAX = " + str(gt_max.exists())
        if gt_max.exists():
            print "Існує новий запис після підрахунку"
        if (gt_max.exists() == False and realCount == isum['csum']):
            print "REsult = Create new inventory record. Count = " + str(realCount)
            desc = 'AutoCreate_' + str(cur_year)
            new_inv = InventoryList(catalog = cfix, count = realCount, description = desc, user = request.user, real_count = realCount, check_all = True).save()
            return HttpResponse('Товар: ' + str(cfix) + '\nЗакрито повністю. Кількість - ' + str(realCount) + ' штук', content_type="text/plain;charset=UTF-8;;" )            
    #isum = ifix.aggregate(Count('pk'), csum = Sum('count'))
    print "Max date = " + str(maxDate['mdate'])
    print "REAL count = " + str(realCount)
    for i in ifix:
        print "inventory = " + str(i) + " status = " + str(i.check_all) + " PORTAL = " + str(i.real_count)
    print "Isum = " + str(isum['csum'])
    
    if realCount != isum['csum']:
        print "Real count not equal COUNT"
    res_str = 'Товар: ' + str(cfix) + '<br>Помилка закриття. Перевірте цей товар вручну.'
    
    context = {'weblink': 'error_message.html', 'mtext': res_str}
    context.update(custom_proc(request))         
    return render(request, 'index.html', context)        
    #return HttpResponse('Fix element = ' + str(cfix) + '\nПомилка закриття. Перевірте цей товар вручну.', content_type="text/plain;charset=UTF-8;;" )


def inventory_fix_catalog1(request, cat_id=None, inv_id=None, type_id=None, update=False):
    cur_year = datetime.date.today().year
    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    exc_list =  InventoryList.objects.filter( Q(date__year = cur_year), (Q(real_count = F('count')) & Q(check_all = True)) )
    im = InventoryList.objects.filter(Q(date__year = cur_year), ( (Q(real_count__gt = F('count')) & Q(check_all = False)) | (Q(real_count__lt = F('count')) & Q(check_all = False)) )).annotate(mdate=Max('date', distinct=True)).order_by('-check_all', 'catalog__manufacturer', 'catalog__id')    
    list = im.exclude(catalog__id__in=[term.catalog.id for term in exc_list])
#    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
#    list = list.values('id', 'catalog__name', 'catalog__ids', 'catalog__id', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'edit_date')
#    return render_to_response("index.html", {"weblink": 'inventory_mistake_list.html', "return_list": list[:100]}, context_instance=RequestContext(request, processors=[custom_proc]))
    cfix_list = None
    if type_id:
        seltype = Type.objects.get(id = type_id)
        cfix_list = Catalog.objects.filter(id__in = list.values('catalog__id'), type = seltype)#[:100]
    else:
        cfix_list = Catalog.objects.filter(id__in = list.values('catalog__id'))#[:100]
    fixed_list = []
    fixed_ilist = []
    for cfix in cfix_list:
        realCount = cfix.get_realshop_count()
        ifix = InventoryList.objects.filter(catalog = cfix, date__year = cur_year)
        isum = ifix.filter(check_all = False, real_count = realCount).aggregate(csum = Sum('count'))
        maxDate = ifix.filter(check_all = False, real_count = realCount).aggregate(mdate = Max('date'))
        gt_max = None
        if maxDate['mdate']:
            gt_max = ifix.filter(date__gt = maxDate['mdate'])
            print "FILTER MAX = " + str(gt_max.exists())
            if gt_max.exists():
                print "Skip this item. Have old record"
            if (gt_max.exists() == False and realCount == isum['csum']):
                print "REsult = Create new inventory record. Count = " + str(realCount)
                desc = 'AutoCreate_' + str(cur_year)
                new_inv = InventoryList(catalog = cfix, count = realCount, description = desc, user = request.user, real_count = realCount, check_all = True).save()
                fixed_list.append(cfix)
                fixed_ilist.append(new_inv)
#                return HttpResponse('Товар: ' + str(cfix) + '\nЗакрито повністю. Кількість - ' + str(realCount) + ' штук', content_type="text/plain;charset=UTF-8;;charset=UTF-8" )            
        if realCount != isum['csum']:
            print "Real count not equal COUNT"
    return HttpResponse('Fixed elements = ' + str(fixed_list) + "\n Inventory save = " + str(fixed_ilist), content_type="text/plain;charset=UTF-8;;" )


def inventory_fix(request, year=None, month=None, day=None, update=False):
    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    im = InventoryList.objects.filter( Q(date__gt = year_ago), (((Q(real_count__gt = F('count')) | Q(real_count__lt = F('count'))) & Q(check_all = True))) ).annotate(mdate=Max('date', distinct=True)).order_by('catalog__id')
    if update == True:
        im.update(check_all=True)
    list = im
    year = datetime.date.today().year
    day_list = []
    year_list = InventoryList.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
    month_list = InventoryList.objects.filter(date__year = year).extra({'month':"Extract(month from date)"}).values_list('month').annotate(Count('id')).order_by('month')
#    list = im.values('id', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'edit_date')
#    return render_to_response("index.html", {"weblink": 'inventory_mistake_list.html', "return_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))
    context = {"weblink": 'inventory_list.html', "return_list": list, "year_list": year_list, 'month_list': month_list, 'day_list': day_list, 'cur_year': year, 'cur_month': month}
    context.update(custom_proc(request))
    return render(request, "index.html", context)

@csrf_exempt
def inventory_add(request):
    inv = None
    balance = 0
    if request.is_ajax():
        if request.method == 'POST':  
            
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id') and POST.has_key('desc') and POST.has_key('count') and POST.has_key('status'):
                pid = request.POST.get('id')
                count = request.POST.get('count')
                desc = request.POST.get('desc')
                status = request.POST.get('status')
                if status == 'false':
                    status = False
                else :
                    status = True

                if desc == '':
                    #search = "Введіть текст опису"
                    jsonDict = {"status": "error", "message": "Вевведіть текст повідомлення!"}
                    return HttpResponse(simplejson.dumps(jsonDict), content_type="aplication/json")
                    #return HttpResponse(search, content_type="text/plain;charset=UTF-8;")
                c = Catalog.objects.get(id = pid)
                
                try:
                    list = InvoiceComponentList.objects.filter(catalog=pid).values('catalog__count', 'catalog__ids')
                    list = list.annotate(sum_catalog=Sum('count'))
                except:
                    list = InvoiceComponentList.objects.none()        
                try:
                    sale_list = ClientInvoice.objects.filter(catalog=pid).values('catalog', 'catalog__price').annotate(sum_catalog=Sum('count'))
                    balance = list[0]['sum_catalog'] - sale_list[0]['sum_catalog']
                except:
                    balance = list[0]['sum_catalog'] - 0
                    
                c.count = balance
                c.save()
                inv = InventoryList(catalog = c, count = count, date = datetime.datetime.now(), user = request.user, description=desc, edit_date = datetime.datetime.now(), check_all = status, real_count=c.count)
                inv.save()
            #rdict = QueryDict(request.body)
            #sel_id = rdict.keys()#[0]
            req_dict = json.loads(request.body)
            if req_dict: 
                if (req_dict.has_key('id') and req_dict.has_key('box_id') and req_dict.has_key('count') and req_dict.has_key('status')) :
                    pid = req_dict['id']
                    count = req_dict['count']
                    box_id = req_dict['box_id']
                    status = req_dict['status']
                    dnow = datetime.datetime.now()
                    user = request.user
                    desc = ''
                    if int(count) <= 0:
#                        print "\n>>> We are the POST request - JSON [COUNT] =  %s <<<<\n" % count
#                        jsonDict = {"status": "error", "message": "Введіть кількість більшу за нуль!"}
#                        return HttpResponse(simplejson.dumps(jsonDict), content_type="aplication/json")
                        res = "Введіть кількість більшу за нуль!"
                        context = { 'status': '400', 'reason': res }
                        response = HttpResponse(json.dumps(context), content_type='application/json')
                        response.status_code = 400
                        return response
                               
                    if box_id == '':
                        jsonDict = {"status": "error", "message": "Виберіть місцезнаходження даного товару!"}
                        return HttpResponse(simplejson.dumps(jsonDict), content_type="aplication/json")           
                    c = Catalog.objects.get(id = pid)
                    b = BoxName.objects.get(id = box_id)
                    shop = get_shop_from_ip(request.META['REMOTE_ADDR'])
 #                   print "\n BOX = %s; catalog = %s\n" % (b.id, c.id)
                    inv = InventoryList(catalog = c, count = count, box_id = b, date = datetime.datetime.now(), user = user, description=desc, edit_date = dnow, check_all = status, real_count=c.get_realshop_count(), shop=shop)
                    inv.save()
                    inv_str = "[%s] Inventory id = %s; count = %s in %s" % (dnow, inv.id, inv.count, inv.real_count) 
                    if not StorageBox.objects.filter(catalog = c, box_name = b):
                        sb = StorageBox(catalog = c, box_name = b, count = count, count_real = c.get_realshop_count(), count_last = 0, shop = shop, date_create = dnow, date_update=dnow, user = user, description=desc)
                        sb.save()
                    else:
                        hist_str = ""
                        sb_list = StorageBox.objects.filter(catalog = c, box_name = b)
                        sb = StorageBox.objects.get(pk = sb_list[0].id)
  #                      print "\nSTORAGE box catalog = " + str(sb[0])
                        count_last = sb.count
                        sb.count = sb.count + int(count)
                        sb.count_real = c.get_realshop_count()
                        sb.date_create = dnow # date create 
                        sb.date_update = dnow
                        if sb.shop != shop:
                            hist_str = hist_str + "["+ str(dnow) + "] Shop changed - " + str(sb.shop) + " -> " + str(shop) + " by user [" + str(user) + "]"  
                        sb.shop = shop
                        sb.user_update = user
                        if sb.history == None:
                            sb.history = ""
                        sb.history = sb.history +  hist_str.decode('utf-8') + "\n" + inv_str.decode('utf-8')
                        sb.save()
    jsonDict = {"status": "done", "message": "Запит виконано", "id": inv.id, "count": inv.count, "description": inv.description, "user__username": inv.user.username, "check_all":inv.check_all, "real_count":inv.real_count} #, "date": inv.date.strftime("%d/%m/%Y [%H:%M]")
    jsonDict.update(sb_boxname = str(sb.box_name))
    jsonDict.update(sb_count = sb.count)
    jsonDict.update(count_add = count)
#    return HttpResponse(simplejson.dumps(jsonDict), content_type="aplication/json")
  #  jsonDict = {"status": "done", "message": "OK!"}
    return HttpResponse(simplejson.dumps(jsonDict), content_type='application/json')
    #return HttpResponse(search, content_type="text/plain;charset=UTF-8;")

@csrf_exempt
def inventory_get(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для перегляду', content_type="text/plain;charset=UTF-8;;")
            POST = request.POST  
            if POST.has_key('catalog_id'):
                cid = request.POST['catalog_id']
                i_list = InventoryList.objects.filter(catalog = cid).values('id', 'count', 'description', 'user', 'user__username', 'date', 'check_all', 'real_count', 'catalog__name', 'catalog__ids', 'box_id__pk', 'box_id__name', 'shop__name', 'edit_date')
                json = list(i_list)
                for x in json:
                    x['date_year'] = x['date'].strftime("%Y")  
                    x['date'] = x['date'].strftime("%d/%m/%Y [%H:%M]")
                    if x['edit_date']:
                        x['edit_date'] = x['edit_date'].strftime("%d/%m/%Y [%H:%M]")
                #json = serializers.serialize('json', p_cred_month, fields=('id', 'date', 'price', 'description', 'user', 'user_username'))
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    return HttpResponse(data_c, content_type='application/json')        

@csrf_exempt
def inventory_get_listid(request):
    date_before = datetime.datetime.today() - datetime.timedelta(days=180)
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                message = 'Error: У вас не має прав для перегляду' #, content_type="text/plain;charset=UTF-8;")
                return HttpResponse(message)
            POST = request.POST  
            if POST.has_key('catalog_ids'):
                cid = request.POST['catalog_ids']
                cid1 = simplejson.loads(cid)
                i_list = InventoryList.objects.filter(catalog__in = cid1, date__gt = date_before, check_all = True).values('id', 'catalog__id', 'count', 'description', 'user', 'user__username', 'date', 'real_count')
                json = list(i_list)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y [%H:%M]")
                #json = serializers.serialize('json', p_cred_month, fields=('id', 'date', 'price', 'description', 'user', 'user_username'))
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    return HttpResponse(i_list, content_type='application/json')        


def inventory_get_count(request):
    sel_id = None
    if request.method == 'POST':
        sel_id = request.POST.get('sel_id')
    list = InventoryList.objects.get(id=sel_id)
    if (list.user != request.user):
        if (auth_group(request.user, 'admin') == False):
            return HttpResponse('Error: У вас не достатньо повноважень для редагування', content_type="text/plain;charset=UTF-8;;")
    return HttpResponse(unicode(list.count), content_type="text/plain;charset=UTF-8;;")

@csrf_exempt
def inventory_set(request):
    if request.is_ajax():
        if request.method == 'POST':
            result = ''  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування', content_type="text/plain;charset=UTF-8;")
            POST = request.POST  
            if POST.has_key('id'):
                id = request.POST['id']
                i_list = InventoryList.objects.get(id = id)
                if POST.has_key('status'):
                    i_list.check_all = not(i_list.check_all)
                    i_list.edit_date = datetime.datetime.now()
                    if i_list.check_all: 
                        result = "Повністю" 
                    else:
                        result = "Частково"
                if POST.has_key('count'):
                    i_list.count = request.POST['count']
                    result = i_list.count 
                if (request.user != i_list.user):
                    if auth_group(request.user, 'admin')==False:
                        return HttpResponse('Error: У вас не має прав для редагування', content_type="text/plain;charset=UTF-8;")
                i_list.save()
                return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
    return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")
    #return HttpResponse(data_c, content_type='application/json')        

@csrf_exempt    
def inventory_delete(request, id=None):
    obj = None
    wid = None
    try:
        if request.is_ajax():
            if request.method == 'POST':  
                POST = request.POST  
                if POST.has_key('id'):
                    wid = request.POST.get( 'id' )
            obj = InventoryList.objects.get(id = wid)
#            print "User = " + str(obj.user) + " - " + str(request.user == obj.user) + " / " + str(auth_group(request.user, 'admin') == False)
            if (request.user != obj.user):
                if (auth_group(request.user, 'admin') == False):
                    return HttpResponse('У вас не вистачає повноважень', status=401, content_type="text/plain;charset=UTF-8;")
            del_logging(obj)
            obj.delete()
            return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")
        else: 
            obj = InventoryList.objects.get(id = id)
    except:
        pass
#    del_logging(obj)
#    bj.delete()
    return HttpResponseRedirect('/inventory/list/')

@csrf_exempt
def catalog_join(request,id1=None, id2=None, ids=None):
    if auth_group(request.user, 'admin')==False:
        #return HttpResponseRedirect('/')
        return HttpResponse('Error: У вас не має прав для обєднання')
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має прав для обєднання')
    if (id1 == id2) and (id1 != None):
        return HttpResponse('Не можливо обєднати товар')
    
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id'):
                id1 = request.POST['id']
            else:
                result = "Введіть ID товару для обєднання"
                return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
            if POST.has_key('id2'):
                id2 = request.POST['id2']
            if POST.has_key('ids'):
                ids = request.POST['ids'].split(',')
                try:
                    ids.remove(id1)
                except:
                    result = "Введіть правильний ID товару для обєднання"
                    return HttpResponse(result, content_type="text/plain;charset=UTF-8;;")

            for i in ids:
                inv = InventoryList.objects.filter(catalog = i).update(catalog=id1)
                InvoiceComponentList.objects.filter(catalog = i).update(catalog = id1)
                ClientInvoice.objects.filter(catalog = i).update(catalog = id1)
                ClientOrder.objects.filter(catalog = i).update(catalog = id1)
                Rent.objects.filter(catalog = i).update(catalog = id1)
                ShopPrice.objects.filter(catalog = i).update(catalog = id1)
                ClientReturn.objects.filter(catalog = i).update(catalog = id1)
                obj_del = Catalog.objects.get(id = i)
                #obj_del.delete()
            result = "ok"
            return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
    
    c1 = Catalog.objects.get(id=id1)
    c2 = Catalog.objects.get(id=id2)
    inv = InventoryList.objects.filter(catalog = id2).update(catalog=id1)
    InvoiceComponentList.objects.filter(catalog = id2).update(catalog = id1)
    ClientInvoice.objects.filter(catalog = id2).update(catalog = id1)
    ClientOrder.objects.filter(catalog = id2).update(catalog = id1)
    Rent.objects.filter(catalog = id2).update(catalog = id1)
    ShopPrice.objects.filter(catalog = id2).update(catalog = id1)
    ClientReturn.objects.filter(catalog = id2).update(catalog = id1)
    
    return HttpResponseRedirect('/invoice/search/result/?name=&id='+c1.ids)


@csrf_exempt
def catalog_sale_edit(request, ids=None):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'admin')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            #if POST.has_key('ids'):
            if POST.has_key('ids') and POST.has_key('sale'):                
                ids = request.POST['ids'].split(',')
                s = request.POST.get('sale')
            if s == '':
                result = "невірні параметри"
                return HttpResponse(result, content_type="text/plain;charset=UTF-8;;")
#                result = "Введіть правильний ID товару для обєднання"
#                return HttpResponse(result, content_type="text/plain;charset=UTF-8;;charset=UTF-8")
            for i in ids:
                obj = Catalog.objects.get(id = i)                                
                obj.sale = s
                obj.last_update = datetime.datetime.now()
                obj.user_update = request.user
                obj.save() 
                #obj_del.delete()
            result = "ok"
            return HttpResponse(result, content_type="text/plain;charset=UTF-8;;")


def catalog_upload_photos(request):
    if auth_group(request.user, 'admin')==False:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))
    #directory = 'd:/velo/portal_photo/upload'
    directory = settings.MEDIA_ROOT + 'upload/photo/'
    #directory_done = 'd:/velo/portal_photo/done'
    directory_done = settings.MEDIA_ROOT + 'download/'    
    files = os.listdir(directory)
    f_list = []
    file_names = []
    file_not_exists = []
    d_f = []
    double_f = []
    
    for f in files:
        sp = []
        double_f = re.split(r'\(\s*\d+\s*\)', f)
        if len(double_f) > 1:
            sp = double_f
        d_f = re.split(r'_+\.', f)
        if len(d_f) > 1:
            sp = d_f 
        if sp == []:
            sp = f.split('.')
#        print "File name = " + str(f)
#        print "SP = " + str(sp)
        exe = sp[1]
        filename = sp[0]
        catalog = Catalog.objects.filter( Q(dealer_code = filename) | Q(ids = filename) )
#        print filename + " - Catalog = " + str(catalog)
        if catalog.exists():
            f_list.append({"filename": f, "exe": exe})
            file_names.append(filename)
            #old_file = directory + '/' + f
            old_file = directory  + f
            s_name = catalog[0].manufacturer.name
            new_folder = s_name.strip().replace(' ', '-').lower()
            if not os.path.exists(directory_done + new_folder):
                os.makedirs(directory_done + new_folder)
            #new_file = directory_done + new_folder + '/' + filename.lower() + '.' + exe                
            new_file = directory_done + new_folder + '/' + f.lower()
#            print "new file = " + new_file
            try:
                os.rename( old_file, new_file )
                if os.path.isfile(new_file):
                    media_dir = new_file.replace(settings.MEDIA_ROOT, '/media/')
                    addphoto = Photo(local = media_dir, date = datetime.datetime.now(), user = request.user, description="")
                    addphoto.save()
                    catalog[0].photo_url.add(addphoto)
            except:
                im1 = Image.open(old_file)
                im2 = Image.open(new_file)
                if im1 == im2:
                    os.remove(old_file)
                im1.close()
                im2.close()
        else:
            file_not_exists.append({"filename": filename, "exe": exe})
            
    cat_list1 = Catalog.objects.filter(Q(ids__in = file_names))
    cat_list2 = Catalog.objects.filter(Q(dealer_code__in = file_names))
    cat_list = cat_list1 
#    print "COUNT1 = " + str(cat_list1.count())
#    print "COUNT2 = " + str(cat_list2.count())
#    print "COUNT = " + str(cat_list.count())
    return render_to_response("index.html", {"weblink": 'catalog_file_upload_photos.html', 'file_list': f_list, 'cat_list': cat_list, 'not_found_files': file_not_exists}, context_instance=RequestContext(request, processors=[custom_proc]))    

@csrf_exempt
def client_invoice_add(request, ids=None):
    shopN = get_shop_from_ip(request.META['REMOTE_ADDR'])
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('ids') and POST.has_key('count'):                
                ids = request.POST['ids'].split(',')
                count = request.POST.get('count')
                if count == '':
                    result = "невірні параметри"
                    return HttpResponse(result, content_type="text/plain;charset=UTF-8;;")
                client = Client.objects.get(id=138)
                for i in ids:
                    c_obj = Catalog.objects.get(id = i)
                    ClientInvoice(client=client, catalog = c_obj, count=count, price=c_obj.price, sum=c_obj.price*int(count), currency=c_obj.currency, sale=c_obj.sale, pay=0, user=request.user, date=datetime.datetime.now(), shop=shopN).save()
                result = "ok"
                return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
            
    data_res = None                
    # JSON Read and Parse
    if request.method == "POST":
        rdict = QueryDict(request.body)
        sel_id = rdict.keys()#[0]
        req_dict = json.loads(request.body)
        if req_dict.has_key('id') and req_dict.has_key('client_id') and req_dict.has_key('count'):
            res = ''
            dres = {}
            dres['f_model'] = None
            cat_pk = int(req_dict['id'])
            value = req_dict['count']
            client_pk = req_dict['client_id']
            cat = Catalog.objects.get(id = cat_pk)
            client = Client.objects.get(id = client_pk)
            if int(value) > cat.get_realshop_count():
                res = u"Дана кількість [%s] більша ніж є товару в магазині [%s]" % (value, cat.get_realshop_count())
                dres['msg'] = res
                dres['status'] = True
            else:
                sum = cat.price * int(value)
                obj = ClientInvoice(client=client, date=datetime.datetime.today(), price=cat.price, sum=sum, sale=int(cat.sale), pay=0, count=int(value), currency=Currency.objects.get(id=3), catalog=cat, user = request.user, shop=shopN)
                obj.save()
                obj.update_sale()
#                dres['url'] = reverse("catalog_edit", kwargs={"id": self.pk}) #'/catalog/edit/' + str(self.pk) 
                dres['status'] = False
                dres['f_model'] = ClientInvoice.objects.filter(pk = obj.pk)
#                print "\n CAT = " + str(dres['f_model'][0].catalog.pk) + "\n"
                pk_cat = dres['f_model'][0].catalog.pk
                dres['f_catalog'] = Catalog.objects.get(pk = pk_cat).json_barcode() 
                if dres['f_model']:
                    dres['f_model'] = serializers.serialize('json', dres['f_model'])
                    #dres['f_catalog'] = serializers.serialize('json', dres['f_catalog'])
#                dres['f_model'] = json.dumps(dres['f_model'], )
            #data = json.dumps(res, skipkeys=True)
            data = simplejson.dumps(dres)
            data_res = data
    return HttpResponse(data_res, content_type='application/json')    
                

@csrf_exempt
def client_invoice_get_boxes(request):
    if request.is_ajax():
        if request.method == 'POST':
            if auth_group(request.user, 'seller') == False:
                print "Error USER - Seller"
                result = 'Error: У вас не має прав для внесення змін'
                return HttpResponse(result, content_type='application/json')
            
            POST = request.POST  
            if POST.has_key('cat_id') and POST.has_key('ci_id'):
                ids = request.POST['cat_id']
                ci_id = request.POST['ci_id']
                c_inv = ClientInvoice.objects.get(id = ci_id)
                catalog = Catalog.objects.get(id = ids)
                if c_inv.pay == c_inv.sum:
                    res = "Товар [" + str(c_inv.id) + "]" + str(c_inv.catalog) + " вже продано і йому не можна додати/змінити місце!"
                    context = { 'status': '400', 'reason': res }
                    response = HttpResponse(json.dumps(context), content_type='application/json')
                    response.status_code = 400
                    return response
                boxes = catalog.get_storage_box()
                a_box = []
                for sbox in boxes:
                    a_box.append({'name': sbox.get_storage_boxes_name(), 'id': sbox.id, 'count': sbox.count})
#                    a_box.append({'name': sbox.get_storage_name(), 'id': sbox.id, 'count': sbox.count })
                result = simplejson.dumps({'status': True, 'boxes': a_box})
                return HttpResponse(result, content_type='application/json')
            if POST.has_key('cat_id_only'):
                ids = request.POST['cat_id_only']
                catalog = Catalog.objects.get(id = ids)
                boxes = catalog.get_storage_box()
                a_box = []
                for sbox in boxes:
                    a_box.append({'name': sbox.get_storage_boxes_name(), 'id': sbox.id, 'count': sbox.count, })
                result = simplejson.dumps({'status': True, 'boxes': a_box})
                return HttpResponse(result, content_type='application/json')
            else:
                res = 'Помилка запиту. Параметр не знайдено!'
                context = { 'status': '400', 'reason': res }
                response = HttpResponse(json.dumps(context), content_type='application/json')
                response.status_code = 400
                return response            
        else:
            result = 'Помилка запиту'
            print "Error AJAX request"
            #return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
            return HttpResponse(result, content_type='application/json')
    else:
        result = 'Помилка запиту. Its not AJAX request'
        return HttpResponse(result, content_type='application/json')    
        
        
@csrf_exempt
def client_invoice_add_boxes(request):
    if request.is_ajax():
        if request.method == 'POST':
            if auth_group(request.user, 'seller') == False:
                print "Error USER - Seller"
                result = 'Error: У вас не має прав для внесення змін'
                return HttpResponse(result, content_type='application/json')
            
            POST = request.POST  
            if POST.has_key('ci_id') and POST.has_key('boxes'):
                ci_id = request.POST['ci_id']
                boxes = request.POST['boxes']
                c_inv = ClientInvoice.objects.get(id = ci_id)
                if c_inv.check_payment():
                    res = "Товар [" + str(c_inv.id) + "]" + str(c_inv.catalog) + " вже продано і йому не можна додати/змінити місце!"
                    context = { 'status': '400', 'reason': res }
                    response = HttpResponse(json.dumps(context), content_type='application/json')
                    response.status_code = 400
                    return response
                box_dct = json.loads(boxes)
                count_sum = 0 
#                print "BOXES = %s" % boxes
                for i in box_dct:
                    print "Box id = %s | COUNT = %s" % (i['boxid'], i['count'])
                    count_sum = count_sum + int(i['count'])

                if count_sum > c_inv.count:
                    res = "Ви вибрали більше товару ніж хочете продати! \n(Вибрано %s шт. - Продаєте %s шт.)" % (count_sum, int(c_inv.count))
                    #result = simplejson.dumps(res)
                    context = { 'status': '400', 'reason': res }
                    response = HttpResponse(json.dumps(context), content_type='application/json')
                    #response = HttpResponse(simplejson.dumps(context), content_type='application/json')
                    response.status_code = 400
                    return response
                
                now = datetime.datetime.now()
                index = 0
                user = request.user
                for box in box_dct: #sbox_ids:
                    sb_count = 0
                    sbox = StorageBox.objects.get(pk = box['boxid'])
                    sb_count = int(box['count']) #sbox_count[index]
                    print "SB COUNT = %s" % sb_count
                    if sb_count > 0:
                        obj_cisb = sbox.get_ci_sb_by_cinv(c_inv)
                        if obj_cisb:  
                            for i in obj_cisb: 
                                i.set_count(sb_count, now, user)
                        else:
                            ClientInvoiceStorageBox(sbox=sbox, cinvoice=c_inv, count=sb_count, date_create=now, user_create=user).save()
                    if sb_count == 0:
                        obj_cisb = sbox.get_ci_sb_by_cinv(c_inv)
                        if obj_cisb:  
                            for i in obj_cisb: 
                                i.delete()
                    index+=1
                #boxes = c_inv.catalog.get_storage_box()
                a_box = []
                for sbox in c_inv.get_ci_sbox():
                    a_box.append({ 'name': sbox, 'id': c_inv.id, 'count': c_inv.count })
#                    a_box.append({'name': sbox.get_storage_name(), 'id': sbox.id, 'count': sbox.count })
                result = simplejson.dumps({'ci_id': c_inv.id, 'status': True, 'boxes': a_box})
                #result = 'ok - ' + c_inv.catalog.name 
                return HttpResponse(result, content_type='application/json')
                #return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
            else:
                result = 'Помилка запиту. Параметри не знайдені!'
                return HttpResponse(result, content_type='application/json')
        else:
            result = 'Помилка запиту'
            print "Error AJAX request"
            #return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
            return HttpResponse(result, content_type='application/json')
    else:
        result = 'Помилка запиту. Its not AJAX request'
        return HttpResponse(result, content_type='application/json')    

        
def check_list(request, year=None, month=None, day=None, all=False, client=None):
    list = None
    listPay = None
    day = day
    month = month
    year = year
    if (year == None) and (month == None) and (day == None):
        day = datetime.datetime.now().day
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        
    if all == True:
        if (month == None):
            list = Check.objects.filter(date__year = year)
            listPay = CheckPay.objects.filter(date__year = year)
        if (day == None and month):
            list = Check.objects.filter(date__year = year, date__month = month)
            listPay = CheckPay.objects.filter(date__year = year, date__month = month)
        if (year == None):
            list = Check.objects.all()
            listPay = CheckPay.objects.all()
        if (client <> None):
            client_id = Client.objects.get(id = client)
            list = Check.objects.filter(client = client_id)
            list_ids = list.values('checkPay')
            print "\n LIST IDS : " + str(dir(list_ids))
            listPay = CheckPay.objects.filter(pk__in = list_ids)
    else:
        list = Check.objects.filter(date__year = year, date__month = month, date__day = day)#.values()
        listPay = CheckPay.objects.filter(date__year = year, date__month = month, date__day = day)
    
    sum_term = 0
    sum_cash = 0
    for lp in listPay :
        sum_term = sum_term + lp.term
        sum_cash = sum_cash + lp.cash
        print "\n CHECK : " + str(dir(lp))
    
    chk_sum = 0
    chk_sum_term = 0
    for i in list:
        if i.catalog != None:
            if i.cash_type.id == 1:
                chk_sum = chk_sum + ((100-i.discount)*0.01*i.catalog.catalog.price*i.count)
            else:
                chk_sum_term = chk_sum_term + ((100-i.discount)*0.01*i.catalog.catalog.price*i.count)
        if i.bicycle != None:
            if i.cash_type.id == 1:
                chk_sum = chk_sum + ((100-i.discount)*0.01*i.bicycle.price*i.count)
            else:
                chk_sum_term = chk_sum_term + ((100-i.discount)*0.01*i.bicycle.price*i.count)                
        if i.workshop != None :
            if i.cash_type.id == 1:
                chk_sum = chk_sum + ((100-i.discount)*0.01*i.workshop.price*i.count)
            else:
                chk_sum_term = chk_sum_term + ((100-i.discount)*0.01*i.workshop.price*i.count)                
    if month == None:
        days = xrange(1, 1)
    else:            
        days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    context = {"weblink": 'check_list.html', "check_list": list, "sum_term":sum_term, "sum_cash":sum_cash, "pay_list": listPay, 'sel_day':day, 'sel_month':month, 'sel_year':year, 'month_days':days, 'chk_sum': chk_sum, 'chk_sum_term': chk_sum_term}
    context.update(custom_proc(request))
    return render(request, "index.html", context)


#************ Друк фіскального чеку на принтері ************** 
def check_print(request, num):
    list = None
    list = Check.objects.filter(check_num = num)
    print "\nLIST ID : " + str(list[0].id) + "\n"
    list_id = []
    chk_pay = []

    for id in list:
        try:
            list_id.append( int(id.catalog.id) )
            #list = None
        except:
            pass
        chk_pay.append(id.checkPay)
    
    ci = ClientInvoice.objects.filter(id__in=list_id)
#    client = ci[0].client
    client = list[0].client
#    sum = 555
    ci_sum = ci.aggregate(suma=Sum('sum'))
    sum = ci_sum['suma']
    if sum == None:
        try: 
            cash = list[0].checkPay.cash
            term = list[0].checkPay.term
            sum =  cash + term
        except:
            sum = 0 

    text = pytils_ua.numeral.in_words(int(sum))
#    month = pytils_ua.dt.ru_strftime(u"%d %B %Y", ci[0].date, inflected=True)
    month = pytils_ua.dt.ru_strftime(u"%d %B %Y", list[0].date, inflected=True)
    request.session['invoice_id'] = list_id
    request.session['chk_num'] = num
    check_num = num
    p_msg = "Роздрукований"
    context = {'check_invoice': ci, 'month': month, 'sum': sum, 'client': client, 'str_number': text, 'check_num': check_num, 'checkPay': chk_pay, 'chk_lst': list, 'weblink': 'client_invoice_sale_check.html', 'print': True, 'printed': p_msg, }
    context.update(custom_proc(request))    
    return render(request, 'index.html', context)
    
#    return render_to_response("index.html", {"weblink": 'check_list.html', "check_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))

def sale_post(token, ci=None, ws=None, cash_pay=0, card_pay=0):
    goods = []
    payments = []
    inv_list = None
    if ci == None:
         inv_list = ws
    if ws == None:
         inv_list = ci
    
    for inv in inv_list:
        ci_dic = {}
#        price =  "%.2f" % inv.price
        count = 1
        discount = 0
        code = ''
        name = ''
        barcode = ''
        if ci == None:
            count = 1
            discount = 0
            code = '99'+str(inv.work_type.pk)
            name = inv.work_type.name[:100] #.encode('cp1251')
            barcode = '' 
        if ws == None:
            count = inv.count
            discount = inv.sale
            code = str(inv.catalog.pk)
            name = inv.catalog.name[:40]
#            barcode = str(inv.catalog.ids)

        gkey = {
        "code": code,
        "name": name, #.encode('cp1251'),
        "barcode": barcode, # "1112222111",
        "excise_barcode": "",
#        "header": "HeaderString",
#        "footer": "FooterTitle",
        "price": str(int(inv.price*100)),#"12200",
        #"uktzed": ""
        } 
                        
        quantity =  count * 1000
        discounts =  [ {
            "type": "DISCOUNT",
            "mode": "PERCENT",
            "value": str(discount) }
        ]
        
        ci_dic.update({'good': gkey})
        if discount <> 0:
            ci_dic.update({'discounts': discounts})
        ci_dic.update({'is_return': 'false'})
        ci_dic.update({'quantity': str(int(quantity))})
        ci_dic.update({"is_winnings_payout": "true",})
        goods.append(ci_dic)
        
        cash_round = int(math.ceil(round(float(cash_pay), 1)*100))
        
        cash = {
        "type": "CASH",
        "value": str(cash_round),#int(float(cash_pay)*100)),
        }
        cashless = {
        "type": "CASHLESS",
        "value": str(int(round(float(card_pay)*100))), 
        "bank_name": "PrivatBank",
        "terminal": "Verifone",
        "acquirer_and_seller": "s1r006k7",
        #"receipt_no": "BANK_no"
        }

    round_status = "false"        
    if cash_pay <> '0':
        payments.append(cash)
        round_status = "true"
        
    if card_pay <> '0':
        payments.append(cashless)
   
     
    url = "https://api.checkbox.ua/api/v1/receipts/sell"
    data_work = {
    "cashier_name": "RiveloName",
    "departament": "RiveloShop",
    "goods":  goods,
    "delivery": {
    },
#    "discounts": [],
    "bonuses": [],
    "payments": payments,      
    "rounding": round_status,
    "header": "Вас вітає веломагазин-майстерня Rivelo!",
    "footer": "До зустрічі на дорогах і стежках України.",
    "stock_code": "string_Bottom",
    "technical_return": "false",
    "context": {
        "additionalProp1": "string_1",
        "additionalProp2": "string_2",
        "additionalProp3": "string_3"
    },
    "is_pawnshop": "false",
    "custom": {
        }
    
    }
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain', 
        'Authorization': token
        }  
    
    jsonString = json.dumps(data_work, indent=4)
    print "\nJSON : \n" + jsonString + "\n"
    
    r = requests.post(url, data=json.dumps(data_work), headers=headers)
    resp_str = json.dumps(r.json(), indent=4)
    print "CREATE Payment: " + resp_str + "\n"
    #print "Balance After: " + str(r.json()['shift']['balance']['balance']/100.0) + "\n"
    return r


def save_chek2db(cash, term, shop, request, ci=None, ws=None, desc=''):
    res = Check.objects.aggregate(max_count=Max('check_num'))
    chkPay = CheckPay(check_num = res['max_count'] + 1, cash = cash, term = term, description='checkbox_id='+desc+";")
    chkPay.user = request.user
    chkPay.save()

    inv_list = None
    cash_sum = 0
    if ci == None:
         inv_list = ws
    if ws == None:
         inv_list = ci
                    
    for inv in inv_list:
        check = Check(check_num=res['max_count'] + 1)
        check.checkPay = chkPay
        check.client = inv.client #Client.objects.get(id=client.id)
        if ci == None:
            check.workshop = inv
            check.count = 1
            check.discount = 0
            cash_sum = inv.price
        if ws == None:
            check.catalog = inv #ClientInvoice.objects.get(pk=inv)
            check.count = inv.count
            check.discount = inv.sale
            cash_sum = inv.sum
        
        if ((float(cash) > 0) and (float(term) > 0)):
            check.description = "Готівка / Термінал"
        if (cash == '0'):
            check.description = "Термінал"
        if (term == '0'):
            check.description = "Готівка"
                        
        t = 1
        if cash >= term:
            if shop == 1:
                t = 1
            if shop == 2:
                t = 10
            check.price = cash_sum #m_val
        else: 
            if shop == 1:
                t = 9 # PUMB = 9 / PB = 2
            if shop == 2:
                t = 2 # PUMB = 9 / PB = 2
            check.price = term 
        check.cash_type = CashType.objects.get(id = t)
        check.print_status = False
        check.user = request.user
        check.save()
    return            

@csrf_exempt
def shop_sale_check_add(request):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    message = ''
    list_id = request.session['invoice_id']
    count = None
    URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    cmd = 'open_port;1;115200;'
    PARAMS = {'address':URL, 'cmd': cmd, 
              'hash': settings.MINI_HASH_1, 
              'user': request.user.username,
             }
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('m_value'):
                m_val = request.POST.get( 'm_value' )
                t_val = request.POST.get( 't_value' )
                term_number =  request.POST.get( 'term' )
                    
                ci = ClientInvoice.objects.filter(id__in = list_id)
                chk_list = Check.objects.filter(catalog__in = ci)
                if chk_list.count() > 0:
                    message = "Даний чек вже існує"
                    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
                #CheckBox casa
                if term_number == '2':
                    token = post_casa_token()
                    resp = sale_post(token, ci=ci, cash_pay = m_val, card_pay = t_val)
                    if resp.status_code == 201:
#                        print "\nSTATUS RESPONCE - " + str(resp.status_code) + "\n"
                        save_chek2db(m_val, t_val, 2, request, ci=ci, desc=str(resp.json()['id']))
                        message = "" + str(resp.json()['id'])
                    else:
                        message = "CHECKBOX - Error\n" + str(resp.text.encode('utf-8'))
                    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")

                try:
                    resp_open = requests.post(url = URL, data = PARAMS)
                    PARAMS['cmd'] = "cashier_registration;1;0"
                    resp_registration = requests.post(url = URL, data = PARAMS)
                    PARAMS['cmd'] = 'open_receipt;0' # відкрити чек
                    resp_registration = requests.post(url = URL, data = PARAMS)
                except:
                    message = "Сервер "+settings.HTTP_MINI_SERVER_IP+" не відповідає"
                    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")

                save_chek2db(m_val, t_val, 1, request, ci=ci)

                for inv in ci:
                    price =  "%.2f" % inv.price
                    count = "%.3f" % inv.count
                    discount = inv.sale
                    if inv.catalog.length <> None:
                        PARAMS['cmd'] = 'add_plu;'+str(inv.catalog.pk)+";0;1;0;1;1;1;"+price+";0;"+inv.catalog.name[:40].encode('cp1251')+";"+count+";"
                        resp = requests.post(url = URL, data = PARAMS)
                    else:
                        PARAMS['cmd'] = 'add_plu;'+str(inv.catalog.pk)+";0;0;0;1;1;1;"+price+";0;"+inv.catalog.name[:40].encode('cp1251')+";"+count+";"
                        resp = requests.post(url = URL, data = PARAMS)
                    PARAMS['cmd'] = 'sale_plu;0;0;0;'+count+";"+str(inv.catalog.pk)+";"
                    resp = requests.post(url = URL, data = PARAMS)
                    PARAMS['cmd'] = 'discount_surcharge;1;0;1;'+"%.2f" % discount+";"
                    resp = requests.post(url = URL, data = PARAMS)
                    #PARAMS['cmd'] = 'cancel_receipt;'
                    #resp = requests.post(url = URL, data = PARAMS)
                        
                if m_val >= t_val:
                    if float(t_val) == 0:
                        PARAMS['cmd'] = "pay;"+"0;0;"
                        resp = requests.post(url = URL, data = PARAMS)
                    else:
                        PARAMS['cmd'] = "pay;0;"+"%.2f" % float(m_val)+";"
                        resp = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = "pay;2;"+"%.2f" % float(t_val)+";"
                        print "PARAM = " + PARAMS['cmd']
                        resp = requests.post(url = URL, data = PARAMS)
                else:
                    if float(m_val) == 0:
                        PARAMS['cmd'] = "pay;"+"2;0;"
                        resp = requests.post(url = URL, data = PARAMS)
                    else:
                        PARAMS['cmd'] = "pay;2;"+"%.2f" % float(t_val)+";"
                        resp = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = "pay;0;"+"%.2f" % float(m_val)+";"
                        resp = requests.post(url = URL, data = PARAMS)   
                    
                PARAMS['cmd'] = 'close_port;'
                resp_close = requests.post(url = URL, data = PARAMS)

        message = "Виконано"
        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
    else:
        message = "Error. Post is not Ajax!"
        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")

@csrf_exempt
def workshop_sale_check_add(request):
    if request.user.is_authenticated()==False:
        return HttpResponse("Для виконання операції, авторизуйтесь")
    message = ''
    list_id = request.session['invoice_id']
#    print ("\nSession >>> "  + str(list_id) + "\n") 
    count = None
    URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    cmd = 'open_port;1;115200;'
    PARAMS = {'address':URL, 'cmd': cmd, 
              'hash': settings.MINI_HASH_1, 
              'user': request.user.username,
              }
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('m_value'):
                m_val = request.POST.get( 'm_value' )
                t_val = request.POST.get( 't_value' )
                term_number =  request.POST.get( 'term' )
                   
                cw = WorkShop.objects.filter(id__in = list_id)
                chk_list = Check.objects.filter(workshop__in = cw)
                if chk_list.count() > 0:
                    message = "Даний чек вже існує"
                #CheckBoX casa
                if term_number == '2':
                    token = post_casa_token()
                    resp = sale_post(token, ws = cw, cash_pay = m_val, card_pay = t_val)
                    if resp.status_code == 201:
#                        print "\nSTATUS RESPONCE - " + str(resp.status_code) + "\n"
                        save_chek2db(m_val, t_val, 2, request, ws = cw, desc=str(resp.json()['id']))
                        message = "" + str(resp.json()['id'])
                    else:
                        message = "CHECKBOX - Error\n" + str(resp.text.encode('utf-8'))
                    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
                    
                else:
                    try:
                        #page = urllib.urlopen(url).read()
                        resp_open = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = "cashier_registration;1;0"
                        resp_registration = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = 'open_receipt;0' # відкрити чек
                        resp_registration = requests.post(url = URL, data = PARAMS)
                    except:
                        message = "Сервер не відповідає"
                        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
#                    save_chek2db(m_val, t_val, 2, request, ws = cw, desc=str(resp.json()['id']))
                    for inv in cw:
                        price =  "%.2f" % inv.price
                        count = "%.3f" % 1
#                        data =  {"cmd": "add_plu", "id":'99'+str(inv.work_type.pk), "cname":inv.work_type.name[:40].encode('utf8'), "price":price, "count": count, "discount": 0}
                        PARAMS['cmd'] = 'add_plu;'+'99'+str(inv.work_type.pk)+";0;0;0;1;1;1;"+price+";0;"+inv.work_type.name[:40].encode('cp1251')+";"+count+";"
                        resp = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = 'sale_plu;0;0;0;'+count+";"+'99'+str(inv.work_type.pk)+";"
                        resp = requests.post(url = URL, data = PARAMS)
                        
                    if m_val >= t_val:
                        if float(t_val) == 0:
                            PARAMS['cmd'] = "pay;"+"0;0;"
                            resp = requests.post(url = URL, data = PARAMS)

                        else:
                            PARAMS['cmd'] = "pay;0;"+m_val+";"
                            resp = requests.post(url = URL, data = PARAMS)
                            PARAMS['cmd'] = "pay;2;"+t_val+";"
                            resp = requests.post(url = URL, data = PARAMS)

                    else:
                        if float(m_val) == 0:
                            PARAMS['cmd'] = "pay;"+"2;0;"
                            resp = requests.post(url = URL, data = PARAMS)

                        else:
                            PARAMS['cmd'] = "pay;2;"+t_val+";"
                            resp = requests.post(url = URL, data = PARAMS)
                            PARAMS['cmd'] = "pay;0;"+m_val+";"
                            resp = requests.post(url = URL, data = PARAMS)
                        
                    PARAMS['cmd'] = 'close_port;'
                    resp_close = requests.post(url = URL, data = PARAMS)
                    save_chek2db(m_val, t_val, 2, request, ws = cw, desc='Kavkazka')
                    
                message = "Виконано"
                return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
    else:
        message = "last Error - def workshop_sale_check_add"
        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")



def check_add(request):
    checkbox_list = [x for x in request.POST if x.startswith('chk_inv')]
    list_id = []
    ci = None
    cw = None
    res = Check.objects.aggregate(max_count=Max('check_num'))
    
    if request.POST.has_key('inv_type'):
        inv_t = request.POST.get( 'inv_type' )
    for id in checkbox_list:
        list_id.append( int(request.POST.get( id )))
    if inv_t == 'shop':
        ci = ClientInvoice.objects.filter(id__in=list_id)
        for inv in ci:
            check = Check(check_num=res['max_count'] + 1)
            check.client = inv.client #Client.objects.get(id=client.id)
            check.catalog = inv #ClientInvoice.objects.get(pk=inv)
            check.description = "Готівка"
            check.count = inv.count
            check.discount = inv.sale
            check.price = inv.price
            check.cash_type = CashType.objects.get(id = 1)
            check.print_status = False
            check.user = request.user
            check.save()    
    else:
        cw = WorkShop.objects.filter(id__in=list_id)
        for inv in cw:
            check = Check(check_num=res['max_count'] + 1)
            check.client = inv.client #Client.objects.get(id=client.id)
            check.workshop = inv #ClientInvoice.objects.get(pk=inv)
            check.description = "Готівка"
            check.count = 1
            check.discount = 0
            check.price = inv.price
            check.cash_type = CashType.objects.get(id = 1)
            check.print_status = False
            check.user = request.user
            check.save()    
        
    #return check_list(request, all=True)
    return HttpResponseRedirect('/check/list/now/')


def check_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має прав для редагування')
    obj = Check.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/check/list/now/')


def check_pay_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має прав для редагування')
    obj = CheckPay.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/check/list/now/')
    

def youtube_set(request):
    json = None
    error = None
    obj = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('youtube_id'):
                youtube_id = request.POST.get('youtube_id')
                obj = YouTube.objects.get(id = youtube_id)

                if POST.has_key('desc'):
                    desc = request.POST.get('desc')
                    obj.description = desc
                    obj.save()
                else:
                    error = "Сталась помилка"
    json = simplejson.dumps({'youtube': obj.description, 'error': error})

    return HttpResponse(json, content_type='application/json')
    

def youtube_url_get(request):
    json = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('youtube_id'):
                youtube_id = request.POST.get('youtube_id')
                obj = YouTube.objects.get(id = youtube_id)
                obj = obj.youtube_hash()
                try:
                    #json = simplejson.dumps({'aData': list(photo_list), 'id': cid, 'cname': c_name})
                    json = simplejson.dumps({'yData': obj, 'id': 'cid'})
                except:
                    error = 'Сталась помилка. Такого відео не знайдено'
                    json = simplejson.dumps({'yData': "None", 'error': error})

            if POST.has_key('catalog_id'):
                youtube_id = request.POST.get('catalog_id')
                obj = Catalog.objects.get(id = catalog_id)
                obj.youtube_url.all()
#                obj = obj.youtube_hash()
                try:
                    #json = simplejson.dumps({'aData': list(photo_list), 'id': cid, 'cname': c_name})
                    json = simplejson.dumps({'yData': obj, 'id': 'cid'})
                except:
                    error = 'Сталась помилка. Такого відео не знайдено'
                    json = simplejson.dumps({'yData': "None", 'error': error})

    return HttpResponse(json, content_type='application/json')
    

def youtube_list(request):
    tube = None
    list = YouTube.objects.all() #filter(count__gt=0).values('id', 'name', 'count', 'price')
    paginator = Paginator(list, 25)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        tube = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tube = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tube = paginator.page(paginator.num_pages)
        
    return render_to_response('index.html', {'tube_list': tube, 'weblink': 'youtube_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def youtube_delete(request, id):
    obj = YouTube.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return redirect('youtube_list')
    #return redirect('post_details', id=post_id)
    # equivalent to: return HttpResponseRedirect(reverse('post_details', args=(post_id, )))


def youtube_url_add(request, id=None):
    a = None
    add_tube = None
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            #if POST.has_key('ids'):
            if POST.has_key('id') and POST.has_key('upload_youtube'):                
                id = request.POST['id']
                url_youtube = request.POST['upload_youtube']
                d = {}
                if url_youtube :
                    try:
                        a = Bicycle.objects.get(pk = id)
                        y = YouTube.objects.get(url = url_youtube)
                        a.youtube_url.add(y)
                        a.save()
                        d['pk'] = y.pk
                        d['url'] = y.url
                        d['status'] = True
                        d['msg'] = 'Такий ролик вже існує.'
                        d['error'] = 'Такий ролик вже існує.'
#                        response = JsonResponse({'error': "Дане відео вже існує", 'pk': y.pk, 'url': u.url})
#                        return response
                    except YouTube.DoesNotExist:
                        add_tube = YouTube.objects.create(url = url_youtube, user = request.user)
                        a.youtube_url.add(add_tube)
                        a.save()
                        d['status'] = True
                        d['pk'] = add_tube.pk
                        d['url'] = add_tube.url
                        
                    except Bicycle.DoesNotExist:
                        d['status'] = False
                        d['error'] = "такого велосипеду не існує"
                        
                    except YouTube.MultipleObjectsReturned:
                        d['status'] = False
                        d['error'] = "Таких роликів є більше ніж один. Видаліть дублікати."

            if POST.has_key('c_id') and POST.has_key('upload_youtube'):
                id = request.POST['c_id']
                url_youtube = request.POST['upload_youtube']
                d = {}
                if url_youtube :
                    try:
                        a = Catalog.objects.get(pk = id)
                        y = YouTube.objects.get(url = url_youtube)
                        a.youtube_url.add(y)
                        a.save()
                        d['pk'] = y.pk
                        d['url'] = y.url
                        d['status'] = True
                        d['msg'] = 'Такий ролик вже існує.'
                        d['error'] = 'Такий ролик вже існує.'

                    except YouTube.DoesNotExist:
                        add_tube = YouTube.objects.create(url = url_youtube, user = request.user)
                        a.youtube_url.add(add_tube)
                        a.save()
                        d['status'] = True
                        d['pk'] = add_tube.pk
                        d['url'] = add_tube.url
                        
                    except Catalog.DoesNotExist:
                        d['status'] = False
                        d['error'] = "такого товару не існує"
                        
                    except YouTube.MultipleObjectsReturned:
                        d['status'] = False
                        d['error'] = "Таких роликів є більше ніж один. Видаліть дублікати."
            if not POST.has_key('c_id') and not POST.has_key('id'):
                response = JsonResponse({'error': "Невірні параметри запиту"})
                return response
            
            response = JsonResponse(d)
            return response

@csrf_exempt
def discount_add(request):
    if auth_group(request.user, 'seller')==True:
    #if request.user.is_authenticated():
        user = request.user
    else:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))

    a = Discount()
    name = ''
    if request.method == 'POST':
        form = DiscountForm(request.POST, instance = a)
        #form = RentForm(request.POST)
        POST = request.POST
        
        if form.is_valid():
#            print "POST = " + form.cleaned_data['name']
#            if POST.has_key('name'):
#                name = request.POST['name']
#            else:
#            name = form.cleaned_data['name']
            ds = form.cleaned_data['date_start']
            de = form.cleaned_data['date_end']
            type = form.cleaned_data['type_id']
            manufacture = form.cleaned_data['manufacture_id']
            #conv_ds = datetime.datetime.strptime(ds, '%d-%m-%Y').date()
            #conv_de = datetime.datetime.strptime(de, '%d-%m-%Y').date()
            f = form.save(commit=False)
            f.date_start = ds
            f.date_end = de
            f.type_id = int(type or 0)
            f.manufacture_id = int(manufacture or 0)
            #f.name = "Black Friday"
#            f.name = name
            f.save()
            
            return HttpResponseRedirect('/discount/list/')
    else:
        form = DiscountForm(instance = a)
    context = {'form': form, 'weblink': 'discount.html'}
    context.update(custom_proc(request))         
    return render(request, 'index.html', context)

@csrf_exempt
def discount_edit(request, id):
    if auth_group(request.user, 'seller')==True:
    #if request.user.is_authenticated():
        user = request.user
    else:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))

    a = Discount.objects.get(pk=id)
    name = ''

    if request.method == 'POST':
        form = DiscountForm(request.POST, instance = a)
        POST = request.POST
        
        if form.is_valid():
            ds = form.cleaned_data['date_start']
            de = form.cleaned_data['date_end']
            type = form.cleaned_data['type_id']
            manufacture = form.cleaned_data['manufacture_id']
            f = form.save(commit=False)
            f.date_start = ds
            f.date_end = de
            f.type_id = int(type or 0)
            f.manufacture_id = int(manufacture or 0)
            f.save()
            
            return HttpResponseRedirect('/discount/list/')
    else:
        form = DiscountForm(instance = a)
    context = {'form': form, 'weblink': 'discount.html', }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)
    

def discount_list(request, year = None):
    list = None
    if year == None:
        year = datetime.datetime.now().year
#    list = Discount.objects.all()#exclude( (Q(url = '') | Q (catalog = None)) )
    list = Discount.objects.filter(date_start__year = year).all()#exclude( (Q(url = '') | Q (catalog = None)) )
    context = {'weblink': 'discount_list.html', 'list': list, }
    context.update(custom_proc(request)) 
    return render(request, 'index.html', context)

@csrf_exempt
def discount_delete(request):
    d = {}
    if (auth_group(request.user, 'seller')==False) or (auth_group(request.user, 'admin')==False):
        d['status'] = False 
        d['msg'] = 'Ви не має достаттньо повноважень для даної функції'
        response = JsonResponse(d)
        return response                
    if request.is_ajax():
        if request.method == 'POST': 
            if request.POST.has_key('id'):
                id = request.POST['id']                
                obj = Discount.objects.get(pk = id)
                obj.delete()
                d['status'] = True
                d['msg'] = 'Done'
                response = JsonResponse(d)
                return response
            else:
                d['status'] = False
                d['msg'] = 'Парамтри не передано або вони невірні'
                response = JsonResponse(d)
                return response
    else:
        return HttpResponse('Error: Щось пішло не так під час запиту')     

@csrf_exempt
def discount_lookup(request):
    data = None
    cur_date = datetime.date.today()
    if request.is_ajax():
        if request.method == "POST":
            if request.POST.has_key(u'query'):
                value = request.POST[u'query']
                if len(value) > 2:
                    model_results = Discount.objects.filter(Q(name__icontains = value), Q(date_end__gt = cur_date) ).order_by('date_start', 'name')
                    data = serializers.serialize("json", model_results, fields = ('id', 'name', 'date_start', 'date_end'), )
#                else:
#                    model_results = Type.objects.all().order_by('name')
#                    data = serializers.serialize("json", model_results, fields = ('id', 'name_ukr', 'name'), use_natural_keys=False)                    
#                    data = []
    return HttpResponse(data)                 


def send_workshop_sound(request):
    base = "http://"+settings.HTTP_WORKSHOP_SERVER_IP+":"+settings.HTTP_WORKSHOP_SERVER_PORT+"/?"
    data =  {"cmd": "play_sound"} #, "id":'77', "cname":bike_s, "price":price, "count": count, "discount": discount}
    url = base + urllib.urlencode(data)
    page = urllib.urlopen(url).read()
    return HttpResponse("Повідомлення на склад відправлено")


def qrscanner(request):
    #current_url = request.get_full_path()
    #list = Country.objects.all()
    #return render_to_response('country_list.html', {'countries': list})
    return render_to_response('index.html', {'weblink': 'scanner_qr.html', 'next': current_url}, context_instance=RequestContext(request, processors=[custom_proc]))
    #return render_to_response('scanner_qr.html', {}, context_instance=RequestContext(request, processors=[custom_proc]))


def qrscanner2(request):
    return render_to_response('index.html', {'weblink': 'scanner_qr_nimiq.html', 'next': current_url}, context_instance=RequestContext(request, processors=[custom_proc]))


### ---------- RRO Casa Function --------------  

def licenseKey():
    xLicenseKey = settings.XLICENSEKEY
    return xLicenseKey

#def post_casa_token(xLicenseKey='test338c45d499f5fea8e7d02280', ):
def post_casa_token(xLicenseKey=licenseKey(), pin_code=settings.PIN_CODE):
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain', 
        'X-License-Key': xLicenseKey #'test338c45d499f5fea8e7d02280'
        }
    data = {"pin_code": pin_code}
    url = "https://api.checkbox.ua/api/v1/cashier/signinPinCode"
    try:
        r = requests.post(url, data=json.dumps(data), headers=headers)
        if r.status_code <> 200:
            return "Error: " + str(r)
    except: 
        return "Connection to server CHECKbox Error!"
    ttoken = r.json()['token_type']
    atoken = r.json()['access_token']
#    print "\n'Authorization' : '" + ttoken.title()+ " " + atoken +"'"
    return ttoken + ' ' + atoken


# X-Report on PRRO
def casa_prro_checkout(request): 
    resp = None
    token = post_casa_token()
    # sending post request and saving response as response object 
    try:
        url = "https://api.checkbox.in.ua/api/v1/reports"
        data = {}
        headers = {
            'Content-type': 'application/json', 
            'Accept': 'text/plain', 
            'Authorization': token
            }
        resp = requests.post(url, data=json.dumps(data), headers=headers)
    except:
        return HttpResponse("Connection failed! Перевірте зєднання з інтернетом")
    
    response = HttpResponse()
    response.write("Response: " + str(resp.status_code) + "<br>")
    if resp.status_code == 200:
        response.write("Status: <br>")
        res_list = str(resp.reason).split(';')
        response.write("JSON: <b>" + str(r.json()) + " </b><br>") 
        response.write("Готівка: <b>" + res_list[1] + " грн.</b><br>")
        response.write("Чек: <b>" + res_list[2] + " грн.</b><br>")
        response.write("Кредитна карта: <b>" + res_list[3] + "</b><br>")
        response.write("інший тип 1: <b>" + res_list[4] + "</b><br>")
        response.write("інший тип 2: <b>" + res_list[5] + "</b><br>")
        response.write("інший тип 3: <b>" + res_list[6] + "</b><br>")
        response.write("інший тип 4: - <b>" + res_list[7] + "</b><br>")

    json_res = resp.json()
    response.write("<br>Кількість чеків:  " + str(resp.json()['sell_receipts_count']) + "<br>")
    response.write("<br>Готівка в касі (сума для вилучення в копійках):  " + str(resp.json()['balance']) + "<br>")
    response.write("<br>Сума оплат (Готівка):  " + str(float(json_res['payments'][1]['sell_sum'])/100) + " грн.")
    response.write("<br>Сума оплат (Термінал):  " + str(float(json_res['payments'][0]['sell_sum'])/100) + " грн. <br>")
    response.write("<br><<< Result: >>> <br>" +str(resp.reason.encode('utf-8')) + "<br><<< Result text >>><br>" +  str(resp.text.encode('utf-8')))
    #jsonString = json.dumps(resp.json(), indent=4)
    jsonString = json.dumps(resp.json(), indent=4)
    print "\n JSON : " + str(jsonString)
    response.write("<br>JSON:" + str(jsonString.replace('\n', '<br />').encode('utf-8')))
    return response


def casa_prro_xreport(request, token=post_casa_token()):
    url = "https://api.checkbox.in.ua/api/v1/reports"
    data = {}
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain', 
        'Authorization': token
        }
    resp = requests.post(url, data=json.dumps(data), headers=headers)
    response = HttpResponse()
    print "\nRESP JSON =" + str(type(resp.json()))
    jsonString = json.dumps(resp.json(), indent=4)
    rr = resp.json() # responce JSON
    casa_status = None # responce for other request
    cashless_sell_sum = 0
    t_h3 = datetime.timedelta(hours=+3)
    res_start_dt = None
    error_msg = None
    if resp.status_code == 400:
        error_msg = rr['message'].encode('utf-8')
        print "Error MSG = " + error_msg 
    else:
        url = "https://api.checkbox.ua/api/v1/cashier/shift"
        data = ""
        headers = {
            'Content-type': 'application/json', 
            'Accept': 'text/plain', 
            'Authorization': token
        }  
        r = requests.get(url, data=json.dumps(data), headers=headers)
        casa_status = r.json()
    
    try:
        d_str_start = casa_status['opened_at']
        dt_start = datetime.datetime.strptime(d_str_start,"%Y-%m-%dT%H:%M:%S.%f+00:00")
        res_start_dt = dt_start  + t_h3
        for i in rr['payments']:
            if i['type'] == "CASHLESS":
                cashless_sell_sum = i["sell_sum"]
    except:
        pass

    format_json = jsonString.replace('\n', '<br />').encode('utf-8')
    day_cred=ClientCredits.objects.all().first()
#    term_sum_1 = day_cred.get_daily_term_shop1()[2]
    term_sum_2 = day_cred.get_daily_term_shop2()[2]
    term_sum_2 = (round((term_sum_2 or 0)*100) or 0)
    jbalance = 0
    try:
        jbalance = rr['balance']
    except:
        pass
        #error_msg = rr['message'].encode('utf-8')
        
    context = {'weblink': 'report_prro.html', 'JSON': rr, 'format_resp': format_json, 'day_term_sum': term_sum_2, 'error_status': error_msg, 'cashless_sum': cashless_sell_sum, 'res_start_dt': res_start_dt, 'casa_status': casa_status, 'JsonBalance': jbalance, 'shop': 2}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def casa_prro_zreport(request):
    resp = None
    token = post_casa_token()
    # sending post request and saving response as response object 
    try:
        url = "https://api.checkbox.ua/api/v1/shifts/close"
        data = {}
        headers = {
            'Content-type': 'application/json', 
            'Accept': 'text/plain', 
            'Authorization': token
            }
        resp = requests.post(url, data=json.dumps(data), headers=headers)
    except:
        return HttpResponse("Connection failed! Перевірте зєднання з інтернетом")
    
    response = HttpResponse()
    rr = resp.json()
    
    response.write("Response: " + str(resp.status_code) + "<br>")
    if resp.status_code == 202:
        response.write("Z-звіт виконанно успішно.<br>")
        response.write("<br><b><span>Готівка в касі: </span></b> " + str(rr["balance"]) + " грн.<br>")
        response.write("Status: <br>")
        res_list = str(resp.reason).split(';')
        response.write("JSON: <b>" + str(resp.json()) + " </b><br>") 
#        response.write("Готівка: <b>" + res_list[1] + " грн.</b><br>")
#        response.write("Чек: <b>" + res_list[2] + " грн.</b><br>")
#        response.write("Кредитна карта: <b>" + res_list[3] + "</b><br>")
#        response.write("інший тип 1: <b>" + res_list[4] + "</b><br>")
#        response.write("інший тип 2: <b>" + res_list[5] + "</b><br>")
#        response.write("інший тип 3: <b>" + res_list[6] + "</b><br>")
#        response.write("інший тип 4: - <b>" + res_list[7] + "</b><br>")

    response.write("<br><<< Result: >>> <br>" +str(resp.reason.encode('utf-8')) + "<br><<< Result text >>><br>" +  str(resp.text.encode('utf-8')))
    return response


def casa_prro_create(request):
    resp = None
    token = post_casa_token()
    xLicenseKey=licenseKey()
    # sending post request and saving response as response object 
    try:
        url = "https://api.checkbox.ua/api/v1/shifts"
        data = {}
        headers = {
            'Content-type': 'application/json', 
            'Accept': 'text/plain',
            'X-License-Key': xLicenseKey, 
            'Authorization': token
            }
        resp = requests.post(url, data=json.dumps(data), headers=headers)
    except:
        return HttpResponse("Connection failed! Перевірте зєднання з інтернетом")
    
    response = HttpResponse()
    response.write("Response: " + str(resp.status_code) + "<br>")
    if int(resp.status_code) == 202:
        response.write("<b>Зміну відкрито </b><br>")
    if int(resp.status_code) == 400:
        response.write("<b>Зміну вже відкрито. Касир працює з даною касою.</b><br>")
        #=======================================================================
        # res_list = str(resp.reason).split(';')
        # response.write("JSON: <b>" + str(r.json()) + " </b><br>") 
        # response.write("Готівка: <b>" + res_list[1] + " грн.</b><br>")
        # response.write("Чек: <b>" + res_list[2] + " грн.</b><br>")
        # response.write("Кредитна карта: <b>" + res_list[3] + "</b><br>")
        # response.write("інший тип 1: <b>" + res_list[4] + "</b><br>")
        # response.write("інший тип 2: <b>" + res_list[5] + "</b><br>")
        # response.write("інший тип 3: <b>" + res_list[6] + "</b><br>")
        # response.write("інший тип 4: - <b>" + res_list[7] + "</b><br>")
        #=======================================================================

    response.write("<br><<< Result: >>> <br>" +str(resp.json()) + "<br><<< Result text >>><br>" +  str(resp.text.encode('utf-8')))
    return response


def casa_prro_in_out(request, sum=0, inout='-'):
    resp = None
    token = post_casa_token()
    xLicenseKey=licenseKey()
    # sending post request and saving response as response object
    sum = sum
    if inout == '-':
         sum = -1 * int(sum)
    try:
        url = "https://api.checkbox.ua/api/v1/receipts/service"
        data = {
                "payment": {
                "type": "CASH",
                "value": str(sum), #<сума у копійках, для створення чеку службового вилучення перед сумою має бути - >,
#                "label": "Cash" #Готівка            
                }
                }
        headers = {
            'Content-type': 'application/json', 
            'Accept': 'text/plain',
            'X-License-Key': xLicenseKey, 
            'Authorization': token
            }
        resp = requests.post(url, data=json.dumps(data), headers=headers)
    except:
        return HttpResponse("Connection failed! Перевірте зєднання з інтернетом")
    
    response = HttpResponse()
    if resp.status_code == 200:
        response.write("Status: <br>")
        res_list = str(resp.reason).split(';')
    response.write("<br><<< Result: >>> <br>" +str(resp.json()) + "<br><<< Result text >>><br>" +  str(resp.text.encode('utf-8')))
    return response


def casa_rro_xreport(request, token=post_casa_token()):
    URL = ''
    URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    cmd = 'open_port;1;115200;'
    PARAMS = {'address':URL, 'cmd': cmd, 
              'hash': settings.MINI_HASH_1, 
              'user': request.user.username,
              }
    resp = None
    try:
        resp_open = requests.post(url = URL, data = PARAMS)
        PARAMS['cmd'] = 'get_cashbox_sum;'
        resp = requests.post(url = URL, data = PARAMS)
    except:
        context = {'weblink': 'error_message.html', 'mtext': "Connection failed! Перевірте зєднання з комп'ютером",}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)        
    if resp.status_code == 200:
        res_list = str(resp.reason).split(';')
    PARAMS['cmd'] = 'close_port;'
    resp_close = requests.post(url = URL, data = PARAMS)
    
    res_start_dt = ''
    error_msg = ''
    casa_status = "<br><<< Result >>> <br>" + str(resp.reason) + "<br><<< Result >>><br>" + str(resp.text) #None # responce for other request
    cashless_sell_sum = float(res_list[3]) * 100 # копійки
    jbalance = float(res_list[1]) * 100 # копійки
    
    day_cred=ClientCredits.objects.all().first()
    term_sum_1 = day_cred.get_daily_term_shop1()[2]
#    term_sum_2 = day_cred.get_daily_term_shop2()[2]
#    term_sum_2 = (round((term_sum_2 or 0)*100) or 0)
    term_sum_1 = (round((term_sum_1 or 0)*100) or 0)
    context = {'weblink': 'report_prro.html', 'day_term_sum': term_sum_1, 'error_status': error_msg, 'cashless_sum': cashless_sell_sum, 'res_start_dt': res_start_dt, 'casa_status': casa_status, 'JsonBalance': jbalance, 'shop': 1}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def casa_checkout(request, id):
    URL = ''
    if id == '1':
        URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    if id == '2':
        URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"
    cmd = 'open_port;1;115200;'
    PARAMS = {'address':URL, 'cmd': cmd, 
              'hash': settings.MINI_HASH_1, 
              'user': request.user.username,
              }
    resp = None
    # sending post request and saving response as response object 
    try:
        resp_open = requests.post(url = URL, data = PARAMS)
        PARAMS['cmd'] = 'get_cashbox_sum;'
        resp = requests.post(url = URL, data = PARAMS)
#        print "Result = " + str(resp)
#        print (resp.status_code, resp.reason) #HTTP
    except:
        context = {'weblink': 'error_message.html', 'mtext': "Connection failed! Перевірте зєднання з комп'ютером",}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)        
        #return HttpResponse("Connection failed! Перевірте зєднання з комп'ютером")
    msg_text = ""
    lines = []
    #response = HttpResponse()
    if resp.status_code == 200:
        #response.write("Status: <br>")
        res_list = str(resp.reason).split(';')
        lines.append("<h2>Кавказька: </h2><br>")
        lines.append("Готівка: <b>" + res_list[1] + " грн.</b><br>")
        lines.append("Чек: <b>" + res_list[2] + " грн.</b><br>")
        lines.append("Кредитна карта: <b>" + res_list[3] + "</b><br>")
        lines.append("інший тип 1: <b>" + res_list[4] + "</b><br>")
        lines.append("інший тип 2: <b>" + res_list[5] + "</b><br>")
        lines.append("інший тип 3: <b>" + res_list[6] + "</b><br>")
        lines.append("інший тип 4: <b>" + res_list[7] + "</b><br>")
        msg_text = "<br>".join(str(line) for line in lines)
        #=======================================================================
        # response.write("Готівка: <b>" + res_list[1] + " грн.</b><br>")
        # response.write("Чек: <b>" + res_list[2] + " грн.</b><br>")
        # response.write("Кредитна карта: <b>" + res_list[3] + "</b><br>")
        # response.write("інший тип 1: <b>" + res_list[4] + "</b><br>")
        # response.write("інший тип 2: <b>" + res_list[5] + "</b><br>")
        # response.write("інший тип 3: <b>" + res_list[6] + "</b><br>")
        # response.write("інший тип 4: - <b>" + res_list[7] + "</b><br>")
        #=======================================================================
    PARAMS['cmd'] = 'close_port;'
    resp_close = requests.post(url = URL, data = PARAMS)
#    response.write("<br><<< Result >>> <br>" +str(resp.reason) + "<br><<< Result >>><br>" +  str(resp.text))
    msg_text = msg_text + "<br>" + "<br><<< Result >>> <br>" + str(resp.reason) + "<br><<< Result >>><br>" + str(resp.text)
    context = {'weblink': 'info_message.html', 'mtext': msg_text,}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)        


def casa_prro_check_view(request, chk_uid, type="text"):
    id = chk_uid
    #id = "7d79fc22-fc85-479b-9102-f29f3444c96a"
    data = {}
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain',         
    }    
    url = ""
    if type == "text":
        url = "https://api.checkbox.in.ua/api/v1/receipts/"+id+"/text"
        r = requests.get(url, data=json.dumps(data), headers=headers)
        content = r.text.encode('utf-8')
        return HttpResponse(content, content_type='text/plain')
    if type == "html":
        url = "https://api.checkbox.in.ua/api/v1/receipts/"+id+"/html?simple=false"
    if type == "pdf":
        url = "https://api.checkbox.in.ua/api/v1/receipts/"+id+"/pdf"

    r = requests.get(url, data=json.dumps(data), headers=headers)
#    with open('recp.txt', 'w') as outfile:
#        outfile.write(r.text.encode('utf-8'))
    response = HttpResponse()
#    response.write("Response: " + str(r.status_code) + "<br>")
#    if resp.status_code == 202:
#        response.write("Status: <br>")
#        res_list = str(resp.reason).split(';')
#        response.write("JSON: <b>" + str(resp.json()) + " </b><br>") 
    response.write("" + r.text.encode('utf-8'))
    return response
    
@csrf_exempt
def casa_command(request, id):
    URL = ''
    if id == '1':
        URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    if id == '2':
        URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"

    #URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    #cmd = 'play_sound'
    cmd = 'open_port;1;115200;'
    #cmd = 'close_port;'
    #cmd = 'get_soft_version;'
    #cmd = 'indicate;Hello World'
    #cmd = 'get_date_time;'
    #cmd = 'get_header;'
    #cmd = 'get_plu_info;1858;'
    #cmd = 'get_plu_info;7247;' # 3 параметр - Штучный/весовой товар (0/1)
    #cmd = 'get_cashbox_sum;';
    #cmd = 'put_logo;logo_rivelo_black.bmp';
    #cmd = 'activate_logo;312;142;';
    #cmd = 'print_receipt_copy;'
    #cmd = 'print_empty_receipt;'
    #cmd = 'set_time;18;29;00'
    #cmd = 'in_out;0;0;0;0;'+str(0.0)+';;;'
    #cmd = 'open_receipt;0' # відкрити чек
    #cmd = 'open_receipt;1' # відкрити чек повернення
    #cmd = "set_cashiers_number;"
    hash = 'rivelo2020casa4kavkazkaSt.'
    user = 'ygrik'
    # defining a params dict for the parameters to be sent to the API 
    PARAMS = {'address':URL,
              'cmd': cmd, 
              'hash': hash, 
              'user': user,
             } 
    resp = None
    # sending post request and saving response as response object 
    try:
        resp_open = requests.post(url = URL, data = PARAMS)
        #PARAMS['cmd'] = 'cashier_registration;1;0;'
        #resp_cashier_reg = requests.post(url = URL, data = PARAMS)
        #PARAMS['cmd'] = 'get_cashbox_sum;'
        #PARAMS['cmd'] = 'in_out;0;0;0;0;'+str(0.0)+';;;' # внесення готівки
        #PARAMS['cmd'] = 'in_out;0;0;0;1;'+str(0.0)+';;;' #Вилучення готівки
        json = None
        if request.is_ajax():
            if request.method == 'POST':  
                POST = request.POST  
                if POST.has_key('command'):
                    cmd = request.POST.get('command')
                    print "\nAjax send = " + cmd + "\n"
                    PARAMS['cmd'] = cmd
                    resp = requests.post(url = URL, data = PARAMS)
                    print "\nJson:" + str(resp)
                    return HttpResponse("Json" + str(resp.text))
#===============================================================================
#                 try:
#                     json = simplejson.dumps({'status_code': resp.status_code, 'resp': resp.reason})
#                 except:
#                     error = 'Сталась помилка'
#                     json = simplejson.dumps({'yData': "None", 'error': error})
# 
#                     return HttpResponse(json, content_type='application/json')
#===============================================================================
        
        #PARAMS['cmd'] = u'get_plu_info;8591;' # 3 параметр - Штучный/весовой товар (0/1)
#        PARAMS['cmd'] = u'add_plu;8591;0;0;0;1;1;1;203.00;0;Трос перемикання JAGWIRE Basics BWC1011;0.00;'.encode('cp1251')
#                                8591;0;0;1;1;1;1;15.00;0;Трос перемикання JAGWIRE Basics BWC1011;1.000;
        #PARAMS['cmd'] = 'execute_Z_report;12321;'
        #PARAMS['cmd'] = 'pay;2;191.90;'
        #PARAMS['cmd'] = 'pay;0;0;'
        
#        print "Result = " + str(resp)
#        print (resp.status_code, resp.reason) #HTTP
    except:
        context = {'weblink': 'error_message.html', 'mtext': "Connection failed! Перевірте зєднання з комп'ютером",}
        context.update(custom_proc(request))
        return render(request, 'index.html', context)        
        
#        print  "Error - Connection failed!"
#        return HttpResponse("Connection failed! Перевірте зєднання з комп'ютером")
    
#    print "\nStatus code = " + str(type(resp)) + "\n"
#    print "Content:" + str(dir(resp))
    #print "Text:" + str(resp.request.body)    
    #print "Text:" + str(resp.text)
    #print "JSON:" + str(resp.json)

    PARAMS['cmd'] = 'close_port;'
    resp_close = requests.post(url = URL, data = PARAMS)

    #return HttpResponse("Status - " + str(resp.reason) + " <br><<< Result >>>" + str(resp.text))
    context = {'weblink': 'casa_cmd_list.html', 'id': id, }
    context.update(custom_proc(request))
    return render(request, 'index.html', context)


def casa_getstatus(request, id):
#    URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    URL = ''
    if id == '1':
        URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    if id == '2':
        URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"

    #hash = 'rivelo2020casa4kavkazkaSt.'
    #user = 'ygrik'
    cmd = 'open_port;1;115200;'
    # defining a params dict for the parameters to be sent to the API 
    PARAMS = {'address':URL,
              'cmd': cmd, 
              'hash': settings.MINI_HASH_1, 
              'user': request.user.username,
              }
 
    resp = None
    # sending post request and saving response as response object 
    try:
        resp_open = requests.post(url = URL, data = PARAMS)
        PARAMS['cmd'] = 'get_status;'
        resp = requests.post(url = URL, data = PARAMS)
        print "Result = " + str(resp)
        print (resp.status_code, resp.reason) #HTTP
    except:
        return HttpResponse("Connection failed! Перевірте зєднання з комп'ютером")
    
    msg_text = ""
    lines = []
#    response = HttpResponse()
    if resp.status_code == 200:
        res_list = str(resp.reason).split(';')
        lines.append("<h2>Кавказька <СТАТУС КАСОВОГО>: </h2><br>")
        lines.append("Касир № <b>" + res_list[1] + "</b><br>")
        lines.append("Зміна № <b>" + res_list[2] + "</b><br>")
        lines.append("Стан чеку - <b>" + res_list[3] + "</b> ( 0 - Чек закритий; 1 - Чек відкритий для продажу; 2 - чек відкритий для оплати; 3 - чек відкритий для повернення; )<br>")
        lines.append("Тривалість зміни - <b>" + res_list[9] + "</b> (0 - менше 23 годин / 1 - більше 23 годин)<br>")
        lines.append("Тривалість зміни - <b>" + res_list[10] + "</b> (0 - менше 24 годин / 1 - більше 24 годин)<br>")
        lines.append("Дата початку зміни - <b>" + res_list[11] + "</b><br>")
        lines.append("Час початку зміни - <b>" + res_list[12] + "</b><br>")
        lines.append("Номер закритого чеку в даній зміні - <b>" + res_list[15] + "</b><br>")
        lines.append("Номер закритого чеку в попередній зміні - <b>" + res_list[16] + "</b><br>")
        lines.append("Кількість касирів - <b>" + res_list[19] + "</b><br>")
        lines.append("Блокування при не передачі даних протягом 72 годин - <b>" + res_list[22] + "</b> // 0 - розблокований; 1 - заблокований;<br>")
        lines.append("Точка блокування 72 години (дата)  - <b>" + res_list[23] + "</b> <br>")
        lines.append("Точка блокування 72 години (час)  - <b>" + res_list[24] + "</b> <br>")
        msg_text = "<br>".join(str(line) for line in lines)
        #=======================================================================
        # response.write("Status: <br>")
        # res_list = str(resp.reason).split(';') 
        # response.write("Касир № <b>" + res_list[1] + "</b><br>")
        # response.write("Зміна № <b>" + res_list[2] + "</b><br>")
        # response.write("Стан чеку - <b>" + res_list[3] + "</b><br>")
        # response.write("Тривалість зміни (0 - менше 23 годин / 1 - більше 23 годин) - <b>" + res_list[9] + "</b><br>")
        # response.write("Тривалість зміни (0 - менше 24 годин / 1 - більше 24 годин) - <b>" + res_list[10] + "</b><br>")
        # response.write("Дата початку зміни - <b>" + res_list[11] + "</b><br>")
        # response.write("Час початку зміни - <b>" + res_list[12] + "</b><br>")
        # response.write("Номер закритого чеку в даній зміні - <b>" + res_list[15] + "</b><br>")
        # response.write("Номер закритого чеку в попередній зміні - <b>" + res_list[16] + "</b><br>")
        # response.write("Кількість касирів - <b>" + res_list[19] + "</b><br>")
        # response.write("Блокування при не передачі даних протягом 72 годин - <b>" + res_list[22] + "</b><br>")
        # response.write("Точка блокування 72 години (дата)  - <b>" + res_list[23] + "</b><br>")
        # response.write("Точка блокування 72 години (час)  - <b>" + res_list[24] + "</b><br>")
        #=======================================================================

    PARAMS['cmd'] = 'close_port;'
    resp_close = requests.post(url = URL, data = PARAMS)
#    response.write("<br><<< Result >>> <br>" +str(resp.reason) + "<br><<< Result >>><br>" +  str(resp.text))
#    return response
    msg_text = msg_text + "<br>" + "<br><<< Result >>> <br>" + str(resp.reason) + "<br><<< Result >>><br>" + str(resp.text)
    context = {'weblink': 'info_message.html', 'mtext': msg_text,}
    context.update(custom_proc(request))
    return render(request, 'index.html', context)        




def casa_z_report(request, id):
    URL = ''
    if id == '1':
        URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    if id == '2':
        URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"
#    URL = "http://" + settings.HTTP_MINI_SERVER_IP + ":" + settings.HTTP_MINI_SERVER_PORT +"/"
    cmd = 'open_port;1;115200;'
    PARAMS = {'address':URL, 'cmd': cmd, 
              'hash': settings.MINI_HASH_1, 
              'user': request.user.username,
              }
 
    resp = None
    # sending post request and saving response as response object 
    try:
        resp_open = requests.post(url = URL, data = PARAMS)
        PARAMS['cmd'] = 'get_cashbox_sum;'
        resp = requests.post(url = URL, data = PARAMS)
        #print "Result = " + str(resp)
        #print (resp.status_code, resp.reason) #HTTP
    except:
        return HttpResponse("Connection failed! Перевірте зєднання з комп'ютером")
    
    response = HttpResponse()
    if resp.status_code == 200:
        response.write("Status: <br>")
        res_list = str(resp.reason).split(';') 
        response.write("Готівка: <b>" + res_list[1] + " грн.</b><br>")
        response.write("Чек: <b>" + res_list[2] + " грн.</b><br>")
        response.write("Кредитна карта: <b>" + res_list[3] + "</b><br>")
        response.write("інший тип 1: <b>" + res_list[4] + "</b><br>")
        response.write("інший тип 2: <b>" + res_list[5] + "</b><br>")
        response.write("інший тип 3: <b>" + res_list[6] + "</b><br>")
        response.write("інший тип 4: - <b>" + res_list[7] + "</b><br>")
        PARAMS['cmd'] = 'cashier_registration;1;0;'
        resp_cashier_reg = requests.post(url = URL, data = PARAMS)
        #print "Sum =  " + str(float(res_list[1]))
        PARAMS['cmd'] = 'in_out;0;0;0;1;'+res_list[1]+';;;' #Вилучення готівки
        resp_cashier_reg = requests.post(url = URL, data = PARAMS)
        PARAMS['cmd'] = 'get_cashbox_sum;'
        resp = requests.post(url = URL, data = PARAMS)
        res_list = str(resp.reason).split(';')
        cash = float(res_list[1])
        term_cash = float(res_list[1])
        #print "CASH = " +  str(cash)
        if cash == 0.0:
            response.write("<br>Готівка в касі = <b>" + str(cash) + " грн</b><br>")
            response.write("Термінал = <b>" + str(term_cash) + " грн</b><br>")
            PARAMS['cmd'] = 'execute_Z_report;12321;'
            resp = requests.post(url = URL, data = PARAMS)

    PARAMS['cmd'] = 'close_port;'
    resp_close = requests.post(url = URL, data = PARAMS)
    response.write("<br><<< Result >>> <br>" +str(resp.reason) + "<br><<< Result >>><br>" +  str(resp.text))
    return response




    