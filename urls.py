# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from catalog.views import main_page
#from catalog.test import current_datetime as curdate
#from django.views.generic.simple import direct_to_template
#from django.views.generic import TemplateView
#url(r'^api/casinova$', TemplateView.as_view(template_name='castle_tm/index.html')),

from django.conf import settings
from django.contrib.auth.views import login, logout
from django.conf.urls.static import static
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from django.conf.urls.static import static

import os
dirname = os.path.dirname(globals()["__file__"])


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^search/$', 'catalog.accounting.views.search'), # old function
#    url(r'^contact/thanks/$', direct_to_template, {'template': 'thanks.html'}),

    # Manufacturer operation
    url(r'^manufacturer/search/$', 'catalog.accounting.views.search'), # old function 
    url(r'^manufacturer/view/$', 'catalog.accounting.views.manufaturer_list'), 
    url(r'^manufacturer/add/$', 'catalog.accounting.views.manufacturer_add'),
    url(r'^manufacturer/edit/(?P<id>\d+)/$', 'catalog.accounting.views.manufacturer_edit'),    
    url(r'^manufacturer/delete/(?P<id>\d+)/$', 'catalog.accounting.views.manufacturer_delete'),
    url(r'^manufacturer/lookup/$', 'catalog.accounting.views.manufacturer_lookup'), # old function

    # Country operation
    url(r'^country/add/$', 'catalog.accounting.views.country_add'),
    url(r'^country/view/$', 'catalog.accounting.views.country_list'),
    url(r'^country/edit/(?P<id>\d+)/$', 'catalog.accounting.views.country_edit'),    
    url(r'^country/delete/(?P<id>\d+)/$', 'catalog.accounting.views.country_del'),
    # Bank operation
    url(r'^bank/add/$', 'catalog.accounting.views.bank_add'),
    url(r'^bank/view/$', 'catalog.accounting.views.bank_list'),
    url(r'^bank/edit/(?P<id>\d+)/$', 'catalog.accounting.views.bank_edit'),    
    url(r'^bank/delete/(?P<id>\d+)/$', 'catalog.accounting.views.bank_del'),

    # Bicycle operation
    url(r'^bicycle-type/add/$', 'catalog.accounting.views.bicycle_type_add'),
    url(r'^bicycle-type/view/$', 'catalog.accounting.views.bicycle_type_list'),
    url(r'^bicycle-type/edit/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_type_edit'),    
    url(r'^bicycle-type/delete/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_type_del'),

    url(r'^bicycle-framesize/add/$', 'catalog.accounting.views.bicycle_framesize_add'),
    url(r'^bicycle-framesize/view/$', 'catalog.accounting.views.bicycle_framesize_list'),
    url(r'^bicycle/framesize/edit/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_framesize_edit'),    
    url(r'^bicycle/framesize/delete/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_framesize_del'),
    #url(r'^bicycle/framesize/delete/(?P<id>\d)/$', 'catalog.accounting.views.bicycle_framesize_del'),

    url(r'^bicycle/add/$', 'catalog.accounting.views.bicycle_add'),
    url(r'^bicycle/year/(?P<year>\d+)/view/$', 'catalog.accounting.views.bicycle_list'),
    url(r'^bicycle/year/(?P<year>\d+)/bycompany/(?P<brand>\d+)/view/$', 'catalog.accounting.views.bicycle_list'),    
    url(r'^bicycle/year/(?P<year>\d+)/bycompany/(?P<brand>\d+)/add/sale/(?P<percent>\d+)/$', 'catalog.accounting.views.bicycle_list'),    
# ?    url(r'^bicycle/all/view/$', 'catalog.accounting.views.bicycle_all_list'),
    url(r'^bicycle/view/$', 'catalog.accounting.views.bicycle_list'),
    url(r'^bicycle/edit/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_edit', name='bicycle-edit'),    
    url(r'^bicycle/delete/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_del'),
    url(r'^bicycle/photo/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_photo', name='bicycle-photo'),
    
    url(r'^bicycle/part/add/$', 'catalog.accounting.views.bicycle_part_add' , name='bikepart_add'),
#    url(r'^delete/(\d+)/$', 'catalog.accounting.views.multiuploader_delete'),
#    url(r'^bicycle/view/list/$', 'catalog.accounting.views.image_view', name='main'),
#    url(r'^multi/$', 'catalog.accounting.views.multiuploader', name='multi'),
    
    # get bicycle price and sale by id 
    url(r'^bicycle/price/$', 'catalog.accounting.views.bicycle_lookup_ajax'),

    url(r'^bicycle/store/report/bysize/(?P<id>\d+)/$', 'catalog.accounting.views.store_report_bysize'),
    url(r'^bicycle/store/report/bytype/(?P<id>\d+)/$', 'catalog.accounting.views.store_report_bytype'),
    url(r'^bicycle/store/price/$', 'catalog.accounting.views.bicycle_store_price'),
    #url(r'^bicycle/store/price/print/$', 'catalog.accounting.views.bicycle_store_price_print'),    
    url(r'^bicycle/store/price/print/$', 'catalog.accounting.views.bicycle_store_price', {'pprint': True}),
    url(r'^bicycle-store/add/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_store_add'),
    url(r'^bicycle-store/add/$', 'catalog.accounting.views.bicycle_store_add'),
    url(r'^bicycle-store/all/view/seller/$', 'catalog.accounting.views.bicycle_store_list_by_seller', {'all': True}),
    url(r'^bicycle-store/view/seller/$', 'catalog.accounting.views.bicycle_store_list_by_seller'),
    url(r'^bicycle-store/view/seller/bysize/(?P<size>\d+)/$', 'catalog.accounting.views.bicycle_store_list_by_seller'),
    url(r'^bicycle-store/view/seller/bysize/(?P<size>\d+)/year/(?P<year>\d+)/$', 'catalog.accounting.views.bicycle_store_list_by_seller'),
    url(r'^bicycle-store/view/seller/year/(?P<year>\d+)/$', 'catalog.accounting.views.bicycle_store_list_by_seller'),
    url(r'^bicycle-store/view/seller/bycompany/(?P<brand>\d+)/$', 'catalog.accounting.views.bicycle_store_list_by_seller', {'all': True}),        
    url(r'^bicycle-store/view/seller/bycompany/(?P<brand>\d+)/html/$', 'catalog.accounting.views.bicycle_store_list_by_seller', {'all': True, 'html': True}),
    url(r'^bicycle-store/now/view/$', 'catalog.accounting.views.bicycle_store_list'),
    url(r'^bicycle-store/all/view/$', 'catalog.accounting.views.bicycle_store_list',{'all': True}),
    url(r'^bicycle-store/view/$', 'catalog.accounting.views.bicycle_store_list'),
    url(r'^bicycle-store/edit/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_store_edit'),
    url(r'^bicycle-store/edit/$', 'catalog.accounting.views.bicycle_store_edit'),
    url(r'^bicycle-store/delete/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_store_del'),
    url(r'^bicycle-store/search/$', 'catalog.accounting.views.bicycle_store_search'),
    url(r'^bicycle-store/search/result/$', 'catalog.accounting.views.bicycle_store_search_result'),
    
    url(r'^bicycle/price/set/$', 'catalog.accounting.views.bicycle_price_set'),

    url(r'^bicycle/sale/add/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_sale_add'),
    url(r'^bicycle/sale/add/$', 'catalog.accounting.views.bicycle_sale_add'),
    url(r'^bicycle/sale/id/(?P<id>\d+)/view/$', 'catalog.accounting.views.bicycle_sale_list'),
    url(r'^bicycle/sale/view/$', 'catalog.accounting.views.bicycle_sale_list'),
    url(r'^bicycle/sale/year/(?P<year>\d+)/view/$', 'catalog.accounting.views.bicycle_sale_list', name='bike-sale-by-year'),
    url(r'^bicycle/sale/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.bicycle_sale_list'),
    url(r'^bicycle/sale/brand/(?P<id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.bicycle_sale_list_by_brand'),    
    url(r'^bicycle/sale/edit/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_sale_edit'),    
    url(r'^bicycle/sale/delete/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_sale_del'),
    url(r'^bicycle/sale/report/month/$', 'catalog.accounting.views.bicycle_sale_report'),
    url(r'^bicycle/sale/service/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_sale_service'),
    url(r'^bicycle/sale/service/$', 'catalog.accounting.views.bicycle_sale_service'),
    url(r'^bicycle/sale/(?P<id>\d+)/check/$', 'catalog.accounting.views.bicycle_sale_check'),
    #url(r'^bicycle/sale/(?P<id>\d+)/check/print/$', 'catalog.accounting.views.bicycle_sale_check_print'),
    url(r'^bicycle/sale/(?P<id>\d+)/check/print/$', 'catalog.accounting.views.bicycle_sale_check', {'param': 'print'}),
    url(r'^bicycle/sale/(?P<id>\d+)/check/email/$', 'catalog.accounting.views.bicycle_sale_check', {'param': 'email'}),
    url(r'^bicycle/sale/(?P<id>\d+)/check/add/$', 'catalog.accounting.views.bicycle_sale_check_add'),
    url(r'^bicycle/sale/report/brand/$', 'catalog.accounting.views.bicycle_sale_report_by_brand'),
    url(r'^bicycle/sale/search/model/$', 'catalog.accounting.views.bicycle_sale_search_by_name'),        
    url(r'^bicycle/sale/search/model/result/$', 'catalog.accounting.views.bsale_search_by_name_result'),
    
    
    # bicycle order by client
    url(r'^bicycle/order/view/$', 'catalog.accounting.views.bicycle_order_list'),
    url(r'^bicycle/order/done/$', 'catalog.accounting.views.bicycle_order_done'),
    url(r'^bicycle/order/add/$', 'catalog.accounting.views.bicycle_order_add'),
    url(r'^bicycle/order/edit/(?P<id>\d+)/$', 'catalog.accounting.views.bicycle_order_edit'),
    url(r'^bicycle/order/(?P<id>\d+)/delete/$', 'catalog.accounting.views.bicycle_order_del'),
    url(r'^bike/lookup/$', 'catalog.accounting.views.bike_lookup'),
    
    #storage bicycle
    url(r'^bicycle/storage/type/view/$', 'catalog.accounting.views.bicycle_storage_type_list'),
    url(r'^bicycle/storage/type/add/$', 'catalog.accounting.views.bicycle_storage_type_add'),
    url(r'^bicycle/storage/add/$', 'catalog.accounting.views.bicycle_storage_add'),
    url(r'^bicycle/storage/(?P<id>\d+)/edit/$', 'catalog.accounting.views.bicycle_storage_edit'),
    url(r'^bicycle/storage/(?P<id>\d+)/delete/$', 'catalog.accounting.views.bicycle_storage_delete'),
    url(r'^bicycle/storage/view/$', 'catalog.accounting.views.bicycle_storage_list'),
        
    # Dealer/Dealer Managers operation
    url(r'^dealer/payment/add/$', 'catalog.accounting.views.dealer_payment_add'),
    url(r'^dealer/payment/view/$', 'catalog.accounting.views.dealer_payment_list'),
    url(r'^dealer/payment/delete/(?P<id>\d+)/$', 'catalog.accounting.views.dealer_payment_del'),

    url(r'^dealer/invoice/add/$', 'catalog.accounting.views.dealer_invoice_add'),
    url(r'^dealer/invoice/view/$', 'catalog.accounting.views.dealer_invoice_list_month'),
    url(r'^dealer/invoice/company/(?P<id>\d+)/view/$', 'catalog.accounting.views.dealer_invoice_list'),
    url(r'^dealer/invoice/company/(?P<id>\d+)/year/(?P<year>\d+)/view/$', 'catalog.accounting.views.dealer_invoice_list'),
    url(r'^dealer/invoice/company/(?P<id>\d+)/(?P<pay>paid|notpaid|sending)/$', 'catalog.accounting.views.dealer_invoice_list'),    
    url(r'^dealer/invoice/year/(?P<year>\d+)/(?P<pay>paid|notpaid|sending)/$', 'catalog.accounting.views.dealer_invoice_list_month'),
    url(r'^dealer/invoice/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.dealer_invoice_list_month'),
    url(r'^dealer/invoice/year/(?P<year>\d+)/view/$', 'catalog.accounting.views.dealer_invoice_list_year'),
    #url(r'^dealer/invoice/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.dealer_invoice_list_month'),
    url(r'^dealer/invoice/view/all/$', 'catalog.accounting.views.dealer_invoice_list'),
    url(r'^dealer/invoice/view/$', 'catalog.accounting.views.dealer_invoice_list'),
    url(r'^dealer/invoice/search/$', 'catalog.accounting.views.dealer_invoice_search'),
    url(r'^dealer/invoice/search/result/$', 'catalog.accounting.views.dealer_invoice_search_result'),
    url(r'^dealer/invoice/edit/(?P<id>\d+)/$', 'catalog.accounting.views.dealer_invoice_edit', name='dealer_invoice_edit'),
    url(r'^dealer/invoice/delete/(?P<id>\d+)/$', 'catalog.accounting.views.dealer_invoice_del'),
    url(r'^dealer/invoice/import/file/$', 'catalog.accounting.views.invoice_import'),
    url(r'^dealer/invoice/import/$', 'catalog.accounting.views.invoice_import_form'),
    url(r'^dealer/invoice/new/$', 'catalog.accounting.views.invoice_new_item'),
    url(r'^dealer/invoice/new/edit/$', 'catalog.accounting.views.invoice_new_edit'),
    url(r'^dealer/invoice/miss/$', 'catalog.accounting.views.invoice_miss_stuff'),
    url(r'^dealer/invoice/recived/set/$', 'catalog.accounting.views.dealer_invoice_set'),
    
    url(r'^dealer/add/$', 'catalog.accounting.views.dealer_add'),
    url(r'^dealer/view/$', 'catalog.accounting.views.dealer_list'),
    url(r'^dealer/edit/(?P<id>\d+)/$', 'catalog.accounting.views.dealer_edit'),
    url(r'^dealer/delete/(?P<id>\d+)/$', 'catalog.accounting.views.dealer_del'),

    url(r'^dealer-manager/add/$', 'catalog.accounting.views.dealer_manager_add'),
    url(r'^dealer-manager/view/$', 'catalog.accounting.views.dealer_manager_list'),
    url(r'^dealer-manager/edit/(?P<id>\d+)/$', 'catalog.accounting.views.dealer_manager_edit'),    
    url(r'^dealer-manager/delete/(?P<id>\d+)/$', 'catalog.accounting.views.dealer_manager_del'),

    #Invoice
    url(r'^invoice/add/$', 'catalog.accounting.views.invoicecomponent_add'),
    url(r'^invoice/catalog/(?P<cid>\d+)/add/$', 'catalog.accounting.views.invoicecomponent_add'),
    url(r'^invoice/manufacture/(?P<mid>\d+)/add/$', 'catalog.accounting.views.invoicecomponent_add'),
#    url(r'^invoice/manufacture/(?P<mid>\d+)/view/$', 'catalog.accounting.views.invoicecomponent_list_by_manufacturer'),
    url(r'^invoice/manufacture/(?P<mid>\d+)/view/$', 'catalog.accounting.views.invoicecomponent_list'),    
    url(r'^invoice/year/(?P<sel_year>\d+)/manufacture/(?P<mid>\d+)/view/$', 'catalog.accounting.views.invoicecomponent_list', name="invoice_year_manufacture"),
#    url(r'^invoice/manufacture/(?P<mid>\d+)/availability/view/$', 'catalog.accounting.views.invoicecomponent_list_by_manufacturer', {'availability': 1}),
    url(r'^invoice/manufacture/(?P<mid>\d+)/availability/view/html/$', 'catalog.accounting.views.invoicecomponent_manufacturer_html', name="sendmail_manufacture"),    
    url(r'^invoice/category/(?P<mid>\d+)/availability/view/html/$', 'catalog.accounting.views.invoicecomponent_category_html', name="sendmail_category"),
#    url(r'^invoice/manufacture/view/$', 'catalog.accounting.views.invoicecomponent_list_by_manufacturer'),
    url(r'^invoice/manufacture/view/$', 'catalog.accounting.views.invoicecomponent_list', {'focus': 1}),
    url(r'^invoice/category/view/$', 'catalog.accounting.views.invoicecomponent_list', {'focus': 2}),
    #url(r'^invoice/category/view/$', 'catalog.accounting.views.invoicecomponent_list_by_category'),
#    url(r'^invoice/category/(?P<cid>\d+)/view/$', 'catalog.accounting.views.invoicecomponent_list_by_category'),
    url(r'^invoice/category/(?P<cid>\d+)/view/$', 'catalog.accounting.views.invoicecomponent_list', name="category_id_list"),
    url(r'^invoice/list/(?P<limit>\d+)/view/$', 'catalog.accounting.views.invoicecomponent_list'),
    url(r'^invoice/price/update/(?P<upday>\d+)/view/$', 'catalog.accounting.views.invoicecomponent_list'),
    url(r'^invoice/list/view/$', 'catalog.accounting.views.invoicecomponent_list'),
    url(r'^invoice/id/(?P<id>\d+)/view/$', 'catalog.accounting.views.invoice_id_list'),
    url(r'^invoice/catalog/(?P<cid>\d+)/view/$', 'catalog.accounting.views.invoice_cat_id_list', name='invoice_catalog_view'), # наявний товар
    url(r'^invoice/delete/(?P<id>\d+)/$', 'catalog.accounting.views.invoicecomponent_del'),
    url(r'^invoice/edit/(?P<id>\d+)/$', 'catalog.accounting.views.invoicecomponent_edit'),
    url(r'^invoice/report/$', 'catalog.accounting.views.invoice_report'),
    url(r'^invoice/all/report/$', 'catalog.accounting.views.invoicecomponent_sum'),
    url(r'^invoice/search/$', 'catalog.accounting.views.invoice_search'),
    #url(r'^invoice/search/result/$', 'catalog.accounting.views.invoice_search_result'),
    url(r'^invoice/search/result/$', 'catalog.accounting.views.invoicecomponent_list'),
    url(r'^invoice/sale/list/$', 'catalog.accounting.views.invoicecomponent_list', {'isale': True}),
    url(r'^invoice/enddate/list/$', 'catalog.accounting.views.invoicecomponent_list', {'enddate': True}),
    url(r'^invoice/print/forum/$', 'catalog.accounting.views.invoicecomponent_print'),

    # Component Type operation
    url(r'^category/add/$', 'catalog.accounting.views.category_add'),
    url(r'^category/view/$', 'catalog.accounting.views.category_list'),
    url(r'^category/edit/(?P<id>\d+)$', 'catalog.accounting.views.category_edit'),
    url(r'^category/delete/(?P<id>\d+)$', 'catalog.accounting.views.category_del'),    
    url(r'^category/get/list/$', 'catalog.accounting.views.category_get_list'),
    url(r'^category/lookup/$', 'catalog.accounting.views.category_lookup'),

    # Catalog operation
    url(r'^catalog/set/type/$', 'catalog.accounting.views.catalog_set_type'),
    url(r'^catalog/add/$', 'catalog.accounting.views.catalog_add'),
    url(r'^catalog/discount/$', 'catalog.accounting.views.catalog_discount_list'),
    url(r'^catalog/id/(?P<id>\d+)/view/$', 'catalog.accounting.views.catalog_list', name="catalog_id_view"),
    url(r'^catalog/view/$', 'catalog.accounting.views.catalog_list'),
    url(r'^catalog/manufacture/(?P<id>\d+)/type/(?P<tid>\d+)/view/$', 'catalog.accounting.views.catalog_manu_type_list'),
    url(r'^catalog/manufacture/(?P<id>\d+)/view/(\d+)$', 'catalog.accounting.views.catalog_part_list'),
    url(r'^catalog/manufacture/(?P<id>\d+)/view/$', 'catalog.accounting.views.catalog_manufacture_list'),
    url(r'^catalog/manufacture/view/$', 'catalog.accounting.views.catalog_manufacture_list'),
    url(r'^catalog/type/(?P<id>\d+)/view/$', 'catalog.accounting.views.catalog_type_list'),    
    url(r'^catalog/edit/$', 'catalog.accounting.views.catalog_set', name="cat_set_attr"),    
    url(r'^catalog/edit/(?P<id>\d+)$', 'catalog.accounting.views.catalog_edit', name='catalog_edit'),
    url(r'^catalog/sale/edit/$', 'catalog.accounting.views.catalog_sale_edit'),
    url(r'^catalog/delete/(?P<id>\d+)$', 'catalog.accounting.views.catalog_delete'),
    url(r'^catalog/search/id/$', 'catalog.accounting.views.catalog_search_id'),
    url(r'^catalog/search/locality/$', 'catalog.accounting.views.catalog_search_locality'),
    url(r'^catalog/search/result/$', 'catalog.accounting.views.catalog_search_result'),
    url(r'^catalog/search/locality/$', 'catalog.accounting.views.catalog_search_result'),
    url(r'^catalog/lookup/$', 'catalog.accounting.views.catalog_lookup'),
    url(r'^catalog/import/$', 'catalog.accounting.views.catalog_import'),
    url(r'^catalog/get/locality/$', 'catalog.accounting.views.catalog_get_locality'),

    # Client
    url(r'^client/(?P<id>\d+)$', 'catalog.accounting.views.client_data'),
    url(r'^clients/balance/$', 'catalog.accounting.views.client_balance_list'),
    url(r'^client/add/$', 'catalog.accounting.views.client_add'),
    url(r'^client/edit/(?P<id>\d+)$', 'catalog.accounting.views.client_edit'),
    url(r'^client/view/$', 'catalog.accounting.views.client_list'),
    url(r'^client/email/view/$', 'catalog.accounting.views.client_email_list'),
    url(r'^client/delete/(?P<id>\d+)$', 'catalog.accounting.views.client_delete'),
    url(r'^client/search/$', 'catalog.accounting.views.client_search'),
    url(r'^client/search/result/$', 'catalog.accounting.views.client_search_result'),
    url(r'^client/result/search/$', 'catalog.accounting.views.client_result'),
    url(r'^client/lookup/$', 'catalog.accounting.views.client_lookup'),
    url(r'^client/lookup/byid/$', 'catalog.accounting.views.client_lookup_by_id'),
    url(r'^client/join/$', 'catalog.accounting.views.client_join'),
    url(r'^client/(?P<id>\d+)/sendcard/', 'catalog.accounting.views.client_card_sendemail'),
    
#delete    url(r'^client/result/$', 'catalog.accounting.views.search_client_id'),
    url(r'^client/invoice/view/$', 'catalog.accounting.views.client_invoice_view'),
    url(r'^client/invoice/set/$', 'catalog.accounting.views.client_invoice_set'),
    url(r'^client/invoice/(?P<id>\d+)/edit/$', 'catalog.accounting.views.client_invoice_edit'),
    url(r'^client/invoice/add/$', 'catalog.accounting.views.client_invoice_add'),
    url(r'^client/(?P<cid>\d+)/invoice/add/$', 'catalog.accounting.views.client_invoice'),
# ajax table for client invoice    
    url(r'^client/(?P<client_id>\d+)/invoice/lookup/$', 'catalog.accounting.views.client_invoice_lookup'),
    url(r'^client/invoice/catalog/(?P<cid>\d+)/add/$', 'catalog.accounting.views.client_invoice'),
    url(r'^client/(?P<id>\d+)/invoice/catalog/(?P<cid>\d+)/add/$', 'catalog.accounting.views.client_invoice'),
    url(r'^sale/(?P<cid>\d+)/$', 'catalog.accounting.views.client_invoice', {'id': 138}), #short link for sale in android device
    url(r'^s/(?P<cid>\d+)/$', 'catalog.accounting.views.client_invoice_shorturl'), #short link for sale in android device    
    url(r'^client/invoice/catalog/(?P<id>\d+)/view/$', 'catalog.accounting.views.client_invoice_id'),
#    url(r'^client/invoice/add/$', 'catalog.accounting.views.client_invoice'),
    url(r'^client/invoice/delete/$', 'catalog.accounting.views.client_invoice_delete'),
    url(r'^client/invoice/(?P<id>\d+)/delete/$', 'catalog.accounting.views.client_invoice_delete'),    
    url(r'^client/invoice/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.client_invoice_view', {'day':"all"}),
    url(r'^client/invoice/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', 'catalog.accounting.views.client_invoice_view'),
    url(r'^client/invoice/report/$', 'catalog.accounting.views.client_invoice_report'),
    url(r'^client/invoice/check/$', 'catalog.accounting.views.client_invoice_check', {'param': 'print'}),
    url(r'^client/invoice/check/email/$', 'catalog.accounting.views.client_invoice_check', {'param': 'email'}),
    url(r'^client/workshop/check/$', 'catalog.accounting.views.client_workshop_check', {'param': 'print'}),
    url(r'^client/workshop/check/email/$', 'catalog.accounting.views.client_workshop_check', {'param': 'email'}),
    
    url(r'^client/invoice/return/(?P<id>\d+)/add/$', 'catalog.accounting.views.client_invioce_return_add'),
    url(r'^client/invoice/return/list/$', 'catalog.accounting.views.client_invioce_return_view'),

    url(r'^clientdebts/add/(?P<id>\d+)$', 'catalog.accounting.views.clientdebts_add'),
    url(r'^clientdebts/view/$', 'catalog.accounting.views.clientdebts_list'),
    url(r'^clientdebts/edit/(?P<id>\d+)$', 'catalog.accounting.views.clientdebts_edit'),
    url(r'^clientdebts/delete/(?P<id>\d+)$', 'catalog.accounting.views.clientdebts_delete'),
    url(r'^clientdebts/(?P<client_id>\d+)/delete/all/$', 'catalog.accounting.views.clientdebts_delete_all'),

    url(r'^clientcredits/add/(?P<id>\d+)$', 'catalog.accounting.views.clientcredits_add'),
    url(r'^clientcredits/view/$', 'catalog.accounting.views.clientcredits_list'),
    url(r'^clientcredits/edit/(?P<id>\d+)$', 'catalog.accounting.views.clientcredits_edit'),    
    url(r'^clientcredits/delete/(?P<id>\d+)$', 'catalog.accounting.views.clientcredits_delete'),
    url(r'^clientcredits/(?P<client_id>\d+)/delete/all/$', 'catalog.accounting.views.clientcredits_delete_all'),
    url(r'^clientcredits/set/$', 'catalog.accounting.views.clientcredits_set'),

    url(r'^client/order/add/$', 'catalog.accounting.views.client_order_add'),
    url(r'^client/order/view/$', 'catalog.accounting.views.client_order_list'),
    url(r'^client/order/delete/(?P<id>\d+)$', 'catalog.accounting.views.client_order_delete'),
    url(r'^client/order/edit/(?P<id>\d+)/$', 'catalog.accounting.views.client_order_edit'),

    url(r'^payform/workshop/$', 'catalog.accounting.views.workshop_payform'),
    url(r'^payform/$', 'catalog.accounting.views.payform'),
    url(r'^catalog/saleform/$', 'catalog.accounting.views.catalog_saleform'),    
    url(r'^client/payform/$', 'catalog.accounting.views.client_payform'),
    url(r'^client/workshop/payform/$', 'catalog.accounting.views.client_ws_payform'),
    # Example:
    # url(r'^catalog/', include('catalog.foo.urls')),
#    url(r'^sendmail/$', 'catalog.accounting.views.sendemail'),
    url(r'^asearch/$', 'catalog.accounting.views.ajax_search'),

    url(r'^media/(?P<path>.*)', 'django.views.static.serve',
     # static files
    #{'document_root': 'D:/develop/catalog/media'}),
    {'document_root': os.path.join(dirname, 'media')}),
    
    url(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    url(r'^accounts/login/$',  'catalog.accounting.views.login'),
    url(r'^accounts/logout/$', 'catalog.accounting.views.logout'),
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^admin/', include('admin.site.urls')),

    url(r'^$', main_page),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/(.*)', admin.site.root),
   
)

urlpatterns += patterns('',
    # WorkShop 
    #operation by GROUP
    url(r'^workgroup/add/$', 'catalog.accounting.views.workgroup_add'),
    url(r'^workgroup/edit/(?P<id>\d+)$', 'catalog.accounting.views.workgroup_edit'),
    url(r'^workgroup/view/$', 'catalog.accounting.views.workgroup_list', name="workgrouplist"),
    url(r'^workgroup/delete/(?P<id>\d+)$', 'catalog.accounting.views.workgroup_delete'),

    url(r'^worktype/add/$', 'catalog.accounting.views.worktype_add'),
    url(r'^worktype/edit/(?P<id>\d+)$', 'catalog.accounting.views.worktype_edit'),
    url(r'^worktype/view/group/(?P<id>\d+)$', 'catalog.accounting.views.worktype_list'),        
    url(r'^worktype/view/$', 'catalog.accounting.views.worktype_list', name="worktypelist"),
    url(r'^worktype/delete/(?P<id>\d+)$', 'catalog.accounting.views.worktype_delete'),
    url(r'^worktype/price/$', 'catalog.accounting.views.worktype_ajax'),    
    url(r'^worktype/lookup/$', 'catalog.accounting.views.worktype_lookup'),
    url(r'^work/depence/add/$', 'catalog.accounting.views.worktype_depence_add', name="add_work_depence"),
    url(r'^work/depence/delete/$', 'catalog.accounting.views.worktype_depence_delete', name="delete_work_depence"), 
    url(r'^work/depence/components/add/$', 'catalog.accounting.views.worktype_depence_component_add', name="add_work_component_depence"),
    url(r'^work/depence/components/delete/$', 'catalog.accounting.views.worktype_depence_component_delete', name="delete_work_components_depence"),

    url(r'^phonestatus/view/$', 'catalog.accounting.views.phonestatus_list'),
    url(r'^phonestatus/add/$', 'catalog.accounting.views.phonestatus_add'),
    url(r'^phonestatus/edit/(?P<id>\d+)$', 'catalog.accounting.views.phonestatus_edit'),
    url(r'^phonestatus/delete/(?P<id>\d+)$', 'catalog.accounting.views.phonestatus_delete'),
    url(r'^workstatus/add/$', 'catalog.accounting.views.workstatus_add'),
    url(r'^workstatus/view/$', 'catalog.accounting.views.workstatus_list'),
    url(r'^workstatus/edit/(?P<id>\d+)$', 'catalog.accounting.views.workstatus_edit'),
    url(r'^workstatus/delete/(?P<id>\d+)$', 'catalog.accounting.views.workstatus_delete'),

    url(r'^workticket/add/$', 'catalog.accounting.views.workticket_add'),
    url(r'^workticket/add/client/(?P<id>\d+)/$', 'catalog.accounting.views.workticket_add'),    
    url(r'^workticket/view/$', 'catalog.accounting.views.workticket_list'),
    url(r'^workticket/edit/$', 'catalog.accounting.views.workticket_edit'),
    url(r'^workticket/edit/(?P<id>\d+)/$', 'catalog.accounting.views.workticket_edit'),    
    url(r'^workticket/delete/(?P<id>\d+)/$', 'catalog.accounting.views.workticket_delete'),
    url(r'^workticket/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.workticket_list'),
    url(r'^workticket/status/(?P<status>\d+)/view/$', 'catalog.accounting.views.workticket_list'),
    url(r'^workticket/all/view/$', 'catalog.accounting.views.workticket_list', {'all': True}),

    url(r'^workshop/price/list/print/$', 'catalog.accounting.views.workshop_pricelist', {'pprint': True}),
    url(r'^workshop/price/list/$', 'catalog.accounting.views.workshop_pricelist', {'pprint': False}),
    url(r'^workshop/add/(?P<id>\d+)/$', 'catalog.accounting.views.workshop_add'),
    url(r'^workshop/add/client/(?P<id_client>\d+)/$', 'catalog.accounting.views.workshop_add'),
    url(r'^workshop/add/$', 'catalog.accounting.views.workshop_add'),
    url(r'^workshop/add/formset/$', 'catalog.accounting.views.workshop_add_formset'),
    url(r'^workshop/edit/(?P<id>\d+)/$', 'catalog.accounting.views.workshop_edit'),
    url(r'^workshop/view/$', 'catalog.accounting.views.workshop_list'),
    url(r'^workshop/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', 'catalog.accounting.views.workshop_list'),
    url(r'^workshop/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.workshop_list', {'day': "all"}),
    url(r'^workshop/year/(?P<year>\d+)/view/$', 'catalog.accounting.views.workshop_list'),
    url(r'^workshop/delete/(?P<id>\d+)/$', 'catalog.accounting.views.workshop_delete'),    
    url(r'^workshop/delete/$', 'catalog.accounting.views.workshop_delete'),
)


#from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
#urlpatterns += staticfiles_urlpatterns()
urlpatterns += patterns('',
    url(r'^manyforms/(?P<author_id>\d+)$', 'catalog.accounting.views.manage_works'),
    url(r'^manyforms/test/$', 'catalog.accounting.views.formset_test'),
    url(r'^workshop/done/client/(?P<id>\d+)/$', 'catalog.accounting.views.formset_test'),
    url(r'^manyforms/test1/$', 'catalog.accounting.views.inline_formset_test'),

    #ajax
    url(r'^insertstory/$', 'catalog.accounting.views.insertstory'),
    url(r'^ajax/test/$', 'catalog.accounting.views.ajax_test'),

    url(r'^preorder/add/$', 'catalog.accounting.views.preorder_add'),
    url(r'^preorder/view/$', 'catalog.accounting.views.preorder_list'),
    url(r'^preorder/edit/(?P<id>\d+)/$', 'catalog.accounting.views.preorder_edit'),
    url(r'^preorder/delete/(?P<id>\d+)/$', 'catalog.accounting.views.preorder_delete'),         

    # my cost
    url(r'^cost/type/add/$', 'catalog.accounting.views.costtype_add'),
    url(r'^cost/type/view/$', 'catalog.accounting.views.costtype_list'),
    url(r'^cost/type/delete/(?P<id>\d+)$', 'catalog.accounting.views.costtype_delete'),    

    url(r'^cost/add/(?P<id>\d+)$', 'catalog.accounting.views.cost_add'),
    url(r'^cost/add/$', 'catalog.accounting.views.cost_add'),
    url(r'^cost/view/$', 'catalog.accounting.views.cost_list'),
    url(r'^cost/delete/(?P<id>\d+)/$', 'catalog.accounting.views.cost_delete'),    
    url(r'^cost/edit/(?P<id>\d+)/$', 'catalog.accounting.views.cost_edit'),

    url(r'^report/sales/user/report/$', 'catalog.accounting.views.user_invoice_report', {'day':"all"}),
    url(r'^report/sales/user/(?P<user_id>\d+)/report/$', 'catalog.accounting.views.user_invoice_report', {'day':"all"}),
    url(r'^report/sales/user/year/(?P<year>\d+)/month/(?P<month>\d+)/report/$', 'catalog.accounting.views.user_invoice_report', {'day':"all"}),
    url(r'^report/sales/user/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/report/$', 'catalog.accounting.views.user_invoice_report'),
    url(r'^report/sales/user/(?P<user_id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/report/$', 'catalog.accounting.views.user_invoice_report', {'day':"all"}),
    url(r'^report/sales/user/(?P<user_id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/report/$', 'catalog.accounting.views.user_invoice_report'),

    url(r'^report/workshop/byuser/$', 'catalog.accounting.views.user_workshop_report', {'day':"all"}),
    url(r'^report/workshop/(?P<user_id>\d+)/byuser/$', 'catalog.accounting.views.user_workshop_report', {'day':"all"}),
    url(r'^report/workshop/byuser/year/(?P<year>\d+)/month/(?P<month>\d+)/$', 'catalog.accounting.views.user_workshop_report', {'day':"all"}),
    url(r'^report/workshop/byuser/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/$', 'catalog.accounting.views.user_workshop_report'),
    url(r'^report/workshop/(?P<user_id>\d+)/byuser/year/(?P<year>\d+)/month/(?P<month>\d+)/$', 'catalog.accounting.views.user_workshop_report', {'day':"all"}),
    url(r'^report/workshop/(?P<user_id>\d+)/byuser/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/$', 'catalog.accounting.views.user_workshop_report'),
    url(r'^report/salary/all_user/$', 'catalog.accounting.views.all_user_salary_report', {'day':"all"}),
    url(r'^report/salary/all_user/year/(?P<year>\d+)/month/(?P<month>\d+)/$', 'catalog.accounting.views.all_user_salary_report', {'day':"all"}),

    url(r'^shop/price/lastadded/(?P<id>\d+)/view/$', 'catalog.accounting.views.shop_price_lastadd'),    
    url(r'^shop/price/lastadded/(?P<id>\d+)/print/$', 'catalog.accounting.views.shop_price_lastadd', {'pprint': True}),
    url(r'^shop/price/company/(?P<mid>\d+)/view/$', 'catalog.accounting.views.shop_price'), #work
    url(r'^shop/price/company/(?P<mid>\d+)/print/$', 'catalog.accounting.views.shop_price', {'pprint': True}), #work
    url(r'^shop/price/bysearch_id/(?P<id>.*)/view/$', 'catalog.accounting.views.shop_price_bysearch_id'),
    url(r'^shop/price/bysearch_id/(?P<id>.*)/print/$', 'catalog.accounting.views.shop_price_bysearch_id_print'),
    url(r'^shop/price/bysearch_name/(?P<id>.*)/view/$', 'catalog.accounting.views.shop_price_bysearch_name'),
    url(r'^shop/price/bysearch_name/(?P<id>.*)/print/$', 'catalog.accounting.views.shop_price_bysearch_name', {'pprint': True}),
    url(r'^shop/price/print/(?P<id>\d+)/add/$', 'catalog.accounting.views.shop_price_print_add'),
#    url(r'^shop/price/print/add/$', 'catalog.accounting.views.ajax_price_print'),
    url(r'^shop/price/print/add/$', 'catalog.accounting.views.shop_price_print_add'),
    url(r'^shop/price/print/view/$', 'catalog.accounting.views.shop_price_print_list', {'pprint': True}),
    url(r'^shop/price/qr/print/view/$', 'catalog.accounting.views.shop_price_qrcode_print_view'),
    url(r'^shop/price/print/empty/$', 'catalog.accounting.views.shop_price_print_delete_all'),    
    url(r'^shop/price/print/list/$', 'catalog.accounting.views.shop_price_print_list'),
    url(r'^shop/price/print/delete/$', 'catalog.accounting.views.shop_price_print_delete'),
    url(r'^shop/price/print/(?P<id>\d+)/delete/$', 'catalog.accounting.views.shop_price_print_delete'),
    url(r'^catalog/price/import/file/$', 'catalog.accounting.views.price_import'),
    url(r'^catalog/price/import/$', 'catalog.accounting.views.price_import_form'),

    url(r'^photo/url/bicycle/add/$', 'catalog.accounting.views.bike_photo_url_add'),
    url(r'^photo/url/add/$', 'catalog.accounting.views.photo_url_add'),
    url(r'^photo/url/get/$', 'catalog.accounting.views.photo_url_get'),
    url(r'^photo/id/(?P<id>\d+)/get/$', 'catalog.accounting.views.photo_url_get', name='photo_get'),
    url(r'^photo/id/(?P<id>\d+)/delete/$', 'catalog.accounting.views.photo_url_delete'),
    url(r'^photo/field/delete/$', 'catalog.accounting.views.photo_del_field', name="photo_del_field"),
    url(r'^catalog/photo/delete/$', 'catalog.accounting.views.photo_url_delete'),
    url(r'^catalog/photo/list/(?P<show>\d+)/page/(?P<page>\d+)/limit/(?P<limit>\d+)/$', 'catalog.accounting.views.photo_list'),
    url(r'^catalog/photo/list/(?P<show>\d+)/page/(?P<page>\d+)/limit/$', 'catalog.accounting.views.photo_list'),
    url(r'^catalog/photo/list/(?P<show>\d+)/$', 'catalog.accounting.views.photo_list'),
    url(r'^catalog/photo/list/$', 'catalog.accounting.views.photo_list'),
        
    url(r'^youtube/list/$', 'catalog.accounting.views.youtube_list', name='youtube_list'),    
    url(r'^youtube/(?P<id>\d+)/delete/$', 'catalog.accounting.views.youtube_delete'),
    url(r'^youtube/add/$', 'catalog.accounting.views.youtube_url_add', name='youtube_add'),
    url(r'^youtube/url/get/$', 'catalog.accounting.views.youtube_url_get'),
    url(r'^youtube/set/$', 'catalog.accounting.views.youtube_set'),
    
    url(r'^workday/user/all/report/$', 'catalog.accounting.views.workday_list'),
    url(r'^workday/alluser/report/$', 'catalog.accounting.views.workday_ajax'),
    url(r'^workday/add/$', 'catalog.accounting.views.workday_add'),
    url(r'^workday/(?P<id>\d+)/delete/$', 'catalog.accounting.views.workday_delete'),
    
    url(r'^clientmessage/add/$', 'catalog.accounting.views.clientmessage_add'),
    url(r'^clientmessage/set/$', 'catalog.accounting.views.clientmessage_set'),
    url(r'^clientmessage/list/$', 'catalog.accounting.views.clientmessage_list'),
    url(r'^clientmessage/(?P<id>\d+)/delete/$', 'catalog.accounting.views.clientmessage_delete'),

    url(r'^client_history/cred/$', 'catalog.accounting.views.client_history_cred'),
    url(r'^client_history/debt/$', 'catalog.accounting.views.client_history_debt'),
    url(r'^client_history/invoice/$', 'catalog.accounting.views.client_history_invoice'),
    
    url(r'^cashtype/view/$', 'catalog.accounting.views.cashtype_list'),
    url(r'^cashtype/list/$', 'catalog.accounting.views.cashtype_list'),
    url(r'^cashtype/add/$', 'catalog.accounting.views.cashtype_add'),
    url(r'^cashtype/edit/(?P<id>\d+)$', 'catalog.accounting.views.cashtype_edit'),
    url(r'^cashtype/delete/(?P<id>\d+)$', 'catalog.accounting.views.cashtype_del'),
    
    url(r'^rent/add/$', 'catalog.accounting.views.rent_add'),
    url(r'^rent/edit/(?P<id>\d+)/$', 'catalog.accounting.views.rent_edit'),
    url(r'^rent/delete/(?P<id>\d+)/$', 'catalog.accounting.views.rent_delete'),    
    url(r'^rent/view/$', 'catalog.accounting.views.rent_list'),

    # Curency operation
    url(r'^curency/add/$', 'catalog.accounting.views.curency_add'),
    url(r'^curency/view/$', 'catalog.accounting.views.curency_list'),
    url(r'^curency/delete/(?P<id>\d+)/$', 'catalog.accounting.views.curency_del'),
    
    url(r'^exchange/add/$', 'catalog.accounting.views.exchange_add'),
    url(r'^exchange/view/$', 'catalog.accounting.views.exchange_list'),
    url(r'^exchange/edit/(?P<id>\d+)/$', 'catalog.accounting.views.exchange_edit'),
    url(r'^exchange/delete/(?P<id>\d+)/$', 'catalog.accounting.views.exchange_del'),    
    
    url(r'^storage/boxes/$', 'catalog.accounting.views.storage_box_list'),
    url(r'^storage/boxes/list/$', 'catalog.accounting.views.storage_boxes'),
    url(r'^storage/boxes/print/$', 'catalog.accounting.views.storage_box_list', {'pprint': True}),
    url(r'^storage/box/(?P<boxname>[\w,.]+)/view/$', 'catalog.accounting.views.storage_box_list'),
    url(r'^storage/box/delete/$', 'catalog.accounting.views.storage_box_delete'),
    url(r'^storage/box/rename/$', 'catalog.accounting.views.storage_box_rename'),

    url(r'^shop/sale/day/add/$', 'catalog.accounting.views.shopdailysales_add'),
    url(r'^shop/sale/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.shopmonthlysales_view'),    
    url(r'^shop/sale/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.shopmonthlysales_view'),    
    url(r'^shop/sale/month/view/$', 'catalog.accounting.views.shopmonthlysales_view'),
    url(r'^shop/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', 'catalog.accounting.views.shopdailysales_view'),    
    url(r'^shop/sale/day/edit/(?P<id>\d+)/$', 'catalog.accounting.views.shopdailysales_edit'),
    url(r'^shop/sale/view/year/(?P<year>\d+)/month/(?P<month>\d+)/$', 'catalog.accounting.views.shopdailysales_list'),    
    url(r'^shop/sale/view/month/(\d+)/$', 'catalog.accounting.views.shopdailysales_list'),
    url(r'^shop/sale/view/$', 'catalog.accounting.views.shopdailysales_list'),
    url(r'^shop/sale/day/(?P<id>\d+)/delete/$', 'catalog.accounting.views.shopdailysales_delete'),

    url(r'^inventory/list/$', 'catalog.accounting.views.inventory_list'),
    url(r'^inventory/mistake/list/$', 'catalog.accounting.views.inventory_mistake'),
    url(r'^inventory/mistake/not/all/list/$', 'catalog.accounting.views.inventory_mistake_not_all'),
    url(r'^inventory/autocheck/list/$', 'catalog.accounting.views.inventory_autocheck'),
    url(r'^inventory/fix/list/$', 'catalog.accounting.views.inventory_fix'),
    url(r'^inventory/fix/cat/(?P<cat_id>\d+)/list/$', 'catalog.accounting.views.inventory_fix_catalog', name="fix_inventory"),
    url(r'^inventory/autofix/$', 'catalog.accounting.views.inventory_fix_catalog1'),
    url(r'^inventory/type/(?P<type_id>\d+)/autofix/$', 'catalog.accounting.views.inventory_fix_catalog1'),
#    url(r'^inventory/fix/cat/(?P<cat_id>\d+)/inv/(?P<inv_id>\d+)/list/$', 'catalog.accounting.views.inventory_fix_catalog', name="fix_inventory"),
    url(r'^inventory/autocheck/$', 'catalog.accounting.views.inventory_autocheck', {'update': True}),
    url(r'^inventory/year/(?P<year>\d+)/list/$', 'catalog.accounting.views.inventory_list'),
    url(r'^inventory/year/(?P<year>\d+)/month/(?P<month>\d+)/list/$', 'catalog.accounting.views.inventory_list'),
    url(r'^inventory/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/list/$', 'catalog.accounting.views.inventory_list'),
    url(r'^inventory/add/$', 'catalog.accounting.views.inventory_add'),
    url(r'^inventory/get/$', 'catalog.accounting.views.inventory_get'),
    url(r'^inventory/count/get/$', 'catalog.accounting.views.inventory_get_count'),
    url(r'^inventory/get/listid/$', 'catalog.accounting.views.inventory_get_listid'),
    url(r'^inventory/set/$', 'catalog.accounting.views.inventory_set'),
#    url(r'^inventory/delete/(?P<id>\d+)/$', 'catalog.accounting.views.inventory_delete'),
    url(r'^inventory/delete/$', 'catalog.accounting.views.inventory_delete'),
    url(r'^catalog/join/$', 'catalog.accounting.views.catalog_join'),
    url(r'^catalog/join/(?P<id1>\d+)/(?P<id2>\d+)/$', 'catalog.accounting.views.catalog_join'),
    
    url(r'^check/list/$', 'catalog.accounting.views.check_list',{'all':True}),
    url(r'^check/list/now/$', 'catalog.accounting.views.check_list',{'all':False}),
    url(r'^check/year/(?P<year>\d+)/view/$', 'catalog.accounting.views.check_list',{'all':True}),
    url(r'^check/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', 'catalog.accounting.views.check_list',{'all':True}),
    url(r'^check/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', 'catalog.accounting.views.check_list',{'all':False}),
    url(r'^check/(?P<num>\d+)/print/$', 'catalog.accounting.views.check_print'),
    url(r'^check/add/$', 'catalog.accounting.views.check_add'),
    url(r'^check/shop/add/$', 'catalog.accounting.views.shop_sale_check_add'),
    url(r'^check/workshop/add/$', 'catalog.accounting.views.workshop_sale_check_add'),
    url(r'^check/delete/(?P<id>\d+)/$', 'catalog.accounting.views.check_delete'),
    url(r'^workshop/playsound/$', 'catalog.accounting.views.send_workshop_sound'),
    url(r'^discount/add/$', 'catalog.accounting.views.discount_add'),
    url(r'^discount/list/$', 'catalog.accounting.views.discount_list'),
    url(r'^discount/delete/$', 'catalog.accounting.views.discount_delete'),
    url(r'^discount/lookup/$', 'catalog.accounting.views.discount_lookup'),
) 

#===============================================================================
# 
# if settings.DEBUG:
#    urlpatterns += patterns('',
#        url(r'^debuginfo$', 'catalog.views.debug'),
#    )
#===============================================================================

#===============================================================================
if settings.DEBUG:
#    urlpatterns += patterns('django.contrib.staticfiles.views',
#        urlurl(r'^static/(?P<path>.*)$', 'serve'),
#    )
#    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += staticfiles_urlpatterns()
#===============================================================================