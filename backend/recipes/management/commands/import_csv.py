import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import CSV files into the database'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        csv_file = 'data/ingredients.csv'

        try:
            with open(csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                ingredients = []
                for row in reader:
                    if len(row) != 2:
                        self.stderr.write(
                            self.style.ERROR(f'Invalid row: {row}'))
                        continue

                    name, measurement_unit = row

                    ingredients.append(
                        Ingredient(name=name.strip().lower(),
                                   measurement_unit=measurement_unit.strip())
                    )
                Ingredient.objects.bulk_create(ingredients,
                                               ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {csvfile}')
            )
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'File {csv_file} not found'))
