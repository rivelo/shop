# -*- coding: utf-8 -*-
from django import template
import MySQLdb

import datetime
from decimal import *


register = template.Library()
import re

@register.filter(name='mul')
def mul(value, arg):
    return round(float(value) * float(arg), 2)

@register.filter(name='div')
def div(value, arg):
    if arg == 0:
        return 0
#    '''Деление'''
    return round(float(value) / float(arg), 2)

@register.filter
def sub(value, arg):
#    '''Вычитание'''
    return round(float(value) - float(arg), 2)

@register.filter
def summa(value, arg):
    value = 0
    value = float(value) + float(arg)
    return round(value,2)

@register.filter
def dictsumm(value, arg):
    v = 0
    q = arg
    for t in value:
        v = v + t['count']
    
    #value = float(value) + float(arg)
    return value
    #return sum(d.get(arg) for d in value)

@register.filter(name='percentage')  
def percentage(sum, percent):  
    try:  
        a_percent = (100 - float(percent)) / 100.0
        return "%.2f" % (float(sum) * a_percent)  
    except ValueError:  
        return ''  

@register.filter(name='dotPart')  
def dotPart(sum, arg):  
    try:  
        e = arg 
        a_percent = (sum - int(sum)) * 100.0
        #return "%.2f" % (a_percent)  
        return round(a_percent)
    except ValueError:  
        return ''  

