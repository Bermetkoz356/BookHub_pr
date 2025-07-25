from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField

User = get_user_model()

# Create your models here.

class Book(models.Model):
    title = models.CharField('Название', max_length=200)
    author = models.CharField('Автор', max_length=100)
    genre = models.CharField('Жанр', max_length=100)
    description = models.TextField('Описание', blank=True)
    cover = models.ImageField('Обложка', upload_to='covers/', blank=True, null=True)
    # Файл книги для скачивания
    file = models.FileField('Файл книги', upload_to='books/', blank=True, null=True)
    author_info = models.TextField('Информация об авторе', blank=True)

    def __str__(self):
        return self.title

class UserBookList(models.Model):
    LIST_TYPE_CHOICES = [
        ('reading', 'Читаю'),
        ('read', 'Прочитано'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    list_type = models.CharField('Тип списка', max_length=10, choices=LIST_TYPE_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book', 'list_type')
        verbose_name = 'Книга в списке пользователя'
        verbose_name_plural = 'Книги в списках пользователей'

    def __str__(self):
        return f'{self.user} — {self.book} ({self.get_list_type_display()})'

class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField('Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.user}: {self.text[:30]}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    bookmarks = models.ManyToManyField('Book', blank=True, related_name='bookmarked_by', verbose_name='Закладки')
    progress = JSONField('Прогресс чтения', blank=True, null=True, help_text='Словарь: {book_id: процент}')
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
    city = models.CharField('Город', max_length=100, blank=True)
    country = models.CharField('Страна', max_length=100, blank=True)

    def __str__(self):
        return f'Профиль {self.user.username}'

class BookRating(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'user')
        verbose_name = 'Оценка книги'
        verbose_name_plural = 'Оценки книг'

    def __str__(self):
        return f'{self.book} — {self.user} ({self.rating})'

class News(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    url = models.URLField('Ссылка на статью')
    description = models.TextField('Краткое описание', blank=True)
    published_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title

class Interview(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    url = models.URLField('Ссылка на интервью')
    description = models.TextField('Краткое описание', blank=True)
    published_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Интервью'
        verbose_name_plural = 'Интервью'

    def __str__(self):
        return self.title

class BookOfTheYear(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга года')
    year = models.PositiveIntegerField('Год')
    description = models.TextField('Краткое описание', blank=True)
    url = models.URLField('Ссылка на статью', blank=True)
    image = models.ImageField('Фото (обложка/иллюстрация)', upload_to='book_of_year/', blank=True, null=True)

    class Meta:
        verbose_name = 'Самая читаемая книга года'
        verbose_name_plural = 'Самые читаемые книги года'

    def __str__(self):
        return f'{self.book} ({self.year})'

class Trend(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    url = models.URLField('Ссылка на тренд')
    description = models.TextField('Краткое описание', blank=True)
    preview_image = models.ImageField('Превью (картинка)', upload_to='trends/', blank=True, null=True)
    published_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Тренд'
        verbose_name_plural = 'Тренды'

    def __str__(self):
        return self.title

class Update(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    url = models.URLField('Ссылка на обновление')
    description = models.TextField('Краткое описание', blank=True)
    published_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Обновление'
        verbose_name_plural = 'Обновления'

    def __str__(self):
        return self.title
