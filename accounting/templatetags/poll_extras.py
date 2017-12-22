# -*- coding: utf-8 -*-
from django import template
from django.contrib.auth.models import Group
import datetime

register = template.Library()


@register.filter(name='mul')
def mul(value, arg):
    return value * arg

@register.filter
def div(value, arg):
    return value / arg

@register.filter
def sub(value, arg):
    return value - arg


@register.inclusion_tag('orm_debug.html')
def orm_debug():
    import re
    try:
        from pygments import highlight
        from pygments.lexers import SqlLexer
        from pygments.formatters import HtmlFormatter
        pygments_installed = True
    except ImportError:
        pygments_installed = False

    from django.db import connection
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
        
        #return "%.2f" % (a_percent)  
        #return round(a_percent)
    except ValueError:  
        return ''  


@register.filter
def qr(value,size="120x120"):
    """
        Usage:
        <img src="{{object.code|qr:"120x130"}}" />
    """
    return "http://chart.apis.google.com/chart?chs=%s&cht=qr&chl=%s&choe=UTF-8&chld=H|0" % (size, value)


from django.http import HttpRequest

@register.filter
def sale_url(value,host):
    """
        Usage:
        {{object.code|sale_url}}"
    """
#    host="192.168.0.102:8001"
    host="rivelo.com.ua/price"
    return "%s/%s/" % (host, value)


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
 
    
@register.filter(name='date_left') 
def date_left(date):
    try:
        now = datetime.datetime.now() 
        res = now - date
    except TypeError:
        return "don't update" 
    return res.days 
    
