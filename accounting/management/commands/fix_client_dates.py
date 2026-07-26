# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from catalog.accounting.models import Client  # Замініть accounting на назву вашого додатка

class Command(BaseCommand):
    help = u'Оновлює некоректні або пусті дати реєстрації клієнтів на основі їх перших операцій'

    def handle(self, *args, **options):
        target_date = datetime.date(2024, 1, 10)

        # Шукаємо клієнтів для перевірки
        clients_to_update = Client.objects.filter(
            Q(reg_date=target_date) | Q(reg_date__isnull=True)
        )

        self.stdout.write(u"Знайдено клієнтів для перевірки: %d" % clients_to_update.count())

        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for client in clients_to_update:
                # Викликаємо метод моделі, який ми створили раніше
                start_year = client.get_absolute_oldest_year()
                new_reg_date = datetime.date(start_year, 1, 1)

                if client.reg_date is None or start_year < 2024:
                    Client.objects.filter(id=client.id).update(reg_date=new_reg_date)
                    updated_count += 1
                else:
                    skipped_count += 1

        # Виводимо фінальний звіт у консоль
        self.stdout.write(self.style.SUCCESS(u"Успішно оновлено: %d" % updated_count))
        self.stdout.write(u"Пропущено (актуальний 2024 рік): %d" % skipped_count)
