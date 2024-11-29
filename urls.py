# -*- coding: utf-8 -*-
#from django.conf.urls import patterns, include, url
from django.conf.urls import *
#from django.conf.urls import url

#from catalog.views import main_page
#from catalog.test import current_datetime as curdate
#from django.views.generic.simple import direct_to_template
#from django.views.generic import TemplateView
#url(r'^api/casinova$', TemplateView.as_view(template_name='castle_tm/index.html')),

from django.conf import settings
from django.contrib.auth.views import login, logout
from django.conf.urls.static import static
#from django.conf.urls.defaults import include
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from django.conf.urls.static import static

import os
dirname = os.path.dirname(globals()["__file__"])


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


from catalog.accounting import views as catalog
#from credit import views as credit_views

#urlpatterns = patterns('',
urlpatterns = [                     
                       
    url(r'^search/$', catalog.search), # old function
#    url(r'^search/$', catalog.accounting.views.search), # old function
#    url(r'^contact/thanks/$', direct_to_template, {'template': 'thanks.html'}),

    # Manufacturer operation
#    url(r'^manufacturer/search/$', catalog.search'), # old function
    url(r'^manufacturer/view/$', catalog.manufaturer_list), 
#    url(r'^manufacturer/view/$', catalog.manufaturer_list'),    
    url(r'^manufacturer/add/$', catalog.manufacturer_add),
    url(r'^manufacturer/edit/(?P<id>\d+)/$', catalog.manufacturer_edit),    
    url(r'^manufacturer/delete/(?P<id>\d+)/$', catalog.manufacturer_delete),
    url(r'^manufacturer/lookup/$', catalog.manufacturer_lookup), # AJAX 

    # Country operation
    url(r'^country/add/$', catalog.country_add),
    url(r'^country/view/$', catalog.country_list),
    url(r'^country/edit/(?P<id>\d+)/$', catalog.country_edit),    
    url(r'^country/delete/(?P<id>\d+)/$', catalog.country_del),
    # Bank operation
    url(r'^bank/add/$', catalog.bank_add),
    url(r'^bank/view/$', catalog.bank_list),
    url(r'^bank/edit/(?P<id>\d+)/$', catalog.bank_edit),    
    url(r'^bank/delete/(?P<id>\d+)/$', catalog.bank_del),

    # Bicycle operation
    url(r'^bicycle-type/add/$', catalog.bicycle_type_add),
    url(r'^bicycle-type/view/$', catalog.bicycle_type_list),
    url(r'^bicycle-type/edit/(?P<id>\d+)/$', catalog.bicycle_type_edit),    
    url(r'^bicycle-type/delete/(?P<id>\d+)/$', catalog.bicycle_type_del),

    url(r'^bicycle-framesize/add/$', catalog.bicycle_framesize_add),
    url(r'^bicycle-framesize/view/$', catalog.bicycle_framesize_list),
    url(r'^bicycle-framesize/lookup/$', catalog.framesize_lookup, name='frame-size-lookup'),
    url(r'^bicycle/framesize/edit/(?P<id>\d+)/$', catalog.bicycle_framesize_edit, name='framesize-edit'),    
    url(r'^bicycle/framesize/delete/(?P<id>\d+)/$', catalog.bicycle_framesize_del),
    #url(r'^bicycle/framesize/delete/(?P<id>\d)/$', catalog.bicycle_framesize_del'),

    url(r'^bicycle/add/$', catalog.bicycle_add),
    url(r'^bicycle/year/(?P<year>\d+)/view/$', catalog.bicycle_list),
    url(r'^bicycle/year/(?P<year>\d+)/bycompany/(?P<brand>\d+)/view/$', catalog.bicycle_list),    
    url(r'^bicycle/year/(?P<year>\d+)/bycompany/(?P<brand>\d+)/add/sale/(?P<percent>\d+)/$', catalog.bicycle_list),    
# ?    url(r'^bicycle/all/view/$', catalog.bicycle_all_list'),
    url(r'^bicycle/view/$', catalog.bicycle_list),
    url(r'^bicycle/edit/(?P<id>\d+)/$', catalog.bicycle_edit, name='bicycle-edit'),    
    url(r'^bicycle/delete/(?P<id>\d+)/$', catalog.bicycle_del),
    url(r'^bicycle/photo/(?P<id>\d+)/$', catalog.bicycle_photo, name='bicycle-photo'),
    
    url(r'^bicycle/part/add/$', catalog.bicycle_part_add, name='bikepart_add'),
#    url(r'^delete/(\d+)/$', catalog.multiuploader_delete'),
#    url(r'^bicycle/view/list/$', catalog.image_view', name='main'),
#    url(r'^multi/$', catalog.multiuploader', name='multi'),
    
    # get bicycle price and sale by id 
    url(r'^bicycle/price/$', catalog.bicycle_lookup_ajax),

    url(r'^bicycle/store/report/bysize/(?P<id>\d+)/$', catalog.store_report_bysize),
    url(r'^bicycle/store/report/bytype/(?P<id>\d+)/$', catalog.store_report_bytype),
    url(r'^bicycle/store/price/$', catalog.bicycle_store_price),
    #url(r'^bicycle/store/price/print/$', catalog.bicycle_store_price_print'),    
    url(r'^bicycle/store/price/print/$', catalog.bicycle_store_price, {'pprint': True}),
    url(r'^bicycle-store/add/(?P<id>\d+)/$', catalog.bicycle_store_add),
    url(r'^bicycle-store/add/$', catalog.bicycle_store_add),
    url(r'^bicycle-store/all/view/seller/$', catalog.bicycle_store_list_by_seller, {'all': True}),
    url(r'^bicycle-store/simple/view/$', catalog.bicycle_store_simple_list, name='bicycle-store-simple' ),
    url(r'^bicycle-store/view/seller/$', catalog.bicycle_store_list_by_seller),
    url(r'^bicycle-store/view/seller/bysize/(?P<size>\d+)/$', catalog.bicycle_store_list_by_seller),
    url(r'^bicycle-store/view/seller/bysize/(?P<size>\d+)/year/(?P<year>\d+)/$', catalog.bicycle_store_list_by_seller),
    url(r'^bicycle-store/view/seller/year/(?P<year>\d+)/$', catalog.bicycle_store_list_by_seller),
    url(r'^bicycle-store/view/seller/bycompany/(?P<brand>\d+)/$', catalog.bicycle_store_list_by_seller, {'all': True}),        
    url(r'^bicycle-store/view/seller/bycompany/(?P<brand>\d+)/html/$', catalog.bicycle_store_list_by_seller, {'all': True, 'html': True}),
#    url(r'^bicycle-store/now/view/$', catalog.bicycle_store_list),
    url(r'^bicycle-store/all/view/$', catalog.bicycle_store_list, {'all': True}),
    url(r'^bicycle-store/shop/all/view/$', catalog.bicycle_store_list, {'shop': True}, name="bicycles-in-all-shops"),
    url(r'^bicycle-store/view/$', catalog.bicycle_store_list),
    url(r'^bicycle-store/shop/(?P<id>\d+)/view/$', catalog.bicycle_store_list, {'shop': None, 'all': False}, name="bicycles-in-shop-by-id"),
    url(r'^bicycle-store/edit/(?P<id>\d+)/$', catalog.bicycle_store_edit),
    url(r'^bicycle-store/edit/$', catalog.bicycle_store_edit),
    url(r'^bicycle-store/delete/(?P<id>\d+)/$', catalog.bicycle_store_del),
    url(r'^bicycle-store/search/$', catalog.bicycle_store_search),
    url(r'^bicycle-store/search/result/$', catalog.bicycle_store_search_result),
    
    url(r'^bicycle/price/set/$', catalog.bicycle_price_set),

    url(r'^bicycle/sale/add/(?P<id>\d+)/$', catalog.bicycle_sale_add),
    url(r'^bicycle/sale/add/$', catalog.bicycle_sale_add),
    url(r'^bicycle/sale/id/(?P<id>\d+)/view/$', catalog.bicycle_sale_list),
#    url(r'^bicycle/sale/id/(?P<id>\d+)/view/$', catalog.bicycle_sale_list_by_brand),
    url(r'^bicycle/sale/view/$', catalog.bicycle_sale_list_by_brand),
    url(r'^bicycle/sale/year/(?P<year>\d+)/view/$', catalog.bicycle_sale_list_by_brand, name='bicycle-sale-by-year'),
    url(r'^bicycle/sale/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.bicycle_sale_list_by_brand, name='bicycle-sale-by-year-month'),
    url(r'^bicycle/sale/brand/(?P<id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.bicycle_sale_list_by_brand, name='bicycle_year_month_sale_by_brand'),    
    url(r'^bicycle/sale/brand/(?P<id>\d+)/year/(?P<year>\d+)/view/$', catalog.bicycle_sale_list_by_brand, name="bicycle_year_sale_by_brand"),
    url(r'^bicycle/sale/brand/(?P<id>\d+)/all/$', catalog.bicycle_sale_list_by_brand, {'all': True, },  name="bicycle_sale_all_by_brand" ),
    url(r'^bicycle/sale/edit/(?P<id>\d+)/$', catalog.bicycle_sale_edit, name='bicycle-sale-edit'),    
    url(r'^bicycle/sale/delete/(?P<id>\d+)/$', catalog.bicycle_sale_del),
    url(r'^bicycle/sale/report/month/$', catalog.bicycle_sale_report),
    url(r'^bicycle/sale/service/(?P<id>\d+)/$', catalog.bicycle_sale_service),
    url(r'^bicycle/sale/service/$', catalog.bicycle_sale_service),
    url(r'^bicycle/sale/(?P<id>\d+)/check/$', catalog.bicycle_sale_check),
    #url(r'^bicycle/sale/(?P<id>\d+)/check/print/$', catalog.bicycle_sale_check_print'),
    url(r'^bicycle/sale/(?P<id>\d+)/check/print/$', catalog.bicycle_sale_check, {'param': 'print'}),
    url(r'^bicycle/sale/(?P<id>\d+)/check/email/$', catalog.bicycle_sale_check, {'param': 'email'}),
    url(r'^bicycle/sale/(?P<id>\d+)/check/add/$', catalog.bicycle_sale_check_add),
    url(r'^bicycle/sale/report/brand/$', catalog.bicycle_sale_report_by_brand),
    url(r'^bicycle/sale/search/model/$', catalog.bicycle_sale_search_by_name),        
    url(r'^bicycle/sale/search/model/result/$', catalog.bsale_search_by_name_result),
    
    url(r'^bicycle/(?P<id>\d+)/tradein/$', catalog.bicycle_tradein_return, name='tradein-return'),
    
    # bicycle order by client
    url(r'^bicycle/order/view/$', catalog.bicycle_order_list),
    url(r'^bicycle/order/done/$', catalog.bicycle_order_done),
    url(r'^bicycle/order/add/$', catalog.bicycle_order_add),
    url(r'^bicycle/order/edit/(?P<id>\d+)/$', catalog.bicycle_order_edit),
    url(r'^bicycle/order/(?P<id>\d+)/delete/$', catalog.bicycle_order_del),
    url(r'^bike/lookup/$', catalog.bike_lookup),
    
    #storage bicycle
    url(r'^bicycle/storage/type/view/$', catalog.bicycle_storage_type_list),
    url(r'^bicycle/storage/type/add/$', catalog.bicycle_storage_type_add),
    url(r'^bicycle/storage/add/$', catalog.bicycle_storage_add),
    url(r'^bicycle/storage/(?P<id>\d+)/edit/$', catalog.bicycle_storage_edit),
    url(r'^bicycle/storage/(?P<id>\d+)/delete/$', catalog.bicycle_storage_delete),
    url(r'^bicycle/storage/view/$', catalog.bicycle_storage_list),
        
    # Dealer/Dealer Managers operation
    url(r'^dealer/payment/add/$', catalog.dealer_payment_add),
    url(r'^dealer/payment/view/$', catalog.dealer_payment_list),
    url(r'^dealer/payment/delete/(?P<id>\d+)/$', catalog.dealer_payment_del),

    url(r'^dealer/invoice/add/$', catalog.dealer_invoice_add),
    url(r'^dealer/invoice/view/$', catalog.dealer_invoice_list_month),
    url(r'^dealer/invoice/company/(?P<id>\d+)/view/$', catalog.dealer_invoice_list),
    url(r'^dealer/invoice/company/(?P<id>\d+)/year/(?P<year>\d+)/view/$', catalog.dealer_invoice_list),
    url(r'^dealer/invoice/company/(?P<id>\d+)/(?P<pay>paid|notpaid|sending)/$', catalog.dealer_invoice_list),    
    url(r'^dealer/invoice/year/(?P<year>\d+)/(?P<pay>paid|notpaid|sending)/$', catalog.dealer_invoice_list_month),
    url(r'^dealer/invoice/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.dealer_invoice_list_month),
    url(r'^dealer/invoice/year/(?P<year>\d+)/view/$', catalog.dealer_invoice_list_year),
    #url(r'^dealer/invoice/month/(?P<month>\d+)/view/$', catalog.dealer_invoice_list_month'),
    url(r'^dealer/invoice/view/all/$', catalog.dealer_invoice_list),
    url(r'^dealer/invoice/view/$', catalog.dealer_invoice_list),
    url(r'^dealer/invoice/search/$', catalog.dealer_invoice_search),
    url(r'^dealer/invoice/search/result/$', catalog.dealer_invoice_search_result),
    url(r'^dealer/invoice/edit/(?P<id>\d+)/$', catalog.dealer_invoice_edit, name='dealer_invoice_edit'),
    url(r'^dealer/invoice/delete/(?P<id>\d+)/$', catalog.dealer_invoice_del),
    url(r'^dealer/invoice/import/file/$', catalog.invoice_import),
    url(r'^dealer/invoice/import/$', catalog.invoice_import_form),
    url(r'^dealer/invoice/new/$', catalog.invoice_new_item),
    url(r'^dealer/invoice/new/edit/$', catalog.invoice_new_edit),
    url(r'^dealer/invoice/miss/$', catalog.invoice_miss_stuff),
    url(r'^dealer/invoice/recived/set/$', catalog.dealer_invoice_set),
    url(r'^dealer/invoice/(?P<id>\d+)/recived/set/$', catalog.dealer_invoice_set, name='dealear_invoice_set_status'),
    
    url(r'^dealer/add/$', catalog.dealer_add),
    url(r'^dealer/view/$', catalog.dealer_list),
    url(r'^dealer/edit/(?P<id>\d+)/$', catalog.dealer_edit),
    url(r'^dealer/delete/(?P<id>\d+)/$', catalog.dealer_del),

    url(r'^dealer-manager/add/$', catalog.dealer_manager_add),
    url(r'^dealer-manager/view/$', catalog.dealer_manager_list),
    url(r'^dealer-manager/edit/(?P<id>\d+)/$', catalog.dealer_manager_edit),    
    url(r'^dealer-manager/delete/(?P<id>\d+)/$', catalog.dealer_manager_del),

    #Invoice
    url(r'^invoice/add/$', catalog.invoicecomponent_add),
    url(r'^invoice/catalog/(?P<cid>\d+)/add/$', catalog.invoicecomponent_add),
   
    url(r'^invoice/manufacture/(?P<mid>\d+)/add/$', catalog.invoicecomponent_add),
    url(r'^invoice/manufacture/(?P<mid>\d+)/category/(?P<cid>\d+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-category-manufacture-by-year-all'}),
    url(r'^invoice/manufacture/(?P<mid>\d+)/lastsale/month/(?P<month>\d+)/$', catalog.invoicecomponent_sales_list, name="invoice-manufacturer-last-sale-by-month"),    
    url(r'^invoice/manufacture/(?P<mid>\d+)/lastsale/month/(?P<month>\d+)/all/$', catalog.invoicecomponent_sales_list, {'all': True}, name="invoice-manufacturer-last-sale-by-month-all"),
    url(r'^invoice/manufacture/(?P<mid>\d+)/category/(?P<cid>\d+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-category-manufacture-by-year-all'}),
    url(r'^invoice/manufacture/(?P<mid>\d+)/category/(?P<cid>\d+)/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-manufacture-category-attr-val-ids-by-year-all'}, name='invoice-category-manufacture-attr-val-ids'),
    url(r'^invoice/manufacture/(?P<mid>\d+)/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-manufacture-attr-val-ids-by-year-all'}, name='invoice-manufacture-attr-val-ids'),    
    url(r'^invoice/year/(?P<sel_year>\d+)/manufacture/(?P<mid>\d+)/category/(?P<cid>\d+)/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-manufacture-category-attr-val-ids-by-year-all'}, name='invoice-manufacture-category-attr-val-ids-by-year-all'),
    url(r'^invoice/year/(?P<sel_year>\d+)/manufacture/(?P<mid>\d+)/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-manufacture-attr-val-ids-by-year-all'}, name='invoice-manufacture-attr-val-ids-by-year-all'),    
#    url(r'^invoice/year/(?P<sel_year>\d+)/manufacture/(?P<mid>\d+)/category/(?P<cid>\d+)/view/all/$', catalog.invoicecomponent_list, {'all': True}),    
#    url(r'^invoice/year/(?P<sel_year>\d+)/manufacture/(?P<mid>\d+)/category/(?P<cid>\d+)/view/$', catalog.invoicecomponent_list, {'all': False}),
#    url(r'^invoice/manufacture/(?P<mid>\d+)/view/$', catalog.invoicecomponent_list_by_manufacturer'),
    url(r'^invoice/manufacture/(?P<mid>\d+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-manufacture-by-year-all'}, name="invoice-manufacture-id-list"),    
    url(r'^invoice/manufacture/(?P<mid>\d+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-manufacture-by-year-all'}, name="manufacture_id_list_all"),
    url(r'^invoice/year/(?P<sel_year>\d+)/manufacture/(?P<mid>\d+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-manufacture-by-year'}, name="invoice-manufacture-by-year"),
    url(r'^invoice/year/(?P<sel_year>\d+)/manufacture/(?P<mid>\d+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-manufacture-by-year-all'}, name="invoice-manufacture-by-year-all"),
    url(r'^invoice/year/(?P<sel_year>\d+)/category/(?P<cid>\d+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-category-by-year-all'}, name="invoice-category-by-year-all"),
    url(r'^invoice/year/(?P<sel_year>\d+)/category/(?P<cid>\d+)/view/$', catalog.invoicecomponent_list, {'all': False}, name="invoice-category-by-year"), # invoice sales filter by current YEAR
#    url(r'^invoice/manufacture/(?P<mid>\d+)/availability/view/$', catalog.invoicecomponent_list_by_manufacturer', {'availability': 1}),
    url(r'^invoice/manufacture/(?P<mid>\d+)/availability/view/html/$', catalog.invoicecomponent_manufacturer_html, name="sendmail_manufacture"),    
    url(r'^invoice/category/(?P<mid>\d+)/availability/view/html/$', catalog.invoicecomponent_category_html, name="sendmail_category"),
#    url(r'^invoice/manufacture/view/$', catalog.invoicecomponent_list_by_manufacturer'),
    url(r'^invoice/manufacture/view/$', catalog.invoicecomponent_list, {'focus': 1, 'mc_search': True}),
    url(r'^invoice/category/view/$', catalog.invoicecomponent_list, {'focus': 2, 'mc_search': True}),
    #url(r'^invoice/category/view/$', catalog.invoicecomponent_list_by_category'),
#    url(r'^invoice/category/(?P<cid>\d+)/view/$', catalog.invoicecomponent_list_by_category'),
    url(r'^invoice/attribute/val/(?P<attr_val_id>\d+)/view/$', catalog.invoicecomponent_list, {'all': False}, name="invoice-attribute-val-id-list"),
    url(r'^invoice/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/$', catalog.invoicecomponent_list, {'all': False}, name="invoice-attribute-values-ids-list"),
    url(r'^invoice/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/all/$', catalog.invoicecomponent_list, {'all': True}, name="invoice-attribute-values-ids-list"),
    
    url(r'^invoice/category/(?P<cid>\d+)/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-cat-attribute-values-ids-by-year-all'}, name="invoice-cat-attribute-value-id"),
    url(r'^invoice/category/(?P<cid>\d+)/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-cat-attribute-values-ids-by-year-all'}, name="invoice-cat-attribute-value-id-all"),

    url(r'^invoice/year/(?P<sel_year>\d+)/category/(?P<cid>\d+)/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-cat-attribute-values-ids-by-year-all'}, name="invoice-cat-attribute-values-ids-by-year-all"),
    url(r'^invoice/year/(?P<sel_year>\d+)/category/(?P<cid>\d+)/attribute/values/(?P<attr_val_ids>([\+]\d+)+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-cat-attribute-values-ids-by-year-all'}, name="invoice-cat-attribute-values-ids-by-year"),
    
    url(r'^invoice/attribute/(?P<attr_id>\d+)/view/$', catalog.invoicecomponent_list, {'all': False}, name="invoice-attribute-id-list"),
    url(r'^invoice/year/(?P<sel_year>\d+)/attribute/val/(?P<attr_val_id>\d+)/view/$', catalog.invoicecomponent_list, {'all': False}, name="invoice-attribute-val-id-list"),
    url(r'^invoice/year/(?P<sel_year>\d+)/attribute/(?P<attr_id>\d+)/view/$', catalog.invoicecomponent_list, {'all': False}, name="invoice-attribute-id-list"),

    url(r'^invoice/category/(?P<cid>\d+)/lastsale/month/(?P<month>\d+)/$', catalog.invoicecomponent_sales_list, name="invoice-category-last-sale-by-month"),    
    url(r'^invoice/category/(?P<cid>\d+)/lastsale/month/(?P<month>\d+)/all/$', catalog.invoicecomponent_sales_list, {'all': True}, name="invoice-category-last-sale-by-month-all"),
    url(r'^invoice/category/(?P<cid>\d+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-category-by-year-all'}, name="invoice-category-id-list"),
    url(r'^invoice/category/(?P<cid>\d+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': "invoice-category-by-year-all"}, name="invoice-category-id-list-all"),
    url(r'^invoice/category/(?P<cid>\d+)/manufacture/(?P<mid>\d+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-category-manufacture-by-year-all'}, name='invoice-category-manufacture-now'),
    url(r'^invoice/category/(?P<cid>\d+)/manufacture/(?P<mid>\d+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-category-manufacture-by-year-all' }, name='invoice-category-manufacture-now-all'),
    url(r'^invoice/year/(?P<sel_year>\d+)/category/(?P<cid>\d+)/manufacture/(?P<mid>\d+)/view/all/$', catalog.invoicecomponent_list, {'all': True, 'url_name': 'invoice-category-manufacture-by-year-all'}, name="invoice-category-manufacture-by-year-all"),
    url(r'^invoice/year/(?P<sel_year>\d+)/category/(?P<cid>\d+)/manufacture/(?P<mid>\d+)/view/$', catalog.invoicecomponent_list, {'all': False, 'url_name': 'invoice-category-manufacture-by-year'} , name="invoice-category-manufacture-by-year"),
    url(r'^invoice/list/(?P<limit>\d+)/view/$', catalog.invoicecomponent_list),
    url(r'^invoice/price/update/(?P<upday>\d+)/view/$', catalog.invoicecomponent_list),
    url(r'^invoice/list/view/$', catalog.invoicecomponent_list),
    url(r'^invoice/id/(?P<id>\d+)/view/$', catalog.invoice_id_list, name='invoice-view'),
    url(r'^invoice/id/(?P<id>\d+)/view/delete/$', catalog.invoice_id_list_delete, name='invoice-list-delete'),    
    url(r'^invoice/catalog/(?P<cid>\d+)/view/$', catalog.invoice_cat_id_list, name='invoice_catalog_view'), # наявний товар
    url(r'^invoice/delete/(?P<id>\d+)/$', catalog.invoicecomponent_del),
    url(r'^invoice/edit/(?P<id>\d+)/$', catalog.invoicecomponent_edit),
    url(r'^invoice/report/$', catalog.invoice_report),
    url(r'^invoice/all/report/$', catalog.invoicecomponent_sum),
    url(r'^invoice/search/$', catalog.invoice_search), # Form for search invoicecomponennt by NAME and ID
    #url(r'^invoice/search/result/$', catalog.invoice_search_result'),
    url(r'^invoice/search/result/$', catalog.invoicecomponent_list),
    url(r'^invoice/search/by/id/(?P<by_id>\d+)$', catalog.invoicecomponent_list, name="serch-invoicecomponennts-by-id"),
    url(r'^invoice/sale/list/$', catalog.invoicecomponent_list, {'isale': True}),
    url(r'^invoice/enddate/list/$', catalog.invoicecomponent_list, {'enddate': True}),
    url(r'^invoice/print/forum/$', catalog.invoicecomponent_print),
    url(r'^invoice/sales/by/year/$', catalog.invoice_sales_by_year), # AJAX for load group sales by Year

    # Component Type operation
    url(r'^category/add/$', catalog.category_add, name='category-add'),
    url(r'^category/view/$', catalog.category_list, name="category-list"),
    url(r'^category/edit/(?P<id>\d+)$', catalog.category_edit),
    url(r'^category/delete/(?P<id>\d+)$', catalog.category_del),    
    url(r'^category/get/list/$', catalog.category_get_list),
    url(r'^category/lookup/$', catalog.category_lookup),
    url(r'^category/plus/manufacture/lookup/$', catalog.category_manufacture_lookup, name="cat-man-lookup"),
    url(r'^category/attr/view/$', catalog.category_attr_list, {'show_attr': True}, name="category-attr-list"),
    url(r'^category/attr/values/view/$', catalog.category_attr_values_list, name="category-attr-value-list"),
    url(r'^category/attr/(?P<aid>\d+)/values/view/$', catalog.category_attr_values_list, name="category-id-attr-value-list"),

    url(r'^attr/filter/$', catalog.category_attr_list, name="attr-filter"),

    # Catalog operation
    url(r'^catalog/set/type/$', catalog.catalog_set_type),
    url(r'^catalog/add/$', catalog.catalog_add, name="catalog_add"),
    url(r'^catalog/discount/$', catalog.catalog_discount_list),
    url(r'^catalog/id/(?P<id>\d+)/view/$', catalog.catalog_list, name="catalog_id_view"),
    url(r'^catalog/view/$', catalog.catalog_list),
    url(r'^catalog/manufacture/(?P<id>\d+)/type/(?P<tid>\d+)/view/$', catalog.catalog_manu_type_list),
    url(r'^catalog/manufacture/(?P<id>\d+)/view/(\d+)$', catalog.catalog_part_list),
    url(r'^catalog/manufacture/(?P<id>\d+)/view/$', catalog.catalog_manufacture_list),
    url(r'^catalog/manufacture/view/$', catalog.catalog_manufacture_list),
    url(r'^catalog/type/(?P<id>\d+)/view/$', catalog.catalog_type_list),    
    url(r'^catalog/edit/$', catalog.catalog_set, name="cat_set_attr"),    
    url(r'^catalog/edit/(?P<id>\d+)$', catalog.catalog_edit, name='catalog_edit'),
    url(r'^catalog/sale/edit/$', catalog.catalog_sale_edit),
    url(r'^catalog/delete/(?P<id>\d+)$', catalog.catalog_delete),
    url(r'^catalog/search/id/$', catalog.catalog_search_id),
    url(r'^catalog/search/locality/$', catalog.catalog_search_locality),
    url(r'^catalog/search/result/$', catalog.catalog_search_result),
    url(r'^catalog/search/locality/$', catalog.catalog_search_result),
    url(r'^catalog/lookup/$', catalog.catalog_lookup, name="catalog-lookup"),
    url(r'^catalog/get/locality/$', catalog.catalog_get_locality),
    url(r'^catalog/search/$', catalog.catalog_search_by_ids), # POST AJAX
    url(r'^catalog/attribute/lookup/$', catalog.catalog_attr_lookup), # POST AJAX
    url(r'^catalog/add/attribute/$', catalog.catalog_add_attr), # POST AJAX
    url(r'^catalog/delete/attribute/$', catalog.catalog_del_attr), # POST AJAX

    # Client
    url(r'^client/(?P<id>\d+)$', catalog.client_data, name="client-data"),
    url(r'^clients/balance/$', catalog.client_balance_list),
    url(r'^client/add/$', catalog.client_add),
    url(r'^client/edit/(?P<id>\d+)$', catalog.client_edit, name="client-edit"),
    url(r'^client/view/$', catalog.client_list),
    url(r'^client/email/view/$', catalog.client_email_list),
    url(r'^client/delete/(?P<id>\d+)$', catalog.client_delete),
    url(r'^client/search/$', catalog.client_search),
    url(r'^client/search/result/$', catalog.client_search_result),
    url(r'^client/result/search/$', catalog.client_result),
    url(r'^client/(?P<id>\d+)/card/$', catalog.client_result, name="client-card-byid"),
    url(r'^client/lookup/$', catalog.client_lookup),
    url(r'^client/lookup/byid/$', catalog.client_lookup_by_id),
    url(r'^client/join/$', catalog.client_join),
    url(r'^client/(?P<id>\d+)/sendcard/', catalog.client_card_sendemail),
    
#delete    url(r'^client/result/$', catalog.search_client_id'),
    url(r'^client/invoice/view/$', catalog.client_invoice_view, name="clientinvoice-view"),
    url(r'^client/invoice/view/notpay/$', catalog.client_invoice_view, {'notpay': True}, name="clientinvoice-now-notpay"),
    url(r'^client/invoice/set/$', catalog.client_invoice_set),
#    url(r'^client/invoice/(?P<id>\d+)/edit/$', catalog.client_invoice_edit, name="client-invoice-edit"),
    url(r'^client/invoice/(?P<ciid>\d+)/edit/$', catalog.client_invoice, name="client-invoice-edit"),
    url(r'^client/invoice/add/$', catalog.client_invoice_add, name='client-invoice-add-by-catalog'),
    url(r'^client/(?P<cid>\d+)/invoice/add/$', catalog.client_invoice),
    url(r'^client/(?P<client_id>\d+)/invoice/sale/$', catalog.client_invoice_view, name="clientinvoice-sale-by-client"),
    url(r'^client/(?P<client_id>\d+)/invoice/sale/all/$', catalog.client_invoice_view, {'day': 'all', 'all': 'all', 'notpay': True}, name="clientinvoice-all-sales-by-client"),
# ajax table for client invoice    
    url(r'^client/(?P<client_id>\d+)/invoice/lookup/$', catalog.client_invoice_lookup),
    url(r'^client/invoice/catalog/(?P<cid>\d+)/add/$', catalog.client_invoice),
    url(r'^client/(?P<id>\d+)/invoice/catalog/(?P<cid>\d+)/add/$', catalog.client_invoice),
    url(r'^sale/(?P<cid>\d+)/$', catalog.client_invoice, {'id': 138}), #short link for sale in android device

    url(r'^client/invoice/catalog/(?P<id>\d+)/view/$', catalog.client_invoice_id, name="client-catalog-sale"),
    url(r'^client/invoice/catalog/(?P<id>\d+)/view/notpay/$', catalog.client_invoice_id, {'notpay': True}),
#    url(r'^client/invoice/add/$', catalog.client_invoice'),
    url(r'^client/invoice/delete/$', catalog.client_invoice_delete),
    url(r'^client/invoice/(?P<id>\d+)/delete/$', catalog.client_invoice_delete, name="client-invoice-delete"),    
    url(r'^client/invoice/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.client_invoice_view, {'day':"all"}, name="client-invoice-month"),
    url(r'^client/invoice/shop/(?P<shop>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.client_invoice_view, {'day':"all"}, name="client-invoice-month-by-shop"),
    url(r'^client/invoice/shop/(?P<shop>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/view/notpay/$', catalog.client_invoice_view, {'notpay': True}, name="client-invoice-month-by-shop-notpay"),
    url(r'^client/invoice/shop/(?P<shop>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/notpay/$', catalog.client_invoice_view, {'notpay': True}, name="client-invoice-day-by-shop-notpay"),
    url(r'^client/invoice/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', catalog.client_invoice_view, {'shop': 0}, name="client-invoice-day"),
    url(r'^client/invoice/shop/(?P<shop>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', catalog.client_invoice_view, name="client-invoice-day-by-shop"),
    url(r'^client/invoice/year/(?P<year>\d+)/month/(?P<month>\d+)/view/notpay/$', catalog.client_invoice_view, {'day':"all", 'notpay': True}, name="client-invoice-month-notpay"),
    url(r'^client/invoice/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/notpay/$', catalog.client_invoice_view, {'notpay': True}, name="client-invoice-day-not-pay"),
    url(r'^client/invoice/report/$', catalog.client_invoice_report),
    url(r'^client/invoice/check/$', catalog.client_invoice_check, {'param': 'print'}),
    url(r'^client/invoice/check/email/$', catalog.client_invoice_check, {'param': 'email'}),
    url(r'^client/invoice/get/boxes/$', catalog.client_invoice_get_boxes), # AJAX request
    url(r'^client/invoice/add/boxes/$', catalog.client_invoice_add_boxes), # AJAX request
    url(r'^client/workshop/check/$', catalog.client_workshop_check, {'param': 'print'}),
    url(r'^client/workshop/check/email/$', catalog.client_workshop_check, {'param': 'email'}),
    
    url(r'^client/invoice/return/(?P<id>\d+)/add/$', catalog.client_invioce_return_add),
    url(r'^client/invoice/return/list/$', catalog.client_invioce_return_view, {'limit': 100}),
    url(r'^client/invoice/return/list/(?P<limit>\d+)/limit/$', catalog.client_invioce_return_view),

    url(r'^clientdebts/add/(?P<id>\d+)$', catalog.clientdebts_add),
    url(r'^clientdebts/view/$', catalog.clientdebts_list),
    url(r'^clientdebts/edit/(?P<id>\d+)$', catalog.clientdebts_edit),
    url(r'^clientdebts/delete/(?P<id>\d+)$', catalog.clientdebts_delete),
    url(r'^clientdebts/(?P<client_id>\d+)/delete/all/$', catalog.clientdebts_delete_all),

    url(r'^clientcredits/add/(?P<id>\d+)$', catalog.clientcredits_add),
    url(r'^clientcredits/view/$', catalog.clientcredits_list),
    url(r'^clientcredits/edit/(?P<id>\d+)$', catalog.clientcredits_edit),    
    url(r'^clientcredits/delete/(?P<id>\d+)$', catalog.clientcredits_delete),
    url(r'^clientcredits/(?P<client_id>\d+)/delete/all/$', catalog.clientcredits_delete_all),
    url(r'^clientcredits/set/$', catalog.clientcredits_set),

    url(r'^client/order/add/$', catalog.client_order_add),
    url(r'^client/order/view/$', catalog.client_order_list),
    url(r'^client/order/delete/(?P<id>\d+)$', catalog.client_order_delete),
    url(r'^client/order/edit/(?P<id>\d+)/$', catalog.client_order_edit),

    url(r'^payform/dealer/$', catalog.dealer_payform),
    url(r'^payform/workshop/$', catalog.workshop_payform),
    url(r'^payform/$', catalog.payform),
    url(r'^catalog/saleform/$', catalog.catalog_saleform),    
    url(r'^client/payform/$', catalog.client_payform),
    url(r'^client/workshop/payform/$', catalog.client_ws_payform),
    
    # Example:
    # url(r'^catalog/', include('catalog.foo.urls')),
#    url(r'^sendmail/$', catalog.sendemail'),
    url(r'^asearch/$', catalog.ajax_search),

#    url(r'^media/(?P<path>.*)', 'django.views.static.serve', {'document_root': os.path.join(dirname, 'media')}),
     # static files
    #{'document_root': 'D:/develop/catalog/media'}),
    #{'document_root': os.path.join(dirname, 'media')}),
    
#    url(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    url(r'^accounts/login/$',  catalog.login),
    url(r'^accounts/logout/$', catalog.logout),
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
#    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
#    url(r'^admin/(.*)', admin.site.root, name='django-admin'),    
    # MAIN PAGE
    url(r'^$', catalog.main_page),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/(.*)', admin.site.root),
   
#)
#urlpatterns += patterns('',
    # WorkShop 
    #operation by GROUP
    url(r'^workgroup/add/$', catalog.workgroup_add),
    url(r'^workgroup/edit/(?P<id>\d+)$', catalog.workgroup_edit),
    url(r'^workgroup/view/$', catalog.workgroup_list, name="workgrouplist"),
    url(r'^workgroup/delete/(?P<id>\d+)$', catalog.workgroup_delete),

    url(r'^worktype/add/$', catalog.worktype_add),
    url(r'^worktype/edit/(?P<id>\d+)$', catalog.worktype_edit),
    url(r'^worktype/view/group/(?P<id>\d+)$', catalog.worktype_list),        
    url(r'^worktype/view/$', catalog.worktype_list, name="worktypelist"),
    url(r'^worktype/delete/(?P<id>\d+)$', catalog.worktype_delete),
    url(r'^worktype/join/(?P<id1>\d+)/(?P<id2>\d+)/$', catalog.worktype_join),
    url(r'^worktype/join/$', catalog.worktype_join),
    url(r'^worktype/price/$', catalog.worktype_ajax),    
    url(r'^worktype/lookup/$', catalog.worktype_lookup),
    url(r'^work/depence/add/$', catalog.worktype_depence_add, name="add_work_depence"),
    url(r'^work/depence/delete/$', catalog.worktype_depence_delete, name="delete_work_depence"), 
    url(r'^work/depence/components/add/$', catalog.worktype_depence_component_add, name="add_work_component_depence"),
    url(r'^work/depence/components/delete/$', catalog.worktype_depence_component_delete, name="delete_work_components_depence"),

    url(r'^phone/status/list/$', catalog.PhoneStatusListView.as_view(), name="genview_phonestatus_list"),
    url(r'^phonestatus/view/$', catalog.phonestatus_list),
    url(r'^phonestatus/add/$', catalog.phonestatus_add, name="phonestatus_add"),
    url(r'^phonestatus/edit/(?P<id>\d+)$', catalog.phonestatus_edit, name="phonestatus_edit"),
    url(r'^phonestatus/delete/(?P<id>\d+)$', catalog.phonestatus_delete, name="phonestatus_delete"),
    url(r'^workstatus/add/$', catalog.workstatus_add),
    url(r'^workstatus/view/$', catalog.workstatus_list),
    url(r'^workstatus/edit/(?P<id>\d+)$', catalog.workstatus_edit),
    url(r'^workstatus/delete/(?P<id>\d+)$', catalog.workstatus_delete),

    url(r'^workticket/add/$', catalog.workticket_add, name="workshop-ticket-create"),
    url(r'^workticket/add/client/(?P<id>\d+)/$', catalog.workticket_add, name="workticket-add-by-client"),    
    url(r'^workticket/view/$', catalog.workticket_list, name="workticket-list"),
    url(r'^workticket/edit/$', catalog.workticket_edit),
    url(r'^workticket/edit/(?P<id>\d+)/$', catalog.workticket_edit, name="workticket_edit"),    
    url(r'^workticket/delete/(?P<id>\d+)/$', catalog.workticket_delete),
    url(r'^workticket/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.workticket_list, name='workticket-list-by-month'),
    url(r'^workticket/year/(?P<year>\d+)/month/(?P<month>\d+)/shop/(?P<shop>\d+)/view/$', catalog.workticket_list, name='workticket-list-by-month-by-shop'),
    url(r'^workticket/status/(?P<status>\d+)/view/$', catalog.workticket_list, name='workticket-list-by-status'),
    url(r'^workticket/status/(?P<status>\d+)/shop/(?P<shop>\d+)/view/$', catalog.workticket_list, name='workticket-list-by-status-by-shop'),
    url(r'^workticket/shop/(?P<shop>\d+)/view/$', catalog.workticket_list, name="workticket-byshop-cur-month"),
    url(r'^workticket/all/view/$', catalog.workticket_list, {'all': True}),

    url(r'^workshop/price/list/print/$', catalog.workshop_pricelist, {'pprint': True}),
    url(r'^workshop/price/list/$', catalog.workshop_pricelist, {'pprint': False}),
    url(r'^workshop/add/(?P<id>\d+)/$', catalog.workshop_add),
    url(r'^workshop/add/client/(?P<id_client>\d+)/$', catalog.workshop_add, name='workshop-add-to-client'),
    url(r'^workshop/add/$', catalog.workshop_add),
    url(r'^workshop/add/formset/$', catalog.workshop_add_formset),
    url(r'^workshop/edit/(?P<id>\d+)/$', catalog.workshop_edit),
    url(r'^workshop/view/$', catalog.workshop_list, name='workshop_list'),
    url(r'^workshop/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', catalog.workshop_list, name='workshop_day'),
    url(r'^workshop/shop/(?P<shop>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', catalog.workshop_list, name='workshop-day-byshop'),
    url(r'^workshop/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.workshop_list, {'day': "all"}),
    url(r'^workshop/year/(?P<year>\d+)/view/$', catalog.workshop_list),
    url(r'^workshop/delete/(?P<id>\d+)/$', catalog.workshop_delete),    
    url(r'^workshop/delete/$', catalog.workshop_delete),
    url(r'^workshop/set/$', catalog.workshop_set), # Ajax POST
    
    url(r'^report/worktype/(?P<id>\d+)/$', catalog.worktype_report, {'limit':"all"}, name='repot_by_work'),    
    url(r'^report/worktype/(?P<id>\d+)/year/(?P<year>\d+)/$', catalog.worktype_report, {'day':"all"}, name='repot_by_work_year'),
    url(r'^report/worktype/(?P<id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/$', catalog.worktype_report, name='repot_by_work_month'),

    url(r'^casa/prro/view/$', catalog.casa_prro_checkout),
    url(r'^casa/prro/check/(?P<chk_uid>[\w-]+)/view/$', catalog.casa_prro_check_view, name='prro_check_text_view'),
    url(r'^casa/prro/check/(?P<chk_uid>[\w-]+)/view/pdf/$', catalog.casa_prro_check_view, {'type':'pdf'}, name='prro_check_pdf_view'),
    url(r'^casa/prro/check/(?P<chk_uid>[\w-]+)/view/html/$', catalog.casa_prro_check_view, {'type':'html'}, name='prro_check_html_view'),
    url(r'^casa/prro/(?P<sum>\d+)/in/$', catalog.casa_prro_in_out, {'inout':"+"}, name = 'prro_in'),
    url(r'^casa/prro/(?P<sum>\d+)/out/$', catalog.casa_prro_in_out, {'inout':"-"}, name = 'prro_out'),
    url(r'^casa/prro/xreport/$', catalog.casa_prro_xreport),
    url(r'^casa/prro/create/$', catalog.casa_prro_create),
    url(r'^casa/prro/zreport/$', catalog.casa_prro_zreport, name='prro-zreport'),
    url(r'^casa/(?P<id>\d+)/view/$', catalog.casa_checkout),
    url(r'^casa/(?P<id>\d+)/status/$', catalog.casa_getstatus),
    url(r'^casa/(?P<id>\d+)/zreport/$', catalog.casa_z_report, name='rro-zreport'),
    url(r'^casa/(?P<id>\d+)/cmd/$', catalog.casa_command),
    url(r'^casa/rro/xreport/$', catalog.casa_rro_xreport, name='rro_xreport'),

#)
#urlpatterns += patterns('',
                        
    url(r'^manyforms/(?P<author_id>\d+)$', catalog.manage_works),
    url(r'^manyforms/test/$', catalog.formset_test),
    url(r'^workshop/done/client/(?P<id>\d+)/$', catalog.formset_test),
    url(r'^manyforms/test1/$', catalog.inline_formset_test),

    #ajax
#    url(r'^insertstory/$', catalog.insertstory),
    url(r'^ajax/test/$', catalog.ajax_test),

    url(r'^preorder/add/$', catalog.preorder_add),
    url(r'^preorder/view/$', catalog.preorder_list),
    url(r'^preorder/edit/(?P<id>\d+)/$', catalog.preorder_edit),
    url(r'^preorder/delete/(?P<id>\d+)/$', catalog.preorder_delete),         

    # my cost
    url(r'^cost/type/add/$', catalog.costtype_add),
    url(r'^cost/type/view/$', catalog.costtype_list),
    url(r'^cost/type/delete/(?P<id>\d+)$', catalog.costtype_delete),    

    url(r'^cost/add/(?P<id>\d+)$', catalog.cost_add),
    url(r'^cost/add/$', catalog.cost_add),
    url(r'^cost/view/$', catalog.cost_list, name='cost-list'),
    url(r'^cost/view/year/(?P<year>\d+)/$', catalog.cost_list, name='cost-list-year'),
    url(r'^cost/view/year/(?P<year>\d+)/month/(?P<month>\d+)/$', catalog.cost_list, name='cost-list-year-month'),
    url(r'^cost/delete/(?P<id>\d+)/$', catalog.cost_delete),    
    url(r'^cost/edit/(?P<id>\d+)/$', catalog.cost_edit),

    url(r'^report/sales/user/report/$', catalog.user_invoice_report, {'day':"all"}),
    url(r'^report/sales/user/(?P<user_id>\d+)/report/$', catalog.user_invoice_report, {'day':"all"}, name='report_sales_by_user_currentmonth'),
    url(r'^report/sales/user/year/(?P<year>\d+)/month/(?P<month>\d+)/report/$', catalog.user_invoice_report, {'day':"all"}),
    url(r'^report/sales/user/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/report/$', catalog.user_invoice_report),
    url(r'^report/sales/user/(?P<user_id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/report/$', catalog.user_invoice_report, {'day':"all"}, name='report_sales_by_user_month'),
    url(r'^report/sales/user/(?P<user_id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/report/$', catalog.user_invoice_report, name='report_sales_by_user_day'),

    url(r'^report/workshop/byuser/$', catalog.user_workshop_report, {'day':"all"}),
    url(r'^report/workshop/(?P<user_id>\d+)/byuser/$', catalog.user_workshop_report, {'day':"all"}, name='report_workshop_by_user_currentmonth'),
    url(r'^report/workshop/byuser/year/(?P<year>\d+)/month/(?P<month>\d+)/$', catalog.user_workshop_report, {'day':"all"}, name='report_user_workshop_year_month'),
    url(r'^report/workshop/byuser/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/$', catalog.user_workshop_report),
    url(r'^report/workshop/(?P<user_id>\d+)/byuser/year/(?P<year>\d+)/month/(?P<month>\d+)/$', catalog.user_workshop_report, {'day':"all"}, name='report_workshop_by_user_month'),
    url(r'^report/workshop/(?P<user_id>\d+)/byuser/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/$', catalog.user_workshop_report, name='report_workshop_by_user_day'),
    url(r'^report/salary/all_user/$', catalog.all_user_salary_report, {'day':"all"}, name='user_salary_report'),
    url(r'^report/salary/all_user/year/(?P<year>\d+)/month/(?P<month>\d+)/$', catalog.all_user_salary_report, {'day':"all"}, name='user_salary_report_by_year_month'),
    url(r'^salary/add/$', catalog.salary_add, name='salary-add'),

    url(r'^shop/price/lastadded/(?P<id>\d+)/view/$', catalog.shop_price_lastadd, name="shop-price-last-added"),    
    url(r'^shop/price/lastadded/(?P<id>\d+)/print/$', catalog.shop_price_lastadd, {'pprint': True}),
    url(r'^shop/price/company/(?P<mid>\d+)/view/$', catalog.shop_price), #work
    url(r'^shop/price/company/(?P<mid>\d+)/print/$', catalog.shop_price, {'pprint': True}), #work
    url(r'^shop/price/bysearch_id/(?P<id>.*)/view/$', catalog.shop_price_bysearch_id),
    url(r'^shop/price/bysearch_id/(?P<id>.*)/print/$', catalog.shop_price_bysearch_id_print, name="shop-price-by-search-id-print"),
    url(r'^shop/price/bysearch_name/(?P<id>.*)/view/$', catalog.shop_price_bysearch_name),
    url(r'^shop/price/bysearch_name/(?P<id>.*)/print/$', catalog.shop_price_bysearch_name, {'pprint': True}),
    url(r'^shop/price/print/(?P<id>\d+)/add/$', catalog.shop_price_print_add),
#    url(r'^shop/price/print/add/$', catalog.ajax_price_print'),
    url(r'^shop/price/print/add/$', catalog.shop_price_print_add, name="shop-price-print-add"),
    url(r'^shop/price/print/add/invoice/$', catalog.shop_price_print_add_invoice),
    url(r'^shop/price/print/view/$', catalog.shop_price_print_list, {'pprint': True}, name='label_print_all'),
    url(r'^shop/price/print/view/(?P<user_id>\d+)/byuser/$', catalog.shop_price_print_list, {'pprint': True}, name='label_print_by_user'),
    url(r'^shop/price/qr/print/view/$', catalog.shop_price_qrcode_print_view),
    url(r'^shop/price/print/empty/$', catalog.shop_price_print_delete_all),    
    url(r'^shop/price/print/duplicate/delete/$', catalog.remove_duplicated_ShopPrice_records, name='shopprice_duplicate_delete'),
    url(r'^shop/price/print/zero/delete/$', catalog.remove_zero_ShopPrice_records, name='shopprice_zero_delete'),
    url(r'^shop/price/print/list/$', catalog.shop_price_print_list, name='shop-price-print-list'),
    url(r'^shop/price/print/list/add/$', catalog.shop_price_print_list_add, name='shop-price-print-list-add'),
    url(r'^shop/price/print/list/(?P<user_id>\d+)/byuser/$', catalog.shop_price_print_list, name='label_list_by_user'),
    url(r'^shop/price/print/delete/$', catalog.shop_price_print_delete),
    url(r'^shop/price/print/delete/(?P<user_id>\d+)/byuser/$', catalog.shop_price_print_delete, name='label_delete_by_user'),
    url(r'^shop/price/print/(?P<id>\d+)/delete/$', catalog.shop_price_print_delete),
    url(r'^catalog/price/import/file/$', catalog.price_import),
    url(r'^catalog/price/import/$', catalog.price_import_form),
    #url(r'^catalog/content/import/form/$', catalog.catalog_import_form'),
    url(r'^catalog/import/$',catalog.catalog_import_form),
    url(r'^catalog/content/import/$', catalog.catalog_import_content),

    url(r'^photo/url/bicycle/add/$', catalog.bike_photo_url_add),
    url(r'^photo/url/add/$', catalog.photo_url_add),
    url(r'^photo/url/get/$', catalog.photo_url_get),
    url(r'^photo/id/(?P<id>\d+)/get/$', catalog.photo_url_get, name='photo_get'),
    url(r'^photo/id/(?P<id>\d+)/delete/$', catalog.photo_url_delete),
    url(r'^photo/field/delete/$', catalog.photo_del_field, name="photo_del_field"),
    url(r'^catalog/photo/delete/$', catalog.photo_url_delete),
    url(r'^catalog/photo/list/(?P<show>\d+)/page/(?P<page>\d+)/limit/(?P<limit>\d+)/$', catalog.photo_list),
    url(r'^catalog/photo/list/(?P<show>\d+)/page/(?P<page>\d+)/limit/$', catalog.photo_list),
    url(r'^catalog/photo/list/(?P<show>\d+)/$', catalog.photo_list),
    url(r'^catalog/(?P<cat_id>\d+)/photo/list/(?P<show>\d+)/$', catalog.photo_list),
    url(r'^catalog/photo/list/$', catalog.photo_list),
    url(r'^catalog/same/list/$', catalog.catalog_same_list),
        
    url(r'^youtube/list/$', catalog.youtube_list, name='youtube_list'),    
    url(r'^youtube/(?P<id>\d+)/delete/$', catalog.youtube_delete),
    url(r'^youtube/add/$', catalog.youtube_url_add, name='youtube_add'),
    url(r'^youtube/url/get/$', catalog.youtube_url_get),
    url(r'^youtube/set/$', catalog.youtube_set),
    
    url(r'^workday/user/all/report/$', catalog.workday_list),
    url(r'^workday/alluser/report/$', catalog.workday_ajax),
    url(r'^workday/add/$', catalog.workday_add),
    url(r'^workday/(?P<id>\d+)/delete/$', catalog.workday_delete),
    
    url(r'^clientmessage/add/$', catalog.clientmessage_add),
    url(r'^clientmessage/set/$', catalog.clientmessage_set),
    url(r'^clientmessage/list/$', catalog.clientmessage_list),
    url(r'^clientmessage/(?P<id>\d+)/delete/$', catalog.clientmessage_delete),

    url(r'^client_history/cred/$', catalog.client_history_cred),
    url(r'^client_history/debt/$', catalog.client_history_debt),
    url(r'^client_history/invoice/$', catalog.client_history_invoice),
    
    url(r'^cashtype/view/$', catalog.cashtype_list),
    url(r'^cashtype/list/$', catalog.cashtype_list),
    url(r'^cashtype/add/$', catalog.cashtype_add),
    url(r'^cashtype/edit/(?P<id>\d+)$', catalog.cashtype_edit),
    url(r'^cashtype/delete/(?P<id>\d+)$', catalog.cashtype_del),
    
    url(r'^rent/add/$', catalog.rent_add),
    url(r'^rent/edit/(?P<id>\d+)/$', catalog.rent_edit),
    url(r'^rent/delete/(?P<id>\d+)/$', catalog.rent_delete),    
    url(r'^rent/view/$', catalog.rent_list, name="rent-list"),

    # Curency operation
    url(r'^curency/add/$', catalog.curency_add),
    url(r'^curency/view/$', catalog.curency_list),
    url(r'^curency/delete/(?P<id>\d+)/$', catalog.curency_del),
    
    url(r'^exchange/add/$', catalog.exchange_add),
    url(r'^exchange/view/$', catalog.exchange_list),
    url(r'^exchange/edit/(?P<id>\d+)/$', catalog.exchange_edit),
    url(r'^exchange/delete/(?P<id>\d+)/$', catalog.exchange_del),    

    url(r'^boxname/search/', catalog.boxname_search, name='boxname-search'),
    
    url(r'^storage/box/add/$', catalog.storage_box_add, name='storage-box-add'), #new function
    url(r'^storagebox/edit/$', catalog.storagebox_edit, name='storagebox-edit'), #new AJAX function    
    url(r'^storage/box/(?P<id>\d+)/edit/$', catalog.storage_box_edit, name='storage-box-edit'), #new function
    url(r'^storage/boxes/$', catalog.storage_boxes_list, name='storage-boxes-list'), #new function
    url(r'^storage/shop/(?P<id>\d+)/boxes/$', catalog.storage_boxes_list, name='storage-boxes-list-by-shop'), #new function
    url(r'^storage/box/(?P<id>\d+)/list/$', catalog.storage_box_list, name='storage-box-itemlist'), #new function
    url(r'^storage/box/name/(?P<boxname>[\w,.]+)/list/$', catalog.storage_boxes_list, name='storage-box-by-name'), #new function
    url(r'^storage/boxes/list/$', catalog.storage_boxes, name="storage_box-list"),
    url(r'^storage/boxes/print/$', catalog.storage_box_list_old, {'pprint': True}), # old function
    url(r'^storage/box/(?P<boxname>[\w,.]+)/view/$', catalog.storage_box_list_old), # old function
    url(r'^storage/box/delete/$', catalog.storage_box_delete), # new function
    url(r'^storage/box/delete/all/$', catalog.storage_box_delete_all, {'all': True}),
    url(r'^storage/box/delete/all/empty/$', catalog.storage_box_delete_all),
    url(r'^storage/box/rename/$', catalog.storage_box_rename), # old function
    url(r'^catalog/(?P<id>\d+)/storage/box/list/$', catalog.storage_box_list_by_catalog, name='storage-box-by-catalog'),

    url(r'^shop/sale/day/add/$', catalog.shopdailysales_add, name='shop-sale-day-add'),
    url(r'^shop/(?P<id>\d+)/sale/day/add/$', catalog.shopdailysales_add, name='shop-id-sale-day-add-by-id'),
    url(r'^shop/sale/month/(?P<month>\d+)/view/$', catalog.shopmonthlysales_view),    
    url(r'^shop/sale/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.shopmonthlysales_view),    
    url(r'^shop/sale/month/view/$', catalog.shopmonthlysales_view),
    url(r'^shop/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', catalog.shopdailysales_view, name="shop-daily-sales"), # Day CASA     
    url(r'^shop/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/shop/(?P<shop>\d+)/view/$', catalog.shopdailysales_view, name="shop-daily-sales-by-shop"), # day CASA by SHOP
    url(r'^shop/sale/day/edit/(?P<id>\d+)/$', catalog.shopdailysales_edit),
    url(r'^shop/sale/view/year/(?P<year>\d+)/month/(?P<month>\d+)/$', catalog.shopdailysales_list),    
    url(r'^shop/sale/view/month/(?P<month>\d+)/$', catalog.shopdailysales_list, name="shop_dailysales_monthly"),
    url(r'^shop/(?P<shop_id>\d+)/sale/view/month/(?P<month>\d+)/$', catalog.shopdailysales_list, name="shop_id_dailysales_monthly"),
    url(r'^shop/(?P<shop_id>\d+)/sale/view/month/(?P<month>\d+)/year/(?P<year>\d+)/$', catalog.shopdailysales_list, name="shop_id_dailysales_monthly"),
    url(r'^shop/sale/view/$', catalog.shopdailysales_list, name="shop_dailysales_monthly_cur"),
    url(r'^shop/sale/day/(?P<id>\d+)/delete/$', catalog.shopdailysales_delete),

    url(r'^inventory/(?P<id>\d+)/edit/$', catalog.inventory_edit, name='inventory-edit'),
    url(r'^inventory/list/$', catalog.inventory_list, name='inventory-list'),
    url(r'^inventory/shop/(?P<shop_id>\d+)/list/$', catalog.inventory_list, name='inventory-list'),
    url(r'^inventory/mistake/list/$', catalog.inventory_mistake),
    url(r'^inventory/mistake/not/all/list/$', catalog.inventory_mistake_not_all),
    url(r'^inventory/autocheck/list/$', catalog.inventory_autocheck),
    url(r'^inventory/fix/list/$', catalog.inventory_fix),
    url(r'^inventory/fix/cat/(?P<cat_id>\d+)/list/$', catalog.inventory_fix_catalog, name="fix_inventory"),
    url(r'^inventory/autofix/$', catalog.inventory_fix_catalog1),
    url(r'^inventory/type/(?P<type_id>\d+)/autofix/$', catalog.inventory_fix_catalog1),
    url(r'^inventory/type/(?P<type_id>\d+)/view/$', catalog.inventory_catalog_type, name="inventory-by-type"),
    url(r'^inventory/manufacturer/(?P<m_id>\d+)/view/$', catalog.inventory_catalog_manufacturer, name="inventory-by-manufacturer"),
#    url(r'^inventory/fix/cat/(?P<cat_id>\d+)/inv/(?P<inv_id>\d+)/list/$', catalog.inventory_fix_catalog', name="fix_inventory"),
    url(r'^inventory/autocheck/$', catalog.inventory_autocheck, {'update': True}),
    url(r'^inventory/year/(?P<year>\d+)/list/$', catalog.inventory_list),
    url(r'^inventory/shop/(?P<shop_id>\d+)/year/(?P<year>\d+)/list/$', catalog.inventory_list),
    url(r'^inventory/year/(?P<year>\d+)/month/(?P<month>\d+)/list/$', catalog.inventory_list),
    url(r'^inventory/shop/(?P<shop_id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/list/$', catalog.inventory_list),
    url(r'^inventory/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/list/$', catalog.inventory_list),
    url(r'^inventory/shop/(?P<shop_id>\d+)/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/list/$', catalog.inventory_list, name='inventory-by-shop-year-month-day'),
    url(r'^inventory/catalog/(?P<cat_id>\d+)/view/$', catalog.inventory_by_catalog_id, name='inventory-by-catalog-id'),
    url(r'^inventory/add/$', catalog.inventory_add, name="inventory-add"),
    url(r'^inventory/get/$', catalog.inventory_get),
    url(r'^inventory/count/get/$', catalog.inventory_get_count),
    url(r'^inventory/get/listid/$', catalog.inventory_get_listid),
    url(r'^inventory/set/$', catalog.inventory_set),
#    url(r'^inventory/delete/(?P<id>\d+)/$', catalog.inventory_delete'),
    url(r'^inventory/delete/$', catalog.inventory_delete),
    url(r'^inventory/search/$', catalog.inventory_search, name="inventory-search-by-catalog-or-type"),
    url(r'^catalog/join/$', catalog.catalog_join),
    url(r'^catalog/join/(?P<id1>\d+)/(?P<id2>\d+)/$', catalog.catalog_join),
    
    url(r'^check/list/$', catalog.check_list,{'all':True}),
    url(r'^check/list/(?P<client>\d+)/client/$', catalog.check_list,{'all':True}),
    url(r'^check/list/now/$', catalog.check_list,{'all':False}),
    url(r'^check/year/(?P<year>\d+)/view/$', catalog.check_list,{'all':True}),
    url(r'^check/year/(?P<year>\d+)/month/(?P<month>\d+)/view/$', catalog.check_list,{'all':True}),
    url(r'^check/year/(?P<year>\d+)/month/(?P<month>\d+)/day/(?P<day>\d+)/view/$', catalog.check_list,{'all':False}),
    url(r'^check/(?P<num>\d+)/print/$', catalog.check_print),
    url(r'^check/add/$', catalog.check_add),
    url(r'^check/shop/add/$', catalog.shop_sale_check_add),
    url(r'^check/workshop/add/$', catalog.workshop_sale_check_add),
    url(r'^check/delete/(?P<id>\d+)/$', catalog.check_delete),
    url(r'^check/pay/(?P<id>\d+)/delete/$', catalog.check_pay_delete, name='check_pay_delete'),
    url(r'^workshop/playsound/$', catalog.send_workshop_sound),
    url(r'^discount/add/$', catalog.discount_add),
    url(r'^discount/(?P<id>\d+)/edit/$', catalog.discount_edit, name="discount_edit"),
    url(r'^discount/list/$', catalog.discount_list),
    url(r'^discount/year/(?P<year>\d+)/list/$', catalog.discount_list, name="discount_year_list"),
    url(r'^discount/delete/$', catalog.discount_delete),
    url(r'^discount/lookup/$', catalog.discount_lookup),
    
    url(r'^qrscanner/$', catalog.qrscanner),
    url(r'^qrscanner2/$', catalog.qrscanner2),
    url(r'^catalog/file/photo/list/$', catalog.catalog_upload_photos),
    
    # не потрібний функціонал
    url(r'^s/(?P<cid>\d+)/$', catalog.client_invoice_shorturl), #short link for sale in android device
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


#) 

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