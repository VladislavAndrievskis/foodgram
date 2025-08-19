import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Импорт данных из csv в модель Ingredient"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Путь к файлу")

    def handle(self, *args, **options):
        print("Заполнение модели Ingredient из csv запущено.")

        # Указываем кодировку UTF-8 при открытии файла
        file_path = options["path"] + "ingredients.csv"
        try:
            with open(file_path, "r", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)

                # Пропускаем заголовок, если он есть
                next(reader, None)

                for row_number, row in enumerate(reader, start=1):
                    try:
                        # Проверяем, что строка не пустая
                        if not row:
                            continue

                        obj, created = Ingredient.objects.get_or_create(
                            name=row[0].strip(),
                            measurement_unit=row[1].strip(),
                        )

                        if not created:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Ингредиент {obj} уже существует"
                                    "в базе данных."
                                )
                            )

                    except IndexError:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Ошибка в строке {row_number}: "
                                "Некорректное количество столбцов"
                            )
                        )
                    except Exception as error:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Ошибка в строке {row_number}: {error}"
                            )
                        )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"Файл не найден по пути: {file_path}")
            )
            return

        self.stdout.write(
            self.style.SUCCESS("Заполнение модели Ingredient завершено.")
        )
