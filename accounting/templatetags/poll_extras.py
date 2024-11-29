# -*- coding: utf-8 -*-
from django import template
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import connection
from django.conf import settings
import json
import requests
import re
import datetime
from django.http import HttpRequest
from catalog.accounting.models import Shop
import calendar


register = template.Library()


@register.filter(name='mul_round')
def mul(value, arg):
    return round(float(value) * float(arg), 2)


@register.filter(name='mul')
def mul(value, arg):
    return (value or 0) * (arg or 0)


@register.filter
def div(value, arg):
    return value / arg


@register.filter
def sub(value, arg):
    res = 0
    try:
        res = value - arg
    except:
        pass
    return res 


@register.filter
def sub_int(value, arg):
    return int(value) - int(arg)


@register.filter
def sale_by_percent(value, arg):
    res = (value / 100) * (100 - arg)    
    return res


ALLOWABLE_VALUES = ("LOGO_TOP", "CLIENT_UNKNOWN", "CLIENT_SALE_1", "CLIENT_SALE_3", "CLIENT_SALE_5", "CLIENT_SALE_7", "CLIENT_SALE_10")
# settings value
@register.simple_tag
def settings_value(name):
    if name in ALLOWABLE_VALUES:
        return getattr(settings, name, "")
    return ''

@register.inclusion_tag('orm_debug.html')
def orm_debug():
    try:
        from pygments import highlight
        from pygments.lexers import SqlLexer
        from pygments.formatters import HtmlFormatter
        pygments_installed = True
    except ImportError:
        pygments_installed = False

    queries = connection.queries
    query_time = 0
    query_count = 0
    for query in queries:
        query_time += float(query['time'])
        query_count += int(1)
        query['sql'] = re.sub(r'(FROM|WHERE)', '\n\\1', query['sql'])
        query['sql'] = re.sub(r'((?:[^,]+,){3})', '\\1\n    ', query['sql'])
        if pygments_installed:
            formatter = HtmlFormatter()
            query['sql'] = highlight(query['sql'], SqlLexer(), formatter)
            pygments_css = formatter.get_style_defs()
        else:
            pygments_css = ''
    return {
        'pygments_css': pygments_css,
        'pygments_installed': pygments_installed,
        'query_time': query_time,
        'query_count': query_count,
        'queries': queries}    

        
@register.filter(name='phone2Str')  
def phone2Str(value):  
    try:  
        s = value
        res = s[0:3]+'-'+s[3:6]+' '+s[6:8]+' '+s[8:10]
        return res
    except ValueError:  
        return ''  


def google_url_shorten(url):
    GOOGLE_URL_SHORTEN_API = "AIzaSyAmFLlPmG7SKuwdCEG2s2TLmwGsgStGbZw"
    req_url = 'https://www.googleapis.com/urlshortener/v1/url?key=' + GOOGLE_URL_SHORTEN_API
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(req_url, data=json.dumps(payload), headers=headers)
    resp = json.loads(r.text)
    return resp['id']


@register.filter
def qr(value,size="120x120"):
    """
        Usage:
        <img src="{{object.code|qr:"120x130"}}" />
    """
#    return "http://chart.apis.google.com/chart?chs=%s&cht=qr&chl=%s&choe=UTF-8&chld=H|0" % (size, value)
#    return "https://chart.googleapis.com/chart?chs=%s&cht=qr&chl=%s&choe=UTF-8&chld=H|0" % (size, value)
    return "https://api.qrserver.com/v1/create-qr-code/?data=%s&amp;size=%s" % (value, size )


@register.filter
def sale_url(value,host):
    """
        Usage:
        {{object.code|sale_url}}"
    """
#    host="192.168.0.102:8001"
    host="rivelo.com.ua/component"
    #return "%s/%s/" % (host, value)
    str_url = "%s/%s/" % (host, value)
    #return google_url_shorten(str_url)
    return str_url


@register.filter
def bike_url(value,host):
    """
        Usage:
        {{object.code|bike_url}}"
    """
#    host="192.168.0.102:8001"
    host="rivelo.com.ua/bicycles"
    #return "%s/%s/" % (host, value)
    str_url = "%s/%s/model/" % (host, value)
    #return google_url_shorten(str_url)
    return str_url


@register.filter
def lenght(value):
    """
        Usage:
        {{object.code|lenght}}"
    """
    return len(value)


@register.filter("truncate_chars")
def truncate_chars(value, max_length):
    if len(value) > max_length:
        truncd_val = value[:max_length]
        if not len(value) == max_length+1 and value[max_length+1] != " ":
            truncd_val = truncd_val[:truncd_val.rfind(" ")]
        return  truncd_val + "..."
    return value

#register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name): 
    group = Group.objects.get(name=group_name) 
    return True if group in user.groups.all() else False
    #return user.groups.filter(name=group_name).exists()


@register.filter(name='has_shop') 
def has_shop(shop, shop_name): 
#    getshop = Shop.objects.get(name=shop_name)
    try:
        if shop.name == shop_name:
            return True
        else:
            return False
    except:
        pass

    
@register.filter(name='date_left') 
def date_left(date):
    try:
        now = datetime.datetime.now() 
        res = now - date
    except TypeError:
        return "don't update" 
    return res.days 


@register.filter(name='addcss')
def addcss(value, arg):
    css_classes = value.field.widget.attrs.get('class', '').split(' ')
    if css_classes and arg not in css_classes:
        css_classes = '%s %s' % (css_classes, arg)
    return value.as_widget(attrs={'class': css_classes})    


@register.filter(name='add_attr')
def add_attr(field, css):
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            key, val = d.split(':')
            attrs[key] = val

    return field.as_widget(attrs=attrs)


@register.filter(name='mrange')
def range(min, max):
    r = xrange(min, max)
    return r 


@register.filter(name='check_uid')
def check_uid(value):
    """
        Usage:
        {{object|check_uid}}"
    """
    res = ''
    q = re.search('checkbox_id=(.+?);', value)
    try:
        res = q.group(1)
        res = '/casa/prro/check/'+res+'/view/'
    except:
        res = ''
    return res


@register.filter(name='check_uid_html')
def check_uid(value):
    """
        Usage:
        {{object|check_uid}}"
    """
    res = ''
    q = re.search('checkbox_id=(.+?);', value)
    try:
        res = q.group(1)
        res = '/casa/prro/check/'+res+'/view/html/'
    except:
        res = ''
    return res


@register.filter
def month_name(month_number):
    month_number = int(month_number)
    return calendar.month_name[month_number]

