import json
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient
from django.db import IntegrityError
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Загружает ингредиенты из файла JSON'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Путь до JSON-файла с ингредиентами')

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        try:
            with open(filename, encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            raise CommandError(f'Файл не найден: {filename}')
        except json.JSONDecodeError as e:
            raise CommandError(f'Ошибка чтения JSON: {e}')

        created_count = 0
        skipped_count = 0

        self.stdout.write(f'Начинаем загрузку {len(data)} ингредиентов...\n')

        for i, item in enumerate(tqdm(data, desc='Загрузка', unit='ингр.'), start=1):
            try:
                name = item['name']
                unit = item['measurement_unit']
                if not name or not unit:
                    self.stderr.write(f'[{i}] Пропущено: пустые поля — {item}')
                    skipped_count += 1
                    continue

                _, created = Ingredient.objects.get_or_create(
                    name=name.strip(), measurement_unit=unit.strip()
                )
                if created:
                    created_count += 1
            except KeyError as e:
                self.stderr.write(f'[{i}] Пропущено: отсутствует ключ {e} — {item}')
                skipped_count += 1
            except IntegrityError as e:
                self.stderr.write(f'[{i}] Ошибка при сохранении: {e} — {item}')
                skipped_count += 1
            except Exception as e:
                self.stderr.write(f'[{i}] Неизвестная ошибка: {e} — {item}')
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f'Успешно добавлено {created_count} ингредиентов.'))
