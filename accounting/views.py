# -*- coding: utf-8 -*-
from django.db.models import Q
from django.db.models import F
from django.db import connection
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import resolve

from models import Manufacturer, Country, Type, Currency, Bicycle_Type, Bicycle,  FrameSize, Bicycle_Store, Bicycle_Sale, Bicycle_Order, Bicycle_Storage, Bicycle_Photo, Storage_Type, Bicycle_Parts
from forms import ContactForm, ManufacturerForm, CountryForm, CurencyForm, CategoryForm, BicycleTypeForm, BicycleForm, BicycleFrameSizeForm, BicycleStoreForm, BicycleSaleForm, BicycleOrderForm, BicycleStorage_Form, StorageType_Form 

from models import Catalog, Client, ClientDebts, ClientCredits, ClientInvoice, ClientOrder, ClientMessage, ClientReturn, InventoryList
from forms import CatalogForm, ClientForm, ClientDebtsForm, ClientCreditsForm, ClientInvoiceForm, ClientOrderForm, ClientEditForm

from models import Dealer, DealerManager, DealerManager, DealerPayment, DealerInvoice, InvoiceComponentList, Bank, Exchange, PreOrder, CashType, Discount
from forms import DealerManagerForm, DealerForm, DealerPaymentForm, DealerInvoiceForm, InvoiceComponentListForm, BankForm, ExchangeForm, PreOrderForm, InvoiceComponentForm, CashTypeForm, DiscountForm 

from models import WorkGroup, WorkType, WorkShop, WorkStatus, WorkTicket, CostType, Costs, ShopDailySales, Rent, ShopPrice, Photo, WorkDay, Check, CheckPay, PhoneStatus, YouTube
from forms import WorkGroupForm, WorkTypeForm, WorkShopForm, WorkStatusForm, WorkTicketForm, CostTypeForm, CostsForm, ShopDailySalesForm, RentForm, WorkDayForm, ImportDealerInvoiceForm, ImportPriceForm, PhoneStatusForm, WorkShopFormset, SalaryForm
  
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile

from django.http import HttpResponse 
from django.http import Http404  

from django.conf import settings
import datetime
import calendar
import codecs
import csv
import re

import StringIO, requests, os
from PIL import Image
from django.utils.text import slugify

from django.db.models import Sum, Count, Max, Avg

from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import Group

import simplejson as json
from django.core import serializers

import pytils_ua
import urllib

from django.core.mail import EmailMultiAlternatives
from urlparse import urlsplit
from django.db.models import F
from django.http import JsonResponse
from django.core.context_processors import request
from _mysql import NULL
#from pyasn1.compat.octets import null


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }

    
def auth_group(user, group):
#    print "****Group  = " + str(group)
#    print "****USER  = " + str(user)
    if user.groups.filter(name=group).exists():
#        print "****Group = " + str(user.groups.filter(name=group))
        return True
#    print "****Group FALSE = " + str(user)
    return False
    #return True if user.groups.filter(name=group) else False


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


def del_logging(obj):
    file_name = 'test_log'
    log_path = settings.MEDIA_ROOT + 'logs/' + file_name + '.log'
    log_file = open(log_path, 'a')
    log_file.write("%s >>> DELETE FROM TABLE %s WHERE id = %s \n" % (str(datetime.datetime.now()), obj._meta.verbose_name, obj.id) )
        
    for f in obj._meta.fields:
        log_file.write("Key = " + f.name + " - ") # field name
        s = "Value = %s" % f.value_from_object(obj) + "\n"
        log_file.write(s.encode('cp1251'))
        #log_file.write("Value = %s" % f.value_from_object(obj).encode('cp1251') + "\n") # field value
            
    #log_file.write("DELETE FROM TABLE " + table_name + obj.name)
    log_file.close()



def send_shop_mail(request, mto, w, subject='Наявний товар'):
    from_email = 'rivelo@ymail.com' 
    to = mto
    text_content = 'www.rivelo.com.ua'
    html_content = w.content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return True #render_to_response("index.html", {'success_data': "Лист відправлено на пошту" + to}, context_instance=RequestContext(request, processors=[custom_proc]))


def prev_url(request):
    #referer = request.META.get('HTTP_REFERER', None)
    referer = request.META['HTTP_REFERER']
    if referer is None:
        pass
         # do something here
    try:
        #redirect_to = urlsplit(referer, 'http', False)[2]
        redirect_to = refer
    except IndexError:
        pass
         # do another thing here
    return redirect_to

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
    return render_to_response('index.html', {'countries': list, 'weblink': 'country_list.html', 'next': current_url}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'list': list, 'weblink': 'cashtype_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def cashtype_add(request):
    a = CashType()
    if request.method == 'POST':
        form = CashTypeForm(request.POST, instance=a)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            CashType(name=name, description=description).save()
            return HttpResponseRedirect('/cashtype/view/')
    else:
        form = CashTypeForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'cashtype.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def cashtype_del(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/cashtype/view/')
    obj = CashType.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/cashtype/view/')


def cashtype_edit(request, id):
    a = CashType.objects.get(pk=id)
    if request.method == 'POST':
        form = CashTypeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/cashtype/view/')
    else:
        form = CashTypeForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'cashtype.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

# ----------- Bicycle --------------
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
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_type.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'types': list, 'weblink': 'bicycle_type_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_framesize_add(request):
    a = FrameSize()
    if request.method == 'POST':
        form = BicycleFrameSizeForm(request.POST, instance=a)
        if form.is_valid():
            name = form.cleaned_data['name']
            cm = form.cleaned_data['cm']
            inch = form.cleaned_data['inch']
            FrameSize(name=name, cm=cm, inch=inch).save()
            return HttpResponseRedirect('/bicycle-framesize/view/')
    else:
        form = BicycleFrameSizeForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_framesize.html', 'text': 'Створення нового розміру рами'}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_framesize_edit(request, id):
    a = FrameSize.objects.get(pk=id)
    if request.method == 'POST':
        form = BicycleFrameSizeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/bicycle-framesize/view/')
    else:
        form = BicycleFrameSizeForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_framesize.html', 'text': 'Розмір рами (редагування)'}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_framesize_del(request, id):
    if auth_group(request.user, 'admin') == False:
        return HttpResponseRedirect('/bicycle-framesize/view/')
    obj = FrameSize.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle-framesize/view/')


def bicycle_framesize_list(request):
    list = FrameSize.objects.all()
    #return render_to_response('bicycle_framesize_list.html', {'framesizes': list.values_list()})
    return render_to_response('index.html', {'framesizes': list, 'weblink': 'bicycle_framesize_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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

    #return render_to_response('bicycle.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle.html', 'text': 'Велосипед з каталогу (створення)'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle.html', 'text': 'Велосипед з каталогу (редагування)'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    bike_company = Bicycle.objects.filter(year__year=year).values('brand', 'brand__name').annotate(num_company=Count('model'))
    #bike_year = Bicycle.objects.values('year').annotate(n_year=Count('year__year'))
    bike_year = Bicycle.objects.filter().extra({'yyear':"Extract(year from year)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('yyear')
    #return render_to_response('bicycle_list.html', {'bicycles': list.values_list()})
    return render_to_response('index.html', {'bicycles': list, 'year': year, 'b_company': bike_company, 'byear': bike_year, 'sale': percent, 'weblink': 'bicycle_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_photo(request, id):
    obj = Bicycle.objects.get(id=id)
    #return render_to_response('bicycle_list.html', {'bicycles': list.values_list()})
    return render_to_response('index.html', {'bicycle': obj, 'weblink': 'bicycle_photo.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_store.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
                return HttpResponse("dont work ajax")
    
    a = Bicycle_Store.objects.get(pk=id)
    if request.method == 'POST':
        form = BicycleStoreForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/bicycle-store/view/')
    else:
        form = BicycleStoreForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_store.html', 'text': 'Редагувати тип'}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_store_del(request, id):
    if request.user.has_perm('accounting.delete_bicycle_store') == False:
        return HttpResponseRedirect('/.')
    #    return HttpResponseRedirect('/bicycle-store/view/seller/')
    obj = Bicycle_Store.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle-store/view/seller/')


def bicycle_store_list(request, all=False):
    list = None
    if all==True:
        list = Bicycle_Store.objects.all()
    else:
        list = Bicycle_Store.objects.filter(count=1) #.values('model__model', 'model__sale', 'model__year', 'model__brand__name', 'model__price', 'model__color', 'model__id', 'size__name', 'size__cm', 'size__inch', 'model__type__type', 'serial_number', 'size', 'price', 'currency', 'count', 'description', 'date', 'id')
        
    price_summ = 0
    bike_summ = 0
    price_profit_summ = 0
    for item in list:
        price_profit_summ = price_profit_summ + item.get_profit()[1] #item['price'] * item['count']
        price_summ = price_summ + item.get_uaprice() 
#        bike_summ = bike_summ + item['count']
#    price_summ = Exchange.objects.filter(currency__ids_char = 'EUR').aggregate(average_val = Avg('value'))['average_val']
    #price_summ = price_summ['average_val']
    bike_sum = list.count()
#    fsize = FrameSize.objects.all().values('name', 'id')
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_store_list.html', 'price_summ': price_summ, 'price_profit_summ':price_profit_summ, 'bike_summ': bike_summ}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    frames = FrameSize.objects.all()
    bike_company = Bicycle_Store.objects.filter(count=1).values('model__brand', 'model__brand__name').annotate(num_company=Count('count'))
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_store_list_by_seller.html', 'price_summ': price_summ, 'real_summ': real_summ, 'bike_summ': bike_summ, 'sizes': frames, 'b_company': bike_company, 'html': html, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_store_search(request):
    return render_to_response('index.html', {'weblink': 'frame_search.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_store_list_by_seller.html', 'price_summ': price_summ, 'real_summ': real_summ, 'bike_summ': bike_summ, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        return render_to_response('bicycle_shop_price_list.html', {'bicycles': list, 'view':False})    
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_shop_price_list.html', 'view':True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_store_list.html', 'text': text, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_store_list_by_seller.html', 'text': text, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_sale_add(request, id=None):
#    a = Bicycle_Sale(currency = Currency.objects.get(pk = 3))
    bike = None
    serial_number = ''
    if id != None:
        bike = Bicycle_Store.objects.get(id=id)
        serial_number = bike.serial_number
        
    if request.method == 'POST':
        form = BicycleSaleForm(request.POST, initial={'currency': 3, 'date': datetime.date.today()})
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
            user = None             
            if request.user.is_authenticated():
                user = request.user            
            
            bs = Bicycle_Sale(model = model, client=client, price = price, currency = currency, sale=sale, date=date, service=service, description=description, user=user, sum=sum)
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
            form = BicycleSaleForm(initial={'model': bike.id, 'price': bike.model.price, 'currency': bike.model.currency.id, 'sale': bike.model.sale, 'date': datetime.date.today()})
#            form = BicycleSaleForm()
        else:
            form = BicycleSaleForm(initial={'currency': 3})
#            form = BicycleSaleForm(instance=a)
    
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_sale.html', 'serial_number': serial_number, 'bike_id': bike.id, 'text': 'Продаж велосипеду', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
            form.save()
            
            cdeb_price = price * (1 - sale/100.0)
            try:
                cdeb = ClientDebts.objects.get(pk=a.debt.id)
                #cdeb.client=client
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
    #serial_number = "test number"
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_sale.html', 'text': 'Редагувати проданий велосипед', 'serial_number': serial_number, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
            list = Bicycle_Sale.objects.filter(pk = id).order_by('date')
        else:
            list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
    if (year != False) & (month != False) & (id == None):
        list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
    header_bike = Bicycle_Sale.objects.filter().extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('date')
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
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_list.html', 'header_links':header_bike, 'price_summ':price_summ, 'profit_summ':profit_summ, 'pay_sum':psum, 'service_summ':service_summ, 'month': month, 'year':year, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_sale_list_by_brand(request, year=False, month=False, id=None):
    list = None
    if (year==False) & (month==False):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        #list = Bicycle_Sale.objects.all().order_by('date')
        if (id != None):
            list = Bicycle_Sale.objects.filter(model__model__brand=1, date__year=year).order_by('date')
        else:
            list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
    else:
       #list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
       list = Bicycle_Sale.objects.filter(model__model__brand=id, date__year=year).order_by('date')
    header_bike = Bicycle_Sale.objects.filter().extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('date')       
    price_summ = 0
    price_opt = 0
    profit_summ = 0
    service_summ = 0
    for item in list:
        #price_summ = price_summ + item.price
        price_summ = price_summ + item.price * ((100-item.sale)*0.01)
        price_opt = price_opt + item.model.price
        profit_summ = profit_summ + item.get_profit()[1]
        if item.service == False:
            service_summ =  service_summ + 1
    try:
        brand = list[0].model.model.brand.name
    except:
        brand = None
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_list.html', 'price_summ':price_summ, 'header_links':header_bike, 'price_opt': price_opt, 'profit_summ':profit_summ, 'service_summ':service_summ, 'year':year, 'brand':brand, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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

#    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
   
#    list = Bicycle_Sale.objects.get(id=id)
    
    #list.save()
    #list = Bicycle_Sale.objects.filter(id=id)
#    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_list.html',})

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
                if term_number == '2':
                    URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"
                bs = Bicycle_Sale.objects.get(id=id)
                chk_list = Check.objects.filter(bicycle = bs.id)
                if chk_list.count()>0:
                    message = "Даний чек вже існує"
                    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")                    
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

                    res = Check.objects.aggregate(max_count=Max('check_num'))
                    chkPay = CheckPay(check_num = res['max_count'] + 1, cash = m_val, term = t_val)
                    chkPay.save()
                    
                    res = Check.objects.aggregate(max_count=Max('check_num'))
                    check = Check(check_num=res['max_count'] + 1)
                    check.checkPay = chkPay
                    check.client = bs.client #Client.objects.get(id=client.id)
                    check.bicycle = bs #ClientInvoice.objects.get(pk=inv)
                    check.description = "Продаж велосипеду"
                    check.count = 1
                    check.discount = bs.sale
                    t = 1
                    if m_val >= t_val:
                        t = 1
                        check.price = m_val
                    else: 
                        t = 2
                        check.price = t_val 
                    check.cash_type = CashType.objects.get(id = t)
                    check.print_status = False
                    check.user = request.user
                    check.save()    

                    price =  "%.2f" % bs.price
                    count = "%.3f" % 1
                    discount = bs.sale
                    #bike_s = 'Велосипед '+ bs.model.model.brand.name.encode('utf8') +'. Модель '+ bs.model.model.model.encode('utf8') +'. '+str(bs.model.model.year.year)+' ('+bs.model.model.color.encode('utf8')+')'
                    bike_s = u'Велосипед '+ bs.model.model.brand.name +u'. Модель '+ bs.model.model.model +'. '+str(bs.model.model.year.year)+' ('+bs.model.model.color+')'
                    #bike_s = bs.model.model.model[:40].encode('utf8')
                    #data =  {"cmd": "add_plu", "id":'77'+str(bs.model.pk), "cname":bike_s, "price":price, "count": count, "discount": discount}
                    #url = base + urllib.urlencode(data)
                    #page = urllib.urlopen(url).read()
                    
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
                    
#===============================================================================
#                     if m_val >= t_val:
#                         data =  {"cmd": "pay", "sum": m_val, "mtype": 0}
#                         url = base + urllib.urlencode(data)
#                         page = urllib.urlopen(url).read()
#                         data =  {"cmd": "pay", "sum": t_val, "mtype": 2}
#                         url = base + urllib.urlencode(data)
#                         page = urllib.urlopen(url).read()
#                     else:
#                         data =  {"cmd": "pay", "sum": t_val, "mtype": 2}
#                         url = base + urllib.urlencode(data)
#                         page = urllib.urlopen(url).read()
#                         data =  {"cmd": "pay", "sum": m_val, "mtype": 0}
#                         url = base + urllib.urlencode(data)
#                         page = urllib.urlopen(url).read()
#                         
#                     base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
#                     data =  {"cmd": "close"}
#                     url = base + urllib.urlencode(data)
#                     page = urllib.urlopen(url).read()
# 
#                     message = "Виконано"
#                 return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
#===============================================================================
    else:
        message = "Error"
        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")



def bicycle_sale_check(request, id=None, param=None):
    list = Bicycle_Sale.objects.get(id=id)
    text = pytils_ua.numeral.in_words((100-int(list.sale))*0.01*int(list.price))
    month = pytils_ua.dt.ru_strftime(u"%d %B %Y", list.date, inflected=True)
    chk_list = Check.objects.filter(bicycle = list.id)
    if chk_list.count()>0:
        chk_num = chk_list[0].check_num
    else:
        chk_num = list.id
    w = render_to_response('bicycle_sale_check.html', {'bicycle': list, 'month':month, 'str_number':text, 'chk_num':chk_num})
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
        
    return render_to_response('index.html', {'bicycle': list, 'month':month, 'chk_num':chk_num, 'str_number':text, 'weblink': 'bicycle_sale_check.html', 'print':'True', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc])) 


def bicycle_sale_search_by_name(request):
    return render_to_response('index.html', {'weblink': 'bicycle_sale_search_by_name.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    for item in list:
        price_summ = price_summ + item.price 
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_list.html', 'price_summ': price_summ, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
    

def bicycle_sale_report(request):
    if auth_group(request.user, 'admin') == False:
        return HttpResponseRedirect('/')
    query = "SELECT EXTRACT(year FROM date) as year, EXTRACT(month from date) as month, MONTHNAME(date) as month_name, COUNT(*) as bike_count, sum(price) as s_price FROM accounting_bicycle_sale GROUP BY year,month;"
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
    return render_to_response('index.html', {'bicycles': list, 'all_sum': sum, 'bike_sum': bike_sum, 'weblink': 'bicycle_sale_report.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_sale_report_by_brand(request):
    #list = Bicycle_Order.objects.annotate(bcount=Count("model")) 
    list = Bicycle_Sale.objects.values('model__model__brand__name', 'model__model__brand', 'model__model__brand__id').annotate(bcount=Count("model__model__model")).order_by('-bcount') #("model__model__brand")
#    objects.filter(date__year=now.year, date__month=now.month).extra(select={'year': "EXTRACT(year FROM date)", 'month': "EXTRACT(month from date)", 'day': "EXTRACT(day from date)"}).values('year', 'month', 'day').annotate(suma=Sum("price")).order_by()    
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_report_bybrand.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]) )    


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
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_order.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    

def bicycle_order_list(request):
    #list = Bicycle_Order.objects.all().order_by("-date")
    list = Bicycle_Order.objects.all().order_by("-date").values('model__id', 'model__model', 'model__brand__name', 'model__year', 'model__color', 'model__type__type', 'client__id', 'client__name', 'client__forumname', 'size', 'price', 'prepay', 'sale', 'date', 'done', 'id', 'currency__name', 'description', 'user')
    return render_to_response('index.html', {'order': list, 'weblink': 'bicycle_order_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    

def bicycle_order_edit(request, id):
    a = Bicycle_Order.objects.get(pk=id)
    if request.method == 'POST':
        form = BicycleOrderForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/bicycle/order/view/')
    else:
        form = BicycleOrderForm(instance=a, initial={'client_id': a.client.pk, 'model_id': a.model.pk})
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_order.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_order_del(request, id):
    obj = Bicycle_Order.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/bicycle/order/view/')    


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

def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]

def bike_lookup(request):
    data = None
    cur_year = datetime.datetime.now().year

    if request.method == "POST":
        if request.POST.has_key(u'query'):
            value = request.POST[u'query']
            if len(value) > 2:
                model_results = Bicycle.objects.filter(year__gte=datetime.datetime(cur_year-2, 1, 1)).filter(Q(model__icontains = value) | Q(brand__name__icontains = value)).order_by('-year')
                data = serializers.serialize("json", model_results, fields = ('id', 'model', 'type', 'brand', 'color', 'price', 'year', 'sale'), use_natural_keys=False)
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
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_storage.html', 'text': 'Вид зберігання'}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_storage_type_list(request):
    #list = Bicycle_Order.objects.all().order_by("-date")
    list = Storage_Type.objects.all().order_by("id")
    return render_to_response('index.html', {'list': list, 'weblink': 'storage_type_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

from django.contrib import messages
from django.shortcuts import  redirect
from django.utils.encoding import smart_str    

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
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_storage.html', 'text': 'Додати велосипед на зберігання'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'list': list, 'weblink': 'bicycle_storage_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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


def dealer_edit(request, id):
    a = Dealer.objects.get(pk=id)
    if request.method == 'POST':
        form = DealerForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dealer/view/')
    else:
        form = DealerForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer.html'}, context_instance=RequestContext(request, processors=[custom_proc]))

 
def dealer_del(request, id):
    obj = Dealer.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/dealer/view/')
 
 
def dealer_list(request):
    list = Dealer.objects.all()
    #return render_to_response('dealer_list.html', {'dealers': list.values_list()})
    return render_to_response('index.html', {'dealers': list, 'weblink': 'dealer_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer_payment.html'})

 
def dealer_payment_del(request, id):
    obj = DealerPayment.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/dealer/payment/view/')
 
 
def dealer_payment_list(request):
    list = DealerPayment.objects.all()
    return render_to_response('index.html', {'dealer_payment': list, 'weblink': 'dealer_payment_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer_invoice.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer_invoice.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

 
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
            
    exchange = Exchange.objects.filter(date=datetime.date.today)
    try:
        exchange_d = Exchange.objects.get(date=datetime.date.today, currency=2)
        exchange_e = Exchange.objects.get(date=datetime.date.today, currency=4)
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
    return render_to_response('index.html', {'dealer_invoice': list, 'sel_company': id, 'sel_year': year, 'exchange': exchange, 'year_list' :yearlist, 'company_list': company_list, 'exchange_d': exchange_d, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'weblink': 'dealer_invoice_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        #now = datetime.date.today()
        #html = "<html><body>Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову.</body></html>" % now
        html = "Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову" % now.strftime('%d-%m-%Y %H:%m')
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': html, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        #return HttpResponse(html)
        exchange_d = 0
        exchange_e = 0
    company_list = list.values("company", "company__name", "company__color").distinct().order_by("company__pk")        
    yearlist = DealerInvoice.list_objects.get_year_list()
    return render_to_response('index.html', {'dealer_invoice': list, 'exchange': exchange, 'exchange_d': exchange_d, 'year_list' :yearlist, 'company_list': company_list, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'sel_month':month, 'sel_year':year, 'weblink': 'dealer_invoice_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'weblink': 'dealer_invoice_search.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def dealer_invoice_search_result(request):
    list = None
    if 'number' in request.GET and request.GET['number']:
         num = request.GET['number']
         list = DealerInvoice.objects.filter(origin_id__icontains = num)
     #list1 = DealerInvoice.objects.all()
    #return render_to_response('index.html', {'invoice_list': list, 'weblink': 'dealer_invoice_list_search.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    else:
        pass
    now = datetime.datetime.now()
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
    company_list = list.values("company", "company__name", "company__color").distinct().order_by("company__pk")
    yearlist = DealerInvoice.list_objects.get_year_list()
    return render_to_response('index.html', {'dealer_invoice': list, 'exchange': exchange, 'exchange_d': exchange_d, 'year_list' :yearlist, 'search_text': num, 'company_list': company_list, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'sel_year':now.year, 'weblink': 'dealer_invoice_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))



def dealer_invoice_set(request):
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
        #return HttpResponse('Ваш запит відхилено. Щось пішло не так', content_type="text/plain;charset=UTF-8;charset=UTF-8", status=401)
        return HttpResponse(simplejson.dumps({'msg':'Ваш запит відхилено. Щось пішло не так'}), content_type="application/json", status=401)


def invoice_new_item(request):
    date=datetime.date.today()
    start_date = datetime.date(date.year, 1, 1)
    end_date = datetime.date(date.year, 3, 31)    
    di = DealerInvoice.objects.filter(received = False).values_list("id", flat=True)
    nday = 14
    list_comp = InvoiceComponentList.objects.filter(invoice__date__gt = date - datetime.timedelta(days=int(nday)), invoice__id__in = di).order_by("invoice__id")    
    return render_to_response('index.html', {'dinvoice_list': list_comp, 'weblink': 'dealer_invoice_new_item.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))  


def invoice_miss_stuff(request):
    date=datetime.date.today()
    start_date = datetime.date(date.year, 1, 1)
    end_date = datetime.date(date.year, 3, 31)    
    
    di = DealerInvoice.objects.filter(received = False).values_list("id", flat=True)
    
    nday = 180
    list_comp = InvoiceComponentList.objects.filter(invoice__date__gt = date - datetime.timedelta(days=int(nday)), invoice__id__in = di).exclude(rcount = F('count')).order_by("invoice__id")    
    return render_to_response('index.html', {'dinvoice_list': list_comp, 'weblink': 'dealer_invoice_new_item.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))  
    
    

#-------------- InvoiceComponentList -----------------------
def invoicecomponent_add(request, mid=None, cid=None):
#    company_list = Manufacturer.objects.all()
    price = 0
    if cid<>None:
        #a = InvoiceComponentList(date=datetime.date.today(), price=0, count=1, currency=Currency.objects.get(id=2), invoice=DealerInvoice.objects.get(id=187), catalog=Catalog.objects.get(id=cid))
        c = Catalog.objects.get(id=cid)        
        a = InvoiceComponentList(date=datetime.date.today(), price=0, count=1, currency=Currency.objects.get(id=2), invoice=DealerInvoice.objects.get(id=187), catalog = c)
        price = c.price
    else:    
        a = InvoiceComponentList(date=datetime.date.today(), price=0, count=1, currency=Currency.objects.get(id=2), invoice=DealerInvoice.objects.get(id=187))
    if request.method == 'POST':
        form = InvoiceComponentListForm(request.POST, instance = a, test1=mid, catalog_id=cid)
        if form.is_valid():
            invoice = form.cleaned_data['invoice']
            date = form.cleaned_data['date']
            catalog = form.cleaned_data['catalog']
            count = form.cleaned_data['count']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            description = form.cleaned_data['description']
            InvoiceComponentList(date=date, invoice=invoice, catalog=catalog, price=price, currency=currency, count=count, description=description).save()
            cat = Catalog.objects.get(id = cid)
            cat.count = cat.count + count
            cat.save()
            #return HttpResponseRedirect('/invoice/list/10/view/')
            #list = InvoiceComponentList.objects.all().values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale').order_by('-id')[:10]
            #return render_to_response('index.html', {'componentlist': list, 'addurl': "/invoice/manufacture/"+str(mid)+"/add", 'weblink': 'invoicecomponent_list.html'})
            return HttpResponseRedirect('/invoice/list/10/view/')
    else:
        form = InvoiceComponentListForm(instance = a, test1=mid, catalog_id=cid)
    return render_to_response('index.html', {'form': form, 'weblink': 'invoicecomponent.html', 'price_ua': price, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    
#    return render_to_response('index.html', {'form': form, 'weblink': 'invoicecomponent.html', 'company_list': company_list, 'price_ua': price, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def invoicecomponent_list(request, mid=None, cid=None, isale=None, limit=0, focus=0, upday=0, sel_year=0, enddate=None, all=False):
    #company_list = Manufacturer.objects.none()
    company_list = Manufacturer.objects.all().only('id', 'name')
    #type_list = Type.objects.none() 
    type_list = Type.objects.all()
    company_name = '' 
    cat_name = ''
    list = None
    id_list=[]
    zsum = 0
    zcount = 0
    
    if 'name' in request.GET and request.GET['name']:
        name = request.GET['name']
        list = InvoiceComponentList.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__dealer_code', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')        
    elif  'id' in request.GET and request.GET['id']:
        id = request.GET['id']
        list = InvoiceComponentList.objects.filter(Q(catalog__ids__icontains=id) | Q(catalog__dealer_code__icontains=id) ).values('catalog').annotate(sum_catalog=Sum('count')).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
    if mid:
        if all == True:
            list = InvoiceComponentList.objects.filter(catalog__manufacturer__id=mid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
        else:
            list = InvoiceComponentList.objects.filter(catalog__manufacturer__id=mid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').exclude(catalog__count = 0)
        company_name = Manufacturer.objects.get(id=mid)
    if cid:
        if all == True:        
            list = InvoiceComponentList.objects.filter(catalog__type__id=cid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
        else:
            list = InvoiceComponentList.objects.filter(catalog__type__id=cid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update').exclude(catalog__count = 0)
        cat_name = type_list.get(id=cid)
    if isale == True:
        list = InvoiceComponentList.objects.filter(catalog__sale__gt = 0).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
    if enddate == True:
        list = InvoiceComponentList.objects.filter(catalog__date__isnull = False, catalog__count__gt = 0).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update', 'catalog__date').order_by('-catalog__date')

    if upday != 0:
        curdate=datetime.datetime.today()
        update = curdate - datetime.timedelta(days=int(upday))
        list = InvoiceComponentList.objects.filter(catalog__last_update__gt = update).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__dealer_code', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
    
    if limit == 0:
        try:
            if enddate == True:
                list = list.annotate(sum_catalog=Sum('count')).order_by("catalog__date")
            else:
                list = list.annotate(sum_catalog=Sum('count')).order_by("catalog__type")
        except:
            list = InvoiceComponentList.objects.none()        
    else:
        list = InvoiceComponentList.objects.all().values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__last_price', 'catalog__dealer_code', 'catalog__sale', 'catalog__count', 'catalog__type__id', 'catalog__description').annotate(sum_catalog=Sum('count')).order_by("catalog__type")
#        list = InvoiceComponentList.objects.all().values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price', 'catalog__sale', 'catalog__count', 'catalog__type__id').annotate(sum_catalog=Sum('count')).order_by("catalog__type")
        list = list[:limit]
    
    for item in list:
        id_list.append(item['catalog'])

    new_list = []
    years_range  = None
    sale_list = None
    if auth_group(request.user, 'admin')==True:
        years_range = ClientInvoice.objects.filter(catalog__in=id_list).extra({'yyear':"Extract(year from date)"}).values_list('yyear').annotate(pk_count = Count('pk')).order_by('date')
    if sel_year > 0:
        sale_list = ClientInvoice.objects.filter(catalog__in=id_list, date__year = sel_year).values('catalog', 'catalog__price').annotate(sum_catalog=Sum('count'))
        #years_range = ClientInvoice.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id'))
    else:
        sale_list = ClientInvoice.objects.filter(catalog__in=id_list).values('catalog', 'catalog__price').annotate(sum_catalog=Sum('count'))

    cat_list = Catalog.objects.filter(pk__in=id_list).values('type__name_ukr', 'description', 'locality', 'id', 'manufacturer__id', 'manufacturer__name', 'photo_url', 'youtube_url', 'last_update', 'user_update__username')        
#    arrive_list = Catalog.objects.filter(pk__in = id_list).new_arrival()
    for element in list:
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
                element['manufacturer__name1']=cat['manufacturer__name']
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
#            element['invoice_price'] = Catalog.objects.get(pk = element['catalog']).invoice_price()
        if element['balance'] == 0:
            print "Element = " + str(element)

    
# update count field in catalog table            
        #upd = Catalog.objects.get(pk = element['catalog'])
        #upd.count = element['balance'] 
        #upd.save()

    cur_year = datetime.date.today().year        
    vars = {'company_list': company_list, 'type_list': type_list, 'componentlist': list, 'zsum':zsum, 'zcount':zcount, 'company_name': company_name, 'company_id':mid, 'category_id':cid, 'category_name':cat_name, 'years_range':years_range, 'cur_year': cur_year, 'weblink': 'invoicecomponent_list.html', 'focus': focus, 'next': current_url(request)}
#    calendar = embeded_calendar()
#    cat_discount = cat_name.get_discount()
#    vars.update({'cat_discount': cat_discount})
    
#    categ = type_list.get(id=cid)
#    vars.update({'type_obj': categ})
    
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


def invoicecomponent_print(request):
    list = None
    id_list=[]
    map_id = []
    
    if 'ids' in request.POST and request.POST['ids']:
        id_list = request.POST['ids'].split(',')
#        map_id = map(int, id_list)
        list = Catalog.objects.filter(id__in = id_list).values('name', 'ids', 'manufacturer__name', 'price', 'sale', 'count', 'type__name').order_by('manufacturer')
    else:
        return HttpResponse("Не вибрано жодного товару", content_type="text/plain;charset=UTF-8;")

    response = HttpResponse()
    response.write(u"<table>")
    response.write(u"<tr> <td>Артикул</td> <td>Виробник</td> <td>Назва</td> <td>Ціна</td> <td>Знижка %</td> <td>Нова ціна</td> </tr>")

    for i in list:
         response.write("<tr>")
         new_price = float(i['price']) / 100.0 * (100 - int(i['sale']))
         response.write("<td>"+ i['ids'] +"</td><td>"+ i['manufacturer__name'] +"</td><td>"+ i['name'] +"</td><td>" + str(i['price']) +u" грн.</td><td>"+ str(i['sale']) +"</td><td>"+ str(new_price) +u" грн.</td>")
         #response.write("<td>"+ i['ids'] +"</td><td>"+ i['name'] +"</td><td>" + i['ids'] +u" грн.</td><td>"+i['ids'] +"</td><td>") #+ str(new_price) +"</td>")
         response.write("</tr>")
    response.write("</table>")
#    response = response.replace("<", "[")
#    response = response.replace(">", "]")
    return response
#    return render_to_response("POST done!!!")


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
    list = Catalog.objects.filter(count__gt=0).values('id', 'name', 'count', 'price')
    #.annotate(sum_catalog=Sum('count'))
    #aggregate(price_sum=Sum('count'))
    psum = 0
    scount = 0
    counter = 0
    for item in list:
        scount = scount + item['count']
        psum = psum + (item['price'] * item['count'])
        counter = counter + 1
    paginator = Paginator(list, 50)
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
        
    return render_to_response('index.html', {'allpricesum':psum, 'countsum': scount, 'counter': counter, 'catalog': catalog, 'weblink': 'invoicecomponent_report.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def invoicecomponent_del(request, id):
    obj = InvoiceComponentList.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    cat = Catalog.objects.get(id = obj.catalog.id)
    cat.count = cat.count - obj.count
    cat.save()
    return HttpResponseRedirect('/invoice/list/10/view/')


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
            return HttpResponseRedirect('/invoice/list/10/view/')
    else:
        form = InvoiceComponentListForm(instance=a, catalog_id=cid)
        #form = InvoiceComponentListForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'invoicecomponent.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def invoice_search(request):
    return render_to_response('index.html', {'weblink': 'invoice_search.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

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
    uaoptsum = 0
    for item in list:
        psum = psum + (item.catalog.price * item.count)
        optsum = optsum + (item.price * item.count)
        uaoptsum = optsum + (item.get_uaprice() * item.count)
        scount = scount + item.count
    dinvoice = DealerInvoice.objects.get(id=id)    
    #return render_to_response('index.html', {'list': list, 'dinvoice':dinvoice, 'company_list':company_list, 'allpricesum':psum, 'alloptsum':optsum, 'countsum': scount, 'weblink': 'invoice_component_report.html'})
    return render_to_response('index.html', {'list': list, 'dinvoice':dinvoice, 'allpricesum':psum, 'alloptsum':optsum, 'ua_optsum':uaoptsum, 'countsum': scount, 'weblink': 'invoice_component_report.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'list': list, 'allpricesum':psum, 'countsum': scount, 'alloptsum':optsum, 'weblink': 'invoice_component_report.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def invoice_import_form(request):
    form = ImportDealerInvoiceForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'import_invoice.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    
    

def invoice_import(request):
# id / name / company / type / color / country / count/ price / currency / invoice_id / rrp_price / currency /
# id / name / count / price / currency / invoice number
    invoice_reader = None
    ids_list = []
    now = datetime.datetime.now()
#    if 'name' in request.GET and request.GET['name']:
#        name = request.GET['name']
    if request.POST and request.FILES:
#    if request.FILES:
        csvfile = request.FILES['csv_file']
        dialect = csv.Sniffer().sniff(codecs.EncodedFile(csvfile, "utf-8").read(1024))
        csvfile.open()
        invoice_reader = csv.reader(codecs.EncodedFile(csvfile, "utf-8"), delimiter=';', dialect=dialect)
        #invoice_reader = csv.reader(csvfile, delimiter=';', quotechar='|')

    name = 'id'
#    path = settings.MEDIA_ROOT + 'csv/' + name + '.csv'
#    csvfile = open(path, 'rb')
#    invoice_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
    w_file = open(settings.MEDIA_ROOT + 'csv/' + name + '_miss.csv', 'wb')
    spamwriter = csv.writer(w_file, delimiter=';', quotechar='|') #, quoting=csv.QUOTE_MINIMAL)
    for row in invoice_reader:
        id = None
        print "ROW[0] = " + row[0]
        id = row[0]
        ids_list.append(row[0])
        try:
            cat = Catalog.objects.get(Q(ids = id) | Q(dealer_code = id))
            print "ID = " + row[0]
#            print "ROW[6] = " + row[6]
            if int(row[6]) > 0:
                cat.price = row[6]
            c = Currency.objects.get(id = row[4])
            inv = DealerInvoice.objects.get(id = row[5])
            InvoiceComponentList(invoice = inv, catalog = cat, count = row[2], price= row[3], currency = c, date = now).save()
            if request.POST.has_key('name'): 
                if request.POST['name'] == 'on':
                    cat.name = row[1] 
            cat.count = cat.count + int(row[2])
            cat.save()
            #if row[6]: 
            #    cat.price = row[6]
            #    cat.save()
                    
        except Catalog.DoesNotExist:
            spamwriter.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]])

    list = Catalog.objects.filter(ids__in = ids_list)
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    


# --------------- Classification ---------

def category_list(request):
    list = Type.objects.all()
    #return render_to_response('category_list.html', {'categories': list.values_list()})
    return render_to_response('index.html', {'categories': list, 'weblink': 'category_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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

   
def category_lookup(request):
    data = None
    if request.is_ajax():
        if request.method == "POST":
            if request.POST.has_key(u'query'):
                value = request.POST[u'query']
                if len(value) > 2:
                    model_results = Type.objects.filter(Q(name__icontains = value) | Q(name_ukr__icontains = value)).order_by('name')
                    data = serializers.serialize("json", model_results, fields = ('id', 'name_ukr', 'name'), use_natural_keys=False)
                else:
                    model_results = Type.objects.all().order_by('name')
                    data = serializers.serialize("json", model_results, fields = ('id', 'name_ukr', 'name'), use_natural_keys=False)                    
#                    data = []
    return HttpResponse(data)                


def category_add(request):
    a = Type()
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance = a)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            name_ukr = form.cleaned_data['name_ukr']
            description_ukr = form.cleaned_data['description_ukr']

            Type(name=name, description=description, name_ukr=name_ukr, description_ukr=description_ukr).save()
            return HttpResponseRedirect('/category/view/')
    else:
        form = CategoryForm(instance = a)
    #return render_to_response('category.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'category.html'}, context_instance=RequestContext(request, processors=[custom_proc]))

def category_edit(request, id):
    a = Type.objects.get(pk=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/category/view/')
    else:
        form = CategoryForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'category.html', 'text': 'Обмін валют (редагування)'}, context_instance=RequestContext(request, processors=[custom_proc]))

def category_del(request, id):
    obj = Type.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/category/view/')    

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
        USDb = res[0]['buy']
        USDs = res[0]['sale']
        c_usd = (float(USDb) + float(USDs)) / 2
        #c_usd = (float(str(soup_usd_b.string)) + float(str(soup_usd_s.string))) / 2
        #c_usd = (float(str(usd_b.string)) + float(str(usd_s.string))) / 2
    except:
        c_usd = 0
    try:
        EURb = res[1]['buy']
        EURs = res[1]['buy']
        c_eur = (float(EURb) + float(EURs)) / 2
    except:
        c_eur = 0
        
    return [c_usd, c_eur]


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
    #return render_to_response('exchange.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'eur': c_eur, 'usd': c_usd, 'weblink': 'exchange.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))



def exchange_list(request):
    #cur = goverla_currency()
    cur = pb_currency()
    c_usd = cur[0]
    c_eur = cur[1]
        
    curdate = datetime.datetime.now()
    list = Exchange.objects.filter(date__month=curdate.month)
    #return render_to_response('exchange_list.html', {'exchange': list.values()})
    return render_to_response('index.html', {'exchange': list, 'eur': c_eur, 'usd': c_usd, 'weblink': 'exchange_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def exchange_edit(request, id):
    a = Exchange.objects.get(pk=id)
    if request.method == 'POST':
        form = ExchangeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/exchange/view/')
    else:
        form = ExchangeForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'exchange.html', 'text': 'Обмін валют (редагування)', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def exchange_del(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/exchange/view/')        
    obj = Exchange.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/exchange/view/')



# -------- Catalog ---------------- 

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
    return render_to_response('index.html', {'form': form, 'weblink': 'manufacturer.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def manufacturer_edit(request, id):
    a = Manufacturer.objects.get(pk=id)
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, request.FILES, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/manufacturer/view/')
    else:
        form = ManufacturerForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'manufacturer.html', 'text': 'Виробник (редагування)', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def manufaturer_list(request):
    list = Manufacturer.objects.all()
    #return render_to_response('manufacturer_list.html', {'manufactures': list.values_list()})
    return render_to_response('index.html', {'manufactures': list, 'weblink': 'manufacturer_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def manufacturer_delete(request, id):
    obj = Manufacturer.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/manufacturer/view/')


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
    return HttpResponse(data)    


def catalog_import_form(request):
    form = ImportPriceForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'catalog_import.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    


def catalog_import(request):
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
        return render_to_response('index.html', {'form': form, 'weblink': 'catalog_import.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    
    
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
        except: # Catalog.DoesNotExist:
            #add_list.append(row)
            m = Manufacturer.objects.get(id=row[8])
            t = Type.objects.get(id=row[7])
            c = Currency.objects.get(id = row[4])
            country = Country.objects.get(id=row[9])                                        
            Catalog(ids=row[0], dealer_code=row[1], name=row[2], manufacturer=m, type=t, year=datetime.datetime.now().year, color='', price=row[3], currency=c, sale=0, country=country, count = 0).save()          

            add_list.append({'id': id, 'code': code, 'photo': row[6], 'name': row[2], 'desc': row[5]});
            log_writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
#        print " ---------- END -------------"            
        
    #list = Catalog.objects.select_related('manufacturer', 'type', 'currency', 'country').filter(Q(ids__in = ids_list))
    return render_to_response('index.html', {'update_list': update_list, 'add_list': add_list, 'ids_list': ids_list, 'weblink': 'catalog_import_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
 


def catalog_add(request):
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має прав для редагування')

    upload_path = ''
    if request.method == 'POST':
        form = CatalogForm(request.POST, request.FILES)
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
            #return HttpResponseRedirect('/catalog/view/')
            return HttpResponseRedirect('/catalog/manufacture/' + str(manufacturer.id) + '/view/5')
    else:
        form = CatalogForm()
    #return render_to_response('catalog.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'catalog.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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

            if POST.has_key('id') and POST.has_key('locality') and auth_group(request.user, 'seller'):
                id = request.POST.get('id')                
                loc = request.POST.get('locality')
                obj = Catalog.objects.get(id = id)                                
                obj.locality = loc
                obj.save() 
                c = Catalog.objects.filter(id = id).values_list('locality', flat=True)
                return HttpResponse(c)
            
            if POST.has_key('id') and POST.has_key('price'):
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

                #return HttpResponse(c)
              #  return HttpResponse(simplejson.dumps(list(c)))
    else :
           return HttpResponse('Error: Щось пішло не так')
    


def catalog_edit(request, id=None):
    a = Catalog.objects.get(pk=id)
    #url1=request.META['HTTP_REFERER']
    if request.method == 'POST':
        form = CatalogForm(request.POST, request.FILES, instance=a)
        if form.is_valid():
            manufacturer = form.cleaned_data['manufacturer']
            type = form.cleaned_data['type']
            a.last_update = datetime.datetime.now()
            a.user_update = request.user
            a.save()
            form.save()
            #return HttpResponseRedirect('/catalog/manufacture/' + str(manufacturer.id) + '/view/5')
#            return HttpResponseRedirect('/catalog/manufacture/' + str(manufacturer.id) + '/type/'+str(type.id)+'/view')
            return catalog_list(request, id = id)
            #return HttpResponseRedirect('/catalog/view/')
            #return HttpResponseRedirect(str(url1))
    else:
        form = CatalogForm(instance=a)
    #url=request.META['HTTP_REFERER']

    return render_to_response('index.html', {'form': form, 'weblink': 'catalog.html', 'cat_pk': id, 'catalog_obj': a.get_photos(), 'youtube_list': a.youtube_url.all(), 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_list(request, id=None):
    list = None
    if id==None:
        list = Catalog.objects.all().order_by("-id")[:10]
    else:
        list = Catalog.objects.filter(id=id)
    #return render_to_response('catalog_list.html', {'catalog': list.values_list()})
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'catalog': list, 'company_list': company_list, 'url': print_url, 'view': True, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_part_list(request, id, num=5):
    list = Catalog.objects.filter(manufacturer=id).order_by("-id")[:num]
    #return render_to_response('catalog_list.html', {'catalog': list.values_list()})
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'weblink': 'catalog_search_id.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_search_locality(request):
    return render_to_response('index.html', {'weblink': 'catalog_search.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
                
    return render_to_response('index.html', {'catalog': list, 'url':print_url, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_lookup(request):
    # Default return list
    data = None
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            # Ignore queries shorter than length 3
            if len(value) > 2:
                #model_results = Catalog.objects.filter(name__icontains=value).values('id', 'ids', 'name', 'price')
                model_results = Catalog.objects.filter(name__icontains=value)
#                results = [ x.name for x in model_results ]
#    json = simplejson.dumps(results)
                data = serializers.serialize("json", model_results, fields=('name','id', 'ids', 'price'))

    if request.is_ajax():
        if request.method == "POST":
            if request.POST.has_key(u'query') and request.POST.has_key(u'type'):
                value = request.POST[u'query']
                type_id = request.POST[u'type']

                if len(value) > 2:
                    model_results = Catalog.objects.filter(name__icontains=value, type = type_id)
                    data = serializers.serialize("json", model_results, fields=('name','id', 'ids', 'price'))
                
    return HttpResponse(data)    
    #return HttpResponse(json)


def catalog_get_locality(request):
    sel_id = None
    if request.method == 'POST':
        sel_id = request.POST.get('sel_id')
    list = Catalog.objects.get(id=sel_id)#.values_list("id", "locality")
    return HttpResponse(unicode(list.locality), content_type='text')


# ------------- Clients -------------
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
 
            a = Client(name=name, forumname=forumname, country=country, city=city, email=email, phone=phone, sale=sale, summ=summ, description=description, phone1=phone1, birthday=birthday, sale_on=sale_on)
            a.save()
            #return HttpResponseRedirect('/client/view/')
            return HttpResponseRedirect('/client/result/search/?id=' + str(a.id))
    else:
        form = ClientForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'client.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'client.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_join(request, id=None):
    #a = Client.objects.get(pk=id)
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
    #else:
        
    return render_to_response('index.html', {'weblink': 'client_join.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_balance_list(request):
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
            
#===============================================================================
#    query = '''select accounting_client.id as id, accounting_client.name as name, sum(accounting_clientcredits.price) as sum_cred, sum(accounting_clientdebts.price) as sum_deb    
#            from accounting_client left join accounting_clientcredits on accounting_client.id=accounting_clientcredits.client_id 
#            left join accounting_clientdebts on  accounting_client.id=accounting_clientdebts.client_id 
#            group by accounting_clientcredits.client_id, accounting_clientdebts.client_id;
#            '''
#                
#===============================================================================
            
    list = None
    list1 = None
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        list = dictfetchall(cursor)
        cursor1 = connection.cursor()
        cursor1.execute(query1)
        list1 = cursor1.fetchall()
        #list = cursor.execute(sql1, )   
        
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
            #item[1]
    s_debt = 0
    s_cred = 0
    for key1 in list[:]:
        s_debt+=key1['sum_deb']
        s_cred+=key1['sum_cred']
        if (key1['sum_deb']==False) & (key1['sum_cred']==False):
            #key1['minus']=9999
            list.remove(key1)
            
    #list = Bicycle_Sale.objects.all().order_by('date')
    return render_to_response('index.html', {'clients': list, 'sum_debt':s_debt, 'sum_cred':s_cred, 'weblink': 'client_balance_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
            

def client_list(request):
    list = Client.objects.all()
    paginator = Paginator(list, 25)
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
    
    return render_to_response('index.html', {'clients': contacts, 'weblink': 'client_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    #return render_to_response('bicycle_list.html', {'bicycles': list.values_list()})
    return render_to_response('index.html', {'client': obj, 'weblink': 'client_data.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def clientdebts_add(request, id=None):
    if request.method == 'POST':
        form = ClientDebtsForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            cash = form.cleaned_data['cash']
            if request.user.is_authenticated():
                user = request.user
            ClientDebts(client=client, date=date, price=price, description=description, user=user, cash=cash).save()
            
#            update_client = Client.objects.get(id=client.id)
#            update_client.summ = update_client.summ + price 
#            update_client.save()
            
            if id != None:
                return HttpResponseRedirect('/client/result/search/?id='+str(id))
            else:
                return HttpResponseRedirect('/clientdebts/view/')
    else:
        if id != None:
            form = ClientDebtsForm(initial={'client': id, 'date': datetime.datetime.now(), })
        else:
            form = ClientDebtsForm()
    #return render_to_response('clientdebts.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'clientdebts.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'client.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    
    return render_to_response('index.html', {'clients': debts, 'weblink': 'clientdebts_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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


def clientcredits_add(request, id=None):
    if request.method == 'POST':
        form = ClientCreditsForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            cash_type = form.cleaned_data['cash_type']
            user = None             
            if request.user.is_authenticated():
                user = request.user
            ClientCredits(client=client, date=date, price=price, description=description, user=user, cash_type=cash_type).save()
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
            form = ClientCreditsForm(initial={'client': id, 'date': datetime.datetime.now(), 'price': borg, 'description': "Закриття боргу "})
        else:
            form = ClientCreditsForm()
        #form = ClientCreditsForm()
    #return render_to_response('clientcredits.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'clientcredits.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    
    return render_to_response('index.html', {'clients': credits, 'weblink': 'clientcredits_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'clientcredits.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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


def client_invoice_shorturl(request, cid=None):
    cat = Catalog.objects.get(id = cid)
#    if not request.user.is_authenticated():
    return render_to_response('index.html', {'weblink': 'guestinvoice.html', 'cat': cat}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_invoice(request, cid=None, id=None):
    cat = Catalog.objects.get(id = cid)
    if not request.user.is_authenticated():
        return render_to_response('index.html', {'weblink': 'guestinvoice.html', 'cat': cat}, context_instance=RequestContext(request, processors=[custom_proc]))
        #return HttpResponseRedirect('/')
    now = datetime.datetime.now()

    if (id):
        client = Client.objects.get(pk = id)
        a = ClientInvoice(client = client, date=datetime.datetime.today(), price=cat.price, sum=cat.price, sale=int(cat.sale), pay=0, count=1, currency=Currency.objects.get(id=3), catalog=cat, user = request.user)
        
    else:
        a = ClientInvoice(date=datetime.datetime.today(), price=cat.price, sum=cat.price, sale=int(Catalog.objects.get(id = cid).sale), pay=0, count=1, currency=Currency.objects.get(id=3), catalog=cat, user = request.user)
        
    if request.method == 'POST':
        #form = ClientInvoiceForm(request.POST, initial = { instance = a, catalog_id = cid, request = request, 'user': request.user} )
        #form = ClientInvoiceForm(initial = { 'instance' : a, 'catalog_id' : cid } )
        form = ClientInvoiceForm(request.POST, instance = a, catalog_id=cid, request = request)
        if form.is_valid():
#            form.save()            
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
            if (clen is not None) and (cat.type.pk == 13):
                description = description + '\nlength:' + str(clen)
                if cat.length is not None:
                    cat.length = cat.length + clen
                else:
                    cat.length = 0
            #user = None #form.cleaned_data['user_id']            
            user_id = form.cleaned_data['user']
            if request.user.is_authenticated():
                #user = request.user
                user = user_id
            ClientInvoice(client=client, catalog=catalog, count=count, sum=sum, price=price, currency=currency, sale=sale, pay=pay, date=date, description=description, user=user).save()
            
            cat.count = cat.count - count
            cat.save()
            
            if pay == sum:
                desc = catalog.name
                ct = CashType.objects.get(id=1)
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=ct)
                ccred.save()
                cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
                cdeb.save()

            #WorkGroup(name=name, description=description).save()
            return HttpResponseRedirect('/client/invoice/view/')
    else:
        form = ClientInvoiceForm(instance = a, catalog_id=cid, request = request)
        #form = ClientInvoiceForm(initial = { 'instance' : a, 'catalog_id' : cid, 'user': request.user})
    nday = 3
    nbox = cat.locality
    b_len = False
    if cat.type.pk == 13:
        b_len = True
        
    #clients_list = ClientInvoice.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'sale', 'client__name').annotate(num_inv=Count('client'))
    clients_list = ClientInvoice.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))

    cat_obj = cat.get_discount_item()

    return render_to_response('index.html', {'form': form, 'weblink': 'clientinvoice.html', 'clients_list': clients_list, 'catalog_obj': cat, 'cat_sale':cat_obj, 'box_number': nbox, 'b_len': b_len}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_invoice_edit(request, id):
    a = ClientInvoice.objects.get(id=id)
    cat = Catalog.objects.get(id = a.catalog.id)
    if not request.user.is_authenticated():
        return render_to_response('index.html', {'weblink': 'guestinvoice.html', 'cat': cat}, context_instance=RequestContext(request, processors=[custom_proc]))
    if (a.pay == a.sum) and ( auth_group(request.user, "admin") == False ):
        #return HttpResponse("Даний товар вже продано і ви не можете його редагувати", content_type="text/plain;charset=UTF-8;")
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Даний товар вже продано і ви не можете його редагувати', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    
    now = datetime.datetime.now()
    old_count = a.count
#    print "OLD count = " + str(old_count)
#    old_length = 0
    cat_id = a.catalog.id
    cat = Catalog.objects.get(id = cat_id)
    if request.method == 'POST':
        form = ClientInvoiceForm(request.POST, instance = a, catalog_id = cat_id, request = request)
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
            clen = form.cleaned_data['length']
            description = form.cleaned_data['description']
            if (clen is not None) and (cat.type.pk == 13):
                if a.description.find('length:')>=0:
                    old_length = a.description.split('\n')[-1].split('length:')[1]
                if cat.length is not None:
                    cat.length = cat.length - float(old_length) + float(clen)
                else:
                    cat.length = 0 - float(old_length) + float(clen)
                description = description + '\nlength:' + str(clen)
#            print "NEW count = " + str(count)
#            print "CAT count = " + str(cat.count)
#            if old_count > count:
                #cat.count = cat.count - (old_count - count)*-1
            cat.count = cat.count + (old_count - count)
#            else: 
#                cat.count = cat.count - (old_count - count)
            cat.save()
            user = a.user
            if request.user.is_authenticated():
                user = request.user
            ClientInvoice(id=id, client=client, catalog=catalog, count=count, sum=sum, price=price, currency=currency, sale=sale, pay=pay, date=date, description=description, user=user).save()

            if pay == sum:
                desc = catalog.name
                ct = CashType.objects.get(id=1)
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=ct)
                ccred.save()
                cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
                cdeb.save()
            
            return HttpResponseRedirect('/client/invoice/view/')
    else:
        form = ClientInvoiceForm(instance = a, catalog_id = cat_id, request = request)
    nday = 3 # користувачі за останні n-днів
    dlen = None
    nbox = cat.locality
    b_len = False
    if cat.type.pk == 13:
        b_len = True
        if a.description.find('length:')>=0:
            dlen = a.description.split('\n')[-1].split(':')[1]
    clients_list = ClientInvoice.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))
    cat_obj = cat.get_discount_item()        
    return render_to_response('index.html', {'form': form, 'weblink': 'clientinvoice.html', 'clients_list': clients_list, 'catalog_obj': cat, 'cat_sale':cat_obj, 'box_number': nbox, 'b_len': b_len, 'desc_len':dlen, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_invoice_set(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
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
                    
#                if request.user != ci_list.user:
#                    return HttpResponse('Error: У вас не має прав для редагування')
                #ci.save()
                
                result = 'Виконано'
                return HttpResponse(result, content_type="text/plain;charset=UTF-8;")
                
            return HttpResponse("Помилка", content_type="text/plain;charset=UTF-8;")


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
                    
#                if request.user != ci_list.user:
#                    return HttpResponse('Error: У вас не має прав для редагування')
                #ci.save()
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


def client_invoice_view(request, month=None, year=None, day=None, id=None, notpay=False):
    # upd = ClientInvoice.objects.filter(sale = None).update(sale=0) # update recors with sale = 0
    
    if year == None:
        year = datetime.datetime.now().year
    if month == None:
        month = datetime.datetime.now().month

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
    for item in list:
#        scount = scount + item['count']
        psum = psum + item.sum
        scount = scount + item.count
        sprofit = sprofit + item.get_profit()[1]        
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)

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
            
    return render_to_response('index.html', {'sel_year':year, 'sel_month':int(month), 'month_days':days, 'sel_day':day, 'buycomponents': cinvoices, 'sumall':psum, 'sum_profit':sprofit, 'countall':scount, 'weblink': 'clientinvoice_list.html', 'view': True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
#        psum = psum + item['sum']
#        scount = scount + item['count']
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
    
    return render_to_response('index.html', {'buycomponents': cinvoices, 'sumall':psum, 'countall':scount, 'sum_profit':sprofit, 'weblink': 'clientinvoice_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_invoice_check(request, param=None):
    list_id = request.session['invoice_id']
    check_num = request.session['chk_num']
    ci = ClientInvoice.objects.filter(id__in=list_id)
    #-------- показ і відправка чеку на електронку ------
    client = ci[0].client
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
        subject, from_email, to = 'Товарний чек від веломагазину Rivelo', 'rivelo@ymail.com', client.email
        text_content = 'www.rivelo.com.ua'
        html_content = w.content
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to, 'rivelo@ukr.net'])
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

    w = render_to_response('client_invoice_sale_check.html', {'check_invoice': wk, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'print':param, 'is_workshop': 'True', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
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


def client_invioce_return_view(request, limit = None):
    cr_list = None
    if limit != None:
        cr_list = ClientReturn.objects.all().order_by('-id')[:limit]
    else:
        cr_list = ClientReturn.objects.all()
    return render_to_response('index.html', {'return_list': cr_list, 'weblink': 'ci_return_list.html'}, context_instance=RequestContext(request, processors=[custom_proc])) 


def client_invioce_return_add(request, id):
    ci = ClientInvoice.objects.get(id=id)
    now = datetime.datetime.now()
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('msg') and POST.has_key('count'):
                msg = request.POST.get('msg')
                count = request.POST.get('count')
                cash = request.POST.get('cash')
                sum = ci.sum / ci.count * int(count)
                res_count = ci.count - int(count)
                if res_count < 0:
                    count = ci.count
                    res_count = 0
                    sum = ci.sum / ci.count * int(count)
                if cash == "false":
                    ClientCredits(client=ci.client, date=now, price=sum, description="Повернення/обмін: " + str(ci.catalog), cash_type=CashType.objects.get(name=u"Повернення"), user=request.user).save()
                if cash == "true":
                    ClientCredits(client=ci.client, date=now, price=sum, description="Повернення/обмін: " + str(ci.catalog), cash_type=CashType.objects.get(name=u"Повернення"), user=request.user).save() 
                    ClientDebts(client=ci.client, date=now, price=sum, description="Повернення/обмін: " + str(ci.catalog), cash=True, user=request.user).save() 
                cat = Catalog.objects.get(id = ci.catalog.id)
                cat.count = cat.count + int(count)
                cat.save() 
                ClientReturn(client = ci.client, catalog = ci.catalog, sum = sum, buy_date = ci.date, buy_user = ci.user, user = request.user, date=now, msg=msg, count=count).save()
                
                if res_count == 0:
                    ci.delete()
                else:
                    ci.count = res_count
                    if ci.sale <> 100:
                        ci.sum = res_count * ci.price
                    ci.pay = res_count * ci.price
                    ci.save()
                            
    return HttpResponse("ok", content_type="text/plain;charset=UTF-8;")
 
#    cr_list = ClientReturn.objects.all()
#    return render_to_response('index.html', {'return_list': cr_list, 'weblink': 'ci_return_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))    


def client_order_list(request):
    now = datetime.datetime.now()
    #list = ClientOrder.objects.filter(Q(status = False) | Q(date__year__gt = 2015))
    list = ClientOrder.objects.filter((Q(status = False)) | Q(date__gt=now-datetime.timedelta(days=360)))
    return render_to_response('index.html', {'c_order': list, 'weblink': 'client_order_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    


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
    return render_to_response('index.html', {'form': form, 'weblink': 'clientorder.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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

    return render_to_response('index.html', {'form': form, 'weblink': 'clientorder.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'У вас немає доступу до даної сторінки!', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
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
    return render_to_response('index.html', {'bicycles': list, 'all_sum': sum, 'bike_sum': bike_sum, 'weblink': 'clientinvoice_sale_report.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_search(request):
    #query = request.GET.get('q', '')
    return render_to_response('index.html', {'weblink': 'client_search.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_search_result(request):
    if request.is_ajax():
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('name'):
                q = request.GET.get('name')
                c = Client.objects.filter(Q(name__icontains = q) | Q(forumname__icontains = q)).values('id','name', 'forumname')
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
        return render_to_response('index.html', {'clients': contacts, 'weblink': 'clientdebts_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

    GET_params = request.GET.copy()  
    return render_to_response('index.html', {'clients':contacts, 'weblink': 'client_list.html', 'c_count': clients.count(), 'GET_params':GET_params, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))



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
    #user = id;
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
        client_name = Client.objects.values('name', 'forumname', 'id', 'phone', 'birthday', 'email').get(id=user)
    except ObjectDoesNotExist:
        client_name = ""
    
    credit_list = None
    cash_id = CashType.objects.get(id = 6)
    if auth_group(request.user, "admin") == False:
        #if str(request.user.username.encode('utf8')) == str(client_name['forumname'].encode('utf8')):
        if request.user.username == client_name['forumname'].encode('utf8'):
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
    workshop_ticket = WorkTicket.objects.filter(client=user).values('id', 'date', 'description', 'status__name', 'phone_status__name', 'phone_user__username', 'phone_date').order_by('-date')
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

    #list_debt = ClientDebts.objects.filter(client='2').values("client", "price").select_related('client')
    #list_debt = ClientDebts.objects.filter(client='2').select_related('client')
    #list_debt = ClientDebts.objects.filter(client='2').annotate(Sum("price"))
    #return render_to_response('index.html', {'clients': list_credit.values_list(), 'weblink': 'client_result.html'})
    #return render_to_response('index.html', {'clients': list_debt.values_list(), 'weblink': 'client_result.html'})
    if email == True :
        return render_to_response('client_result.html', {'clients': res, 'invoice': client_invoice, 'email': email, 'client_invoice_sum': client_invoice_sum, 'workshop': client_workshop, 'client_workshop_sum': client_workshop_sum, 'debt_list': debt_list, 'credit_list': credit_list, 'client_name': client_name, 'b_bike': b_bike, 'workshopTicket': workshop_ticket, 'messages': messages, 'status_msg':status_msg, 'status_rent':status_rent, 'status_order':status_order, 'tdelta': tdelta})        
    return render_to_response('index.html', {'weblink': 'client_result.html', 'clients': res, 'invoice': client_invoice, 'email': email, 'client_invoice_sum': client_invoice_sum, 'workshop': client_workshop, 'client_workshop_sum': client_workshop_sum, 'debt_list': debt_list, 'credit_list': credit_list, 'client_name': client_name, 'b_bike': b_bike, 'workshopTicket': workshop_ticket, 'messages': messages, 'status_msg':status_msg, 'status_rent':status_rent, 'status_order':status_order, 'tdelta': tdelta}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_lookup(request):
    data = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            if len(value) > 2:
                #model_results = Client.objects.filter(name__icontains=value)
                model_results = Client.objects.filter(Q(name__icontains = value) | Q(forumname__icontains = value))
                data = serializers.serialize("json", model_results, fields=('name','id', 'sale', 'forumname'))
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
def workgroup_add(request):
    if request.method == 'POST':
        form = WorkGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            WorkGroup(name=name, description=description).save()
            return HttpResponseRedirect('/workgroup/view/')
    else:
        form = WorkGroupForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'workgroup.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def workgroup_edit(request, id):
    a = WorkGroup.objects.get(pk=id)
    if request.method == 'POST':
        form = WorkGroupForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workgroup/view/')
    else:
        form = WorkGroupForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'workgroup.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def workgroup_list(request, id=None):
    list = WorkGroup.objects.all().order_by("tabindex")
    return render_to_response('index.html', {'workgroups': list, 'weblink': 'workgroup_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def workgroup_delete(request, id):
    obj = WorkGroup.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workgroup/view/')


def worktype_add(request):
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
    return render_to_response('index.html', {'form': form, 'weblink': 'worktype.html', 'add_edit_text': 'Створити'}, context_instance=RequestContext(request, processors=[custom_proc]))


def worktype_edit(request, id):
    a = WorkType.objects.get(pk=id)
    if request.method == 'POST':
        form = WorkTypeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            #return HttpResponseRedirect('/worktype/view/')
            return HttpResponseRedirect('/worktype/view/group/'+ str(a.work_group.id))
    else:
        form = WorkTypeForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'worktype.html', 'add_edit_text': 'Редагувати'}, context_instance=RequestContext(request, processors=[custom_proc]))


def worktype_list(request, id=None):
    list = None
    if id != None:
        list = WorkType.objects.filter(work_group=id)
    else:
        list = WorkType.objects.all()
    worklist = WorkType.objects.all().order_by('work_group')
    component_type_list = Type.objects.all().order_by('group')
    return render_to_response('index.html', {'worktypes': list, 'worklist': worklist, 'component_type_list':component_type_list, 'weblink': 'worktype_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

#===============================================================================
# 
# def worktype_list(request):
#    list = WorkType.objects.all()
#    return render_to_response('index.html', {'worktypes': list, 'weblink': 'worktype_list.html'})
#===============================================================================

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
    return HttpResponseRedirect('/worktype/view/')


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
    return render_to_response('index.html', {'form': form, 'text': text, 'weblink': 'workstatus.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'text': text, 'weblink': 'workstatus.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'workstatus': list.values_list(), 'phonestatuslist': plist, 'weblink': 'workstatus_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def workstatus_delete(request, id):
    obj = WorkStatus.objects.get(id=id)
    del_logging(obj)
    if (auth_group(request.user, 'admin') == True):
        obj.delete()
    return HttpResponseRedirect('/workstatus/view/')


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
 #   list = PhoneStatus.objects.all()
#    return render_to_response('index.html', {'phonestatus': list.values_list(), 'weblink': 'workstatus_list.html'})


def phonestatus_add(request):
    text = 'Додати статус дзвінка'
    if request.method == 'POST':
        form = PhoneStatusForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            PhoneStatus(name=name, description=description).save()
            return HttpResponseRedirect('/workstatus/view/')
    else:
        form = PhoneStatusForm()
    return render_to_response('index.html', {'form': form, 'text': text, 'weblink': 'workstatus.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'text': text, 'weblink': 'workstatus.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def phonestatus_delete(request, id):
    obj = PhoneStatus.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workstatus/view/')


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
 #           user = form.cleaned_data['user']
  #          if user == '' or user == None:
            user = request.user 
            WorkTicket(client=client, date=date, end_date=end_date, status=status, description=description, user=user).save()
#phone_status=phone_status,            
            return HttpResponseRedirect('/workticket/view/')
    else:
        #form = WorkTicketForm()

        if client != None:
            form = WorkTicketForm(initial={'client': client.id, 'status': 1})
        else:
            form = WorkTicketForm(initial={'date': datetime.datetime.today(), 'status': 1, 'end_date': datetime.datetime.now()+datetime.timedelta(3)})
        
    return render_to_response('index.html', {'form': form, 'weblink': 'workticket.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
            if request.user.is_authenticated():
                user = request.user
            WorkTicket(id = id, client=client, date=date, end_date=end_date, status=status, description=description, user=user).save()
            return HttpResponseRedirect('/workticket/view/')
    else:
        form = WorkTicketForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'workticket.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def workticket_list(request, year=None, month=None, all=False, status=None):
    cur_year = datetime.datetime.now().year
    wy = WorkTicket.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('pk')) #annotate(year_count=Count('date__year'))
    list = None
    if month != None:
        list = WorkTicket.objects.filter(date__year=year, date__month=month)
    if (year == None) and (month == None):
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        list = WorkTicket.objects.filter(date__year=year, date__month=month)
    if all == True:
        list = WorkTicket.objects.filter(date__year=cur_year)
    if status == '1':
        #ws = WorkStatus.objects.get(id=status)
        list = WorkTicket.objects.filter(status__id__in=[status,1]) # Прийнято
    if status == '2':
        list = WorkTicket.objects.filter(status__id__in=[status,2]) # Ремонтується       
    if status == '3':
        list = WorkTicket.objects.filter(status__id__in=[status,3]) # Виконано       
    if status == '4':
        list = WorkTicket.objects.filter(status__id__in=[status,4]) # Виконано невидано 
    if status == '5':
        list = WorkTicket.objects.filter(status__id__in=[status,5]) # Віддано без ремонта 
    if status == '6':
        list = WorkTicket.objects.filter(status__id__in=[status,6]) # Відкладено

    return render_to_response('index.html', {'workticket':list.order_by('-date'), 'sel_year': int(year), 'sel_month':int(month), 'status': status, 'year_ticket': wy, 'weblink': 'workticket_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def workticket_delete(request, id):
    obj = WorkTicket.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workticket/view/')


def workshop_add(request, id=None, id_client=None):
    if request.user.is_authenticated():
        user = request.user
    else:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))
#        return HttpResponse('Error: У вас не має прав для редагування, або ви не Авторизувались на сайті')
    now = datetime.datetime.now()
    work = None
    wclient = None
    if id != None:
        work = WorkType.objects.get(id=id)
    if id_client!=None:
        wclient = Client.objects.get(id=id_client)
    
    if request.method == 'POST':
        form = WorkShopForm(request.POST)
        
        if form.is_valid():
            form.save()
            #WorkShop(client=client, date=date, work_type=work_type, price=price, description=description, user=user).save()
            return HttpResponseRedirect('/workshop/view/')
    else:
        if work != None:
            form = WorkShopForm(initial={'work_type': work.id, 'price': work.get_sale_price, 'user': request.user})
        elif wclient != None:
            form = WorkShopForm(initial={'client': wclient.id, 'user': request.user})
        else:        
            form = WorkShopForm(initial={'user': request.user})
    nday = 7
    try:
        wc_name = wclient.name
        wc_id = wclient.id
    except:
        wc_name = None
        wc_id = None
    clients_list = WorkShop.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))        
    return render_to_response('index.html', {'form': form, 'weblink': 'workshop.html', 'clients_list':clients_list, 'client_name': wc_name, 'client_id': wc_id, 'work': work, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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


def workshop_edit(request, id):
    if not request.user.is_authenticated():    
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не залогувались на порталі або у вас не вистачає повноважень для даних дій.'}, context_instance=RequestContext(request, processors=[custom_proc]))
    now = datetime.datetime.now()
    a = WorkShop.objects.get(pk=id)
    work = a.work_type
    owner = a.user
    old_p = a.price
    if (request.user <> owner) and (auth_group(request.user, 'admin') == False):
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Ви не є влаником даної роботи або не залогувались на порталі. Робота створена користувачем - <b>' + str(owner)+ '</b>'}, context_instance=RequestContext(request, processors=[custom_proc]))             
    
    if request.method == 'POST':
        form = WorkShopForm(request.POST, instance=a)
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            work_type = form.cleaned_data['work_type']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            pay = a.pay #form.cleaned_data['pay']
            #user = request.user 
            user = form.cleaned_data['user']
#            if (request.user == owner) or (auth_group(request.user, 'admin')==True):
#                user = form.cleaned_data['user']
#            else:
#                user = owner
#                cur_date_renew = datetime.datetime.now()
            WorkShop(id=id, client=client, date=date, work_type=work_type, price=price, description=description, user=user, pay = pay).save()                 
            #===================================================================
            # if (pay == False) or (auth_group(request.user, 'admin') == True):
            #     #WorkShop(id=id, client=client, date=date, work_type=work_type, price=price, description=description, user=user, pay = pay).save()
            #     WorkShop(id=id, client=client, date=date, work_type=work_type, price=price, description=description, user=user, pay = pay).save()
            # else:
            #     a.price = old_p 
            #     a.date = cur_date_renew
            #     a.description = description
            #     a.user = user
            #     a.save()
            #===================================================================
            return HttpResponseRedirect('/workshop/view/')
    else:
        form = WorkShopForm(instance=a)
    nday = 7
    clients_list = WorkShop.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))        
    return render_to_response('index.html', {'form': form, 'weblink': 'workshop.html', 'clients_list':clients_list, 'client_name': a.client, 'work': work}, context_instance=RequestContext(request, processors=[custom_proc]))


def workshop_list(request, year=None, month=None, day=None):
    now = datetime.datetime.now()
    if year == None:
        year = now.year
    if month == None:
        month = now.month
    
    if day == None:
        day = now.day
        list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date")
    else:
        if day == 'all':
            list = WorkShop.objects.filter(date__year=year, date__month=month).order_by("-date")
            day = 0
        else:
            list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date")
    sum = 0 
    for item in list:
        sum = sum + item.price
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    return render_to_response('index.html', {'workshop': list, 'summ':sum, 'sel_year':int(year), 'sel_month':int(month), 'sel_day':int(day), 'month_days': days, 'weblink': 'workshop_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    #return HttpResponseRedirect('/workshop/view/')


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


def worktype_lookup(request):
    data = []
    if request.method == "POST":
        if request.POST.has_key(u'query'):
            value = request.POST[u'query']
            if len(value) > 2:
                results = WorkType.objects.filter(name__icontains = value, disable = False)
                data = serializers.serialize("json", results, fields=('name', 'id', 'price', 'dependence_work', 'get_sale_price', 'sale', 'work_group'))
            else:
                data = []
    return HttpResponse(data)    


def workshop_pricelist(request, pprint=False):
    list = WorkType.objects.all().values('name', 'price', 'id', 'description', 'work_group', 'work_group__name').order_by('work_group__tabindex')
    if pprint:
        return render_to_response('workshop_pricelist.html', {'work_list': list, 'pprint': True})
    else:        
        return render_to_response('index.html', {'work_list': list, 'weblink': 'workshop_pricelist.html', 'pprint': False}, context_instance=RequestContext(request, processors=[custom_proc]))    

#------------- Shop operation --------------
def shopdailysales_add(request):
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має доступу до даної дії. Можливо ви не авторизувались.')
    lastCasa = None
    now = datetime.datetime.now()
    if request.method == 'POST':
        form = ShopDailySalesForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            cash = form.cleaned_data['cash']
            tcash = form.cleaned_data['tcash']
            ocash = form.cleaned_data['ocash']
            if form.cleaned_data['user']:
                user = form.cleaned_data['user']
            else:
                user = request.user
            date = now
            if request.user.is_authenticated():
                user = request.user
            ShopDailySales(date=date, price=price, description=description, user = user, cash=cash, tcash=tcash, ocash=ocash).save()
            return HttpResponseRedirect('/shop/sale/view/')
    else:        
        unknown_client = Client.objects.get(id = settings.CLIENT_UNKNOWN)
        print "USER - " + str(unknown_client.pk)
        
        deb = ClientDebts.objects.filter(date__year=now.year, date__month=now.month, date__day=now.day).order_by()
        cred = ClientCredits.objects.filter(date__year=now.year, date__month=now.month, date__day=now.day).order_by()
#        cash_credsum = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price"))
        try:
            cashCred = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price")).get(cash_type=1)['suma']
        except ClientCredits.DoesNotExist:
            cashCred = 0
        try:
            #TcashCred = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price")).get(cash_type=2)['suma'] # PRIVAT
            TcashCred = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price")).get(cash_type=9)['suma'] # PUMB
        except ClientCredits.DoesNotExist:
            TcashCred = 0
        try:
            cashDeb = deb.values('cash').annotate(suma=Sum("price")).get(cash='True')['suma']
        except ClientDebts.DoesNotExist:
            cashDeb = 0

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
                if ci.check_pay() == False:
#                    print "FILTER ok!!!"
                    ci_status = ci_status + 1
            other_ci = ci_array.exclude(sum = F('pay'))
        except ClientInvoice.DoesNotExist:
            ci_status = 0
           
            
        #lastCasa = ShopDailySales.objects.filter(date__year=now.year, date__month=now.month).order_by('-pk')[0]
        #lastCasa = ShopDailySales.objects.filter(date__gt = now - datetime.timedelta(days=int(10))).order_by('-pk')[0]
        lastCasa = ShopDailySales.objects.latest('date')
                
        casa = cashCred - cashDeb
        form = ShopDailySalesForm(initial={'cash': casa, 'ocash': cashDeb, 'tcash':TcashCred, 'user': request.user})
    return render_to_response('index.html', {'form': form, 'weblink': 'shop_daily_sales.html', 'lastcasa': lastCasa, 'ci_status': ci_status, 'other_ci':other_ci, 'unk_cash': unk_cash}, context_instance=RequestContext(request, processors=[custom_proc]))


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
            
#    strdate = pytils_ua.dt.ru_strftime(u"%d %B %Y", datetime.datetime(int(year), int(month), 1), inflected=True)
    date_month = pytils_ua.dt.ru_strftime(u"%B %Y", datetime.datetime(int(year), int(month), 1), inflected=False)

    return render_to_response('index.html', {'sum_cred': sum_cred, 'sum_deb': sum_deb, 'Cdeb': deb, 'Ccred':cred, 'date_month': date_month, 'sel_year': int(year), 'year_list':year_list, 'sel_month':int(month), 'l_month': xrange(1,13), 'weblink': 'shop_monthly_sales_view.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def shopdailysales_view(request, year, month, day):
#    deb = ClientDebts.objects.values('date__year').annotate(suma=Sum("price"))
    cred = None
    cash_id = CashType.objects.get(id = 6) # Заробітна плата
    if auth_group(request.user, "admin") == False:
        cred = ClientCredits.objects.filter(date__year=year, date__month=month, date__day=day).exclude(cash_type = cash_id).order_by()
    else:    
        cred = ClientCredits.objects.filter(date__year=year, date__month=month, date__day=day).order_by()        

    deb = ClientDebts.objects.filter(date__year=year, date__month=month, date__day=day).order_by()
    #cred = ClientCredits.objects.filter(date__year=year, date__month=month, date__day=day).order_by()
    try:
        cash_credsum = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price"))
        cashCred = cash_credsum.get(cash_type=1)['suma']
    except ClientCredits.DoesNotExist:
        cashCred = 0
    try:
        cash_debsum = deb.values('cash').annotate(suma=Sum("price"))
        cashDeb = cash_debsum.get(cash='True')['suma']        
    except ClientDebts.DoesNotExist:
        cashDeb = 0
    casa = cashCred - cashDeb
    deb_sum = 0
    cred_sum = 0
    for c in cred:
        cred_sum = cred_sum + c.price
    for d in deb:    
        deb_sum = deb_sum + d.price
    sel_date = datetime.date(int(year), int(month), int(day))
    strdate = pytils_ua.dt.ru_strftime(u"%d %B %Y", sel_date, inflected=True)
    return render_to_response('index.html', {'Cdeb': deb, 'Ccred':cred, 'date': strdate, 'd_sum': deb_sum, 'c_sum': cred_sum, 'cash_credsum': cash_credsum, 'cash_debsum':cash_debsum, 'casa':casa, 'weblink': 'shop_daily_sales_view.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def shopdailysales_edit(request, id):
    now = datetime.datetime.now()
    a = ShopDailySales.objects.get(pk=id)
    if request.method == 'POST':
        form = ShopDailySalesForm(request.POST, instance=a)
        if form.is_valid():
            date = form.cleaned_data['date']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            cash = form.cleaned_data['cash']
            tcash = form.cleaned_data['tcash']
            ocash = form.cleaned_data['ocash']
            user = form.cleaned_data['user']
            group = Group.objects.get(name='admin') 
            if group not in request.user.groups.all():
                date = now
            if request.user.is_authenticated():
                user = request.user

            ShopDailySales(pk=a.pk, date=date, price=price, description=description, user = user, cash=cash, tcash=tcash, ocash=ocash).save()
            return HttpResponseRedirect('/shop/sale/view/')
    else:
        form = ShopDailySalesForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'shop_daily_sales.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def shopdailysales_list(request, month=None, year=None):    
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має доступу до даної дії. Можливо ви не авторизувались.')
    now = datetime.datetime.now()
    if month == None:
        month = now.month
    if year == None:
        year = now.year
    list = ShopDailySales.objects.filter(date__year=year, date__month=month)
    total_sum = list.aggregate(total_cash=Sum('cash'), total_tcash=Sum('tcash'), total_price=Sum('price'), total_ocash=Sum('ocash'))
    sum = 0 
#    for item in list:
#        sum = sum + item.price
#'summ':sum,
    return render_to_response('index.html', {'shopsales': list, 'total_sum': total_sum, 'l_month': xrange(1,13), 'sel_month':int(month), 'weblink': 'shop_sales_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def shopdailysales_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має доступу до даної дії. Можливо ви не авторизувались.')
    obj = ShopDailySales.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/shop/sale/view/')


#from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import A4
#from reportlab.pdfbase import pdfmetrics
#from reportlab.pdfbase import ttfonts


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
    return render_to_response('price_list.html', {'catalog': list})    


def shop_price_bysearch_name(request, id, pprint = False):
    url = '/shop/price/bysearch_name/'+id+'/print/'
    list = Catalog.objects.filter(name__icontains=id, count__gt=0).order_by("manufacturer","-id")
    if pprint:
        return render_to_response('price_list.html', {'catalog': list})
    return render_to_response('index.html', {'catalog': list, 'weblink': 'price_list.html', 'view': True, 'link': url, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    


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
                        sp = ShopPrice()
                        sp.catalog = cat
                        sp.scount = s
                        sp.dcount = 0
                        sp.user = request.user
                        sp.save()
                else:
                    cat = Catalog.objects.get(id=ids[0])
                    sp = ShopPrice()
                    sp.catalog = cat
                    sp.scount = s
                    sp.dcount = 0
                    sp.user = request.user
                    sp.save()
                return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")

    if request.method == 'POST':
        cat = Catalog.objects.get(id=id)
        sp = ShopPrice()
        sp.catalog = cat
        sp.scount = 1
        sp.dcount = 1
        sp.user = request.user
        sp.save()
    
    return HttpResponseRedirect('/shop/price/print/view/')
#    list = ShopPrice.objects.all().order_by("-id")
#    return render_to_response('manual_price_list.html', {'price_list': list})    


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
                print "Invoice list:"
                for obj in cat_list:
                    print "Cat = " + str(obj.catalog)
                    sp = ShopPrice()
                    sp.catalog = obj.catalog
                    sp.scount = 1 # count of price
                    sp.dcount = 0
                    sp.user = request.user
                    sp.save()
                    
                status_msg = "Цінники з накладної #" + str(di_obj.origin_id) + " додані"
                #return HttpResponse('Ваш запит виконано', content_type="text/plain;charset=UTF-8;charset=UTF-8")
                return HttpResponse(simplejson.dumps({'status': di_obj.received, 'msg': status_msg}), content_type="application/json")
    else:
        return HttpResponse(simplejson.dumps({'msg':'Ваш запит відхилено. Щось пішло не так'}), content_type="application/json", status=401)



#def shop_price_print_view(request):
#    list = ShopPrice.objects.all().order_by("user")
#    return render_to_response('manual_price_list.html', {'price_list': list, 'view': True}, context_instance=RequestContext(request, processors=[custom_proc]))    


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


def shop_price_print_list(request, pprint=False):
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
            
#    return render_to_response('mtable_pricelist.html', {'price_list': list}, context_instance=RequestContext(request, processors=[custom_proc]))
    if pprint:
        return render_to_response('manual_price_list.html', {'price_list': plist, 'view': True}, context_instance=RequestContext(request, processors=[custom_proc]))
    return render_to_response('index.html', {'weblink': 'mtable_pricelist.html', 'price_list': plist}, context_instance=RequestContext(request, processors=[custom_proc]))    
    

def shop_price_print_delete_all(request):
    list = ShopPrice.objects.all().delete()
    return render_to_response('index.html', {'weblink': 'manual_price_list.html', 'price_list': list}, context_instance=RequestContext(request, processors=[custom_proc]))        
#    return render_to_response('manual_price_list.html', {'price_list': list, 'view': True}, context_instance=RequestContext(request, processors=[custom_proc]))    


def shop_price_print_delete(request, id=None):
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
        obj = ShopPrice.objects.get(id=id)
        del_logging(obj)
        obj.delete()
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
    return render_to_response('index.html', {'costtypes': list, 'weblink': 'costtype_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def costtype_delete(request, id):
    obj = CostType.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/cost/type/view/')


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
    return render_to_response('index.html', {'form': form, 'weblink': 'cost.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'cost.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def cost_list(request):
    list = Costs.objects.all().order_by("-date")
    sum = 0
    for item in list:
        sum = sum + item.price
        
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

    return render_to_response('index.html', {'costs': pcost, 'summ': sum, 'weblink': 'cost_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def cost_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/cost/view/')
    obj = Costs.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/cost/view/')


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
        print "POST is true"
        if form.is_valid():
            print "FORM is true"
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
        print "FORM is false"
        form = SalaryForm(initial={'user': user.pk})

    return render_to_response('index.html', {'form': form, 'weblink': 'salary.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'msg_list': client_msg, 'weblink': 'client_msg_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))            


def clientmessage_delete(request, id):
    obj = ClientMessage.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/clientmessage/list/')


def payform(request):
    checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
    if bool(checkbox_list) == False:
        return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
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
            return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'chk_list': chk_list, 'error_msg':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        
    for inv in ci:
        if client!=inv.client:
            error_msg = "Вибрані позиції різних клієнтів"
            return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'error_msg':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        if inv.check_pay() and ('send_check' not in request.POST):
            if (auth_group(request.user, 'admin') == False):
                error_msg = "Вибрані позиції вже оплачені"
                return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'error_msg':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        
        client = inv.client
        #inv.pay = inv.sum
        desc = desc + inv.catalog.name + "; "
        sum = sum + inv.sum
    #-------- показ і відправка чеку на електронку ------
    if 'send_check' in request.POST:
        if inv.check_pay() == False:
            if (auth_group(request.user, 'admin') == False):
                error_msg = "Вибрані позиції ще не оплачені і на них не можна друкувати фіскальний чек"
                return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'error_msg':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        
        text = pytils_ua.numeral.in_words(int(sum))
        month = pytils_ua.dt.ru_strftime(u"%d %B %Y", ci[0].date, inflected=True)
        request.session['invoice_id'] = list_id
        check_num = Check.objects.aggregate(Max('check_num'))['check_num__max']+1
        request.session['chk_num'] = check_num
        return render_to_response('index.html', {'check_invoice': ci, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'check_num':check_num, 'weblink': 'client_invoice_sale_check.html', 'print': True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
     
    user = client.id
    if user == 138:
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
    return render_to_response('index.html', {'messages': cmsg,'checkbox': list_id, 'invoice': ci, 'summ': sum, 'balance':bal, 'client': client, 'chk_list': chk_list, 'error_msg':error_msg, 'weblink': 'payform.html', 'next': url}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        return render_to_response('index.html', {'weblink': 'client_invoice_sale_check.html', 'check_invoice': wk, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'print':'True', 'is_workshop': 'True', 'check_num':check_num, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))        

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
    return render_to_response('index.html', {'messages': cmsg,'checkbox': list_id, 'invoice': wk, 'summ': sum, 'balance':bal, 'client': client, 'weblink': 'payform.html', 'workshop':True}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_ws_payform(request):
    user = None            
    if request.user.is_authenticated():
        user = request.user
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
        print "SERVER 1 - SEND request"
        cash_id = CashType.objects.get(id = 1) # готівка Каказька
        term_id = CashType.objects.get(id = 9) # термінал Кавказька
    if int(shop_number) == 2:
        print "SERVER 2 - SEND request"
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
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_id)
                ccred.save()
        if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
            pay = request.POST['pay_terminal']
            #cash_type = CashType.objects.get(id = 9) # термінал приват = 2; ПУМБ = 9
            if float(request.POST['pay_terminal']) != 0:
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=term_id)
                ccred.save()

        ccred = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
        ccred.save()
        for item in wk:
            item.pay = True
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
        ccred = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
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
            ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_type)
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
            ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_type)
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
            
    ccred = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
    ccred.save()
    for item in wk:
        item.pay = True
        item.save()

    if client.id == 138:
        return HttpResponseRedirect('/workshop/view/')
         
    url = '/client/result/search/?id=' + str(client.id)
    return HttpResponseRedirect(url)



def client_payform(request):
    checkbox_list = [x for x in request.POST if x.startswith('checkbox_')]
    list_id = []
    user = None
    if request.user.is_authenticated():
        user = request.user
    else:
        error_msg = "Для даної дії потрібно авторизуватись!"
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

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
            if inv.check_pay():
                if (auth_group(request.user, 'admin') == False):
                    error_msg = "Вибрані позиції вже оплачені!"
                    return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'error_msg':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
       
#--------- Begin section to send data to CASA ---------
        try: 
            resp_open = requests.post(url = URL, data = PARAMS)
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
            inv.save()
            
    else:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext':'Не вибрано жодного товару', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

# Без друку касового чеку
    print_check = request.POST.get("print_check", False)
    if print_check == False:
        if (float(request.POST['pay']) != 0) or (float(request.POST['pay_terminal']) != 0):
            if (client.id == settings.CLIENT_UNKNOWN):
#                print "CLIENT id = " + str(client.id) + " -- SUM = " + str(sum)
                if (float(request.POST['pay']) + float(request.POST['pay_terminal']) < sum):
                #return HttpResponse("Невідомий клієнт не може мати борг", content_type="text/plain;charset=UTF-8;;charset=UTF-8");
                    return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': "Невідомий клієнт не може мати борг"}, context_instance=RequestContext(request, processors=[custom_proc]))
        
        if 'pay' in request.POST and request.POST['pay']:
            pay = request.POST['pay']
#            cash_type = CashType.objects.get(id = 1) # готівка
            if float(request.POST['pay']) != 0:
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_id)
                ccred.save()
        if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
            pay = request.POST['pay_terminal']
#            cash_type = CashType.objects.get(id = 9) # термінал
            if float(request.POST['pay_terminal']) != 0:
                ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=term_id)
                ccred.save()
   
        cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
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
        cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
        cdeb.save()
#===============================================================================
#        base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
#        data =  {"cmd": "cancel_receipt"}
#        url = base + urllib.urlencode(data)
#        page = urllib.urlopen(url).read()
#===============================================================================
        if status == True:
            #===================================================================
            # base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            # data =  {"cmd": "close"}
            # url = base + urllib.urlencode(data)
            # page = urllib.urlopen(url).read()
            #===================================================================
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
                #===============================================================
                # data =  {"cmd": "pay", "sum": 0, "mtype": 0}
                # url = base + urllib.urlencode(data)
                # page = urllib.urlopen(url).read()
                #===============================================================
            else:
                PARAMS['cmd'] = "pay;0;"+"%.2f" % float(pay)+";"
                resp = requests.post(url = URL, data = PARAMS)
                PARAMS['cmd'] = "pay;2;0;"
                resp = requests.post(url = URL, data = PARAMS)
                #===============================================================
                # data =  {"cmd": "pay", "sum": pay, "mtype": 0}
                # url = base + urllib.urlencode(data)
                # page = urllib.urlopen(url).read()
                # data =  {"cmd": "pay", "sum": 0, "mtype": 2}
                # url = base + urllib.urlencode(data)
                # page = urllib.urlopen(url).read()
                #===============================================================
        if float(pay) <> 0:
            PARAMS['cmd'] = 'close_port;'
            resp_close = requests.post(url = URL, data = PARAMS)
            #===================================================================
            # base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            # data =  {"cmd": "close"}
            # url = base + urllib.urlencode(data)
            # page = urllib.urlopen(url).read()
            #===================================================================

    if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
        pay = request.POST['pay_terminal']
        #cash_type = CashType.objects.get(id = 9) # термінал
        if float(request.POST['pay_terminal']) != 0:
            ccred = ClientCredits(client=client, date=now, price=pay, description=desc, user=user, cash_type=cash_id)
            ccred.save()
#===============================================================================
#            base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
#            data =  {"cmd": "open"}
#            url = base + urllib.urlencode(data)
#            page = urllib.urlopen(url).read()
#===============================================================================
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
                #===============================================================
                # data =  {"cmd": "pay", "sum": 0, "mtype": 2}
                # url = base + urllib.urlencode(data)
                # page = urllib.urlopen(url).read()
                #===============================================================
                PARAMS['cmd'] = "pay;2;0;"
                resp = requests.post(url = URL, data = PARAMS)
            else:
                PARAMS['cmd'] = "pay;2;"+"%.2f" % float(pay)+";"
                resp = requests.post(url = URL, data = PARAMS)
                PARAMS['cmd'] = "pay;0;0;"
                resp = requests.post(url = URL, data = PARAMS)
                #===============================================================
                # data =  {"cmd": "pay", "sum": pay, "mtype": 2}
                # url = base + urllib.urlencode(data)
                # page = urllib.urlopen(url).read()
                # data =  {"cmd": "pay", "sum": 0, "mtype": 0}
                # url = base + urllib.urlencode(data)
                # page = urllib.urlopen(url).read()
                #===============================================================
 
        if float(pay) <> 0:
            PARAMS['cmd'] = 'close_port;'
            resp_close = requests.post(url = URL, data = PARAMS)
            #===================================================================
            # base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            # data =  {"cmd": "close"}
            # url = base + urllib.urlencode(data)
            # page = urllib.urlopen(url).read()
            #===================================================================
               
    cdeb = ClientDebts(client=client, date=now, price=sum, description=desc, user=user, cash=0)
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
    if user_id == '0':
        user_id = None
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
            
    return render_to_response('index.html', {'sel_user':user, 'sel_year':year, 'sel_month':month, 'sel_day':day, 'month_days':days, 'buycomponents': cinvoices, 'sumall':psum, 'sum_salary':psum*0.05, 'countall':scount, 'weblink': 'report_clientinvoice_byuser.html', 'view': True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))



def worktype_report(request, id, month=None, year=None, day=None,  limit=None):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/')    

    work_type = WorkType.objects.get(id=id)
        
    if year == None:
        year = datetime.datetime.now().year
    if month <> None:
        list = WorkShop.objects.filter(date__year=year, date__month=month, work_type__id=id).order_by("-date", "-id")
    if month == None:
        month = datetime.datetime.now().month        
    if day == 'all':
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
            
    return render_to_response('index.html', {'sel_user':user, 'sel_year':year, 'years': year_list, 'sel_month':month, 'month_list':month_list, 'sel_day':day, 'month_days':days, 'workshop': cinvoices, 'sumall':psum, 'countall':scount, 'work_type': work_type,  'weblink': 'report_worktype.html', 'view': True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    



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
            
    return render_to_response('index.html', {'sel_user':user, 'sel_year':year, 'sel_month':month, 'sel_day':day, 'month_days':days, 'workshop': cinvoices, 'sumall':psum, 'sum_salary':psum*0.4, 'countall':scount, 'weblink': 'report_workshop_byuser.html', 'view': True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def all_user_salary_report(request, month=None, year=None, day=None, user_id=None):
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
        w_list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username', 'user').annotate(total_price=Sum('price'))
        c_list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum'))
        b_list = Bicycle_Sale.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum'))
    else:
        if day == 'all':
            w_list = WorkShop.objects.filter(date__year=year, date__month=month).values('user', 'user__username', 'user').annotate(total_price=Sum('price'))
            c_list = ClientInvoice.objects.filter(date__year=year, date__month=month).values('user', 'user__username').annotate(total_price=Sum('sum'))
            b_list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).values('user', 'user__username').annotate(total_price=Sum('sum'))
            qwsum = WorkShop.objects.filter(date__year=year, date__month=month, user__in = users).values('user', 'user__username', 'user').annotate(total_price=Sum('price')).order_by('user')
            qcsum = ClientInvoice.objects.filter(date__year=year, date__month=month, user__in = users).values('user', 'user__username').annotate(total_price=Sum('sum'))
            qbsum = Bicycle_Sale.objects.filter(date__year=year, date__month=month, user__in = users).values('user', 'user__username').annotate(total_price=Sum('sum'))
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
                    print 'EMPTY ' +  str(type(dic['workshop'])) + str(dic['client_inv']) + str(dic['bicycle'])
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
            w_list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username', 'user').annotate(total_price=Sum('price'))
            c_list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum'))
            b_list = Bicycle_Sale.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum'))

#    user_list = User.objects.filter(is_active = True)
#    request.user.points_set.all()

    bsum = 0
    csum = 0
    wsum = 0
    for b in b_list:
        bsum = bsum + b['total_price']
    for c in c_list:
        csum = csum + c['total_price']
    for w in w_list:
        wsum = wsum + w['total_price']
    
    return render_to_response('index.html', {'sel_year':year, 'sel_month':month, 'workshop':w_list, 'cinvoice': c_list, 'bicycle_list':b_list, 'qwsum': qbsum1,  'll':l, 'res': res, 'bike_sum': bsum, 'c_sum': csum, 'w_sum': wsum, 'weblink': 'report_salary_all_user.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
            date_start = form.cleaned_data['date_start']
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
            cash_type = CashType.objects.get(id = 1) # готівка
            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=deposit, description="Завдаток за прокат "+str(catalog), user=user, cash_type=cash_type)
            ccred.save()
            r.cred = ccred
            r.save()
            return HttpResponseRedirect('/rent/view/')
    else:
        form = RentForm(instance = a)
        #form = RentForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'rent.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    

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
    return render_to_response('index.html', {'rent': list, 'weblink': 'rent_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))    


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


from django.views.decorators.csrf import csrf_protect
from django.contrib import auth 

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


def logout(request):
    auth.logout(request)
    next_page = request.POST['next_page']
    # Перенаправление на страницу.
    if next_page:
        #return HttpResponseRedirect(next_page)
        return HttpResponseRedirect("/.")
    else:
        return HttpResponseRedirect("/.")


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
                p_cred_month = None
                cash_id = CashType.objects.get(id = 6)
                if auth_group(request.user, "admin") == False:
                    client_name = Client.objects.values('name', 'forumname', 'id', 'phone', 'birthday', 'email').get(id = clientId)
                    if str(request.user.username) == str(client_name['forumname']):
                        p_cred_month = ClientCredits.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                    else:    
                        p_cred_month = ClientCredits.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id').exclude(cash_type = cash_id)
                else: 
                    p_cred_month = ClientCredits.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                
                #p_cred_month = ClientCredits.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                #p_cred_month = ClientCredits.objects.filter(client = cid, date__month = cmonth, date__year = cyear).values('id', 'price', 'description', 'user', 'user__username', 'date')
                json = list(p_cred_month)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")

                return HttpResponse(simplejson.dumps(json), content_type='application/json')

#                search_c = ClientCredits.objects.filter(client = clientId)
#                data_c = serializers.serialize('json',search_c)
    
    return HttpResponse(data_c, content_type='application/json')    
    #return HttpResponse(simplejson.dumps(list(search)))


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
    
#                search_c = ClientDebts.objects.filter(client = clientId).prefetch_related('user__username')
#                data_c = serializers.serialize('json', search_c)
                
    
    return HttpResponse(data_c, content_type='application/json')    


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
                obj.save()

                c = InvoiceComponentList.objects.filter(id = id).values('rcount', 'user__username', 'id')
                #return HttpResponse(c, content_type='text/plain;charset=UTF-8;')
            
    results = {'value': c[0]['rcount'], 'user': c[0]['user__username'], 'id':c[0]['id']}
    json = simplejson.dumps(results)
    return HttpResponse(json, content_type='application/json')
    

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
            
                
#                    return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': 'Такого фото вже не існує, спробуйте оновити сторінку, та повторіть спробу'}, context_instance=RequestContext(request, processors=[custom_proc]))                    
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
            
    return render_to_response('index.html', {'weblink': 'photo_list.html', 'list': list, 'text': text, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        #t_catalog.type = Type.objects.get(id = q)
        t_catalog.update(type = Type.objects.get(id = q))
        return HttpResponse('ok')
        #t_catalog.save()
    if POST.has_key('id'):
#        cid = request.GET.get('id')                
        t_catalog = Catalog.objects.get(id = cid) #.values_list('type__name')
        t_catalog.type = Type.objects.get(id = q) 
        t_catalog.save()
    
    cat = Catalog.objects.filter(id = cid).values('type__name', 'type__id')
    return HttpResponse(simplejson.dumps(list(cat)), content_type="application/json")
#    return HttpResponse(cat[0][0], content_type="text/plain;charset=UTF-8;")


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


def storage_box_list(request, boxname=None, pprint=False):
    if boxname:
        list = Catalog.objects.filter(locality = boxname)
    else:
        #list = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').order_by('locality')
        list = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').values('locality').annotate(icount = Count('locality')).order_by('locality')
        #boxlist = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').values('locality').annotate(icount=Count('locality')).order_by('locality')
    if pprint:
        return render_to_response('storage_box.html', {'boxes': list, 'pprint': True}, context_instance=RequestContext(request, processors=[custom_proc]))
    cur_year = datetime.date.today().year
    return render_to_response("index.html", {"weblink": 'storage_box.html', "boxes": list, 'pprint': False, 'cur_year': cur_year}, context_instance=RequestContext(request, processors=[custom_proc]))


def storage_box_delete(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                wid = request.POST.get( 'id' )
    if wid:
        id = wid
    obj = Catalog.objects.get(id=id)
    obj.locality = ''
    obj.save()
    return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")
    #return HttpResponseRedirect('/workshop/view/')


def storage_box_delete_all(request, all=False):
    if all == True:
        obj = Catalog.objects.exclude(locality__exact='').update(locality='')
    else:
        obj = Catalog.objects.filter(count__lte = 0).update(locality='')
    
    return HttpResponse("Виконано", content_type="text/plain;charset=UTF-8;")



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
    return render_to_response("index.html", {"weblink": 'storage_boxes.html', "boxes": boxlist}, context_instance=RequestContext(request, processors=[custom_proc]))    


def inventory_list(request, year=None, month=None, day=None):
    pyear = year
    list = None
    day_list = None
    if (year == None):
        year = datetime.datetime.now().year
    else:
        year = year
    list = InventoryList.objects.filter(date__year = year)
    if (month != None):
        list = list.filter(date__month = month)
        day_list = InventoryList.objects.filter(date__year = year, date__month = month).extra({'day':"Extract(day from date)"}).values_list('day').annotate(Count('id')).order_by('day')        
    if (day != None):
        list = list.filter(date__day = day)
    if (pyear == None) and (month == None) and (day == None):
         month = datetime.datetime.now().month
         day = datetime.datetime.now().day        
         list = list.filter(date__month = month, date__day = day)
    #list = InventoryList.objects.filter(date__year = year, date__month = month, date__day = day)
    #list = InventoryList.objects.filter(date__year = year, date__month = month)
    year_list = InventoryList.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
    month_list = InventoryList.objects.filter(date__year = year).extra({'month':"Extract(month from date)"}).values_list('month').annotate(Count('id')).order_by('month')

    return render_to_response("index.html", {"weblink": 'inventory_list.html', "return_list": list, "year_list": year_list, 'month_list': month_list, 'day_list': day_list, 'cur_year': year, 'cur_month': month}, context_instance=RequestContext(request, processors=[custom_proc]))


def inventory_mistake(request, year=None, month=None, day=None):
    #im = InventoryList.objects.filter(check_all = True).annotate(dcount=Max('date')).order_by('date')
    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    #im = InventoryList.objects.filter(check_all = True, date__gt = year_ago).annotate(mdate=Max('date', distinct=True)).order_by('catalog__manufacturer', 'catalog__id').values('id', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'mdate', 'edit_date')
#    im = InventoryList.objects.filter(Q(date__gt = year_ago), ( (Q(real_count = F('count')) & Q(check_all = False)) | (Q(real_count__gt = F('count')) & Q(check_all = True)) | (Q(real_count__lt = F('count')) & Q(check_all = True)) )).annotate(mdate=Max('date', distinct=True)).order_by('-check_all', 'catalog__manufacturer', 'catalog__id').values('id', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'mdate', 'edit_date')
    im = InventoryList.objects.filter(Q(date__gt = year_ago), ( (Q(real_count = F('count')) & Q(check_all = False)) | (Q(real_count__gt = F('count')) & Q(check_all = True)) | (Q(real_count__lt = F('count')) & Q(check_all = True)) )).order_by('-check_all', 'catalog__manufacturer', 'catalog__id')
    #list = im.filter(Q(real_count__lt = F('count')) | Q(real_count__gt = F('count')))#.values('id', 'catalog', )
    #list = im.exclude( Q(real_count = F('count')) & Q(check_all = True) ) 
    #list = im.exclude( check_all = True, real_count__gt = F('count'), real_count__lt = F('count'))
    list = im 
    #list = InventoryList.objects.filter(check_all = True, real_count__lt = F('count'))
    #return render_to_response("index.html", {"weblink": 'inventory_mistake_list.html', "return_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))
    year = datetime.date.today().year
    day_list = []
    year_list = InventoryList.objects.filter().extra({'year':"Extract(year from date)"}).values_list('year').annotate(Count('id')).order_by('year')
    month_list = InventoryList.objects.filter(date__year = year).extra({'month':"Extract(month from date)"}).values_list('month').annotate(Count('id')).order_by('month')
    return render_to_response("index.html", {"weblink": 'inventory_list.html', "return_list": list, "year_list": year_list, 'month_list': month_list, 'day_list': day_list, 'cur_year': year, 'cur_month': month}, context_instance=RequestContext(request, processors=[custom_proc]))


def inventory_autocheck(request, year=None, month=None, day=None, update=False):
    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    im = InventoryList.objects.filter( Q(date__gt = year_ago), ((Q(real_count = F('count')) & Q(check_all = False))) ).annotate(mdate=Max('date', distinct=True)).order_by('catalog__id')
    if update == True:
        im.update(check_all=True)
    list = im.values('id', 'catalog__name', 'catalog__ids', 'catalog__id', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'edit_date')
    return render_to_response("index.html", {"weblink": 'inventory_mistake_list.html', "return_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))

#
def inventory_mistake_not_all(request, year=None, month=None, day=None):
    year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    exc_list =  InventoryList.objects.filter( Q(date__gt = year_ago), (Q(real_count = F('count')) & Q(check_all = True)) )
#    im = InventoryList.objects.filter(Q(date__gt = year_ago), ( (Q(real_count__gt = F('count')) & Q(check_all = False)) | (Q(real_count__lt = F('count')) & Q(check_all = False)) )).annotate(mdate=Max('date', distinct=True)).order_by('-check_all', 'catalog__manufacturer', 'catalog__id').values('id', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'mdate', 'edit_date', 'catalog__id')    
    im = InventoryList.objects.filter(Q(date__gt = year_ago), ( (Q(real_count__gt = F('count')) & Q(check_all = False)) | (Q(real_count__lt = F('count')) & Q(check_all = False)) )).order_by('-check_all', 'catalog__manufacturer', 'catalog__id')    
    list = im.exclude(catalog__id__in=[term.catalog.id for term in exc_list])
    #list = im 
    #list = InventoryList.objects.filter(check_all = True, real_count__lt = F('count'))
#    return render_to_response("index.html", {"weblink": 'inventory_mistake_list.html', "return_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))
    paginator = Paginator(list, 50)
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
    return render_to_response("index.html", {"weblink": 'inventory_list.html', "return_list": inv_list, "year_list": year_list, 'month_list': month_list, 'day_list': day_list, 'cur_year': year, 'cur_month': month}, context_instance=RequestContext(request, processors=[custom_proc]))



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
    return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext': res_str}, context_instance=RequestContext(request, processors=[custom_proc]))        
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
    return render_to_response("index.html", {"weblink": 'inventory_list.html', "return_list": list, "year_list": year_list, 'month_list': month_list, 'day_list': day_list, 'cur_year': year, 'cur_month': month}, context_instance=RequestContext(request, processors=[custom_proc]))


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
                
    jsonDict = {"status": "done", "message": "", "id": inv.id, "count": inv.count, "description": inv.description, "user__username": inv.user.username, "date": inv.date.strftime("%d/%m/%Y [%H:%M]"), "check_all":inv.check_all, "real_count":inv.real_count}
    return HttpResponse(simplejson.dumps(jsonDict), content_type="aplication/json")
    #search = "ok"
    #return HttpResponse(search, content_type="text/plain;charset=UTF-8;")


def inventory_get(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для перегляду', content_type="text/plain;charset=UTF-8;;")
            POST = request.POST  
            if POST.has_key('catalog_id'):
                cid = request.POST['catalog_id']
                i_list = InventoryList.objects.filter(catalog = cid).values('id', 'count', 'description', 'user', 'user__username', 'date', 'check_all', 'real_count', 'catalog__name', 'catalog__ids')
                json = list(i_list)
                for x in json:
                    x['date_year'] = x['date'].strftime("%Y")  
                    x['date'] = x['date'].strftime("%d/%m/%Y [%H:%M]")
                #json = serializers.serialize('json', p_cred_month, fields=('id', 'date', 'price', 'description', 'user', 'user_username'))
                return HttpResponse(simplejson.dumps(json), content_type='application/json')

    return HttpResponse(data_c, content_type='application/json')        


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

    
def inventory_delete(request, id=None):
    obj = None
    wid = None
#    if auth_group(request.user, 'admin') == False:
#        if request.is_ajax():
#            return HttpResponse('У вас не вистачає повноважень', status=401, content_type="text/plain;charset=UTF-8;")
            #return HttpResponse("У вас не вистачає повноважень", content_type="text/plain;charset=UTF-8;;charset=UTF-8;charset=UTF-8")
#        return HttpResponseRedirect('/inventory/list/')
    try:
        if request.is_ajax():
            if request.method == 'POST':  
                POST = request.POST  
                if POST.has_key('id'):
                    wid = request.POST.get( 'id' )
            obj = InventoryList.objects.get(id = wid)
            print "User = " + str(obj.user) + " - " + str(request.user == obj.user) + " / " + str(auth_group(request.user, 'admin') == False)
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
                
#                result = ''
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


def client_invoice_add(request, ids=None):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            #if POST.has_key('ids'):
            if POST.has_key('ids') and POST.has_key('count'):                
                ids = request.POST['ids'].split(',')
                count = request.POST.get('count')
            if count == '':
                result = "невірні параметри"
                return HttpResponse(result, content_type="text/plain;charset=UTF-8;;")
#                result = "Введіть правильний ID товару для обєднання"
#                return HttpResponse(result, content_type="text/plain;charset=UTF-8;;charset=UTF-8")
            client = Client.objects.get(id=138)
            for i in ids:
                c_obj = Catalog.objects.get(id = i)
                ClientInvoice(client=client, catalog = c_obj, count=count, price=c_obj.price, sum=c_obj.price*int(count), currency=c_obj.currency, sale=c_obj.sale, pay=0, user=request.user, date=datetime.datetime.now()).save()
                
            result = "ok"
            return HttpResponse(result, content_type="text/plain;charset=UTF-8;;")


def check_list(request, year=None, month=None, day=None, all=False):
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
    else:
        list = Check.objects.filter(date__year = year, date__month = month, date__day = day)#.values()
        listPay = CheckPay.objects.filter(date__year = year, date__month = month, date__day = day)
    
    sum_term = 0
    sum_cash = 0
    for lp in listPay :
        sum_term = sum_term + lp.term
        sum_cash = sum_cash + lp.cash
    
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
    return render_to_response("index.html", {"weblink": 'check_list.html', "check_list": list, "sum_term":sum_term, "sum_cash":sum_cash, "pay_list": listPay, 'sel_day':day, 'sel_month':month, 'sel_year':year, 'month_days':days, 'chk_sum': chk_sum, 'chk_sum_term': chk_sum_term}, context_instance=RequestContext(request, processors=[custom_proc]))


#************ Друк фіскального чеку на принтері ************** 
def check_print(request, num):
    list = None
    list = Check.objects.filter(check_num = num)
    list_id = []
    
    for id in list:
        list_id.append( int(id.catalog.id) )
    ci = ClientInvoice.objects.filter(id__in=list_id)
    client = ci[0].client
#    sum = 555
    ci_sum = ci.aggregate(suma=Sum('sum'))
    sum = ci_sum['suma']
    text = pytils_ua.numeral.in_words(int(sum))
    month = pytils_ua.dt.ru_strftime(u"%d %B %Y", ci[0].date, inflected=True)
    request.session['invoice_id'] = list_id
    request.session['chk_num'] = num
    check_num = num
    p_msg = "(Роздрукований)"
    return render_to_response('index.html', {'check_invoice': ci, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'check_num':check_num, 'weblink': 'client_invoice_sale_check.html', 'print': True, 'printed': p_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    
#    return render_to_response("index.html", {"weblink": 'check_list.html', "check_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))


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
                if term_number == '2':
                    URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"
                ci = ClientInvoice.objects.filter(id__in = list_id)
                chk_list = Check.objects.filter(catalog__in = ci)
                if chk_list.count() > 0:
                    message = "Даний чек вже існує"
                    return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
                else:
                    try:
                        resp_open = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = "cashier_registration;1;0"
                        resp_registration = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = 'open_receipt;0' # відкрити чек
                        resp_registration = requests.post(url = URL, data = PARAMS)
                    except:
                        message = "Сервер "+settings.HTTP_MINI_SERVER_IP+" не відповідає"
                        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")

                    res = Check.objects.aggregate(max_count=Max('check_num'))
                    chkPay = CheckPay(check_num = res['max_count'] + 1, cash = m_val, term = t_val)
                    chkPay.user = request.user
                    chkPay.save()
                    
                    for inv in ci:
                        check = Check(check_num=res['max_count'] + 1)
                        checkPay = chkPay
                        check.client = inv.client #Client.objects.get(id=client.id)
                        check.catalog = inv #ClientInvoice.objects.get(pk=inv)
                        check.description = "Готівка / Термінал"
                        check.count = inv.count
                        check.discount = inv.sale
                        t = 1
                        if m_val >= t_val:
                            t = 1
                            check.price = inv.sum #m_val
                        else: 
                            t = 9 # PUMB = 9 / PB = 2
                            check.price = t_val 
                        check.cash_type = CashType.objects.get(id = t)
                        check.print_status = False
                        check.user = request.user
                        check.save()    

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
        message = "Error"
        return HttpResponse(message, content_type="text/plain;charset=UTF-8;")


def workshop_sale_check_add(request):
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
                if term_number == '2':
                    URL = "http://" + settings.HTTP_MINI_SERVER_IP_2 + ":" + settings.HTTP_MINI_SERVER_PORT_2 +"/"
                cw = WorkShop.objects.filter(id__in = list_id)
                chk_list = Check.objects.filter(catalog__in = cw)
                if chk_list.count() > 0:
                    message = "Даний чек вже існує"
                else:
                    #base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                    #data =  {"cmd": "open"}
                    #url = base + urllib.urlencode(data)
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

                    res = Check.objects.aggregate(max_count=Max('check_num'))
                    chkPay = CheckPay(check_num = res['max_count'] + 1, cash = m_val, term = t_val)
                    chkPay.user = request.user
                    chkPay.save()
                    
                    for inv in cw:
                        check = Check(check_num=res['max_count'] + 1)
                        check.client = inv.client #Client.objects.get(id=client.id)
                        check.checkPay = chkPay
                        check.workshop = inv #ClientInvoice.objects.get(pk=inv)
                        check.description = "Майстерня. Готівка / Термінал"
                        check.count = 1
                        check.discount = inv.work_type.sale
                        check.price = inv.price
                        t = 1
                        if m_val >= t_val:
                            t = 1
                        else: 
                            t = 9 # PUMB

                        check.cash_type = CashType.objects.get(id = t)
                        check.print_status = False
                        check.user = request.user
                        check.save()

                    for inv in cw:
                        price =  "%.2f" % inv.price
                        count = "%.3f" % 1
#                        data =  {"cmd": "add_plu", "id":'99'+str(inv.work_type.pk), "cname":inv.work_type.name[:40].encode('utf8'), "price":price, "count": count, "discount": 0}
                        PARAMS['cmd'] = 'add_plu;'+'99'+str(inv.work_type.pk)+";0;0;0;1;1;1;"+price+";0;"+inv.work_type.name[:40].encode('cp1251')+";"+count+";"
                        resp = requests.post(url = URL, data = PARAMS)
                        PARAMS['cmd'] = 'sale_plu;0;0;0;'+count+";"+'99'+str(inv.work_type.pk)+";"
                        resp = requests.post(url = URL, data = PARAMS)
                        

#                        url = base + urllib.urlencode(data)
#                        page = urllib.urlopen(url).read()
#                        data =  {"cmd": "pay", "sum": 0, "mtype": 0}
#                        url = base + urllib.urlencode(data)
#                        page = urllib.urlopen(url).read()
                    
                    if m_val >= t_val:
                        if float(t_val) == 0:
                            #data =  {"cmd": "pay", "sum": 0, "mtype": 0}
                            #url = base + urllib.urlencode(data)
                            #page = urllib.urlopen(url).read()
                            PARAMS['cmd'] = "pay;"+"0;0;"
                            resp = requests.post(url = URL, data = PARAMS)

                        else:
                            #===================================================
                            # val = "%.2f" % float(m_val)
                            # data =  {"cmd": "pay", "sum": val, "mtype": 0}
                            # url = base + urllib.urlencode(data)
                            # page = urllib.urlopen(url).read()
                            # val = "%.2f" % float(t_val)
                            # data =  {"cmd": "pay", "sum": t_val, "mtype": 2}
                            # url = base + urllib.urlencode(data)
                            #===================================================
                            #page = urllib.urlopen(url).read()
                            PARAMS['cmd'] = "pay;0;"+m_val+";"
                            resp = requests.post(url = URL, data = PARAMS)
                            PARAMS['cmd'] = "pay;2;"+t_val+";"
                            resp = requests.post(url = URL, data = PARAMS)

                    else:
                        if float(m_val) == 0:
#                            data =  {"cmd": "pay", "sum": 0, "mtype": 2}
#                            url = base + urllib.urlencode(data)
#                            page = urllib.urlopen(url).read()
                            PARAMS['cmd'] = "pay;"+"2;0;"
                            resp = requests.post(url = URL, data = PARAMS)

                        else:
                            #===================================================
                            # val = "%.2f" % float(t_val)
                            # data =  {"cmd": "pay", "sum": val, "mtype": 2}
                            # url = base + urllib.urlencode(data)
                            # page = urllib.urlopen(url).read()
                            # val = "%.2f" % float(m_val)
                            # data =  {"cmd": "pay", "sum": val, "mtype": 0}
                            # url = base + urllib.urlencode(data)
                            # page = urllib.urlopen(url).read()
                            #===================================================
                            PARAMS['cmd'] = "pay;2;"+t_val+";"
                            resp = requests.post(url = URL, data = PARAMS)
                            PARAMS['cmd'] = "pay;0;"+m_val+";"
                            resp = requests.post(url = URL, data = PARAMS)
                        
                    #base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                    #data =  {"cmd": "close"}
                    #url = base + urllib.urlencode(data)
                    #page = urllib.urlopen(url).read()
                    PARAMS['cmd'] = 'close_port;'
                    resp_close = requests.post(url = URL, data = PARAMS)

                message = "Виконано"
                return HttpResponse(message, content_type="text/plain;charset=UTF-8;")
    else:
        message = "Error"
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
    return render_to_response('index.html', {'form': form, 'weblink': 'discount.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'discount.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    

def discount_list(request, year = None):
    list = None
    if year == None:
        year = datetime.datetime.now().year
#    list = Discount.objects.all()#exclude( (Q(url = '') | Q (catalog = None)) )
    list = Discount.objects.filter(date_start__year = year).all()#exclude( (Q(url = '') | Q (catalog = None)) )
    return render_to_response('index.html', {'weblink': 'discount_list.html', 'list': list, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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


def discount_lookup(request):
    data = None
    cur_date = datetime.date.today()
    if request.is_ajax():
        if request.method == "POST":
            if request.POST.has_key(u'query'):
                value = request.POST[u'query']
                if len(value) > 2:
                    model_results = Discount.objects.filter(Q(name__icontains = value), Q(date_end__gt = cur_date) ).order_by('date_start', 'name')
                    data = serializers.serialize("json", model_results, fields = ('id', 'name', 'date_start', 'date_end'), use_natural_keys=False)
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

### ---------- RRO Casa Function --------------  

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
        print "Result = " + str(resp)
        print (resp.status_code, resp.reason) #HTTP
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

    PARAMS['cmd'] = 'close_port;'
    resp_close = requests.post(url = URL, data = PARAMS)
    response.write("<br><<< Result >>> <br>" +str(resp.reason) + "<br><<< Result >>><br>" +  str(resp.text))
    return response


    
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
                    PARAMS['cmd'] = cmd
                    resp = requests.post(url = URL, data = PARAMS)
                try:
                    json = simplejson.dumps({'status_code': resp.status_code, 'resp': resp.reason})
                except:
                    error = 'Сталась помилка'
                    json = simplejson.dumps({'yData': "None", 'error': error})

                    return HttpResponse(json, content_type='application/json')
        
        #PARAMS['cmd'] = u'get_plu_info;8591;' # 3 параметр - Штучный/весовой товар (0/1)
#        PARAMS['cmd'] = u'add_plu;8591;0;0;0;1;1;1;203.00;0;Трос перемикання JAGWIRE Basics BWC1011;0.00;'.encode('cp1251')
#                                8591;0;0;1;1;1;1;15.00;0;Трос перемикання JAGWIRE Basics BWC1011;1.000;
        #PARAMS['cmd'] = 'execute_Z_report;12321;'
        #PARAMS['cmd'] = 'pay;2;191.90;'
        #PARAMS['cmd'] = 'pay;0;0;'
        
#        print "Result = " + str(resp)
#        print (resp.status_code, resp.reason) #HTTP
    except:
        print  "Error - Connection failed!"
        return HttpResponse("Connection failed! Перевірте зєднання з комп'ютером")
    
#    print "Content:" + str(resp.content)
#    print "Text:" + str(resp.request.body)    
    #print "JSON:" + str(resp.json)

    PARAMS['cmd'] = 'close_port;'
    resp_close = requests.post(url = URL, data = PARAMS)

    #return HttpResponse("Status - " + str(resp.reason) + " <br><<< Result >>>" + str(resp.text))
    return render_to_response('index.html', {'weblink': 'casa_cmd_list.html', 'id': id, 'next': current_url}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    
    response = HttpResponse()
    if resp.status_code == 200:
        response.write("Status: <br>")
        res_list = str(resp.reason).split(';') 
        response.write("Касир № <b>" + res_list[1] + "</b><br>")
        response.write("Зміна № <b>" + res_list[2] + "</b><br>")
        response.write("Стан чеку - <b>" + res_list[3] + "</b><br>")
        response.write("Тривалість зміни (0 - менше 23 годин / 1 - більше 23 годин) - <b>" + res_list[9] + "</b><br>")
        response.write("Тривалість зміни (0 - менше 24 годин / 1 - більше 24 годин) - <b>" + res_list[10] + "</b><br>")
        response.write("Дата початку зміни - <b>" + res_list[11] + "</b><br>")
        response.write("Час початку зміни - <b>" + res_list[12] + "</b><br>")
        response.write("Номер закритого чеку в даній зміні - <b>" + res_list[15] + "</b><br>")
        response.write("Номер закритого чеку в попередній зміні - <b>" + res_list[16] + "</b><br>")
        response.write("Кількість касирів - <b>" + res_list[19] + "</b><br>")
        response.write("Блокування при не передачі даних протягом 72 годин - <b>" + res_list[22] + "</b><br>")
        response.write("Точка блокування 72 години (дата)  - <b>" + res_list[23] + "</b><br>")
        response.write("Точка блокування 72 години (час)  - <b>" + res_list[24] + "</b><br>")

    PARAMS['cmd'] = 'close_port;'
    resp_close = requests.post(url = URL, data = PARAMS)
    response.write("<br><<< Result >>> <br>" +str(resp.reason) + "<br><<< Result >>><br>" +  str(resp.text))
    return response


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




    