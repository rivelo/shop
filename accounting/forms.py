# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from models import Manufacturer, Country, Type, Bicycle_Type, Bicycle, Currency, FrameSize, Bicycle_Store, Catalog, Size, Bicycle_Sale, Bicycle_Order, Wheel_Size, Storage_Type, Bicycle_Storage, Bicycle_Photo 
from models import DealerManager, DealerPayment, DealerInvoice, Dealer, Bank, ShopDailySales, PreOrder, InvoiceComponentList, ClientOrder, InventoryList, Discount
from models import Client, ClientDebts, CostType, Costs, ClientCredits, WorkGroup, WorkType, WorkShop, WorkTicket, WorkStatus, Rent, ClientInvoice, CashType, Exchange, Type, ClientMessage, WorkDay, PhoneStatus
from models import Shop, BoxName

from django.contrib.auth.models import User
import datetime

from django.db.models import Q

from django.forms import formset_factory

#TOPIC_CHOICES = (
#    ('general', 'General enquiry'),
#    ('bug', 'Bug report'),
#    ('suggestion', 'Suggestion'),
#)

def get_shop_from_ip(ip_addr):
    ip = '.'.join(ip_addr.split('.')[0:3])
    dict_shop = Shop.objects.filter( ip_addr__contains = ip )
#    print "\nIP = " + str(ip) + " >>>>> dict_shop" + str(dict_shop) 
    if dict_shop.first():
        return dict_shop.first()
    else:
        return "----"


class JQuerySelect(forms.Select):
    class Media:
        css = {
            'all': ('/media/autocomplete.css',)
        }
        js = ('/media/jquery.select-autocomplete.js', '/media/jquery-1.3.1.min.js' , '/media/jquery.autocomplete.pack.js')

class SelectFromModel(forms.Field):
    widget = forms.Select()
    def __init__(self, objects, *args, **kwargs):
        self.objects = objects
        super(SelectFromModel, self).__init__(*args, **kwargs)
        self.loadChoices()
    def loadChoices(self):
        choices = ()
        for object in self.objects.order_by('id'):
            choices += ((object.id, object.name),)
        self.widget.choices = choices
    def clean(self, value):
        value = int(value)
        for cat_id, cat_title in self.widget.choices:
            if cat_id == value:
                return self.objects.get(pk=cat_id)
        raise forms.ValidationError(u'Error Country')


class ManufacturerForm(forms.ModelForm):
    name = forms.CharField()
    www = forms.URLField(initial='http://', help_text='url', )
    country = forms.ModelChoiceField(queryset = Country.objects.all())
    logo = forms.ImageField(required=False)
    description = forms.CharField(widget=forms.Textarea())
    class Meta:
        model = Manufacturer
        fields = '__all__'

class CountryForm(forms.ModelForm):
    #name = forms.CharField(label='Country name')
    class Meta:
        model = Country
        fields = '__all__'

class BankForm(forms.ModelForm):
    name = forms.CharField(label='Bank name')
    
    class Meta:
        model = Bank
        fields = '__all__'


class CurencyForm(forms.ModelForm):
    ids = forms.CharField()
    ids_char = forms.CharField()
    name = forms.CharField()
    country = forms.ModelChoiceField(queryset = Country.objects.all())
    class Meta:
        model = Currency
        fields = '__all__'


class ExchangeForm(forms.ModelForm):
    #date = forms.DateField(initial=datetime.datetime.today)
    date = forms.DateField(initial=datetime.datetime.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))    
    #currency = SelectFromModel(objects = Currency.objects.all())
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    value = forms.DecimalField()
    class Meta:
        model = Exchange
        fields = '__all__'    

#Type model
class CategoryForm(forms.ModelForm):
    name = forms.CharField(label='Component type')
    description = forms.CharField(label='Description of type', widget=forms.Textarea())
    name_ukr = forms.CharField(label='Назва (українською)')
    description_ukr = forms.CharField(label='Опис (українською)', widget=forms.Textarea())
    class Meta:
        model = Type
        fields = '__all__'

# --------- Bicycle -------------
class BicycleTypeForm(forms.ModelForm):
#    type = forms.CharField(label='Bicycle type')
#    description = forms.CharField(label='Description of type', widget=forms.Textarea(), max_length=255)
    class Meta:
        model = Bicycle_Type
        fields = '__all__'


class BicycleFrameSizeForm(forms.ModelForm):
    name = forms.CharField(label='Назва')
    cm = forms.FloatField(min_value=0, label='Розмір, см (cm)')
    inch = forms.FloatField(min_value=0, label='Розмір, дюйми (inch)')
    class Meta:
        model = FrameSize
        fields = '__all__'    


class BicycleForm(forms.ModelForm):
    model = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size': '80'}), )
    type = forms.ModelChoiceField(queryset = Bicycle_Type.objects.all()) #adult, kids, mtb, road, hybrid
    #brand = SelectFromModel(objects=Manufacturer.objects.all())
    brand = forms.ModelChoiceField(queryset = Manufacturer.objects.all())
    #year = forms.DateField(initial=datetime.date.today, input_formats=("%d.%m.%Y"), widget=forms.DateTimeInput(format='%d.%m.%Y'))
    year = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))    
    color = forms.CharField(max_length=255)
    wheel_size = forms.ModelChoiceField(queryset = Wheel_Size.objects.all())
#    sizes = forms.CharField(required=False)
    photo = forms.ImageField(required=False)
    weight = forms.FloatField(min_value=0, initial=0)
    price = forms.FloatField(initial=0)
    offsite_url = forms.URLField(required=False)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), initial=Currency.objects.get(ids_char = 'UAH'))
    sale = forms.FloatField(min_value=0, initial=0, required=False)
    warranty = forms.IntegerField(min_value=0, initial=1)
    geometry = forms.ImageField(required=False)
    internet = forms.BooleanField(required=False)
    rating = forms.IntegerField(min_value=0, initial=0)
    description = forms.CharField(label='Description', widget=forms.Textarea(attrs={'size': '180'}), required=False)
    country_made = forms.ModelChoiceField(queryset = Country.objects.all())

    class Meta:
        model = Bicycle
        fields = '__all__'


class BicycleStoreForm(forms.ModelForm):
    model = forms.ModelChoiceField(queryset = Bicycle.objects.all(), required=False)
    serial_number = forms.CharField(max_length=50)
    size = forms.ModelChoiceField(queryset = FrameSize.objects.all())
    price = forms.FloatField(required=False)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), required=False)
    count = forms.IntegerField(min_value=0, initial = 1, required=False)
    realization = forms.BooleanField(required=False)
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)

  #  def clean_count(self):
  #      data = self.cleaned_data['count']
  #      print "\nCLEAN count = %s" % data
  #      return 1

    def is_valid(self):
#        print "\nVALID def is Work - %s" % self.errors
        """Return True if the form has no errors, or False otherwise."""
        return self.is_bound and not self.errors

    def clean(self):
        super(BicycleStoreForm, self).clean()
        return self.cleaned_data
    
        #return self
#===============================================================================
#     def clean_price(self):
#         data = self.cleaned_data['pk']
#         ins = Bicycle_Store.objects.filter(pk = data)
#         if not ins:
#             raise forms.ValidationError("Такого велосипеду не існує!")
#         return ins[0].price
# 
#     def clean_currency(self):
#         data = self.id #cleaned_data['pk']
#         ins = Bicycle_Store.objects.filter(pk = data)
#         if not ins:
#             raise forms.ValidationError("Такого велосипеду в магазині не існує!")
#         return ins[0].currency
#===============================================================================
    
    class Meta:
        model = Bicycle_Store
        fields = '__all__'


class BicycleSaleForm(forms.ModelForm):
    model = forms.ModelChoiceField(queryset = Bicycle_Store.objects.filter(count = 1), required=False, label="Модель")
    client = forms.ModelChoiceField(queryset = Client.objects.all()) #.order_by("-id"))
    price = forms.FloatField(label="Ціна")
    sum = forms.FloatField(label="Сума", initial=0)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), label="Валюта")
    sale = forms.IntegerField(initial = 0, label="Знижка")
    date = forms.DateTimeField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), label="Дата продажу")
    service = forms.BooleanField(required=False, label="Перший сервіс") 
    description = forms.CharField(label='Опис', widget=forms.Textarea(), required=False)
    #debt = forms.ModelChoiceField(queryset = ClientDebts.objects.all(), required=False)
    #debt = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True), widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        bike_id = kwargs.pop('bike_id', None)
        super(BicycleSaleForm, self).__init__(*args, **kwargs)
        if bike_id<>None:
            self.fields['model'].queryset = Bicycle_Store.objects.filter(model = bike_id)             

    class Meta:
        model = Bicycle_Sale
        fields = '__all__'
        exclude = ['debt', ]


class BicycleSaleEditForm(forms.ModelForm):
    model = forms.ModelChoiceField(queryset = Bicycle_Store.objects.none(), required=False)
    client = forms.ModelChoiceField(queryset = Client.objects.all()) #.order_by("-id"))
    price = forms.FloatField()
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    sale = forms.IntegerField(initial = 0)    
    date = forms.DateTimeField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    service = forms.BooleanField(required=False) 
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        bike_id = kwargs.pop('bike_id', None)
        super(BicycleSaleEditForm, self).__init__(*args, **kwargs)
        if bike_id<>None:
            self.fields['model'].queryset = Bicycle_Store.objects.filter(model = bike_id)             
    
    class Meta:
        model = Bicycle_Sale
        fields = '__all__'


class BicycleOrderForm(forms.ModelForm):
    cur_year = datetime.datetime.today().year
    client_id = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), max_length=50, label = 'Клієнт')
    model_id = forms.CharField(widget=forms.TextInput(attrs={'size': '100'}), label = 'Модель велосипеду')    
    size = forms.CharField(max_length=50, label = 'Розмір рами')
    price = forms.FloatField(initial = 0, label = 'Ціна')
    sale = forms.IntegerField(initial = 0, label = 'Знижка (%)')
    prepay = forms.FloatField(initial = 0, label = 'Аванс')
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), label='Валюта')
    date = forms.DateTimeField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), label='Дата')
    description = forms.CharField(label='Опис', widget=forms.Textarea(), required=False)
    
    class Meta:
        model = Bicycle_Order
        fields = '__all__'
        exclude = ['user', 'done', 'client', 'model']         


#===============================================================================
# class BicycleForm(forms.ModelForm):
#     cur_year = datetime.datetime.today().year
#     client_id = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}), max_length=50, label = 'Клієнт')
#     #client = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'autocomplete'}), queryset = Client.objects.all(), empty_label="", label = 'Клієнт')    
# #    client = forms.IntegerField(widget=forms.HiddenInput(), label = 'Клієнт')
# #    model = forms.IntegerField(widget=forms.HiddenInput(), label = 'Модель велосипеду')
#     #model = forms.ModelChoiceField(queryset = Bicycle.objects.filter(year__gte=datetime.datetime(cur_year-1, 1, 1)).order_by('-year'), empty_label="", label = 'Модель велосипеду')
#     model_id = forms.CharField(widget=forms.TextInput(attrs={'size': '100'}), label = 'Модель велосипеду')    
#     size = forms.CharField(max_length=50, label = 'Розмір рами')
#     price = forms.FloatField(initial = 0, label = 'Ціна')
#     sale = forms.IntegerField(initial = 0, label = 'Знижка (%)')
#     prepay = forms.FloatField(initial = 0, label = 'Аванс')
#     currency = forms.ModelChoiceField(queryset = Currency.objects.all(), label='Валюта')
#     date = forms.DateTimeField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), label='Дата')
#     #done = forms.BooleanField(required=False) 
#     description = forms.CharField(label='Опис', widget=forms.Textarea(), required=False)
#     
#     class Meta:
#         model = Bicycle_Order
#         fields = '__all__'
#         exclude = ['user', 'done', 'client', 'model']         
#===============================================================================


class StorageType_Form(forms.ModelForm):
    type = forms.CharField(widget=forms.TextInput(attrs={'size': 150, }), max_length=255, label = 'Назва')
    price = forms.FloatField(initial = 0, label = 'Ціна')
    description = forms.CharField(label='Опис', widget=forms.Textarea(), required=False)
    
    class Meta:
        model = Storage_Type
        fields = '__all__'
        exclude = []         


class BicycleStorage_Form(forms.ModelForm):
    client = forms.CharField(widget=forms.TextInput(attrs={'size': '100'}), max_length=50, label = 'Клієнт')
    model = forms.CharField(widget=forms.TextInput(attrs={'size': 150, 'title': 'Модель велосипеду',}), label = 'Модель велосипеду')
    color = forms.CharField(widget=forms.TextInput(attrs={'size': 50,}), required=False)
    size = forms.FloatField(initial = 0, label = 'Розмір рами', help_text=' см', required=False)
    wheel_size = forms.ModelChoiceField(queryset = Wheel_Size.objects.all())
    type = forms.ModelChoiceField(queryset = Storage_Type.objects.all(), label = 'Вид зберігання') #full time / 1,2 riding time / 1 month
    biketype = forms.ModelChoiceField(queryset = Bicycle_Type.objects.all()) #adult, kids, mtb, road, hybrid
    serial_number = forms.SlugField(max_length=50, error_messages={'required': 'Введіть серійний номер рами який складається з літер та цифр'}, label = 'Серійний номер')
    service = forms.BooleanField(initial = False, required=False)
    washing = forms.BooleanField(initial = False, required=False)
    #photo = forms.ImageField(required=False)
    #photo = forms.ImageField(widget=files_widget.forms.ImagesWidget())
    date_in = forms.DateField(initial = datetime.date.today, label='Дата', input_formats=['%d.%m.%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    d_out = (datetime.date.today().month+4)%12
    if d_out == 0:
        d_out = 1
    date_out = forms.DateField(input_formats=['%d.%m.%Y', '%d/%m/%Y'], initial = datetime.date.today().replace(month= d_out, day=1), widget=forms.DateTimeInput(format='%d.%m.%Y'), label='Дата завершення зберігання')
    done = forms.BooleanField(initial = False, required=False)        
    price = forms.FloatField(initial = 0, label = 'Ціна велосипеду (оціночна)', help_text=' гривень')
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), label='Валюта', initial = 3)
    #date = forms.DateTimeField(initial = datetime.datetime.today(), input_formats=['%Y.%m.%d. %H:%M:%S'], label='Дата створення', widget=forms.SplitDateTimeWidget(date_format='%d.%m.%Y', time_format='%H:%M:%S'))
    date = forms.DateTimeField(initial = datetime.datetime.today, input_formats=['%d.%m.%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M:%S'), )    
    description = forms.CharField(label='Опис', widget=forms.Textarea(), required=False, help_text='Опис велосипеду, зовнішній стан, наявність аксесуарів')

    def clean_client(self):
        data = self.cleaned_data['client']
        client = Client.objects.get(pk = data)
#        if "fred@example.com" not in data:
#            raise forms.ValidationError("You have forgotten about Fred!")
        data = client
        return data
    
    class Meta:
        model = Storage_Type
        fields = ('client', 'model', 'serial_number', 'color', 'wheel_size', 'biketype', 'type', 'price', 'currency', 'service', 'washing', )
        exclude = []         
    
    
# --------- Dealers ------------
class DealerForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    country = forms.ModelChoiceField(queryset = Country.objects.all())
    city = forms.CharField()
    street = forms.CharField()
    www = forms.URLField()
    description = forms.CharField(label='Description of type', widget=forms.Textarea())
    director = forms.CharField()
    class Meta:
        model = Dealer
        fields = '__all__'


class DealerManagerForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone = forms.CharField()
    description = forms.CharField(label='Description', widget=forms.Textarea())
    company = forms.ModelChoiceField(queryset = Dealer.objects.all())
    #company = SelectFromModel(objects=Dealer.objects.all())
    class Meta:
        model = DealerManager
        fields = '__all__'
    

class DealerPaymentForm(forms.ModelForm):
    dealer_invoice = forms.ModelChoiceField(queryset = DealerInvoice.objects.filter(payment=False))
    invoice_number = forms.CharField(max_length=255)
    date = forms.DateField(initial = datetime.date.today, label='Дата', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    bank = forms.ModelChoiceField(queryset = Bank.objects.all())
    price = forms.FloatField(initial=0)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    letter = forms.BooleanField(initial = False, required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)
    class Meta:
        model = DealerPayment
        fields = '__all__'
    
  

class DealerInvoiceForm(forms.ModelForm):
    origin_id = forms.CharField(max_length=255, label='Номер накладної')
    date = forms.DateTimeField(initial = datetime.date.today, label='Дата', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    company = forms.ModelChoiceField(queryset = Dealer.objects.all())
    manager = forms.ModelChoiceField(queryset = DealerManager.objects.all())
    price = forms.FloatField(initial=0)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    file = forms.CharField(max_length=255)
    received = forms.BooleanField(initial = False, required=False) 
    payment = forms.BooleanField(initial = False, required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)

    class Meta:
        model = DealerInvoice
        fields = '__all__'


class ImportDealerInvoiceForm(forms.Form):
    csv_file = forms.FileField(allow_empty_file=False)
    name = forms.BooleanField(label='Назва товару', required=False)
    recomended = forms.BooleanField(label='Ціна товару', initial=True, required=False)
    invoice_number = forms.CharField(label='Id Накладної для імпорту', required=False)
    create_catalog = forms.BooleanField(label='Створювати картки товарів?', required=False)

    def clean(self):
        cleaned_data = super(ImportDealerInvoiceForm, self).clean()
        csvdata = cleaned_data.get("csv_file")
        if (csvdata == None):
            raise forms.ValidationError("Виберіть файл для імпорту!")
        return cleaned_data 




class ImportPriceForm(forms.Form):
    csv_file = forms.FileField(allow_empty_file=False)
    change_ids = forms.BooleanField(label='Замінити артикул на новий', required=False)
    recomended = forms.BooleanField(label='Ціна товару', required=False)
    description = forms.BooleanField(label='Опис', required=False)
    photo = forms.BooleanField(label='Фото', required=False)
    name = forms.BooleanField(label='Оновити назву товару', required=False)
    currency = forms.BooleanField(label='Курс валюти', required=False)
    check_catalog_id = forms.BooleanField(label='Перевірка наявності товару по артикулу/штрихкоду', required=False)
    col_count = forms.IntegerField(min_value=3, initial = 3, label = 'Кількість стовбців у файлі')

    def clean_csv_file(self):
        csvdata = self.cleaned_data['csv_file']
        print '\nCSV = ' + str(csvdata) + "\n" 
        if not (csvdata):
            raise forms.ValidationError("Виберіть CSV файл для імпорту!")
        return csvdata

    def clean_change_ids(self):
        data = self.cleaned_data['change_ids']
#        print '\nIDS Work = ' + str(data) + "\n"
#        if not (data):
#            raise forms.ValidationError("Поставте галочку!")
        return data

    def clean_col_count(self):
        data = self.cleaned_data['col_count']
        if int(data) > 10:
            raise forms.ValidationError(u"Кількість стовбців більша за 10")
        return data

    def clean(self):
        cleaned_data = super(ImportPriceForm, self).clean()
        csvdata = cleaned_data.get("csv_file")
        if (csvdata == None):
            raise forms.ValidationError("Виберіть файл для імпорту!")
        return cleaned_data 


class InvoiceComponentListForm(forms.ModelForm):
    invoice = forms.ModelChoiceField(queryset = DealerInvoice.objects.filter(received=False))
    catalog = forms.ModelChoiceField(queryset = Catalog.objects.none(), required=False)
    #catalog = forms.ModelChoiceField(queryset = Catalog.objects.filter(manufacturer=36))
    count = forms.IntegerField(min_value=0, initial = 1)
    price = forms.FloatField(initial=0)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    date = forms.DateTimeField(initial = datetime.date.today, label='Дата', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        #self.default_username = default_username
        test1 = kwargs.pop('test1', None)
        catalog_id = kwargs.pop('catalog_id', None)
        super(InvoiceComponentListForm, self).__init__(*args, **kwargs)
        if test1<>None:
            self.fields['catalog'].queryset = Catalog.objects.filter(manufacturer = test1) 
        if catalog_id<>None:
            self.fields['catalog'].queryset = Catalog.objects.filter(id = catalog_id)             

    class Meta:
        model = InvoiceComponentList
        fields = '__all__'


class InvoiceComponentForm(forms.ModelForm):
    invoice = forms.ModelChoiceField(queryset = DealerInvoice.objects.all(), required=False)
    #catalog = forms.ModelChoiceField(queryset = Catalog.objects.all())
    #catalog = forms.ModelChoiceField(queryset = Catalog.objects.defer(None))
    catalog = forms.ChoiceField()
    count = forms.IntegerField(min_value=0, initial = 1)
    price = forms.FloatField(initial=0)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    date = forms.DateTimeField(initial = datetime.date.today, label='Дата', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super(InvoiceComponentForm, self).__init__( *args, **kwargs)
        instance = kwargs.get('instance')
        CHOICES = (
            (item.id, item.name) for item in  Catalog.objects.all()
         )
        choices_field = forms.ChoiceField(choices=CHOICES)
        self.fields['catalog'] = choices_field
        
    class Meta:
        model = InvoiceComponentList
        fields = '__all__'

  
#class ContactForm(forms.ModelForm):
#    topic = forms.ChoiceField(choices=TOPIC_CHOICES)
#    message = forms.CharField(widget=forms.Textarea())
#    sender = forms.EmailField(required=False)
#   
#    class Meta:
#        model = ClientMessage
#        fields = '__all__'


# --------- Product Catalog ------------
class CatalogForm(forms.ModelForm):
    ids = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'size': 30, 'title': 'код товару',}))
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size': 100, 'title': 'Назва',}))
    manufacturer = forms.ModelChoiceField(queryset = Manufacturer.objects.all(), label='Виробник')
#    type = forms.ModelChoiceField(queryset = Type.objects.all())
    size = forms.ModelChoiceField(queryset = Size.objects.all(), required=False)
    weight = forms.FloatField(min_value=0, required=False, label='Вага (грам)')
    photo = forms.ImageField(required=False)
    color = forms.CharField(max_length=255, label='Колір')
    year = forms.IntegerField(initial = datetime.datetime.today().year, min_value = 1999, max_value = datetime.datetime.today().year)
    sale = forms.FloatField(initial=0, required=False)
    #sale_to = forms.DateField(initial=datetime.date.today)
    sale_to = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    price = forms.FloatField(min_value=0, label='Ціна')
    currency = forms.ModelChoiceField(initial = 3, queryset = Currency.objects.all())
    count = forms.IntegerField(initial=0, required=False)
    length = forms.FloatField(initial=0, required=False)
    country = forms.ModelChoiceField(queryset = Country.objects.all())    
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255, required=False)
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y',) , required=False, )    

    def __init__(self, *args, **kwargs):
        #cid = kwargs.pop('ids', None)
        self.request = kwargs.pop("request")
        super(CatalogForm, self).__init__(*args, **kwargs)

    def clean_ids(self):
        data = self.cleaned_data['ids']
        #res = Catalog.objects.filter( Q(ids__icontains = data) | Q(dealer_code__icontains=data))
        res = Catalog.objects.filter( Q(dealer_code = data) )
        if res:
            raise forms.ValidationError("Товар з таким кодом вже існує!")
        return data.strip()

    def clean_dealer_code(self):
        data = self.cleaned_data['dealer_code']
        return data.strip()

    def clean_price(self):
        obj = None
        try:
            obj = Catalog.objects.get(pk=self.instance.pk)
        except:
            pass    
        data = self.cleaned_data['price']
        if (auth_group(self.request.user, 'admin')==False) and ('price' in self.changed_data):
            raise forms.ValidationError(u"У вас не має прав Адміністратора для зміни ціни " + str(obj.price) + u" грн. -> " + str(data) + u" грн.")
        return data
        
    def clean_sale(self):
        obj = None
        try:
            obj = Catalog.objects.get(pk=self.instance.pk)
        except:
            pass        
        data = self.cleaned_data['sale']
        if (auth_group(self.request.user, 'admin')==False) and ('sale' in self.changed_data):
            raise forms.ValidationError(u"У вас не має прав Адміністратора для зміни знижки " + str(int(obj.sale)) + " -> " +str(int(data)) + u" %")
        #if (discount > sprice) and (auth_group(self.request.user, 'admin')==False):
#            print "IF discount > sale /// Sprice = " + str(sprice) + " --- Discount = " + str(discount)
        #    raise forms.ValidationError(u"Знижка не може бути більше за встановлену на товар " + str(int(discount)) + u" грн.")
        return data
        
    class Meta:
        model = Catalog
        fields = '__all__'
        exclude = ['size']


# ---------- Client -------------
class ClientForm(forms.ModelForm):
    name = forms.CharField(max_length=255, required=True, label=u"Прізвище, Імя, Побатькові")
    forumname = forms.CharField(max_length=255, required=False, label=u"Нік (nickname, forumName)")    
    country = forms.ModelChoiceField(queryset = Country.objects.all(), initial=1 , label=u"Країна")
    city = forms.CharField(max_length=255, label=u"Місто")
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=255, required=False)
    phone1 = forms.CharField(max_length=255, required=False)
    sale = forms.IntegerField(required=False, initial=0)
    summ = forms.FloatField(initial=0)
    birthday = forms.DateField(label='Дата народженя (d.m.Y)', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), required=False)
    description = forms.CharField(label=u'Примітки', widget=forms.Textarea(), max_length=255, required=False)    

    def clean_phone(self):
        data = self.cleaned_data['phone']
        res = Client.objects.filter( Q(phone__icontains = data) | Q(phone1__icontains=data))
        if res:
            raise forms.ValidationError("Клієнт з таким номером телефону вже існує!")
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data

    def clean_name(self):
        data = self.cleaned_data['name']
        res = Client.objects.filter( Q(name__icontains = data) )
        if res:
            raise forms.ValidationError("Клієнт з таким іменем вже існує!")
        if len(data) < 2:
            raise forms.ValidationError("Імя клієнта занадто коротке. Воно повинно мати що найменше 3 символи!")
        return data

    class Meta:
        model = Client
        fields = '__all__'


class ClientEditForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    forumname = forms.CharField(max_length=255, required=False)    
    country = forms.ModelChoiceField(queryset = Country.objects.all(), initial=1)
    city = forms.CharField(max_length=255)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=255, required=False)
    phone1 = forms.CharField(max_length=255, required=False)
    sale = forms.IntegerField(required=False, initial=0)
    summ = forms.FloatField(initial=0)
    birthday = forms.DateField(label='Дата народженя (d/m/Y)', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255, required=False)    

    class Meta:
        model = Client
        fields = '__all__'


class ClientDebtsForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset = Client.objects.all(), label="Клієнт")
#    date = forms.DateTimeField(initial=datetime.date.today)
    date = forms.DateTimeField(initial = datetime.datetime.now, label='Дата', input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    price = forms.FloatField(label='Сума')
    description = forms.CharField(label='Опис', widget=forms.Textarea(), max_length=255)
    cash = forms.BooleanField(initial=False, label="Каса?", required=False)    

    class Meta:
        model = ClientDebts
        fields = '__all__'


class ClientCreditsForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset = Client.objects.all())
    date = forms.DateTimeField(initial = datetime.datetime.now, label='Дата', input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    price = forms.FloatField()
    cash_type = forms.ModelChoiceField(queryset = CashType.objects.all())
    description = forms.CharField(label='DescripCred', widget=forms.Textarea(), max_length=255)    

    class Meta:
        model = ClientCredits
        fields = '__all__'


def auth_group(user, group):
    return True if user.groups.filter(name=group) else False


class ClientInvoiceForm(forms.ModelForm):
    #client = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'autocomplete'}), queryset = Client.objects.all(), empty_label="")
    client = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset = Client.objects.all(), empty_label="")
    #catalog = forms.ModelChoiceField(queryset = Catalog.objects.filter(manufacturer=36))
    count = forms.FloatField(min_value=0, initial = 1, label = "Кількість")
    catalog = forms.ModelChoiceField(queryset = Catalog.objects.all(), widget=forms.HiddenInput(), label="Товар")    
    
    price = forms.FloatField(initial=0, label="Ціна")
    sum = forms.FloatField(initial=0, label="Сума")
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    sale = forms.IntegerField(min_value=0, initial = 0, label="Знижка (%)")
    pay = forms.FloatField(initial=0, widget=forms.HiddenInput(), label="Оплачено")
#    date = forms.DateTimeField(initial = datetime.datetime.today(), label='Дата', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    date = forms.DateTimeField(initial = datetime.datetime.now, label='Дата',  input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)
    length = forms.FloatField(initial=0, label="Довжина", widget=forms.HiddenInput())
    #user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True), required=True, label='Користувач')
    user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True), required=True, label='Користувач')
    shop = forms.ModelChoiceField(queryset = Shop.objects.all(), required=False, label='Магазин')

    def __init__(self, *args, **kwargs):
        cid = kwargs.pop('catalog_id', None)
        self.request = kwargs.pop("request")
        super(ClientInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['catalog'].queryset = Catalog.objects.filter(id = cid)

#    def clean_sale(self):
#        data = self.cleaned_data['sale']
#        if int(data) > 100:
#            raise forms.ValidationError(u"Знижка не може бути більше за 100%")
#        return data
        
    def clean(self):
        #sale = 0
        cleaned_data = super(ClientInvoiceForm, self).clean()
        sale = cleaned_data.get("sale")
        client = cleaned_data.get("client")
        cid = cleaned_data.get("catalog")
#        cat = Catalog.objects.get(id = cid)
        cat = cid
        sprice = (100-sale)*0.01*cat.price
        cat_sale = (100-cat.sale)*0.01*cat.price
        discount = cat.get_discount()
#        print "GET Sprice = " + str(sprice) + " --- Discount = " + str(discount)
        try:
            discount = discount[0]
        except: 
            discount = discount
#        print "CAT sale = " + str(cat_sale) + " --- Discount = " + str(discount)            
        if discount > cat_sale:
            discount = cat_sale
        if (discount > sprice) and (auth_group(self.request.user, 'admin')==False):
#            print "IF discount > sale /// Sprice = " + str(sprice) + " --- Discount = " + str(discount)
            raise forms.ValidationError(u"Знижка не може бути більше за встановлену на товар " + str(int(discount)) + u" грн.")
#            return cleaned_data 
        if ((sale > 100) or (sale > cat.sale+20)) and (auth_group(self.request.user, 'admin')==False) and (discount == 0):
            ssale = cat.sale + 20
            raise forms.ValidationError(u"Знижка не може бути більше 100% або більша за встановлену на товар " + str(int(ssale)) + "%")
        return cleaned_data 
    
    class Meta:
        model = ClientInvoice
        fields = '__all__'
        exclude = ['chk_del'] #, 'user']         


class ClientOrderForm(forms.ModelForm):
    #client = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'autocomplete'}), queryset = Client.objects.all(), empty_label="")
    client = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset = Client.objects.all(), empty_label="")
#    catalog = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'autocomplete'}), queryset = Catalog.objects.all())
#    catalog = forms.CharField(label='Товар', widget=forms.TextInput(attrs={'width':'300px'}), required=True)    
    #catalog = forms.ModelChoiceField(queryset = '')    
    post_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)    
    description = forms.CharField(label='Опис товару', widget=forms.Textarea(), required=False)    
    count = forms.IntegerField(min_value=0, initial = 1, label='Кількість')
    price = forms.FloatField(initial=0, label='Ціна')
    sum = forms.FloatField(initial=0, label='Сума')
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), label='Валюта')
    pay = forms.FloatField(initial=0, label='Передоплата')
    cash_type = forms.ModelChoiceField(queryset = CashType.objects.all(), initial=CashType.objects.get(name="Готівка"))
    date = forms.DateTimeField(initial = datetime.datetime.now, label='Дата',  input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    status = forms.BooleanField(initial = False, required=False)

    class Meta:
        model = ClientOrder
        fields = '__all__'
        exclude = ['user', 'catalog', 'credit']         
    
#===============================================================================
#    def __init__(self, *args, **kwargs):
#        cid = kwargs.pop('catalog_id', None)
#        super(ClientOrderForm, self).__init__(*args, **kwargs)
#        self.fields['catalog'].queryset = Catalog.objects.filter(id = cid)
#===============================================================================


class CashTypeForm(forms.ModelForm):
#    name = forms.CharField(max_length=100)
#    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255)    
 
    class Meta:
        model = CashType
        fields = '__all__'        


class CostTypeForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255)    
 
    class Meta:
        model = CostType
        fields = '__all__'

    
class CostsForm(forms.ModelForm):
    #date = forms.DateTimeField(initial=datetime.date.today)
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    cost_type = forms.ModelChoiceField(queryset = CostType.objects.all())
    price = forms.FloatField()
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255)    

    class Meta:
        model = Costs
        fields = '__all__'


# ================== WorkShop ==========================
class WorkGroupForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    description = forms.CharField(label='Description', widget=forms.Textarea()) 

    class Meta:
        model = WorkGroup
        fields = '__all__'

        
class WorkTypeForm(forms.ModelForm):
    name = forms.CharField(max_length=255, label='Назва роботи')
    work_group = forms.ModelChoiceField(queryset = WorkGroup.objects.all(), label='Група робіт')
    price = forms.FloatField(label='Ціна')
    description = forms.CharField(label='Короткий опис роботи', widget=forms.Textarea())
   
    class Meta:
        model = WorkType
        fields = '__all__'


class WorkShopForm(forms.ModelForm):
    work_type = forms.CharField(widget=forms.HiddenInput(), label="Робота")
    client = forms.CharField(widget=forms.HiddenInput())
    #date = forms.DateTimeField(initial = datetime.datetime.now, label='Дата',  input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'), required=False)
    #date = forms.DateTimeField(initial = datetime.datetime.now, label='Дата',  input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'), required=False)
    date = forms.DateTimeField(initial = datetime.datetime.now, label='Дата',  input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'), required=False)
    #price = forms.FloatField(initial=0, label="Ціна" ,widget=forms.TextInput(attrs={'class': 'form-control'}) )
    price = forms.FloatField(label="Ціна" ,widget=forms.TextInput(attrs={'class': 'form-control'}) )
    #pay = forms.BooleanField(initial=False, required=False, label="Оплачено?")
    description = forms.CharField(label='Опис', widget=forms.Textarea(), max_length=255, required=False)
    user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True), required=True, label='Користувач')
    shop = forms.ModelChoiceField(queryset = Shop.objects.all(), required=False, label='Магазин')
    hour = forms.IntegerField(initial = 0, required=False, label='Витрачені (Години)')
    time = forms.IntegerField(initial = 0, required=False, label='Витрачені (Хвилини)')
    ticket = forms.ModelChoiceField(queryset = WorkTicket.objects.all(), required=False, label='Заявка на ремонт')
    #ticket = forms.ModelChoiceField(queryset = WorkTicket.objects.filter(status = WorkStatus.objects.filter( name='Ремонтується' )), required=False, label='Заявка на ремонт')    

    def __init__(self, *args, **kwargs):
        cid = kwargs.pop('client_id', None)
        wt_id = kwargs.pop('wticket_id', None)
        try:
            self.request = kwargs.pop("request")
        except:
            pass
        super(WorkShopForm, self).__init__(*args, **kwargs)
        stat_id = WorkStatus.objects.filter( name='Ремонтується' ).first()
        if cid:
            self.fields['ticket'].queryset = WorkTicket.objects.filter(client = cid.id, status =  stat_id)
        if wt_id:
#            print "\nEDIT WORKSHOP - " + str(cid.id)
            #self.fields['ticket'].queryset = WorkTicket.objects.filter(id = wt_id.id)
            self.fields['ticket'].queryset = WorkTicket.objects.filter(Q(client = cid.id, status =  stat_id) | Q(id = wt_id.id))
        if (cid == None) and (wt_id == None):
            shopN = get_shop_from_ip(self.request.META['REMOTE_ADDR'])
            self.fields['ticket'].queryset = WorkTicket.objects.filter(status = WorkStatus.objects.filter( name='Ремонтується' ), shop = shopN.id)
            if not self.fields['ticket'].queryset:
                self.fields['ticket'].queryset = WorkTicket.objects.filter(status = WorkStatus.objects.filter( name='Ремонтується' ))
    
    def clean_time(self):
        #dh = self.cleaned_data['hour']
        dm = self.cleaned_data['time']
        #if int(dm) > 60:
        #    raise forms.ValidationError("Час в хвилинах більше 60 хвилин") 
        #res = int(dm) - (60 * (int(dm) / 60))
        res = dm
        return res

    def clean_client(self):
        data = self.cleaned_data['client']
        res = Client.objects.filter(pk = data)
        if not res:
            raise forms.ValidationError("Клієнт з таким ПІБ або номером телефону не існує!")
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return res[0]
  
    def clean_work_type(self):
        data = self.cleaned_data['work_type']
        res = WorkType.objects.filter(pk = data)
        if not res:
            raise forms.ValidationError("Такої роботи не існує або ви її не вибрали!")
        return res[0]

    def clean(self):
        cleaned_data = super(WorkShopForm, self).clean()
        htime = cleaned_data.get("hour")
        mtime = cleaned_data.get("time")
        ticket = cleaned_data.get("ticket")
        client = cleaned_data.get("client")
        get_client = Client.objects.get(pk = client.pk)
        try:
            get_ticket = WorkTicket.objects.get(pk = ticket.pk)
            if get_client.id != get_ticket.client.id:
                self.add_error('client', "Клієнт не підходить під заявку. Виберіть іншого клієнта або заявку")
        except:
            pass
            #self.add_error('client', "Клієнт підходить")
        
#        print "\nChange field Time!!!" + str(self.has_changed())
        res = int(htime) * 60 + int(mtime)
#        self.time = 111
        cleaned_data['time'] = res
        return cleaned_data 
 
#         try:
#             data = self.cleaned_data['client']
#             res = Client.objects.filter(pk = data)
#         # no user with this username or email address
#         except User.DoesNotExist:
#             self.add_error['no_user'] = 'User does not exist'
#             return False
# 
#         if cc_client == '':
#             msg = "Must put 'help' in subject when cc'ing yourself."
#             self.add_error('client', msg)
#             self.add_error('work_type', msg)
#             return False
#===============================================================================

    def save(self, commit=True):
#        client = Client.objects.get(id = self.cleaned_data['client'])
#        work = WorkType.objects.get(id = self.cleaned_data['work_type'])
        self.time = self.cleaned_data['time']
        #self.time = int(self.cleaned_data['hour']) *60 + int(self.time)  
        return super(WorkShopForm, self).save(commit)
    
    class Meta:
        model = WorkShop
        fields = '__all__'
        exclude = ['pay', ]  # 'time', 'ticket'

WorkShopFormset = formset_factory(WorkShopForm, extra=1)

class WorkStatusForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255)
    
    class Meta:
        model = WorkStatus
        fields = '__all__'


class WorkTicketForm(forms.ModelForm):
#    client = forms.ModelChoiceField(queryset = Client.objects.all())
    client = forms.CharField(widget=forms.HiddenInput())
    #date = forms.DateTimeField(initial=datetime.date.today)
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), label="Дата")    
    #end_date = forms.DateTimeField(initial=datetime.date.today)
    end_date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    status = forms.ModelChoiceField(queryset = WorkStatus.objects.all(), label='Статус')
    description = forms.CharField(label='Опис', widget=forms.Textarea(attrs={'class': 'form-control'}))
    shop = forms.ModelChoiceField(queryset = Shop.objects.all(), label = 'Магазин', required=False)
    bicycle = forms.CharField(label='Велосипед', widget=forms.TextInput(attrs={'class': 'form-control'}), required=False )
    bike_part_type = forms.ModelChoiceField(queryset = Type.objects.all(), label = "Запчастина", required=False, widget=forms.Select(attrs = {'hidden': '',}) )
    #bike_part_type = forms.ModelChoiceField(queryset = Type.objects.all(), label = "Запчастина", widget=forms.Select(attrs={'class': 'form-control'}))
    estimate_time = forms.NumberInput()
    #estimate_time = forms.NumberInput(widget=forms.NumberInput(attrs={'class': 'form-control'}) , label="Орієнтовний час виконання (години)")

    def clean_client(self):
        data = self.cleaned_data['client']
        res = Client.objects.filter(pk = data)
        if not res:
            raise forms.ValidationError("Клієнт з таким ПІБ або номером телефону не існує!")
        return res[0]

    def clean_description(self):
        desc = self.cleaned_data['description']
        #res = desc.replace('\n', '<br>').strip()
        res = desc.strip()
        if not res:
            raise forms.ValidationError("Заповніть форму на ремонт!")
        return res

#    def clean_shop(self):
#        print ("\nCLEAN SHOP = " + str(self) )
#        if not self:
#            raise forms.ValidationError("Магазин не вибраний")
#        return self
    
    class Meta:
        model = WorkTicket
        fields = '__all__'
        exclude = ['phone_date', 'phone_user', 'phone_status', 'user', 'history', ]


class PhoneStatusForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255)

    class Meta:
        model = PhoneStatus
        fields = '__all__'
    

class ShopDailySalesForm(forms.ModelForm):
    #date = forms.DateTimeField( input_formats=['%d.%m.%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M:%S'), label="Дата" )
    date = forms.DateTimeField(initial=datetime.datetime.today, input_formats=['%d.%m.%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M:%S'), label="Дата")
    price = forms.FloatField(initial=0, label="Сума в касі")    
    description = forms.CharField(label='Опис', widget=forms.Textarea(), required=False)
    user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True), required=False, label='Користувач')
    cash = forms.FloatField(label="Готівка в касі")
    tcash = forms.FloatField(label="Термінал")
    ocash = forms.FloatField(label="Видано з каси")
    
    class Meta:
        model = ShopDailySales
        fields = '__all__'


class PreOrderForm(forms.ModelForm):
    date = forms.DateTimeField(initial = datetime.date.today, label='Дата замовлення')
    date_pay = forms.DateTimeField(initial = datetime.date.today, label='Кінцева дата внесення предоплати')
    date_delivery = forms.DateTimeField(initial = datetime.date.today, label='Дата поставки')
    company = forms.ModelChoiceField(queryset = Dealer.objects.all())
    manager = forms.ModelChoiceField(queryset = DealerManager.objects.all(), required=False)
    price = forms.FloatField(initial=0)
    price_pay = forms.FloatField(initial=0)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    file = forms.CharField(max_length=255)
    received = forms.BooleanField(initial = False, required=False) 
    payment = forms.BooleanField(initial = False, required=False)
    #payment = forms.ModelChoiceField(queryset = DealerPayment.objects.all())
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)

    class Meta:
        model = PreOrder
        fields = '__all__'


class RentForm(forms.ModelForm):
#    catalog = forms.ModelChoiceField(queryset = Catalog.objects.filter(id__in = ClientInvoice.objects.filter(client__id=516).values('catalog__id')))
    catalog = forms.ModelChoiceField(queryset = Catalog.objects.filter(id__in = ClientInvoice.objects.filter(client__name='Прокат').values('catalog__id')))
    client = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'autocomplete'}), queryset = Client.objects.all(), empty_label="")    
#    date_start = forms.DateTimeField( label='Дата початку')
    date_end = forms.DateTimeField(initial = datetime.date.today() + datetime.timedelta(days=3), label='Закінчення прокату')
#    date_start = forms.DateTimeField(initial = datetime.datetime.today(), label='Дата початку')
#    date_end = forms.DateTimeField(initial = datetime.date.today() + datetime.timedelta(days=3), label='Закінчення прокату')
    
#    count = forms.IntegerField(initial=1)
    deposit = forms.FloatField(label='Завдаток', initial=0)
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), label='Валюта')
    cash_type = forms.ModelChoiceField(queryset = CashType.objects.all(), label='Вид оплати')
#    status = forms.BooleanField(initial = False, required=False)
    description = forms.CharField(label='Коментар', widget=forms.Textarea(), required=False)
#    field_order = ['catalog','client','date_start', 'date_end', 'deposit', 'currency', 'description']

    class Meta:
        model = Rent
        #fields = '__all__'
#        fields = ['catalog','client','date_start', 'date_end', 'deposit', 'currency', 'cash_type', 'description']
        fields = ['catalog','client', 'date_end', 'deposit', 'currency', 'cash_type', 'description']
        exclude = ['cred', 'user', 'status', 'count']


class WorkDayForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True), required=True, label='Користувач')
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), label='Дата')
    status = forms.IntegerField(min_value=0, initial = 0, label='Статус')
    description = forms.CharField(widget=forms.Textarea(), required=False, label='Опис')
    
    class Meta:
        model = WorkDay
        fields = '__all__'
        
        
class DiscountForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    manufacture_id = forms.CharField(widget=forms.HiddenInput(), label="Виробник", required=False)
    type_id = forms.CharField(widget=forms.HiddenInput(), label="", required=False)
    date_start = forms.DateField( widget=forms.HiddenInput())
    date_end = forms.DateField( widget=forms.HiddenInput())
    sale = forms.IntegerField(min_value=0, initial = 0, label='Знижка %')
    description = forms.CharField(widget=forms.Textarea(), required=False, label='Опис')

    class Meta:
        model = Discount
        fields = '__all__'
#        exclude = ['name']


class SalaryForm(forms.Form):
    #cost_type = forms.CharField(widget=forms.HiddenInput(), label="Робота")
    client = forms.CharField(widget=forms.HiddenInput())
    date = forms.DateTimeField(initial = datetime.datetime.now, label='Дата',  input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'), required=False)
    price = forms.FloatField(initial=0, label="Сума" ,widget=forms.TextInput(attrs={'class': 'form-control'}) )
    description = forms.CharField(label='Опис', widget=forms.Textarea(), max_length=255, required=False)
    user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True), required=True, label='Користувач')

    def clean_client(self):
        data = self.cleaned_data['client']
        res = Client.objects.filter(pk = data)
        if not res:
            raise forms.ValidationError("Клієнт з таким ПІБ або номером телефону не існує!")
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return res[0]
  
    #===========================================================================
    # def clean_work_type(self):
    #     data = self.cleaned_data['work_type']
    #     res = WorkType.objects.filter(pk = data)
    #     if not res:
    #         raise forms.ValidationError("Такої роботи не існує або ви її не вибрали!")
    #     return res[0]
    #===========================================================================


    #===========================================================================
    # def save(self, commit=True):
    #     client = Client.objects.get(id = self.cleaned_data['client'])
    #     work = WorkType.objects.get(id = self.cleaned_data['work_type'])
    #     self.cleaned_data['client'] = client.id
    #     self.cleaned_data['work_type'] = work.id
    #     return super(WorkShopForm, self).save(commit)
    #===========================================================================
    
#    class Meta:
#        model = Costs
#        fields = '__all__'
#        exclude = ['cost_type']

class BoxNameEditForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True, ), required=False, label='Користувач')

    def clean(self):
        cleaned_data = super(BoxNameEditForm, self).clean()
        name = cleaned_data.get("name")
        shop = cleaned_data.get("shop")
        user = cleaned_data.get("user")
        try:
            get_user = User.objects.get(pk = user.pk)
        except:
            self.add_error('user', "Користувач не увійшов на портал або не вибраний у полі!")
        try:
            get_shop = Shop.objects.get(pk = shop.pk)
        except:
            self.add_error('shop', "Магазин не вибраний!")
        if len(name.split('.')) <> 4:
            self.add_error('name', "В назві не вистачає частини розташування. Перевірте поле уважніше!")
        if name.find(' ') >= 0 :
            self.add_error('name', "В назві є пробіли. Виправіть поле!")

        sel_let = ''
        res = False
        if shop.name.upper()[0] == u"М":
            sel_let = 'm'
        if shop.name.upper()[0] == u"К":
            sel_let = 'k'
        if sel_let == name.lower()[0]:
            res = True
        if res == False:
            self.add_error('name', "Місце має не вірну назву або ви вибрали не правильний магазин!")

#        cleaned_data['description'] = "write  test string"
        return cleaned_data 
        

    class Meta:
        model = BoxName
        fields = '__all__'
#        exclude = ['name']
    

           
#class BoxNameForm(forms.ModelForm):
class BoxNameForm(forms.ModelForm):
    name = forms.CharField()
#    shop = forms.ModelChoiceField(initial=0, label="Сума" ,widget=forms.TextInput(attrs={'class': 'form-control'}) )
    shop = forms.ModelChoiceField(queryset = Shop.objects.all(), required=False, label='Магазин')
    mark_delete = forms.BooleanField(required=False)
    description = forms.CharField(label='Опис', widget=forms.Textarea(), max_length=255, required=False)
    user = forms.ModelChoiceField(queryset = User.objects.filter(is_active = True, ), required=False, label='Користувач')

#    def __init__(self, *args, **kwargs):
#        user = kwargs.pop('bike_id', None)
#        try:
#            self.request = kwargs.pop("request")
#        except:
#            pass
  #      instance = kwargs.pop('instance')
#        print "INST = %s " % instance
#        super(BoxNameForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        data_name = self.cleaned_data['name']
        res = BoxName.objects.filter(name = data_name)
        if res:
            raise forms.ValidationError("Місце з такою назвою вже існує!")
        if len(data_name.split('.')) <> 4:
            raise forms.ValidationError("В назві не вистачає частини розташування. Перевірте поле уважніше!")
        if data_name.find(' ') >= 0 :
            raise forms.ValidationError("В назві є пробіли. Виправіть поле!")
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data_name

    def clean_shop(self):
        data = self.cleaned_data['shop']
        try:
            st = data.name
        except:
            raise forms.ValidationError("Магазин не вибраний!")
        return data

    def clean_user(self):
        data = self.cleaned_data['user']
        if not data:
            raise forms.ValidationError("Користувач не вибраний або не увійшов на портал")
        if (auth_group(data, 'seller')==False): # and ('price' in self.changed_data):
            raise forms.ValidationError(u"У вибраного користувача не має доступу до даної функції")
        return data

    def clean(self):
        cleaned_data = super(BoxNameForm, self).clean()
        name = cleaned_data.get('name')
        shop = cleaned_data.get('shop')
        sel_let = ''
        res = False
        if shop.name.upper()[0] == u"М":
            sel_let = 'm'
        if shop.name.upper()[0] == u"К":
            sel_let = 'k'
        n0 = name.lower()[0] or ''            
        if sel_let == name.lower()[0]:
            res = True
        if res == False:
            #raise forms.ValidationError("Місце має не вірну назву або ви вибрали не правильний магазин!")
            self.add_error('name', "Місце має не вірну назву або ви вибрали не правильний магазин!")
        return cleaned_data
      
    class Meta:
        model = BoxName
        fields = '__all__'
#        exclude = ['name']


class InventoryListForm(forms.ModelForm):
    
    class Meta:
        model = InventoryList
        fields = '__all__'
        exclude = ['catalog']


