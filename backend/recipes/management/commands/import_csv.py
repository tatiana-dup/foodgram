import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import CSV files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', type=str, help='Path to the CSV file'
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    self.stderr.write(self.style.ERROR(f'Invalid row: {row}'))
                    continue

                name, measurement_unit = row

                Ingredient.objects.update_or_create(
                    name=name.strip().lower(),
                    measurement_unit=measurement_unit.strip()
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {csvfile}')
        )
