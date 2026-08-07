# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.accounting.models import Catalog

class Command(BaseCommand):
    help = u'Оновлює поле count в моделі Catalog на основі реальних залишків'

    def handle(self, *args, **options):
        with transaction.atomic():
            catalogs = Catalog.objects.all()
            total_updated = 0
            
            # Додано символ u перед рядком для підтримки кирилиці в Python 2
            self.stdout.write(u'Початок оновлення кількості товарів...')
            
            for item in catalogs:
                real_count = item.get_realshop_count()
                
                if real_count < 0:
                    real_count = 0
                
                if item.count != real_count:
                    item.count = real_count
                    item.save(update_fields=['count'])
                    total_updated += 1

            # Виправлено форматування рядка через оператор % із Unicode
            success_msg = u'Оновлення завершено! Успішно виправлено позицій: %s' % total_updated
            self.stdout.write(self.style.SUCCESS(success_msg))
