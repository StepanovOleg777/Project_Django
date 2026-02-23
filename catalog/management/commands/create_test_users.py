from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from users.models import User


class Command(BaseCommand):
    help = 'Создает тестовых пользователей и добавляет их в группы'

    def handle(self, *args, **options):
        # Создаем или получаем группы
        moderator_group, _ = Group.objects.get_or_create(name='Модератор продуктов')
        content_manager_group, _ = Group.objects.get_or_create(name='Контент-менеджер')

        # Тестовый модератор
        moderator, created = User.objects.get_or_create(
            email='moderator@example.com',
            defaults={
                'first_name': 'Модератор',
                'last_name': 'Тестовый',
                'is_active': True,
            }
        )

        if created:
            moderator.set_password('moderator123')
            moderator.save()
            self.stdout.write(self.style.SUCCESS('Создан тестовый модератор: moderator@example.com / moderator123'))
        else:
            self.stdout.write(self.style.WARNING('Модератор уже существует: moderator@example.com'))

        # Добавляем в группу модераторов
        moderator.groups.add(moderator_group)

        # Тестовый контент-менеджер
        content_manager, created = User.objects.get_or_create(
            email='content@example.com',
            defaults={
                'first_name': 'Контент',
                'last_name': 'Менеджер',
                'is_active': True,
            }
        )

        if created:
            content_manager.set_password('content123')
            content_manager.save()
            self.stdout.write(self.style.SUCCESS('Создан контент-менеджер: content@example.com / content123'))
        else:
            self.stdout.write(self.style.WARNING('Контент-менеджер уже существует: content@example.com'))

        # Добавляем в группу контент-менеджеров
        content_manager.groups.add(content_manager_group)

        # Обычный пользователь (не модератор)
        regular_user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'first_name': 'Обычный',
                'last_name': 'Пользователь',
                'is_active': True,
            }
        )

        if created:
            regular_user.set_password('user123')
            regular_user.save()
            self.stdout.write(self.style.SUCCESS('Создан обычный пользователь: user@example.com / user123'))
        else:
            self.stdout.write(self.style.WARNING('Обычный пользователь уже существует: user@example.com'))

        # Проверяем права
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('Проверка прав:')
        self.stdout.write('=' * 50)

        self.stdout.write(f'\nМодератор ({moderator.email}):')
        self.stdout.write(f'  - Группы: {[g.name for g in moderator.groups.all()]}')
        self.stdout.write(f'  - Право can_unpublish_product: {moderator.has_perm("catalog.can_unpublish_product")}')

        self.stdout.write(f'\nКонтент-менеджер ({content_manager.email}):')
        self.stdout.write(f'  - Группы: {[g.name for g in content_manager.groups.all()]}')
        self.stdout.write(
            f'  - Право can_unpublish_product: {content_manager.has_perm("catalog.can_unpublish_product")}')
        self.stdout.write(f'  - Право change_product: {content_manager.has_perm("catalog.change_product")}')

        self.stdout.write(f'\nОбычный пользователь ({regular_user.email}):')
        self.stdout.write(f'  - Группы: {[g.name for g in regular_user.groups.all()]}')
        self.stdout.write(f'  - Право can_unpublish_product: {regular_user.has_perm("catalog.can_unpublish_product")}')