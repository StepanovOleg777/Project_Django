from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создает группы с правами для модераторов'

    def handle(self, *args, **options):
        # Получаем контент-тайп для модели Product
        content_type = ContentType.objects.get_for_model(Product)

        # Получаем нужные разрешения
        try:
            can_unpublish = Permission.objects.get(
                codename='can_unpublish_product',
                content_type=content_type
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Разрешение can_unpublish_product не найдено!')
            )
            return

        delete_product = Permission.objects.get(
            codename='delete_product',
            content_type=content_type
        )
        change_product = Permission.objects.get(
            codename='change_product',
            content_type=content_type
        )
        view_product = Permission.objects.get(
            codename='view_product',
            content_type=content_type
        )

        # Создаем группу "Модератор продуктов"
        moderator_group, created = Group.objects.get_or_create(
            name='Модератор продуктов'
        )

        # Назначаем права группе
        moderator_group.permissions.add(
            can_unpublish,
            delete_product,
            change_product,
            view_product
        )

        # Создаем группу "Контент-менеджер"
        content_manager_group, cm_created = Group.objects.get_or_create(
            name='Контент-менеджер'
        )

        # Назначаем права для контент-менеджера
        content_manager_group.permissions.add(
            change_product,
            view_product
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Модератор продуктов" создана успешно!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Группа "Модератор продуктов" уже существует, обновлена.')
            )

        if cm_created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Контент-менеджер" создана успешно!')
            )

        # Выводим список прав для каждой группы
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('Права группы "Модератор продуктов":')
        self.stdout.write('=' * 50)
        for perm in moderator_group.permissions.all():
            self.stdout.write(f'  - {perm.name}')

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('Права группы "Контент-менеджер":')
        self.stdout.write('=' * 50)
        for perm in content_manager_group.permissions.all():
            self.stdout.write(f'  - {perm.name}')