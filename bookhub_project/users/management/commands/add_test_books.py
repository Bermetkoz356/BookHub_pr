from django.core.management.base import BaseCommand
from users.models import Book

TEST_BOOKS = [
    {
        'title': 'Война и мир',
        'author': 'Лев Толстой',
        'genre': 'Роман',
        'description': 'Эпический роман о войне 1812 года и судьбах русских аристократов.'
    },
    {
        'title': 'Преступление и наказание',
        'author': 'Фёдор Достоевский',
        'genre': 'Роман',
        'description': 'История студента Раскольникова, совершившего убийство.'
    },
    {
        'title': 'Мастер и Маргарита',
        'author': 'Михаил Булгаков',
        'genre': 'Фантастика',
        'description': 'Мистический роман о визите дьявола в Москву.'
    },
    {
        'title': 'Анна Каренина',
        'author': 'Лев Толстой',
        'genre': 'Роман',
        'description': 'Трагическая история любви Анны Карениной.'
    },
    {
        'title': 'Идиот',
        'author': 'Фёдор Достоевский',
        'genre': 'Роман',
        'description': 'Роман о судьбе князя Мышкина.'
    },
    {
        'title': 'Обломов',
        'author': 'Иван Гончаров',
        'genre': 'Роман',
        'description': 'История оленивом дворянине Илье Обломове.'
    },
    {
        'title': 'Дубровский',
        'author': 'Александр Пушкин',
        'genre': 'Приключения',
        'description': 'Роман о благородном разбойнике.'
    },
    {
        'title': 'Евгений Онегин',
        'author': 'Александр Пушкин',
        'genre': 'Роман в стихах',
        'description': 'Классика русской литературы.'
    },
    {
        'title': 'Доктор Живаго',
        'author': 'Борис Пастернак',
        'genre': 'Роман',
        'description': 'История любви на фоне революции.'
    },
    {
        'title': 'Тихий Дон',
        'author': 'Михаил Шолохов',
        'genre': 'Роман',
        'description': 'Эпопея о донских казаках.'
    },
    {
        'title': 'Белая гвардия',
        'author': 'Михаил Булгаков',
        'genre': 'Роман',
        'description': 'Роман о гражданской войне.'
    },
    {
        'title': 'Пикник на обочине',
        'author': 'Аркадий и Борис Стругацкие',
        'genre': 'Фантастика',
        'description': 'Фантастический роман о Зоне.'
    },
    {
        'title': 'Мы',
        'author': 'Евгений Замятин',
        'genre': 'Антиутопия',
        'description': 'Роман-антиутопия о тоталитарном будущем.'
    },
    {
        'title': 'Собачье сердце',
        'author': 'Михаил Булгаков',
        'genre': 'Фантастика',
        'description': 'Сатирическая повесть о профессоре Преображенском.'
    },
    {
        'title': 'Двенадцать стульев',
        'author': 'Илья Ильф и Евгений Петров',
        'genre': 'Сатира',
        'description': 'Знаменитый роман о поисках сокровищ.'
    },
]

class Command(BaseCommand):
    help = 'Добавляет тестовые книги в базу данных.'

    def handle(self, *args, **kwargs):
        created = 0
        for data in TEST_BOOKS:
            obj, was_created = Book.objects.get_or_create(
                title=data['title'],
                defaults={
                    'author': data['author'],
                    'genre': data['genre'],
                    'description': data['description'],
                }
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Добавлено книг: {created}')) 