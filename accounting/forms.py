# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from models import Manufacturer, Country, Type, Bicycle_Type, Bicycle, Currency, FrameSize, Bicycle_Store, Catalog, Size, Bicycle_Sale, Bicycle_Order, Wheel_Size, Storage_Type, Bicycle_Storage, Bicycle_Photo 
from models import DealerManager, DealerPayment, DealerInvoice, Dealer, Bank, ShopDailySales, PreOrder, InvoiceComponentList, ClientOrder, InventoryList
from models import Client, ClientDebts, CostType, Costs, ClientCredits, WorkGroup, WorkType, WorkShop, WorkTicket, WorkStatus, Rent, ClientInvoice, CashType, Exchange, Type, ClientMessage, WorkDay

from django.contrib.auth.models import User
import datetime

TOPIC_CHOICES = (
    ('general', 'General enquiry'),
    ('bug', 'Bug report'),
    ('suggestion', 'Suggestion'),
)

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
    type = forms.CharField(label='Bicycle type')
    description = forms.CharField(label='Description of type', widget=forms.Textarea(), max_length=255)
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
    #currency = SelectFromModel(objects=Currency.objects.all())
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), initial=Currency.objects.get(ids_char = 'UAH'))
    sale = forms.FloatField(min_value=0, initial=0, required=False)
    warranty = forms.IntegerField(min_value=0, initial=1)
    geometry = forms.ImageField(required=False)
    internet = forms.BooleanField(required=False)
    rating = forms.IntegerField(min_value=0, initial=0)
    description = forms.CharField(label='Description', widget=forms.Textarea(attrs={'size': '180'}), required=False)

    class Meta:
        model = Bicycle
        fields = '__all__'


class BicycleStoreForm(forms.ModelForm):
    model = forms.ModelChoiceField(queryset = Bicycle.objects.all(), required=False)
    serial_number = forms.CharField(max_length=50)
    size = forms.ModelChoiceField(queryset = FrameSize.objects.all())
    price = forms.FloatField()
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    count = forms.IntegerField(min_value=0, initial = 1)
    realization = forms.BooleanField(required=False)
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)
    
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
    user = forms.ModelChoiceField(queryset = User.objects.all(), widget=forms.HiddenInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        bike_id = kwargs.pop('bike_id', None)
        super(BicycleSaleForm, self).__init__(*args, **kwargs)
        if bike_id<>None:
            self.fields['model'].queryset = Bicycle_Store.objects.filter(model = bike_id)             

    class Meta:
        model = Bicycle_Sale
        fields = '__all__'
        exclude = ['debt']


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
    #client = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'autocomplete'}), queryset = Client.objects.all(), empty_label="", label = 'Клієнт')    
#    client = forms.IntegerField(widget=forms.HiddenInput(), label = 'Клієнт')
#    model = forms.IntegerField(widget=forms.HiddenInput(), label = 'Модель велосипеду')
    #model = forms.ModelChoiceField(queryset = Bicycle.objects.filter(year__gte=datetime.datetime(cur_year-1, 1, 1)).order_by('-year'), empty_label="", label = 'Модель велосипеду')
    model_id = forms.CharField(widget=forms.TextInput(attrs={'size': '100'}), label = 'Модель велосипеду')    
    size = forms.CharField(max_length=50, label = 'Розмір рами')
    price = forms.FloatField(initial = 0, label = 'Ціна')
    sale = forms.IntegerField(initial = 0, label = 'Знижка (%)')
    prepay = forms.FloatField(initial = 0, label = 'Аванс')
    currency = forms.ModelChoiceField(queryset = Currency.objects.all(), label='Валюта')
    date = forms.DateTimeField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), label='Дата')
    #done = forms.BooleanField(required=False) 
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
    date_out = forms.DateField(input_formats=['%d.%m.%Y', '%d/%m/%Y'], initial = datetime.date.today().replace(month=(datetime.date.today().month+4)%12, day=1), widget=forms.DateTimeInput(format='%d.%m.%Y'), label='Дата завершення зберігання')
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


class ImportPriceForm(forms.Form):
    csv_file = forms.FileField(allow_empty_file=False)
    change_ids = forms.BooleanField(label='Замінити артикул на новий', required=False)
    recomended = forms.BooleanField(label='Ціна товару', required=False)
    description = forms.BooleanField(label='Опис', required=False)
    photo = forms.BooleanField(label='Фото', required=False)
    

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

  
class ContactForm(forms.ModelForm):
    topic = forms.ChoiceField(choices=TOPIC_CHOICES)
    message = forms.CharField(widget=forms.Textarea())
    sender = forms.EmailField(required=False)
    class Meta:
        model = ClientMessage
        fields = '__all__'


# --------- Product Catalog ------------
class CatalogForm(forms.ModelForm):
    ids = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'size': 30, 'title': 'код товару',}))
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size': 100, 'title': 'Назва',}))
    manufacturer = forms.ModelChoiceField(queryset = Manufacturer.objects.all())
    type = forms.ModelChoiceField(queryset = Type.objects.all())
    size = forms.ModelChoiceField(queryset = Size.objects.all(), required=False)
    weight = forms.FloatField(min_value=0, required=False)
    photo = forms.ImageField(required=False)
    color = forms.CharField(max_length=255)
    year = forms.IntegerField(initial = datetime.datetime.today().year, min_value = 1900, max_value = 2020)
    sale = forms.FloatField(initial=0, required=False)
    #sale_to = forms.DateField(initial=datetime.date.today)
    sale_to = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    price = forms.FloatField(min_value=0)
    currency = forms.ModelChoiceField(initial = 3, queryset = Currency.objects.all())
    count = forms.IntegerField(initial=0, required=False)
    length = forms.FloatField(initial=0, required=False)
    country = forms.ModelChoiceField(queryset = Country.objects.all())    
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255, required=False)    

    class Meta:
        model = Catalog
        fields = '__all__'

# ---------- Client -------------
class ClientForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    forumname = forms.CharField(max_length=255, required=False)    
    country = forms.ModelChoiceField(queryset = Country.objects.all(), initial=1)
    city = forms.CharField(max_length=255)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=255, required=False)
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
    date = forms.DateTimeField(initial = datetime.datetime.now(), label='Дата', input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    price = forms.FloatField(label='Сума')
    description = forms.CharField(label='Опис', widget=forms.Textarea(), max_length=255)
    cash = forms.BooleanField(initial=False, label="Каса?", required=False)    

    class Meta:
        model = ClientDebts
        fields = '__all__'


class ClientCreditsForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset = Client.objects.all())
    date = forms.DateTimeField(initial = datetime.datetime.now(), label='Дата', input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
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
    catalog = forms.ModelChoiceField(queryset = Catalog.objects.all(), label="Товар")    
    
    price = forms.FloatField(initial=0, label="Ціна")
    sum = forms.FloatField(initial=0, label="Сума")
    currency = forms.ModelChoiceField(queryset = Currency.objects.all())
    sale = forms.IntegerField(min_value=0, initial = 0, label="Знижка (%)")
    pay = forms.FloatField(initial=0, label="Оплачено")
#    date = forms.DateTimeField(initial = datetime.datetime.today(), label='Дата', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    date = forms.DateTimeField(initial = datetime.datetime.now(), label='Дата',  input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)
    length = forms.FloatField(initial=0, label="Довжина", widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        cid = kwargs.pop('catalog_id', None)
        self.request = kwargs.pop("request")
        super(ClientInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['catalog'].queryset = Catalog.objects.filter(id = cid)
        
    def clean(self):
        cleaned_data = super(ClientInvoiceForm, self).clean()
        sale = cleaned_data.get("sale")
        client = cleaned_data.get("client")
        cid = cleaned_data.get("catalog")
        #cat = Catalog.objects.get(id = cid)
        cat = cid        
        if ((sale > 100) or (sale > cat.sale+20)) and (auth_group(self.request.user, 'admin')==False):
            # Only do something if both fields are valid so far.
            ssale = cat.sale + 20
            raise forms.ValidationError(u"Знижка не може бути більше 100% або більша за встановлену на товар " + str(int(ssale)) + "%")
    
    class Meta:
        model = ClientInvoice
        fields = '__all__'
        exclude = ['chk_del', 'user']         


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
    date = forms.DateTimeField(initial = datetime.datetime.now(), label='Дата',  input_formats=['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'))
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
    name = forms.CharField(max_length=100)
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255)    
 
    class Meta:
        model = CostType
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
    name = forms.CharField(max_length=255)
    work_group = forms.ModelChoiceField(queryset = WorkGroup.objects.all())
    price = forms.FloatField()
    description = forms.CharField(label='Description', widget=forms.Textarea())
    class Meta:
        model = WorkType
        fields = '__all__'    

class WorkShopForm(forms.ModelForm):
    #client = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'autocomplete'}), queryset = Client.objects.all(), empty_label="", label="Клієнт")
    client = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset = Client.objects.all(), empty_label="")
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), required=False, label="Дата")
#    work_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'autocomplete', 'width':'340px'}), queryset = WorkType.objects.all())
    work_type = forms.ModelChoiceField(queryset = WorkType.objects.all(), label="Робота")    
    price = forms.FloatField(initial=0, label="Ціна")
    pay = forms.BooleanField(initial=False, required=False, label="Оплачено?")
    description = forms.CharField(label='Опис', widget=forms.Textarea(), max_length=255, required=False)
    
    class Meta:
        model = WorkShop
        fields = '__all__'


class WorkStatusForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    description = forms.CharField(label='Description', widget=forms.Textarea(), max_length=255)
    
    class Meta:
        model = WorkStatus
        fields = '__all__'


class WorkTicketForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset = Client.objects.all())
    #date = forms.DateTimeField(initial=datetime.date.today)
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))    
    #end_date = forms.DateTimeField(initial=datetime.date.today)
    end_date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    status = forms.ModelChoiceField(queryset = WorkStatus.objects.all())
    description = forms.CharField(label='Ticket', widget=forms.Textarea())
    
    class Meta:
        model = WorkTicket
        fields = '__all__'


class ShopDailySalesForm(forms.ModelForm):
    #date = forms.DateTimeField(initial=datetime.date.today)
    date = forms.DateTimeField(initial=datetime.datetime.today, input_formats=['%d.%m.%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M:%S'), label="Дата")
    price = forms.FloatField(initial=0, label="Сума в касі")    
    description = forms.CharField(label='Опис', widget=forms.Textarea(), required=False)
    user = forms.ModelChoiceField(queryset = User.objects.all(), required=True, label='Користувач')
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
    date_start = forms.DateTimeField(initial = datetime.datetime.today(), label='Дата початку')
    date_end = forms.DateTimeField(initial = datetime.date.today() + datetime.timedelta(days=3), label='Закінчення прокату')
#    count = forms.IntegerField(initial=1)
    deposit = forms.FloatField(label='Завдаток', initial=0)
#    status = forms.BooleanField(initial = False, required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea(), required=False)

    class Meta:
        model = Rent
        fields = '__all__'
        exclude = ['cred', 'user', 'status', 'count']



class WorkDayForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset = User.objects.all(), required=True, label='Користувач')
    date = forms.DateField(initial=datetime.date.today, input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'), label='Дата')
    status = forms.IntegerField(min_value=0, initial = 0, label='Статус')
    description = forms.CharField(widget=forms.Textarea(), required=False, label='Опис')
    class Meta:
        model = WorkDay
        fields = '__all__'
    
