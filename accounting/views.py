# -*- coding: utf-8 -*-

from django.db.models import Q
from django.db.models import F
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import resolve

from models import Manufacturer, Country, Type, Currency, Bicycle_Type, Bicycle,  FrameSize, Bicycle_Store, Bicycle_Sale, Bicycle_Order
from forms import ContactForm, ManufacturerForm, CountryForm, CurencyForm, CategoryForm, BicycleTypeForm, BicycleForm, BicycleFrameSizeForm, BicycleStoreForm, BicycleSaleForm, BicycleOrderForm, BicycleOrderEditForm 

from models import Catalog, Client, ClientDebts, ClientCredits, ClientInvoice, ClientOrder, ClientMessage, ClientReturn, InventoryList
from forms import CatalogForm, ClientForm, ClientDebtsForm, ClientCreditsForm, ClientInvoiceForm, ClientOrderForm

from models import Dealer, DealerManager, DealerManager, DealerPayment, DealerInvoice, InvoiceComponentList, Bank, Exchange, PreOrder, CashType
from forms import DealerManagerForm, DealerForm, DealerPaymentForm, DealerInvoiceForm, InvoiceComponentListForm, BankForm, ExchangeForm, PreOrderForm, InvoiceComponentForm, CashTypeForm

from models import WorkGroup, WorkType, WorkShop, WorkStatus, WorkTicket, CostType, Costs, ShopDailySales, Rent, ShopPrice, Photo, WorkDay, Check, CheckPay
from forms import WorkGroupForm, WorkTypeForm, WorkShopForm, WorkStatusForm, WorkTicketForm, CostTypeForm, CostsForm, ShopDailySalesForm, RentForm, WorkDayForm

  
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth

from django.http import HttpResponse 
from django.http import Http404  

from django.conf import settings
import datetime
import calendar

from django.db.models import Sum, Count, Max

from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.utils import simplejson
from django.core import serializers

import pytils_ua
import urllib
from django.conf import settings

now = datetime.datetime.now()


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }

    
def auth_group(user, group):
    return True if user.groups.filter(name=group) else False


def current_url(request):
    return request.get_full_path()


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
    #for s in obj:
    #    result = result + ' | ' + s 
    #log_file.write("DELETE FROM TABLE " + table_name + " WHERE id = " + obj.name + "\n")
    log_file.write("%s >>> DELETE FROM TABLE %s WHERE id = %s \n" % (str(datetime.datetime.now()), obj._meta.verbose_name, obj.id) )
    #obj._meta.object_name
    #obj._meta.verbose_name
    #obj.__class__.__name__
    
    #for obj_f in obj._meta.get_all_field_names():
    #    log_file.write("Key %s Value \n" % obj_f)
        
    for f in obj._meta.fields:
        log_file.write("Key = " + f.name + " - ") # field name
        s = "Value = %s" % f.value_from_object(obj) + "\n"
        log_file.write(s.encode('cp1251'))
        #log_file.write("Value = %s" % f.value_from_object(obj).encode('cp1251') + "\n") # field value
            
    #log_file.write("DELETE FROM TABLE " + table_name + obj.name)
    log_file.close()


from urlparse import urlsplit

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
            return HttpResponse(json, mimetype='application/json')            

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
    return render_to_response('index.html', {'types': list.values(), 'weblink': 'bicycle_type_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        
    destination = open(settings.MEDIA_ROOT + '/upload/'+ dir + file.name, 'wb+')
    #destination = open('/media/upload/'+file.name, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()        
    return upload_suffix


def bicycle_add(request):
    if (auth_group(request.user, 'seller') or auth_group(request.user, 'admin')) == False:
        return HttpResponseRedirect('/bicycle/view/')
#    a = Bicycle(year=datetime.date.today())
    a = Bicycle()    
    if request.method == 'POST':
#        form = BicycleForm(request.POST, request.FILES, instance=a)
        form = BicycleForm(request.POST, request.FILES)        
        if form.is_valid():
            #bicycle = form.save()
            model = form.cleaned_data['model']
            type = form.cleaned_data['type']
            brand = form.cleaned_data['brand']
            color = form.cleaned_data['color']
            photo = form.cleaned_data['photo']
            year = form.cleaned_data['year']
            weight = form.cleaned_data['weight']
            price = form.cleaned_data['price']
            currency = form.cleaned_data['currency']
            description = form.cleaned_data['description']
            sale = form.cleaned_data['sale']
            #processUploadedImage(request.FILES['photo']) 
            #photo = photo,
            #upload_path = processUploadedImage(photo)
            upload_path = ""
            #handle_uploaded_file(photo)
            Bicycle(model = model, type=type, brand = brand, color = color, photo=upload_path, weight = weight, price = price, currency = currency, description=description, year=year, sale=sale).save()
            return HttpResponseRedirect('/bicycle/view/')
            #return HttpResponseRedirect(bicycle.get_absolute_url())
    else:
#        form = BicycleForm(instance=a)
        form = BicycleForm()        

    #return render_to_response('bicycle.html', {'form': form})
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle.html', 'text': 'Велосипед з каталогу (створення)'}, context_instance=RequestContext(request, processors=[custom_proc]))


def bicycle_edit(request, id):
    if (auth_group(request.user, 'seller') or auth_group(request.user, 'admin')) == False:
        return HttpResponseRedirect('/bicycle/view/')
    
    a = Bicycle.objects.get(pk=id)
    if request.method == 'POST':
        form = BicycleForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
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
    #return render_to_response('bicycle_list.html', {'bicycles': list.values_list()})
    return render_to_response('index.html', {'bicycles': list, 'year': year, 'b_company': bike_company, 'sale': percent, 'weblink': 'bicycle_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
#===============================================================================
#            model = form.cleaned_data['model']
#            serial_number = form.cleaned_data['serial_number']
#            size = form.cleaned_data['size']
#            price = form.cleaned_data['price']
#            currency = form.cleaned_data['currency']
#            description = form.cleaned_data['description']
#            realization = form.cleaned_data['realization']
#            count = form.cleaned_data['count']
#            date = form.cleaned_data['date']            
#            Bicycle_Store(id = id, model = model, serial_number=serial_number, size = size, price = price, currency = currency, description=description, realization=realization, count=count, date=date).save()
#===============================================================================
            form.save()
            return HttpResponseRedirect('/bicycle-store/view/seller/')
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

#стара функція, можна видалити
def bicycle_store_list(request, all=False):
    list = None
    if all==True:
        list = Bicycle_Store.objects.all()
    else:
        list = Bicycle_Store.objects.filter(count=1).values('model__model', 'model__sale', 'model__year', 'model__brand__name', 'model__price', 'model__color', 'model__id', 'size__name', 'size__cm', 'size__inch', 'model__type__type', 'serial_number', 'size', 'price', 'currency', 'count', 'description', 'date', 'id')
        
    price_summ = 0
    bike_summ = 0
    for item in list:
        price_summ = price_summ + item['price'] * item['count'] 
        bike_summ = bike_summ + item['count']
    
#    fsize = FrameSize.objects.all().values('name', 'id')
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_store_list.html', 'price_summ': price_summ, 'bike_summ': bike_summ}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    a = Bicycle_Sale()
    bike = None
    serial_number = ''
    if id != None:
        bike = Bicycle_Store.objects.get(id=id)
        serial_number = bike.serial_number
        
    if request.method == 'POST':
        form = BicycleSaleForm(request.POST, initial={'currency': 3, 'date': datetime.date.today()}, instance=a)
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
            form = BicycleSaleForm(initial={'model': bike.id, 'price': bike.model.price, 'currency': bike.model.currency.id, 'sale': bike.model.sale, 'date': datetime.date.today()}, instance=a)
        else:
            form = BicycleSaleForm(initial={'currency': 3}, instance=a)
    
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
    if (year==False) & (month==False):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        #list = Bicycle_Sale.objects.all().order_by('date')
        if (id != None):
            list = Bicycle_Sale.objects.filter(model=id).order_by('date')
        else:
            list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
    else:
       list = Bicycle_Sale.objects.filter(date__year=year, date__month=month).order_by('date')
       
    psum = 0
    price_summ = 0
    service_summ = 0
    for item in list:
        price_summ = price_summ + item.price
        psum = psum + item.sum
        if item.service == False:
            service_summ =  service_summ + 1
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_list.html', 'price_summ':price_summ, 'pay_sum':psum, 'service_summ':service_summ, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
       
    price_summ = 0
    price_opt = 0
    service_summ = 0
    for item in list:
        price_summ = price_summ + item.price
        price_opt = price_opt + item.model.price
        if item.service == False:
            service_summ =  service_summ + 1
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_list.html', 'price_summ':price_summ, 'price_opt': price_opt, 'service_summ':service_summ, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
                    
                return HttpResponse(message, mimetype="text/plain")
            
    else:
        message = "Error"

#    return HttpResponse(message, mimetype="text/plain")
   
#    list = Bicycle_Sale.objects.get(id=id)
    
    #list.save()
    #list = Bicycle_Sale.objects.filter(id=id)
#    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_list.html',})

def bicycle_sale_check_add(request, id):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    message = ''
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                b_id = request.POST.get( 'id' )
                m_val = request.POST.get( 'm_value' )
                t_val = request.POST.get( 't_value' )
                bs = Bicycle_Sale.objects.get(id=id)
                chk_list = Check.objects.filter(bicycle = bs.id)
                if chk_list.count()>0:
                    message = "Даний чек вже існує"
                else:
                    base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                    data =  {"cmd": "open"}
                    url = base + urllib.urlencode(data)
#                    page = urllib.urlopen(url).read()
                    try:
                        page = urllib.urlopen(url).read()
                    except:
                        message = "Сервер не відповідає"
                        return HttpResponse(message, mimetype="text/plain")

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
#                    str = 'Велосипед '+ bs.model.model.brand +'. Модель '+ bs.model.model.model +'. '+bs.model.model.year.year+' ('+bs.model.model.color+')'
                    bike_s = 'Велосипед '+ bs.model.model.brand.name.encode('utf8') +'. Модель '+ bs.model.model.model.encode('utf8') +'. '+str(bs.model.model.year.year)+' ('+bs.model.model.color.encode('utf8')+')'
                    #bike_s = bs.model.model.model[:40].encode('utf8')
                    data =  {"cmd": "add_plu", "id":'77'+str(bs.model.pk), "cname":bike_s, "price":price, "count": count, "discount": discount}
                    url = base + urllib.urlencode(data)
                    page = urllib.urlopen(url).read()
                    if m_val >= t_val:
                        data =  {"cmd": "pay", "sum": m_val, "mtype": 0}
                        url = base + urllib.urlencode(data)
                        page = urllib.urlopen(url).read()
                        data =  {"cmd": "pay", "sum": t_val, "mtype": 2}
                        url = base + urllib.urlencode(data)
                        page = urllib.urlopen(url).read()
                    else:
                        data =  {"cmd": "pay", "sum": t_val, "mtype": 2}
                        url = base + urllib.urlencode(data)
                        page = urllib.urlopen(url).read()
                        data =  {"cmd": "pay", "sum": m_val, "mtype": 0}
                        url = base + urllib.urlencode(data)
                        page = urllib.urlopen(url).read()
                        
                    base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                    data =  {"cmd": "close"}
                    url = base + urllib.urlencode(data)
                    page = urllib.urlopen(url).read()

                    message = "Виконано"
                return HttpResponse(message, mimetype="text/plain")
    else:
        message = "Error"



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
    list = Bicycle_Sale.objects.annotate(bcount=Count("model__model__model")).order_by("model__model__brand")
#    objects.filter(date__year=now.year, date__month=now.month).extra(select={'year': "EXTRACT(year FROM date)", 'month': "EXTRACT(month from date)", 'day': "EXTRACT(day from date)"}).values('year', 'month', 'day').annotate(suma=Sum("price")).order_by()    
    return render_to_response('index.html', {'bicycles': list, 'weblink': 'bicycle_sale_report_bybrand.html'})    


def bicycle_order_add(request):
    
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
            done = form.cleaned_data['done']
            description = form.cleaned_data['description']
            user = None             
            cashtype = None
            if request.user.is_authenticated():
                user = request.user
              
            if request.POST.has_key('cash'):
                o_id = request.POST.get( 'cash' )            
                cashtype = CashType.objects.get(id = o_id)
                
            Bicycle_Order(client=client, model=model, size=size, price=price, sale=sale, currency=currency, date=date, done=done, description=description, prepay=prepay, user=user).save()
            ClientCredits(client=client, date=date, price=prepay, description="Передоплата за "+str(model), user=user, cash_type=cashtype).save()                        
            return HttpResponseRedirect('/bicycle/order/view/')
    else:
        form = BicycleOrderForm(instance = a)
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_order.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    

def bicycle_order_list(request):
    #list = Bicycle_Order.objects.all().order_by("-date")
    list = Bicycle_Order.objects.all().order_by("-date").values('model__id', 'model__model', 'model__brand__name', 'model__year', 'model__color', 'model__type__type', 'client__id', 'client__name', 'client__forumname', 'size', 'price', 'prepay', 'sale', 'date', 'done', 'id', 'currency__name')
    return render_to_response('index.html', {'order': list, 'weblink': 'bicycle_order_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    

def bicycle_order_edit(request, id):
    a = Bicycle_Order.objects.get(pk=id)
    
    if request.method == 'POST':
        #form = BicycleOrderEditForm(request.POST, instance=a, bike_id=a.model.id)
        form = BicycleOrderEditForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/bicycle/order/view/')
    else:
        #form = BicycleOrderEditForm(instance=a, bike_id=a.model.id)
        form = BicycleOrderEditForm(instance=a)
   
    return render_to_response('index.html', {'form': form, 'weblink': 'bicycle_order.html'})


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
                return HttpResponse(res, mimetype="text/plain")
                #search = Bicycle_Order.objects.filter(id=o_id).values('done', 'description')
                #return HttpResponse(simplejson.dumps(list(search)), mimetype="application/json")

    #            return HttpResponse(simplejson.dumps(list()), mimetype="application/json")
    return HttpResponse("Помилка скрипта", mimetype="text/plain")
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
    return HttpResponse(simplejson.dumps(list(search)), mimetype="application/json")

def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]

def bike_lookup(request):
    data = None
    cur_year = datetime.datetime.now().year
    #if request.is_ajax():
    if request.method == "POST":
        if request.POST.has_key(u'query'):
            value = request.POST[u'query']
            if len(value) > 2:
                model_results = Bicycle.objects.filter(year__gte=datetime.datetime(cur_year-1, 1, 1)).filter(Q(model__icontains = value) | Q(brand__name__icontains = value)).order_by('-year')
                #.values('id', 'model', 'type__type', 'brand__name',  'color', 'price', 'sale')
                #.values('id', 'model', 'type__type', 'brand__name', 'year', 'color', 'price', 'sale');
                data = serializers.serialize("json", model_results, fields = ('id', 'model', 'type', 'brand', 'color', 'price', 'year', 'sale'), use_natural_keys=False)
#                data = serializers.serialize("json", list(model_results))
#                data_dict = ValuesQuerySetToDict(model_results)
#                data = simplejson.dumps(data_dict)
            else:
                data = []
    return HttpResponse(data)                


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
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer.html'})


def dealer_edit(request, id):
    a = Dealer.objects.get(pk=id)
    if request.method == 'POST':
        form = DealerForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dealer/view/')
    else:
        form = DealerForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer.html'})

 
def dealer_del(request, id):
    obj = Dealer.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/dealer/view/')
 
 
def dealer_list(request):
    list = Dealer.objects.all()
    #return render_to_response('dealer_list.html', {'dealers': list.values_list()})
    return render_to_response('index.html', {'dealers': list, 'weblink': 'dealer_list.html'})


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
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer-manager.html'})


def dealer_manager_edit(request, id):
    a = DealerManager.objects.get(pk=id)
    if request.method == 'POST':
        form = DealerManagerForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dealer-manager/view/')
    else:
        form = DealerManagerForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'dealer-manager.html'})

 
def dealer_manager_del(request, id):
    obj = DealerManager.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/dealer-manager/view/')
 
 
def dealer_manager_list(request):
    list = DealerManager.objects.all()
    #return render_to_response('dealer-manager_list.html', {'dealer_managers': list.values_list()})
    return render_to_response('index.html', {'dealer_managers': list, 'weblink': 'dealer-manager_list.html'})


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
    return render_to_response('index.html', {'dealer_payment': list, 'weblink': 'dealer_payment_list.html'})


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
 

 
def dealer_invoice_list(request, id=False, pay='all'):
    if id == False:
        list = DealerInvoice.objects.all()
    else:
        list = DealerInvoice.objects.filter(company=id)
        if pay == 'paid':
            list = DealerInvoice.objects.filter(company=id, payment=True)
        if pay == 'notpaid':
            list = DealerInvoice.objects.filter(company=id, payment=False)
        if pay == 'sending':
            list = DealerInvoice.objects.filter(company=id, received=False)
        if pay == 'all':
            list = DealerInvoice.objects.filter(company=id)   

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
        
    return render_to_response('index.html', {'dealer_invoice': list, 'sel_company': id, 'sel_year': year, 'exchange': exchange, 'exchange_d': exchange_d, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'weblink': 'dealer_invoice_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def dealer_invoice_list_month(request, year=False, month=False, pay='all'):
    if month == False:
        now = datetime.datetime.now()
        month=now.month
    if year == False:
        now = datetime.datetime.now()
        year=now.year
    list = None
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
        now = datetime.date.today()
        html = "<html><body>Не має курсу валют. Введіть <a href=""/exchange/view/"" >курс валют на сьогодні</a> (%s) та спробуйте знову.</body></html>" % now
        return HttpResponse(html)
         
        exchange_d = 0
        exchange_e = 0
    
    return render_to_response('index.html', {'dealer_invoice': list, 'exchange': exchange, 'exchange_d': exchange_d, 'exchange_e': exchange_e, 'summ': summ, 'summ_debt': summ_debt, 'sel_month':month, 'sel_year':year, 'weblink': 'dealer_invoice_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def dealer_invoice_search(request):
    #query = request.GET.get('q', '')
    return render_to_response('index.html', {'weblink': 'dealer_invoice_search.html'})


def dealer_invoice_search_result(request):
    list = None
    if 'number' in request.GET and request.GET['number']:
        num = request.GET['number']
        list = DealerInvoice.objects.filter(origin_id__icontains = num)
    #list1 = DealerInvoice.objects.all()
    return render_to_response('index.html', {'invoice_list': list, 'weblink': 'dealer_invoice_list_search.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def invoice_new_item(request):
    date=datetime.date.today()
    start_date = datetime.date(date.year, 1, 1)
    end_date = datetime.date(date.year, 3, 31)    
    
    di = DealerInvoice.objects.filter(received = False).values_list("id", flat=True)
    
#    list_comp = InvoiceComponentList.objects.filter(invoice__date__year = date.year, invoice__date__month = date.month, invoice__id__in = di) #(invoice = list[1].id)
    nday = 10
    list_comp = InvoiceComponentList.objects.filter(invoice__date__gt = date - datetime.timedelta(days=int(nday)), invoice__id__in = di).order_by("invoice__id")    
    #date__gt=now-datetime.timedelta(days=int(nday))
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


def invoicecomponent_list(request, mid=None, cid=None, limit=0, focus=0):
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
        list = InvoiceComponentList.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')        
    elif  'id' in request.GET and request.GET['id']:
        id = request.GET['id']
        list = InvoiceComponentList.objects.filter(Q(catalog__ids__icontains=id) | Q(catalog__dealer_code__icontains=id) ).values('catalog').annotate(sum_catalog=Sum('count')).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
    if mid:
        list = InvoiceComponentList.objects.filter(catalog__manufacturer__id=mid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
        company_name = Manufacturer.objects.get(id=mid)
    if cid:
        list = InvoiceComponentList.objects.filter(catalog__type__id=cid).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale', 'catalog__count', 'catalog__type__name', 'catalog__type__id', 'catalog__user_update__username', 'catalog__last_update')
        cat_name = type_list.get(id=cid)
    
    if limit == 0:
        try:
            list = list.annotate(sum_catalog=Sum('count')).order_by("catalog__type")
        except:
            list = InvoiceComponentList.objects.none()        
    else:
        list = InvoiceComponentList.objects.all().values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__price', 'catalog__sale', 'catalog__count', 'catalog__type__id', 'catalog__description').annotate(sum_catalog=Sum('count')).order_by("catalog__type")
#        list = InvoiceComponentList.objects.all().values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price', 'catalog__sale', 'catalog__count', 'catalog__type__id').annotate(sum_catalog=Sum('count')).order_by("catalog__type")
        list = list[:limit]
    
    for item in list:
        id_list.append(item['catalog'])

    new_list = []
    sale_list = ClientInvoice.objects.filter(catalog__in=id_list).values('catalog', 'catalog__price').annotate(sum_catalog=Sum('count'))
    cat_list = Catalog.objects.filter(pk__in=id_list).values('type__name_ukr', 'description', 'locality', 'id', 'manufacturer__id', 'manufacturer__name', 'photo_url', 'last_update', 'user_update__username')        
    for element in list:
        element['balance']=element['sum_catalog']
        element['c_sale']=0
        for sale in sale_list:
            if element['catalog']==sale['catalog']:
                element['c_sale']=sale['sum_catalog']
                element['balance']=element['sum_catalog'] - element['c_sale']
        for cat in cat_list:
            if element['catalog']==cat['id']:
                element['manufacturer__id']=cat['manufacturer__id']
                element['manufacturer__name1']=cat['manufacturer__name']
                element['manufacturer__name']=cat['manufacturer__name']
                element['locality']=cat['locality']
                element['type__name_ukr']=cat['type__name_ukr']
                element['description']=cat['description']
                element['photo_url']=cat['photo_url']
                element['last_update']=cat['last_update']
                element['user_update']=cat['user_update__username']

        if element['balance']!=0:
            new_list.append(element)
            zsum = zsum + (element['balance'] * element['catalog__price'])
            zcount = zcount + element['balance']

# update count field in catalog table            
        #upd = Catalog.objects.get(pk = element['catalog'])
        #upd.count = element['balance'] 
        #upd.save()
    
    return render_to_response('index.html', {'company_list': company_list, 'type_list': type_list, 'componentlist': list, 'zsum':zsum, 'zcount':zcount, 'company_name': company_name, 'company_id':mid, 'category_name':cat_name, 'weblink': 'invoicecomponent_list.html', 'focus': focus, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def invoicecomponent_manufacturer_html(request, mid):
    list = Catalog.objects.filter(manufacturer__id=mid, count__gt=0).order_by('type__id')
    
    zcount = 0
    for elem in list:
        zcount = zcount + elem.count
    
    if mid == None:
        company_name = ""
    else:
        company_name = Manufacturer.objects.get(id=mid)
        
    return render_to_response('index.html', {'componentlist': list, 'company_name': company_name, 'zcount': zcount, 'weblink': 'component_list_by_manufacturer_html.html'})


def invoicecomponent_category_html(request, mid):
    list = Catalog.objects.filter(type__id=mid, count__gt=0).order_by('manufacturer__id')
    zcount = 0
    for elem in list:
        zcount = zcount + elem.count
    
    if mid == None:
        category = ""
    else:
        category = Type.objects.get(id=mid)
        
    return render_to_response('index.html', {'componentlist': list, 'type_name': category, 'zcount': zcount, 'weblink': 'component_list_by_type_html.html'})


from django.db.models import F

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

# Пошук товару по назві і артикулу
def invoice_search_result(request):
    list = None
    psum = 0
    zsum = 0
    scount = 0
    zcount = 0
    id_list = []
    if 'name' in request.GET and request.GET['name']:
        name = request.GET['name']
        #list = Catalog.objects.filter(name__icontains = name).order_by('manufacturer') 
#        list = InvoiceComponentList.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price', 'catalog__sale').annotate(sum_catalog=Sum('count'))
        list = InvoiceComponentList.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__manufacturer__id', 'catalog__price', 'catalog__sale', 'catalog__description', 'catalog__type__id').annotate(sum_catalog=Sum('count'))        
    elif  'id' in request.GET and request.GET['id']:
        id = request.GET['id']
        #list = InvoiceComponentList.objects.filter(catalog__ids__icontains=id)
#        list = InvoiceComponentList.objects.filter(catalog__ids__icontains=id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__manufacturer__id', 'catalog__price', 'catalog__sale', 'catalog__description', 'catalog__type__id').annotate(sum_catalog=Sum('count')) 
        list = InvoiceComponentList.objects.filter(Q(catalog__ids__icontains=id) | Q(catalog__dealer_code__icontains=id)).values('catalog').annotate(sum_catalog=Sum('count')).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__manufacturer__id', 'catalog__price', 'catalog__sale', 'catalog__description', 'catalog__type__id', 'sum_catalog', 'catalog__dealer_code')
#        list = InvoiceComponentList.objects.filter(catalog__ids__icontains=id).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'catalog__manufacturer__id', 'catalog__price', 'catalog__sale', 'catalog__type__id').annotate(sum_catalog=Sum('count'))        
        #list = Catalog.objects.filter(ids__icontains = id).order_by('manufacturer')

    for item in list:
        psum = psum + (item['catalog__price'] * item['sum_catalog'])
        scount = scount + item['sum_catalog']
        id_list.append(item['catalog'])
#        list_sale = ClientInvoice.objects.filter(catalog__name__icontains=name).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price').annotate(sum_catalog=Sum('count'))
#        list_sale = ClientInvoice.objects.filter(catalog__in=id_list).values('catalog', 'catalog__name', 'catalog__ids', 'catalog__price').annotate(sum_catalog=Sum('count'))
    sale_list = ClientInvoice.objects.filter(catalog__in=id_list).values('catalog', 'catalog__price', 'catalog__type__name', 'catalog__type__id', 'catalog__locality').annotate(sum_catalog=Sum('count'))        
    for element in list:
        element['c_sale']=0
        for sale in sale_list:
            if element['catalog']==sale['catalog']:
                element['c_sale']=sale['sum_catalog']
                element['catalog__type__name'] = sale['catalog__type__name']                
                element['catalog__type__id'] = sale['catalog__type__id']
                element['catalog__locality'] = sale['catalog__locality']
        if element.get('catalog__type__name') == None:
            element['catalog__type__name'] = Catalog.objects.values('type__name').get(id=element['catalog'])['type__name']
        element['balance']=element['sum_catalog'] - element['c_sale']                
        zsum = zsum + ((element['sum_catalog'] - element['c_sale']) * element['catalog__price'])
        zcount = zcount + (element['sum_catalog'] - element['c_sale'])
#        return render_to_response('index.html', {'componentlist': list, 'salelist': list_sale, 'allpricesum':psum, 'zsum':zsum, 'zcount':zcount, 'countsum': scount, 'weblink': 'invoicecomponent_list_test.html'})

    category_list = Type.objects.filter(name_ukr__isnull=False).order_by('name_ukr')
    company_list = Manufacturer.objects.all()
    return render_to_response('index.html', {'company_list': company_list, 'category_list': category_list, 'componentlist': list, 'allpricesum':psum, 'zsum':zsum, 'zcount':zcount, 'countsum': scount, 'weblink': 'invoicecomponent_list_test.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    #return render_to_response('index.html', {'componentlist': list, 'allpricesum':psum, 'countsum': scount, 'weblink': 'invoicecomponent_list.html'})        


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


def invoice_id_list(request, id=None, limit=0):
#    query = "select id, count(*) as ccount, invoice_id as invoice, sum(price*count) as suma from accounting_invoicecomponentlist group by invoice_id;"
    query = '''select accounting_invoicecomponentlist.id, count(*) as ccount, accounting_invoicecomponentlist.invoice_id as invoice, sum(accounting_invoicecomponentlist.price*accounting_invoicecomponentlist.count) as suma, accounting_dealerinvoice.origin_id
    from accounting_invoicecomponentlist left join accounting_dealerinvoice on accounting_dealerinvoice.id=invoice_id  
    group by accounting_invoicecomponentlist.invoice_id;'''
    
    company_list = None
#===============================================================================
#    try:
#        cursor = connection.cursor()
#        cursor.execute(query)
#        company_list = dictfetchall(cursor)
#        
#    except TypeError:
#        res = "Помилка"
#===============================================================================

    list = None
    if limit == 0:
        list = InvoiceComponentList.objects.filter(invoice=id).order_by('-id').values('catalog__price', 'count', 'id', 'price', 'invoice__origin_id', 'invoice__company__name', 'invoice__manager__name', 'invoice__price', 'invoice__currency__ids_char' , 'catalog__ids', 'catalog__manufacturer', 'catalog__name', 'rcount', 'price', 'catalog__currency__name', 'date', 'description', 'user__username', 'currency__ids_char', 'catalog__id')
    else:
        list = InvoiceComponentList.objects.filter(invoice=id).order_by('-id').values('catalog__price', 'count', 'id', 'price', 'invoice__origin_id', 'invoice__company__name', 'invoice__manager__name', 'invoice__price', 'invoice__currency__ids_char' , 'catalog__ids', 'catalog__manufacturer', 'catalog__name', 'rcount', 'price', 'catalog__currency__name', 'date', 'description', 'user__username', 'currency__ids_char', 'catalog__id')[:limit]
    psum = 0
    optsum = 0
    scount = 0
    for item in list:
        psum = psum + (item['catalog__price'] * item['count'])
        #psum = psum + (item.catalog.price * item.count)
        optsum = optsum + (item['count'] * item['price'])
        scount = scount + item['count']
    dinvoice = DealerInvoice.objects.get(id=id)    
    
    #return render_to_response('index.html', {'list': list, 'dinvoice':dinvoice, 'company_list':company_list, 'allpricesum':psum, 'alloptsum':optsum, 'countsum': scount, 'weblink': 'invoice_component_report.html'})
    return render_to_response('index.html', {'list': list, 'dinvoice':dinvoice, 'allpricesum':psum, 'alloptsum':optsum, 'countsum': scount, 'weblink': 'invoice_component_report.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def invoice_cat_id_list(request, cid=None, limit=0):
    list = InvoiceComponentList.objects.filter(catalog=cid).order_by('-id').values('catalog__price', 'count', 'id', 'price', 'invoice__origin_id', 'invoice__company__name', 'invoice__manager__name', 'invoice__price', 'invoice__currency__ids_char' , 'catalog__ids', 'catalog__manufacturer', 'catalog__name', 'rcount', 'price', 'catalog__currency__name', 'date', 'description', 'user__username', 'currency__ids_char', 'catalog__id')
    psum = 0
    scount = 0
    for item in list:
        psum = psum + (item['catalog__price'] * item['count'])
        scount = scount + item['count']
        #psum = psum + (item.catalog.price * item.count)
        #scount = scount + item.count
        
    return render_to_response('index.html', {'list': list, 'allpricesum':psum, 'countsum': scount, 'weblink': 'invoice_component_report.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def invoice_import(request):
# id / name / company / type / color / country / count/ price / currency / invoice_id / rrp_price / currency /
# id / name / count / price / currency / invoice number
    ids_list = []
#    if 'name' in request.GET and request.GET['name']:
#        name = request.GET['name']
    name = 'id'
    path = settings.MEDIA_ROOT + 'csv/' + name + '.csv'
    csvfile = open(path, 'rb')
    invoice_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
    w_file = open(settings.MEDIA_ROOT + 'csv/' + name + '_miss.csv', 'wb')
    spamwriter = csv.writer(w_file, delimiter=';', quotechar='|') #, quoting=csv.QUOTE_MINIMAL)
    for row in invoice_reader:
        id = None
        #print row[0] + " - " + row[2]
        id = row[0]
        ids_list.append(row[0])
        try:
            cat = Catalog.objects.get(Q(ids = id) | Q(dealer_code = id))
            print "ROW[6] = " + row[6]
            if int(row[6]) > 0:
                cat.price = row[6]
                print "IF = " + row[6]
            c = Currency.objects.get(id = row[4])
            inv = DealerInvoice.objects.get(id = row[5])
            InvoiceComponentList(invoice = inv, catalog = cat, count = row[2], price= row[3], currency = c, date= now).save()
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
    return HttpResponse(json, mimetype='application/json')
   
#    return render_to_response('index.html', {'categories': list, 'weblink': 'category_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return render_to_response('index.html', {'form': form, 'weblink': 'category.html'})

def category_edit(request, id):
    a = Type.objects.get(pk=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/category/view/')
    else:
        form = CategoryForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'category.html', 'text': 'Обмін валют (редагування)'})

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


def exchange_add(request):
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
    return render_to_response('index.html', {'form': form, 'weblink': 'exchange.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def exchange_list(request):
    curdate = datetime.datetime.now()
    list = Exchange.objects.filter(date__month=curdate.month)
    #return render_to_response('exchange_list.html', {'exchange': list.values()})
    return render_to_response('index.html', {'exchange': list, 'weblink': 'exchange_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


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
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            www = form.cleaned_data.get('www')
            country = form.cleaned_data.get('country')
            logo = form.cleaned_data.get('logo')
            upload_path = processUploadedImage(logo, 'manufecturer/') 
            #a = Manufacturer(name=name, description=description, www=www, logo=upload_path, country=country)
            #a.save()
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


def catalog_import(request):
# id / company / type / name / color / country / price / currency / 
# id / name / company / type / color / country / count/ price / currency / invoice_id / rrp_price / currency /

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
        #return HttpResponse("Виконано", mimetype="text/plain")

    list = Catalog.objects.filter(ids__in = ids_list)
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_add(request):
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


def catalog_edit(request, id=None):
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
                
            if auth_group(request.user, 'admin')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            
            if POST.has_key('id') and POST.has_key('price'):
                id = request.POST.get('id')
                p = request.POST.get('price')
                obj = Catalog.objects.get(id = id)
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
              #  return HttpResponse(simplejson.dumps(list(c)))
       
    a = Catalog.objects.get(pk=id)
    #url1=request.META['HTTP_REFERER']
    if request.method == 'POST':
        form = CatalogForm(request.POST, instance=a)
        if form.is_valid():
            manufacturer = form.cleaned_data['manufacturer']
            type = form.cleaned_data['type']
            a.last_update = datetime.datetime.now()
            a.user_update = request.user
            a.save()
            form.save()
            #return HttpResponseRedirect('/catalog/manufacture/' + str(manufacturer.id) + '/view/5')
            return HttpResponseRedirect('/catalog/manufacture/' + str(manufacturer.id) + '/type/'+str(type.id)+'/view')
            #return HttpResponseRedirect(str(url1))
    else:
        form = CatalogForm(instance=a)
    #url=request.META['HTTP_REFERER']
    return render_to_response('index.html', {'form': form, 'weblink': 'catalog.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_list(request, id=None):
    list = None
    if id==None:
        list = Catalog.objects.all().order_by("-id")[:10]
    else:
        list = Catalog.objects.filter(id=id)
    #return render_to_response('catalog_list.html', {'catalog': list.values_list()})
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
    obj = Catalog.objects.get(id=id)
    #del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/catalog/search/')


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
    return HttpResponse(data)    
    #return HttpResponse(json)


def photo_list(request):
    list = Photo.objects.all().values('user', 'date', 'url', 'catalog__name', 'catalog__id', 'catalog__ids', 'user__username', 'id').order_by('-date')
    return render_to_response('index.html', {'weblink': 'photo_list.html', 'list': list, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def catalog_get_locality(request):
    sel_id = None
    if request.method == 'POST':
        sel_id = request.POST.get('sel_id')
    list = Catalog.objects.get(id=sel_id)#.values_list("id", "locality")
    return HttpResponse(unicode(list.locality), mimetype='text')


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
            sale = form.cleaned_data['sale']
            summ = form.cleaned_data['summ']
            description = form.cleaned_data['description']
 
            a = Client(name=name, forumname=forumname, country=country, city=city, email=email, phone=phone, sale=sale, summ=summ, description=description)
            a.save()
            #return HttpResponseRedirect('/client/view/')
            return HttpResponseRedirect('/client/result/search/?id=' + str(a.id))
    else:
        form = ClientForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'client.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_edit(request, id):
    a = Client.objects.get(pk=id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            #return HttpResponseRedirect('/client/view/')
            return HttpResponseRedirect('/client/result/search/?id='+id)
    else:
        form = ClientForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'client.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_join(request, id=None):
    #a = Client.objects.get(pk=id)
    if request.method == 'POST':
        POST = request.POST
        if POST.has_key('client_main') and POST.has_key('client_1'): # and POST.has_key('client_1'):
            main_id = request.POST.get('client_main')
            first_id = request.POST.get('client_1')
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
    
    if (id):
        client = Client.objects.get(pk = id)
        a = ClientInvoice(client = client, date=datetime.datetime.today(), price=cat.price, sum=Catalog.objects.get(id = cid).price, sale=int(Catalog.objects.get(id = cid).sale), pay=0, count=1, currency=Currency.objects.get(id=3), catalog=Catalog.objects.get(id = cid))
    else:
        a = ClientInvoice(date=datetime.datetime.today(), price=cat.price, sum=Catalog.objects.get(id = cid).price, sale=int(Catalog.objects.get(id = cid).sale), pay=0, count=1, currency=Currency.objects.get(id=3), catalog=Catalog.objects.get(id = cid))
    if request.method == 'POST':
        form = ClientInvoiceForm(request.POST, instance = a, catalog_id=cid)
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
            if (clen is not None) and (cat.type.pk == 13):
                description = description + '\nlength:' + str(clen)
                if cat.length is not None:
                    cat.length = cat.length + clen
                else:
                    cat.length = 0

            user = None #form.cleaned_data['user_id']            
            if request.user.is_authenticated():
                user = request.user
            
            ClientInvoice(client=client, catalog=catalog, count=count, sum=sum, price=price, currency=currency, sale=sale, pay=pay, date=date, description=description, user=user).save()
            cat.count = cat.count - count
            cat.save()
            
            if pay == sum:
                desc = catalog.name
                ct = CashType.objects.get(id=1)
                ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=pay, description=desc, user=user, cash_type=ct)
                ccred.save()
                cdeb = ClientDebts(client=client, date=datetime.datetime.now(), price=sum, description=desc, user=user, cash=0)
                cdeb.save()

            #WorkGroup(name=name, description=description).save()
            return HttpResponseRedirect('/client/invoice/view/')
    else:
        form = ClientInvoiceForm(instance = a, catalog_id=cid)
    nday = 3
    nbox = cat.locality
    b_len = False
    if cat.type.pk == 13:
        b_len = True
        
    #clients_list = ClientInvoice.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'sale', 'client__name').annotate(num_inv=Count('client'))
    clients_list = ClientInvoice.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))
    return render_to_response('index.html', {'form': form, 'weblink': 'clientinvoice.html', 'clients_list': clients_list, 'box_number': nbox, 'b_len': b_len}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_invoice_edit(request, id):
    a = ClientInvoice.objects.get(id=id)
    old_count = a.count
    old_length = 0
    cat_id = a.catalog.id
    cat = Catalog.objects.get(id = cat_id)
    if request.method == 'POST':
        form = ClientInvoiceForm(request.POST, instance = a, catalog_id = cat_id)
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
            if old_count > count:
                cat.count = cat.count - (old_count - count)*-1
            else: 
                cat.count = cat.count - (old_count - count)
            cat.save()
            user = a.user
            if request.user.is_authenticated():
                user = request.user
            ClientInvoice(id=id, client=client, catalog=catalog, count=count, sum=sum, price=price, currency=currency, sale=sale, pay=pay, date=date, description=description, user=user).save()

            if pay == sum:
                desc = catalog.name
                ct = CashType.objects.get(id=1)
                ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=pay, description=desc, user=user, cash_type=ct)
                ccred.save()
                cdeb = ClientDebts(client=client, date=datetime.datetime.now(), price=sum, description=desc, user=user, cash=0)
                cdeb.save()
            
            return HttpResponseRedirect('/client/invoice/view/')
    else:
        form = ClientInvoiceForm(instance = a, catalog_id = cat_id)
        
    nday = 3 # користувачі за останні n-днів
    dlen = None
    nbox = cat.locality
    b_len = False
    if cat.type.pk == 13:
        b_len = True
        if a.description.find('length:')>=0:
            dlen = a.description.split('\n')[-1].split(':')[1]
    clients_list = ClientInvoice.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))        
    return render_to_response('index.html', {'form': form, 'weblink': 'clientinvoice.html', 'clients_list': clients_list, 'box_number': nbox, 'b_len': b_len, 'desc_len':dlen, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_invoice_delete(request, id):
    obj = ClientInvoice.objects.get(id=id)
    cat = Catalog.objects.get(id = obj.catalog.id)
    if cat.type.pk == 13:
        if obj.description.find('length:')==0:
            old_length = obj.description.split('\n')[-1].split(':')[1]
            cat.length = cat.length - float(old_length)
    del_logging(obj)
    obj.delete()
    cat.count = cat.count + obj.count
    cat.save()
    return HttpResponseRedirect('/client/invoice/view/')


def client_invoice_view(request, month=None, year=None, day=None, id=None):
    
    if year == None:
        year = datetime.datetime.now().year
    if month == None:
        month = datetime.datetime.now().month

    if day == None:
        day = datetime.datetime.now().day
        list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date", "-id").values('id', 'client__id', 'client__name', 'sum', 'count', 'catalog__ids', 'catalog__name', 'price', 'currency__name', 'sale', 'pay', 'date', 'description', 'user__username', 'catalog__count', 'catalog__locality', 'catalog__pk', 'client__forumname')
    else:
        if day == 'all':
            list = ClientInvoice.objects.filter(date__year=year, date__month=month).order_by("-date", "-id").values('id', 'client__id', 'client__name', 'sum', 'count', 'catalog__ids', 'catalog__name', 'price', 'currency__name', 'sale', 'pay', 'date', 'description', 'user__username', 'catalog__count', 'catalog__locality', 'catalog__pk', 'client__forumname')
        else:
            list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date", "-id").values('id', 'client__id', 'client__name', 'sum', 'count', 'catalog__ids', 'catalog__name', 'price', 'currency__name', 'sale', 'pay', 'date', 'description', 'user__username', 'catalog__count', 'catalog__locality', 'catalog__pk', 'client__forumname')
            day = int(day)
            
    psum = 0
    scount = 0
    for item in list:
        psum = psum + item['sum']
        scount = scount + item['count']
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    
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
            
    return render_to_response('index.html', {'sel_year':year, 'sel_month':int(month), 'month_days':days, 'sel_day':day, 'buycomponents': cinvoices, 'sumall':psum, 'countall':scount, 'weblink': 'clientinvoice_list.html', 'view': True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def client_invoice_lookup(request, client_id):
    list = None
    client_invoice_sum = 0
    if request.is_ajax():
        list = ClientInvoice.objects.filter(client=client_id).order_by("-date", "-id")
        for a in list:
            client_invoice_sum = client_invoice_sum + a.sum

        #return HttpResponse("AJAX - TEST TAB for myTable")            
        return render_to_response('clientinvoice_ajax.html', {'invoice': list, 'client_invoice_sum': client_invoice_sum})
    #return HttpResponse("TEST TAB for myTable")
    return render_to_response('clientinvoice_ajax.html', {'invoice': list})


def client_invoice_id(request, id):
    list = ClientInvoice.objects.filter(catalog__id=id).order_by("-date", "-id").values('id', 'client__id', 'client__name', 'sum', 'count', 'catalog__ids', 'catalog__name', 'price', 'currency__name', 'sale', 'pay', 'date', 'description', 'user__username', 'catalog__count', 'catalog__locality', 'catalog__pk', 'client__forumname')
    psum = 0
    scount = 0
    for item in list:
        psum = psum + item['sum']
        scount = scount + item['count']
    
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
    
    return render_to_response('index.html', {'buycomponents': cinvoices, 'sumall':psum, 'countall':scount, 'weblink': 'clientinvoice_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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

    w = render_to_response('client_invoice_sale_check.html', {'check_invoice': wk, 'month':month, 'sum': sum, 'client': client, 'str_number':text, 'print':'True', 'is_workshop': 'True', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
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


def client_invioce_return_view(request):
    cr_list = ClientReturn.objects.all()
    return render_to_response('index.html', {'return_list': cr_list, 'weblink': 'ci_return_list.html'}, context_instance=RequestContext(request, processors=[custom_proc])) 


def client_invioce_return_add(request, id):
    ci = ClientInvoice.objects.get(id=id)
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
                            
    return HttpResponse("ok", mimetype="text/plain")
 
#    cr_list = ClientReturn.objects.all()
#    return render_to_response('index.html', {'return_list': cr_list, 'weblink': 'ci_return_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))    


def client_order_list(request):
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
            catalog = None
            if post:
                catalog = Catalog.objects.get(id=post)
            form.save()
            a.catalog = catalog
            a.save()
            cred = ClientCredits.objects.get(id = a.credit.id)
            cred.price = pay
#            cred.cash_type = CashType.objects.get(name=u"Готівка")
            cred.cash_type = cash_type
            cred.save()
            return HttpResponseRedirect('/client/order/view/')
    else:
        form = ClientOrderForm(instance=a)

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



def client_invoice_sale_report(request):
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
    client = None
    #clients = Client.objects.filter(name__icontains=username)
    if description:
        clients = Client.objects.filter(Q(description__icontains=description))
    if city:
        clients = Client.objects.filter(Q(city__icontains=city))
    if phone:
        clients = Client.objects.filter(Q(phone__icontains=phone))
    if username:
        clients = Client.objects.filter(Q(name__icontains=username) | Q(forumname__icontains=username))
        
    if clients.count() == 1:
        return HttpResponseRedirect("/client/result/search/?id=" + str(clients[0].id))
    paginator = Paginator(clients, 25)
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
    
    return render_to_response('index.html', {'clients':contacts, 'weblink': 'client_list.html', 'c_count': clients.count(), 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


from django.db import connection

#----- Виписка клієнта -----
def client_result(request, tdelta = 30):
    
    user = request.GET['id'] 
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
    workshop_ticket = WorkTicket.objects.filter(client=user).values('id', 'date', 'description', 'status__name').order_by('-date')
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
    return render_to_response('index.html', {'weblink': 'client_result.html', 'clients': res, 'invoice': client_invoice, 'client_invoice_sum': client_invoice_sum, 'workshop': client_workshop, 'client_workshop_sum': client_workshop_sum, 'debt_list': debt_list, 'credit_list': credit_list, 'client_name': client_name, 'b_bike': b_bike, 'workshopTicket': workshop_ticket, 'messages': messages, 'status_msg':status_msg, 'status_rent':status_rent, 'status_order':status_order, 'tdelta': tdelta}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    list = WorkGroup.objects.all()
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
    return render_to_response('index.html', {'form': form, 'weblink': 'worktype.html'})


def worktype_edit(request, id):
    a = WorkType.objects.get(pk=id)
    if request.method == 'POST':
        form = WorkTypeForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/worktype/view/')
    else:
        form = WorkTypeForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'worktype.html'})


def worktype_list(request, id=None):
    list = None
    if id != None:
        list = WorkType.objects.filter(work_group=id)
    else:
        list = WorkType.objects.all()
    
    return render_to_response('index.html', {'worktypes': list, 'weblink': 'worktype_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

#===============================================================================
# 
# def worktype_list(request):
#    list = WorkType.objects.all()
#    return render_to_response('index.html', {'worktypes': list, 'weblink': 'worktype_list.html'})
#===============================================================================


def worktype_delete(request, id):
    obj = WorkType.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/worktype/view/')


def workstatus_add(request):
    if request.method == 'POST':
        form = WorkStatusForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            WorkStatus(name=name, description=description).save()
            return HttpResponseRedirect('/workstatus/view/')
    else:
        form = WorkStatusForm()
    return render_to_response('index.html', {'form': form, 'weblink': 'workstatus.html'})


def workstatus_edit(request, id):
    a = WorkStatus.objects.get(pk=id)
    if request.method == 'POST':
        form = WorkStatusForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/workstatus/view/')
    else:
        form = WorkStatusForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'workstatus.html'})


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
    return render_to_response('index.html', {'workstatus': list.values_list(), 'weblink': 'workstatus_list.html'})


def workstatus_delete(request, id):
    obj = WorkStatus.objects.get(id=id)
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
            description = form.cleaned_data['description']
            WorkTicket(client=client, date=date, end_date=end_date, status=status, description=description).save()
            return HttpResponseRedirect('/workticket/view/')
    else:
        #form = WorkTicketForm()

        if client != None:
            form = WorkTicketForm(initial={'client': client.id, 'status': 1})
        else:
            form = WorkTicketForm(initial={'date': datetime.datetime.today(), 'status': 1, 'end_date': datetime.datetime.now()+datetime.timedelta(3)})
        
        
    return render_to_response('index.html', {'form': form, 'weblink': 'workticket.html'})


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
                obj.save() 
                c = WorkTicket.objects.filter(pk = id).values_list('status__name', flat=True)
                return HttpResponse(c)
            if POST.has_key('desc_w'):
                id = request.POST.get('desc_w')
                desc = request.POST.get('value')
                obj = WorkTicket.objects.get(pk = id)
                obj.description = desc 
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
            description = form.cleaned_data['description']
            user = form.cleaned_data['user']
            if request.user.is_authenticated():
                user = request.user
            WorkTicket(id = id, client=client, date=date, end_date=end_date, status=status, description=description, user=user).save()
            return HttpResponseRedirect('/workticket/view/')
    else:
        form = WorkTicketForm(instance=a)
    return render_to_response('index.html', {'form': form, 'weblink': 'workticket.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def workticket_list(request, year=None, month=None, all=False, status=None):
#    cur_year = datetime.datetime.now().year
    list = None
    if month != None:
        list = WorkTicket.objects.filter(date__year=year, date__month=month)
    if (year == None) and (month == None):
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        list = WorkTicket.objects.filter(date__year=year, date__month=month)
    if all == True:
        list = WorkTicket.objects.all()
    if status == '1':
        #ws = WorkStatus.objects.get(id=status)
        list = WorkTicket.objects.filter(status__id__in=[status,2])
    if status == '4':
        list = WorkTicket.objects.filter(status__id__in=[status,4])
        
    
    return render_to_response('index.html', {'workticket':list, 'sel_year':year, 'sel_month':int(month), 'weblink': 'workticket_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def workticket_delete(request, id):
    obj = WorkTicket.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workticket/view/')


def workshop_add(request, id=None, id_client=None):
    work = None
    wclient = None
    if id != None:
        work = WorkType.objects.get(id=id)
    if id_client!=None:
        wclient = Client.objects.get(id=id_client)
    
    if request.method == 'POST':
        form = WorkShopForm(request.POST)
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            work_type = form.cleaned_data['work_type']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            pay = form.cleaned_data['pay']
            user = form.cleaned_data['user']            
            if request.user.is_authenticated():
                user = request.user
            
            WorkShop(client=client, date=date, work_type=work_type, price=price, description=description, user=user, pay=pay).save()
            return HttpResponseRedirect('/workshop/view/')
    else:
        if work != None:
            form = WorkShopForm(initial={'work_type': work.id, 'price': work.price})
        elif wclient != None:
            form = WorkShopForm(initial={'client': wclient.id})
        else:        
            form = WorkShopForm()
    
    nday = 7
    clients_list = WorkShop.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))        
    return render_to_response('index.html', {'form': form, 'weblink': 'workshop.html', 'clients_list':clients_list, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def workshop_edit(request, id):
    a = WorkShop.objects.get(pk=id)
    if request.method == 'POST':
        form = WorkShopForm(request.POST, instance=a)
        if form.is_valid():
            client = form.cleaned_data['client']
            date = form.cleaned_data['date']
            work_type = form.cleaned_data['work_type']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            pay = form.cleaned_data['pay']
            if request.user.is_authenticated():
                user = request.user
            WorkShop(id=id, client=client, date=date, work_type=work_type, price=price, description=description, pay = pay, user=user).save()
            return HttpResponseRedirect('/workshop/view/')
    else:
        form = WorkShopForm(instance=a)

    nday = 7
    clients_list = WorkShop.objects.filter(date__gt=now-datetime.timedelta(days=int(nday))).values('client__id', 'client__name', 'client__sale').annotate(num_inv=Count('client'))        
    return render_to_response('index.html', {'form': form, 'weblink': 'workshop.html', 'clients_list':clients_list}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        else:
            list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day).order_by("-date")
    sum = 0 
    for item in list:
        sum = sum + item.price
    days = xrange(1, calendar.monthrange(int(year), int(month))[1]+1)
    return render_to_response('index.html', {'workshop': list, 'summ':sum, 'sel_year':year, 'sel_month':month, 'sel_day':day, 'month_days': days, 'weblink': 'workshop_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def workshop_delete(request, id=None):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('id'):
                wid = request.POST.get( 'id' )
    if wid:
        id = wid 
    obj = WorkShop.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/workshop/view/')


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
    return HttpResponse(simplejson.dumps(list(search)), mimetype="application/json")


def workshop_pricelist(request, pprint=False):
    list = WorkType.objects.all().values('name', 'price', 'id', 'description', 'work_group', 'work_group__name').order_by('work_group__tabindex')
    if pprint:
        return render_to_response('workshop_pricelist.html', {'work_list': list, 'pprint': True})
    else:        
        return render_to_response('index.html', {'work_list': list, 'weblink': 'workshop_pricelist.html', 'pprint': False}, context_instance=RequestContext(request, processors=[custom_proc]))    

#------------- Shop operation --------------
def shopdailysales_add(request):
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
            user = form.cleaned_data['user']
            date = now
            if request.user.is_authenticated():
                user = request.user
            ShopDailySales(date=date, price=price, description=description, user = user, cash=cash, tcash=tcash, ocash=ocash).save()
            return HttpResponseRedirect('/shop/sale/view/')
    else:        
        deb = ClientDebts.objects.filter(date__year=now.year, date__month=now.month, date__day=now.day).order_by()
        cred = ClientCredits.objects.filter(date__year=now.year, date__month=now.month, date__day=now.day).order_by()
#        cash_credsum = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price"))
        try:
            cashCred = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price")).get(cash_type=1)['suma']
        except ClientCredits.DoesNotExist:
            cashCred = 0
        try:
            TcashCred = cred.values('cash_type', 'cash_type__name').annotate(suma=Sum("price")).get(cash_type=2)['suma']
        except ClientCredits.DoesNotExist:
            TcashCred = 0
        try:
            cashDeb = deb.values('cash').annotate(suma=Sum("price")).get(cash='True')['suma']
        except ClientDebts.DoesNotExist:
            cashDeb = 0

        #lastCasa = ShopDailySales.objects.filter(date__year=now.year, date__month=now.month).order_by('-pk')[0]
        #lastCasa = ShopDailySales.objects.filter(date__gt = now - datetime.timedelta(days=int(10))).order_by('-pk')[0]
        lastCasa = ShopDailySales.objects.latest('date')
                
        casa = cashCred - cashDeb
        form = ShopDailySalesForm(initial={'cash': casa, 'ocash': cashDeb, 'tcash':TcashCred})
    return render_to_response('index.html', {'form': form, 'weblink': 'shop_daily_sales.html', 'lastcasa': lastCasa}, context_instance=RequestContext(request, processors=[custom_proc]))


def shopmonthlysales_view(request, year=now.year, month=now.month):
    if auth_group(request.user, 'admin') == False:
        return HttpResponseRedirect("/.")
    deb = ClientDebts.objects.filter(date__year=year, date__month=month ).extra(select={'year': "EXTRACT(year FROM date)", 'month': "EXTRACT(month from date)", 'day': "EXTRACT(day from date)"}).values('year', 'month', 'day').annotate(suma=Sum("price")).order_by()
    cred = ClientCredits.objects.filter(Q(date__year=year), Q(date__month=month), Q(cash_type__name='Готівка') | Q(cash_type__name='Термінал pb.ua') | Q(cash_type=None)).extra(select={'year': "EXTRACT(year FROM date)", 'month': "EXTRACT(month from date)", 'day': "EXTRACT(day from date)"}).values('year', 'month', 'day').annotate(suma=Sum("price")).order_by()
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
#'date': strdate,
    return render_to_response('index.html', {'sum_cred': sum_cred, 'sum_deb': sum_deb, 'Cdeb': deb, 'Ccred':cred, 'date_month': date_month, 'sel_year': year, 'l_month': xrange(1,13), 'weblink': 'shop_monthly_sales_view.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def shopdailysales_view(request, year, month, day):
#    deb = ClientDebts.objects.values('date__year').annotate(suma=Sum("price"))
    deb = ClientDebts.objects.filter(date__year=year, date__month=month, date__day=day).order_by()
    cred = ClientCredits.objects.filter(date__year=year, date__month=month, date__day=day).order_by()
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

from django.contrib.auth.models import Group

def shopdailysales_edit(request, id):
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


def shopdailysales_list(request, month=now.month):
    list = ShopDailySales.objects.filter(date__year=now.year, date__month=month)
    sum = 0 
    for item in list:
        sum = sum + item.price
    return render_to_response('index.html', {'shopsales': list, 'summ':sum, 'weblink': 'shop_sales_list.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


def shopdailysales_delete(request, id):
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
        if request.method == 'GET':  
            GET = request.GET  
            if GET.has_key('id'):
                q = request.GET.get( 'id' )
                s = 1 
                if GET.has_key('scount'):
                    s = request.GET.get( 'scount' )
                cat = Catalog.objects.get(id=q)
                sp = ShopPrice()
                sp.catalog = cat
                sp.scount = s
                sp.dcount = 0
                sp.user = request.user
                sp.save()
                return HttpResponse("Виконано", mimetype="text/plain")

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


def shop_price_print_view(request):
    list = ShopPrice.objects.all().order_by("user")
    return render_to_response('manual_price_list.html', {'price_list': list, 'view': True}, context_instance=RequestContext(request, processors=[custom_proc]))    


def shop_price_qrcode_print_view(request):
    list = ShopPrice.objects.all().order_by("user")
    return render_to_response('manual_qrcode_price_list.html', {'price_list': list, 'view': True}, context_instance=RequestContext(request, processors=[custom_proc]))    


def shop_price_print_list(request):
    list = ShopPrice.objects.all().order_by("user", "date", "catalog__manufacturer")
#    return render_to_response('mtable_pricelist.html', {'price_list': list}, context_instance=RequestContext(request, processors=[custom_proc]))
    return render_to_response('index.html', {'weblink': 'mtable_pricelist.html', 'price_list': list}, context_instance=RequestContext(request, processors=[custom_proc]))    
    

def shop_price_print_delete_all(request):
    list = ShopPrice.objects.all().delete()
    return render_to_response('index.html', {'weblink': 'manual_price_list.html', 'price_list': list}, context_instance=RequestContext(request, processors=[custom_proc]))        
#    return render_to_response('manual_price_list.html', {'price_list': list, 'view': True}, context_instance=RequestContext(request, processors=[custom_proc]))    


def shop_price_print_delete(request, id):
    obj = ShopPrice.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/shop/price/print/list/')


import csv

def price_import(request):

    ids_list = []
#    if 'name' in request.GET and request.GET['name']:
#        name = request.GET['name']
    name = 'import'
    path = settings.MEDIA_ROOT + 'csv/' + name + '.csv'
    csvfile = open(path, 'rb')
    pricereader = csv.reader(csvfile, delimiter=';', quotechar='|')
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
            if id <> u'0':
                cat = Catalog.objects.get(ids = id)
                print('Catalog =  [' +id+ ']['+code+']# '+row[3]+'')
                ids_list.append(row[0])
            else:
                print(' CODE  ['+code+']# '+row[3]+'')
                cat = Catalog.objects.get(dealer_code = code)
                ids_list.append(row[1])
            
            #cat = Catalog.objects.get(ids = id)          
                  
            #if len(code) > 1:
            #    cat = Catalog.objects.get(dealer_code = code)
            if code != u'0':
                cat.dealer_code = code
            cat.price = row[3]
            #cat.dealer_code = row[1]
            cat.currency = Currency.objects.get(id = row[4])
            cat.last_update = datetime.datetime.now()
            #cat.user_update = request.user
            cat.user_update = User.objects.get(username='import')
            cat.save()
            
            #spamwriter.writerow([row[0], row[1], row[2], row[3], row[4]],)
        except: # Catalog.DoesNotExist:
                      
            spamwriter.writerow([row[0], row[1], row[2], row[3], row[4]])
        #return HttpResponse("Виконано", mimetype="text/plain")

    list = Catalog.objects.filter(ids__in = ids_list)
    return render_to_response('index.html', {'catalog': list, 'weblink': 'catalog_list.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
    

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
    if Check.objects.filter(catalog__id__in = list_id):
        error_msg = "Дана позиція вже існує в чеку №:"
        chk_list = Check.objects.filter(catalog__id__in = list_id).values("check_num", "catalog__catalog__name")
#        for ichek in Check.objects.filter(catalog__id__in = list_id).values("check_num"):
#            url =  '<a href="/check/'+str(ichek['check_num'])+'/print/">['+str(ichek['check_num'])+'],</a>'
            #error_msg = error_msg + "["+str(ichek['check_num'])+"]"
        return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'chk_list': chk_list, 'error_msg':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        
    for inv in ci:
        if client!=inv.client:
            error_msg = "Вибрані позиції різних клієнтів"
            return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'error_msg':error_msg, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        
        client = inv.client
        #inv.pay = inv.sum
        desc = desc + inv.catalog.name + "; "
        sum = sum + inv.sum
    #-------- показ і відправка чеку на електронку ------
    if 'send_check' in request.POST:
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
    return render_to_response('index.html', {'messages': cmsg,'checkbox': list_id, 'invoice': ci, 'summ': sum, 'balance':bal, 'client': client, 'weblink': 'payform.html', 'next': url}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        check_num = Check.objects.aggregate(Max('check_num'))['check_num__max']+1
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
    for inv in wk:
        if client!=inv.client:
            return render_to_response('index.html', {'weblink': 'error_manyclients.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))
        client = inv.client
        desc = desc + inv.work_type.name + "; "
        sum = sum + inv.price

    if (float(request.POST['pay']) != 0) or (float(request.POST['pay_terminal']) != 0):
        base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
        data =  {"cmd": "get_status"}
        url = base + urllib.urlencode(data)
        try:
            page = urllib.urlopen(url).read()
            base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            data =  {"cmd": "open"}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()
        except:
            return HttpResponse("Включіть комп'ютер з касовим апаратом")
    
    if (float(request.POST['pay']) == 0) and (float(request.POST['pay_terminal']) == 0):
        ccred = ClientDebts(client=client, date=datetime.datetime.now(), price=sum, description=desc, user=user, cash=0)
        ccred.save()
        for item in wk:
            item.pay = True
            item.save()
        if client.id == 138:
            return HttpResponseRedirect('/workshop/view/')
        url = '/client/result/search/?id=' + str(client.id)
        return HttpResponseRedirect(url)
           
    if 'pay' in request.POST and request.POST['pay']:
        pay = request.POST['pay']
        cash_type = CashType.objects.get(id = 1) # готівка
        if float(request.POST['pay']) != 0:
            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=pay, description=desc, user=user, cash_type=cash_type)
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
                check.cash_type = CashType.objects.get(id = 1)
                check.print_status = False
                check.user = user
                check.save()
                price =  "%.2f" % inv.price
                count = "%.3f" % 1
                data =  {"cmd": "add_plu", "id":'99'+str(inv.work_type.pk), "cname":inv.work_type.name[:40].encode('utf8'), "price":price, "count": count, "discount": 0}
                url = base + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
            data =  {"cmd": "pay", "sum": 0, "mtype": 0}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()
            
    if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
        pay = request.POST['pay_terminal']
        cash_type = CashType.objects.get(id = 2) # термінал
        if float(request.POST['pay_terminal']) != 0:
            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=pay, description=desc, user=user, cash_type=cash_type)
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
                check.cash_type = CashType.objects.get(id = 2)
                check.print_status = False
                check.user = user
                check.save()
                price =  "%.2f" % inv.price
                count = "%.3f" % 1
                data =  {"cmd": "add_plu", "id":'99'+str(inv.work_type.pk), "cname":inv.work_type.name[:40].encode('utf8'), "price":price, "count": count, "discount": 0}
                url = base + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
            data =  {"cmd": "pay", "sum": 0, "mtype": 2}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()

    base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
    data =  {"cmd": "close"}
    url = base + urllib.urlencode(data)
    page = urllib.urlopen(url).read()
            
    ccred = ClientDebts(client=client, date=datetime.datetime.now(), price=sum, description=desc, user=user, cash=0)
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

    desc = ""
    count = None
    sum = 0
    client = None
    res = Check.objects.aggregate(max_count=Max('check_num'))
    check = None
    
    if len(checkbox_list):
        for id in checkbox_list:
            list_id.append( int(id.replace('checkbox_', '')) )
        ci = ClientInvoice.objects.filter(id__in=list_id)
        client = ci[0].client
        
        try: 
            base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            data =  {"cmd": "get_status"}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()            
            base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            data =  {"cmd": "open"}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()
        except:
            return HttpResponse("Включіть комп'ютер з касовим апаратом")
                
        for inv in ci:
            inv.pay = inv.sum
            desc = desc + inv.catalog.name + "; "
            sum = sum + inv.sum
            inv.save()
            
    else:
        return render_to_response('index.html', {'weblink': 'error_message.html', 'mtext':'Не вибрано жодного товару', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))

    if (float(request.POST['pay']) != 0) or (float(request.POST['pay_terminal']) != 0):
        base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
        data =  {"cmd": "get_status"}
        url = base + urllib.urlencode(data)
        page = urllib.urlopen(url).read()
        try:
            page = urllib.urlopen(url).read()
        except:
            message = "Сервер не відповідає"
            return HttpResponse(message, mimetype="text/plain")
    
    if (float(request.POST['pay']) == 0) and (float(request.POST['pay_terminal']) == 0):
        cdeb = ClientDebts(client=client, date=datetime.datetime.now(), price=sum, description=desc, user=user, cash=0)
        cdeb.save()
        if client.id == 138:
            return HttpResponseRedirect('/client/invoice/view/')
        url = '/client/result/search/?id=' + str(client.id)
        return HttpResponseRedirect(url)
    
    if 'pay' in request.POST and request.POST['pay']:
        pay = request.POST['pay']
        cash_type = CashType.objects.get(id = 1) # готівка
        if float(request.POST['pay']) != 0:
            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=pay, description=desc, user=user, cash_type=cash_type)
            ccred.save()
#===============================================================================
#            base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
#            data =  {"cmd": "open"}
#            url = base + urllib.urlencode(data)
#            page = urllib.urlopen(url).read()
#===============================================================================
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
                check.cash_type = CashType.objects.get(id = 1)
                check.print_status = False
                check.user = user
                check.save()
                price =  "%.2f" % inv.price
                count = "%.3f" % inv.count                
                discount = inv.sale
                data =  {"cmd": "add_plu", "id":inv.catalog.pk, "cname":inv.catalog.name[:40].encode('utf8'), "price":price, "count": count, "discount": discount}
                url = base + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
            data =  {"cmd": "pay", "sum": 0, "mtype": 0}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()

        if float(pay) <> 0:
            base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            data =  {"cmd": "close"}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()
            

    if 'pay_terminal' in request.POST and request.POST['pay_terminal']:
        pay = request.POST['pay_terminal']
        cash_type = CashType.objects.get(id = 2) # термінал
        if float(request.POST['pay_terminal']) != 0:
            ccred = ClientCredits(client=client, date=datetime.datetime.now(), price=pay, description=desc, user=user, cash_type=cash_type)
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
                check.cash_type = CashType.objects.get(id = 2)
                check.print_status = False
                check.user = user
                check.save()
                price =  "%.2f" % inv.price
                count = "%.3f" % inv.count
                discount = inv.sale
                data =  {"cmd": "add_plu", "id":inv.catalog.pk, "cname":inv.catalog.name[:40].encode('utf8'), "price":price, "count": count, "discount": discount}
                url = base + urllib.urlencode(data)
                page = urllib.urlopen(url).read()
            data =  {"cmd": "pay", "sum": 0, "mtype": 2}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()
 
        if float(pay) <> 0:
            base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
            data =  {"cmd": "close"}
            url = base + urllib.urlencode(data)
            page = urllib.urlopen(url).read()
               
#                data =  {"id":inv.catalog.pk, "cname":inv.catalog.name[:40].encode('utf8')}
#                url = base + urllib.urlencode(data)
#                page = urllib.urlopen(url).read()
        
    cdeb = ClientDebts(client=client, date=datetime.datetime.now(), price=sum, description=desc, user=user, cash=0)
    cdeb.save()
    if client.id == 138:
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
    #user_id = 5; #choper
    #user_id = 6; #andre
    #user_id = 4; #ygrik
    #user_id = 7; #Vadymyr

    if request.user.is_authenticated():
        user_id = request.user.id
    else:
        user_id = None
    
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

    user = User.objects.get(id=user_id)
            
    return render_to_response('index.html', {'sel_user':user, 'sel_year':year, 'sel_month':month, 'sel_day':day, 'month_days':days, 'buycomponents': cinvoices, 'sumall':psum, 'sum_salary':psum*0.05, 'countall':scount, 'weblink': 'report_clientinvoice_byuser.html', 'view': True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def user_workshop_report(request, month=None, year=None, day=None, user_id=None):
    #user_id = 5; #choper
    #user_id = 6; #andre
    #user_id = 4; #ygrik
    #user_id = 7; #Vadymyr

    if request.user.is_authenticated():
        user_id = request.user.id
        #user_id = 4;
    else:
        user_id = None
    
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

    user = User.objects.get(id=user_id)
            
    return render_to_response('index.html', {'sel_user':user, 'sel_year':year, 'sel_month':month, 'sel_day':day, 'month_days':days, 'workshop': cinvoices, 'sumall':psum, 'sum_salary':psum*0.4, 'countall':scount, 'weblink': 'report_workshop_byuser.html', 'view': True, 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def all_user_salary_report(request, month=None, year=None, day=None):
   
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
        else:
            w_list = WorkShop.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username', 'user').annotate(total_price=Sum('price'))
            c_list = ClientInvoice.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum'))
            b_list = Bicycle_Sale.objects.filter(date__year=year, date__month=month, date__day=day).values('user', 'user__username').annotate(total_price=Sum('sum'))
    
    bsum = 0
    csum = 0
    wsum = 0
    for b in b_list:
        bsum = bsum + b['total_price']
    for c in c_list:
        csum = csum + c['total_price']
    for w in w_list:
        wsum = wsum + w['total_price']

    
    return render_to_response('index.html', {'sel_year':year, 'sel_month':month, 'workshop':w_list, 'cinvoice': c_list, 'bicycle_list':b_list, 'bike_sum': bsum, 'c_sum': csum, 'w_sum': wsum, 'weblink': 'report_salary_all_user.html', 'next': current_url(request)}, context_instance=RequestContext(request, processors=[custom_proc]))


def rent_add(request):
    a = Rent()
    if request.method == 'POST':
        form = RentForm(request.POST, instance = a)
        #form = RentForm(request.POST)
        if form.is_valid():
            catalog = form.cleaned_data['catalog']
            client = form.cleaned_data['client']
            date_start = form.cleaned_data['date_start']
            date_end = form.cleaned_data['date_end']
            count = form.cleaned_data['count']
            deposit = form.cleaned_data['deposit']
            status = form.cleaned_data['status']
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
            return HttpResponse(matches, mimetype="text/plain")

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

       
from django.core.mail import EmailMultiAlternatives
def sendemail(request):
    list = Catalog.objects.filter(manufacturer = 28, count__gt=0).order_by("type")    
    company = Manufacturer.objects.get(id=28)
    company_list = Manufacturer.objects.all()
    
    w = render_to_response('price_list.html', {'catalog': list, 'company': company, 'company_list': company_list,})
    
    
    subject, from_email, to = 'hello', 'rivelo@ymail.com', 'rivelo@ukr.net'
    text_content = 'This is an important message.'
#    html_content = '<p>This is an <strong>important</strong> message.</p>'
    html_content = w.content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
#    send_mail('Rivelo shop', 'Here is the new message with you check.', 'rivelo@ymail.com', ['igor.panchuk@gmail.com'], fail_silently=False)
    #send_mail('subj - Test rivelo check', 'Here is the new message with you check.', 'rivelo@ymail.com', ['igor.panchuk@gmail.com'],)
    # Define these once; use them twice!
    strFrom = 'rivelo@ymail.com'
    strTo = 'rivelo@ukr.net'
#    send_mail('Товарний Чек - Test rivelo check', 'Here is the new message with you check.', 'rivelo@ymail.com', [strTo,],)
    #send_mail('subj - Test rivelo check', ‘message’, ‘from@mail.ru’, ‘rivelo@ymail.com’)        
    #return render_to_response('index.html', {'weblink': 'index.html'})
    return render_to_response("index.html", {"weblink": 'top.html'}, context_instance=RequestContext(request, processors=[custom_proc]))


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
        
            #return HttpResponse(simplejson.dumps(TheStory), mimetype="application/json")
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
                return HttpResponse(simplejson.dumps(json), mimetype='application/json')
        
            if 'clientId' in request.POST and request.POST['clientId']:
                clientId = request.POST['clientId']
                p_cred_month = ClientCredits.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date', 'cash_type', 'cash_type__name', 'cash_type__id')
                #p_cred_month = ClientCredits.objects.filter(client = cid, date__month = cmonth, date__year = cyear).values('id', 'price', 'description', 'user', 'user__username', 'date')
                json = list(p_cred_month)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")

                return HttpResponse(simplejson.dumps(json), mimetype='application/json')

#                search_c = ClientCredits.objects.filter(client = clientId)
#                data_c = serializers.serialize('json',search_c)
    
    return HttpResponse(data_c, mimetype='application/json')    
    #return HttpResponse(simplejson.dumps(list(search)))


def client_history_debt(request):
    data_c = None
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для перегляду')
            POST = request.POST  
            if POST.has_key('client_id') and POST.has_key('cred_day'):
                cid = request.POST['client_id']
                cday = request.POST['cred_day']
                n_day = int(cday) - 30;
                p_debt_month = ClientDebts.objects.filter(client = cid, date__gt=now-datetime.timedelta(days=int(cday)), date__lt=now-datetime.timedelta(days=n_day)).values('id', 'price', 'description', 'user', 'user__username', 'date')
                json = list(p_debt_month)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")

                return HttpResponse(simplejson.dumps(json), mimetype='application/json')
                
                
            if 'clientId' in request.POST and request.POST['clientId']:
                clientId = request.POST['clientId']
                p_debt_month = ClientDebts.objects.filter(client = clientId).values('id', 'price', 'description', 'user', 'user__username', 'date')
                #p_cred_month = ClientCredits.objects.filter(client = cid, date__month = cmonth, date__year = cyear).values('id', 'price', 'description', 'user', 'user__username', 'date')
                json = list(p_debt_month)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")

                return HttpResponse(simplejson.dumps(json), mimetype='application/json')
    
#                search_c = ClientDebts.objects.filter(client = clientId).prefetch_related('user__username')
#                data_c = serializers.serialize('json', search_c)
                
    
    return HttpResponse(data_c, mimetype='application/json')    


def client_history_invoice(request):
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

                return HttpResponse(simplejson.dumps(json), mimetype='application/json')
            
    return HttpResponse()#result, mimetype='application/json')


def insertstory(request):
    if 'TextStory' in request.POST and request.POST['TextStory']:
        TheStory = request.POST['TextStory']
    #return render_to_response('news_list.html')
    search = Client.objects.filter(forumname__icontains = TheStory).values_list('name', flat=True)    
    return HttpResponse(simplejson.dumps(list(search)))


def xhr_test(request):
    if request.is_ajax():
        price = 56 #Catalog.objects.get(id=448).value("price")
        message = "Hello AJAX; Price = " + str(price)
    else:
        message = "Hello"
#    if 'TextStory' in request.POST and request.POST['TextStory']:
#        TheStory = request.POST['TextStory']
    #return HttpResponse(message, mimetype="text/plain")
    return HttpResponse(simplejson.dumps({'response': message, 'result': 'success', 'param1':'Ти таки', 'param2':'натиснув його!'}), mimetype='application/json')


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
    
    #return HttpResponse(simplejson.dumps(response), mimetype="application/json")#    return HttpResponse(simplejson.dumps(list(search)), mimetype='application/json')
    return HttpResponse(simplejson.dumps(list(search)), mimetype="application/json")
    #return HttpResponse(serialized_queryset, mimetype='application/json')
#    return HttpResponse(message, mimetype="text/plain")


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
    #return HttpResponse(simplejson.dumps(list(search)), mimetype="application/json")
    return HttpResponse(search, mimetype="text/plain")


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
                #return HttpResponse(c, mimetype='text/plain')
            
    results = {'value': c[0]['rcount'], 'user': c[0]['user__username'], 'id':c[0]['id']}
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')
    

def photo_url_add(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id') and POST.has_key('url'):
                pid = request.POST.get('id')
                p_url = request.POST.get('url')
                
                if Photo.objects.filter(url = p_url):
                    return HttpResponse("Таке фото вже існує", mimetype="text/plain")
                
                p1 = Photo(url = p_url, date = datetime.datetime.now(), user = request.user, description="")
                p1.save()
                c = Catalog.objects.get(id = pid)
                c.photo_url.add(p1)
                c.save()

    search = "ok"
    return HttpResponse(search, mimetype="text/plain")


def photo_url_get(request):
    if request.is_ajax():
        if request.method == 'POST':  
#            if auth_group(request.user, 'admin')==False:
#                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id'):
                pid = request.POST.get('id')
                #photo_list = Photo.objects.filter(catalog__id = pid).values_list('url', 'description', 'id')
                photo_list = Photo.objects.filter(catalog__id = pid).values('url', 'description', 'id')
                cat = Catalog.objects.get(id = pid)
                c_name = "[" + cat.ids + "] - " + cat.name
                try:
                    json = simplejson.dumps({'aData': list(photo_list), 'id': pid, 'cname': c_name})
                except:
                    json = simplejson.dumps({'aData': "None", 'id': pid, 'cname': c_name})
#                json = simplejson.dumps(photo_list)

    return HttpResponse(json, mimetype='application/json')


def photo_url_delete(request, id=None):
    obj = None
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/catalog/photo/list/')
    try:
        if request.is_ajax():
            if request.method == 'POST':  
                POST = request.POST  
                if POST.has_key('id'):
                    wid = request.POST.get( 'id' )
            obj = Photo.objects.get(id = wid)
            del_logging(obj)
            obj.delete()
            return HttpResponse("Виконано", mimetype="text/plain")
        else: 
            obj = Photo.objects.get(id = id)
    except:
        pass
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/catalog/photo/list/')
    

def catalog_set_type(request):
#    if request.is_ajax():
#        if request.method == 'POST':  
#            POST = request.POST  
#            if POST.has_key('value'):
#                q = request.GET.get('value')
#                cid = request.GET.get('id')
#    else:
#        message = "Error"
    if auth_group(request.user, 'seller')==False:
        return HttpResponse('Error: У вас не має прав для редагування')
    q = request.POST.get('value')
    cid = request.POST.get('id')

    t_catalog = Catalog.objects.get(id = cid) #.values_list('type__name')
    t_catalog.type = Type.objects.get(id=q) 
    t_catalog.save()
    
    cat = Catalog.objects.filter(id = cid).values('type__name', 'type__id')
    return HttpResponse(simplejson.dumps(list(cat)), mimetype="application/json")

#    return HttpResponse(cat[0][0], mimetype="text/plain")

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
        list = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').order_by('locality')
    if pprint:
        return render_to_response('storage_box.html', {'boxes': list, 'pprint': True})

    return render_to_response("index.html", {"weblink": 'storage_box.html', "boxes": list, 'pprint': False}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    return HttpResponse("Виконано", mimetype="text/plain")
    #return HttpResponseRedirect('/workshop/view/')


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
    return HttpResponse("Виконано", mimetype="text/plain")


def storage_boxes(request):
    boxlist = Catalog.objects.exclude(locality__isnull=True).exclude(locality__exact='').values('locality').annotate(icount=Count('locality')).order_by('locality')
    return render_to_response("index.html", {"weblink": 'storage_boxes.html', "boxes": boxlist}, context_instance=RequestContext(request, processors=[custom_proc]))    


def inventory_list(request, year=None, month=None, day=None):
#    if (year != None and month != None and day != None):
    if (year == None) and (month == None) and (day == None):
        day = datetime.datetime.now().day
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
    else:
        day = day
        month = month
        year = year
        
    list = InventoryList.objects.filter(date__year = year, date__month = month, date__day = day)
    return render_to_response("index.html", {"weblink": 'inventory_list.html', "return_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))


def inventory_mistake(request, year=None, month=None, day=None):
#    if (year != None and month != None and day != None):
#===============================================================================
#    if (year == None) and (month == None) and (day == None):
#        day = datetime.datetime.now().day
#        month = datetime.datetime.now().month
#        year = datetime.datetime.now().year
#    else:
#        day = day
#        month = month
#        year = year
#===============================================================================

#******** RAW SQL *******
#mysql> select t.catalog_id, t.count, t.date from ( select catalog, MAX(date) as
#mdate from accounting_inventorylist group by catalog) r inner join accounting_in
#ventorylist t on t.catalog = r.catalog and t.date=r.mdate;

#mysql> select count(t.catalog_id) from ( select catalog_id, MAX(date) as mdate f
#rom accounting_inventorylist group by catalog_id) r inner join accounting_invent
#orylist t on t.catalog_id = r.catalog_id and t.date=r.mdate where t.check_all =

#mysql> select catalog_id, count, real_count, Max(date) from accounting_inventory
#list where count != real_count and check_all=True group by catalog_id;

    #im = InventoryList.objects.filter(check_all = True).annotate(dcount=Max('date')).order_by('date')
    im = InventoryList.objects.filter(check_all = True).annotate(mdate=Max('date', distinct=True)).order_by('catalog__manufacturer', 'catalog__id').values('id', 'catalog__name', 'catalog__ids', 'catalog__manufacturer__name', 'count', 'date', 'description', 'user__username', 'real_count', 'check_all', 'mdate', 'edit_date')
    #list = im.filter(Q(real_count__lt = F('count')) | Q(real_count__gt = F('count')))#.values('id', 'catalog', )
    list = im.exclude(real_count = F('count'))
     
    #list = InventoryList.objects.filter(check_all = True, real_count__lt = F('count'))
    return render_to_response("index.html", {"weblink": 'inventory_mistake_list.html', "return_list": list}, context_instance=RequestContext(request, processors=[custom_proc]))


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
                    return HttpResponse(simplejson.dumps(jsonDict), mimetype="aplication/json")
                    #return HttpResponse(search, mimetype="text/plain")
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
    return HttpResponse(simplejson.dumps(jsonDict), mimetype="aplication/json")
    #search = "ok"
    #return HttpResponse(search, mimetype="text/plain")


def inventory_get(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для перегляду')
            POST = request.POST  
            if POST.has_key('catalog_id'):
                cid = request.POST['catalog_id']
                i_list = InventoryList.objects.filter(catalog = cid).values('id', 'count', 'description', 'user', 'user__username', 'date', 'check_all', 'real_count')

                json = list(i_list)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y [%H:%M]")
                
                #json = serializers.serialize('json', p_cred_month, fields=('id', 'date', 'price', 'description', 'user', 'user_username'))
                return HttpResponse(simplejson.dumps(json), mimetype='application/json')
        
    
    return HttpResponse(data_c, mimetype='application/json')        


def inventory_set(request):
    if request.is_ajax():
        if request.method == 'POST':  
            if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для редагування')
            POST = request.POST  
            if POST.has_key('id'):
                
                id = request.POST['id']
                i_list = InventoryList.objects.get(id = id)
                i_list.check_all = not(i_list.check_all)
                i_list.edit_date = datetime.datetime.now()
                if request.user != i_list.user:
                    return HttpResponse('Error: У вас не має прав для редагування')
                i_list.save()
                result = ''
                if i_list.check_all: 
                    result = "Повністю" 
                else:
                    result = "Частково"
                return HttpResponse(result, mimetype="text/plain")
                
    return HttpResponse("Виконано", mimetype="text/plain")
    #return HttpResponse(data_c, mimetype='application/json')        

    
def inventory_delete(request, id=None):
    obj = None
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/inventory/list/')
    try:
        if request.is_ajax():
            if request.method == 'POST':  
                POST = request.POST  
                if POST.has_key('id'):
                    wid = request.POST.get( 'id' )
            obj = InventoryList.objects.get(id = wid)
            del_logging(obj)
            obj.delete()
            return HttpResponse("Виконано", mimetype="text/plain")
        else: 
            obj = InventoryList.objects.get(id = id)
    except:
        pass
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/inventory/list/')


def catalog_join(request,id1, id2):
    if auth_group(request.user, 'admin')==False:
        return HttpResponseRedirect('/')
    if auth_group(request.user, 'seller')==False:
                return HttpResponse('Error: У вас не має прав для обєднання')
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
    else:
        day = day
        month = month
        year = year
    if all == True:
        list = Check.objects.all()
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
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('m_value'):
                m_val = request.POST.get( 'm_value' )
                t_val = request.POST.get( 't_value' )
                ci = ClientInvoice.objects.filter(id__in = list_id)
                chk_list = Check.objects.filter(catalog__in = ci)
                if chk_list.count()>0:
                    message = "Даний чек вже існує"
                else:
                    base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                    data =  {"cmd": "open"}
                    url = base + urllib.urlencode(data)
                    try:
                        page = urllib.urlopen(url).read()
                    except:
                        message = "Сервер не відповідає"
                        return HttpResponse(message, mimetype="text/plain")

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
                            t = 2
                            check.price = t_val 
                        check.cash_type = CashType.objects.get(id = t)
                        check.print_status = False
                        check.user = request.user
                        check.save()    


                    for inv in ci:
                        price =  "%.2f" % inv.price
                        count = "%.3f" % inv.count
                        discount = inv.sale
                        data =  {"cmd": "add_plu", "id":str(inv.catalog.pk), "cname":inv.catalog, "price":price, "count": count, "discount": discount}
                        url = base + urllib.urlencode(data)
                        page = urllib.urlopen(url).read()
                    
                    if m_val >= t_val:
                        if float(t_val) == 0:
                            data =  {"cmd": "pay", "sum": 0, "mtype": 0}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                        else:
                            val = "%.2f" % float(m_val)
                            data =  {"cmd": "pay", "sum": val, "mtype": 0}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                            val = "%.2f" % float(t_val)
                            data =  {"cmd": "pay", "sum": t_val, "mtype": 2}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                    else:
                        if float(m_val) == 0:
                            data =  {"cmd": "pay", "sum": 0, "mtype": 2}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                        else:
                            val = "%.2f" % float(t_val)
                            data =  {"cmd": "pay", "sum": val, "mtype": 2}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                            val = "%.2f" % float(m_val)
                            data =  {"cmd": "pay", "sum": val, "mtype": 0}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                        
                    base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                    data =  {"cmd": "close"}
                    url = base + urllib.urlencode(data)
                    page = urllib.urlopen(url).read()

                message = "Виконано"
                return HttpResponse(message, mimetype="text/plain")
    else:
        message = "Error"
        return HttpResponse(message, mimetype="text/plain")


def workshop_sale_check_add(request):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    message = ''
    list_id = request.session['invoice_id']
    count = None
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('m_value'):
                m_val = request.POST.get( 'm_value' )
                t_val = request.POST.get( 't_value' )
                cw = WorkShop.objects.filter(id__in = list_id)
                chk_list = Check.objects.filter(catalog__in = cw)
                if chk_list.count()>0:
                    message = "Даний чек вже існує"
                else:
                    base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                    data =  {"cmd": "open"}
                    url = base + urllib.urlencode(data)
                    try:
                        page = urllib.urlopen(url).read()
                    except:
                        message = "Сервер не відповідає"
                        return HttpResponse(message, mimetype="text/plain")

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
                        check.discount = 0
                        check.price = inv.price
                        t = 1
                        if m_val >= t_val:
                            t = 1
                        else: 
                            t = 2

                        check.cash_type = CashType.objects.get(id = t)
                        check.print_status = False
                        check.user = request.user
                        check.save()
                        


                    for inv in cw:
                        price =  "%.2f" % inv.price
                        count = "%.3f" % 1
                        data =  {"cmd": "add_plu", "id":'99'+str(inv.work_type.pk), "cname":inv.work_type.name[:40].encode('utf8'), "price":price, "count": count, "discount": 0}
                        url = base + urllib.urlencode(data)
                        page = urllib.urlopen(url).read()
                        data =  {"cmd": "pay", "sum": 0, "mtype": 0}
                        url = base + urllib.urlencode(data)
                        page = urllib.urlopen(url).read()
                    
                    if m_val >= t_val:
                        if float(t_val) == 0:
                            data =  {"cmd": "pay", "sum": 0, "mtype": 0}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                        else:
                            val = "%.2f" % float(m_val)
                            data =  {"cmd": "pay", "sum": val, "mtype": 0}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                            val = "%.2f" % float(t_val)
                            data =  {"cmd": "pay", "sum": t_val, "mtype": 2}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                    else:
                        if float(m_val) == 0:
                            data =  {"cmd": "pay", "sum": 0, "mtype": 2}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                        else:
                            val = "%.2f" % float(t_val)
                            data =  {"cmd": "pay", "sum": val, "mtype": 2}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                            val = "%.2f" % float(m_val)
                            data =  {"cmd": "pay", "sum": val, "mtype": 0}
                            url = base + urllib.urlencode(data)
                            page = urllib.urlopen(url).read()
                        
                    base = "http://"+settings.HTTP_MINI_SERVER_IP+":"+settings.HTTP_MINI_SERVER_PORT+"/?"
                    data =  {"cmd": "close"}
                    url = base + urllib.urlencode(data)
                    page = urllib.urlopen(url).read()

                message = "Виконано"
                return HttpResponse(message, mimetype="text/plain")
    else:
        message = "Error"
        return HttpResponse(message, mimetype="text/plain")



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
    obj = Check.objects.get(id=id)
    del_logging(obj)
    obj.delete()
    return HttpResponseRedirect('/check/list/now/')

    
    