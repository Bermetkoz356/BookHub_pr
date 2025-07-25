from django.contrib import admin
from .models import Book, UserBookList, Comment, UserProfile, BookRating, News, Interview, BookOfTheYear, Trend, Update

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre')
    search_fields = ('title', 'author', 'genre')
    fields = ('title', 'author', 'author_info', 'genre', 'description', 'cover', 'file')

@admin.register(UserBookList)
class UserBookListAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'list_type', 'added_at')
    list_filter = ('list_type', 'user')
    search_fields = ('user__username', 'book__title')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    search_fields = ('user__username', 'book__title', 'text')
    list_filter = ('book',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'city', 'country')
    search_fields = ('user__username',)
    filter_horizontal = ('bookmarks',)

@admin.register(BookRating)
class BookRatingAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    search_fields = ('book__title', 'user__username', 'review')
    list_filter = ('rating', 'created_at')

class TrendAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'url', 'preview_image')
    search_fields = ('title', 'description', 'url')
    fields = ('title', 'url', 'description', 'preview_image', 'published_at')
    readonly_fields = ('published_at',)

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'url')
    search_fields = ('title', 'description', 'url')
    fields = ('title', 'url', 'description', 'published_at')
    readonly_fields = ('published_at',)

class InterviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'url')
    search_fields = ('title', 'description', 'url')
    fields = ('title', 'url', 'description', 'published_at')
    readonly_fields = ('published_at',)

class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'url')
    search_fields = ('title', 'description', 'url')
    fields = ('title', 'url', 'description', 'published_at')
    readonly_fields = ('published_at',)

class BookOfTheYearAdmin(admin.ModelAdmin):
    list_display = ('book', 'year', 'url', 'image')
    search_fields = ('book__title', 'description', 'url')
    list_filter = ('year', 'book')
    fields = ('book', 'year', 'url', 'description', 'image')

admin.site.register(News, NewsAdmin)
admin.site.register(Interview, InterviewAdmin)
admin.site.register(BookOfTheYear, BookOfTheYearAdmin)
admin.site.register(Trend, TrendAdmin)
admin.site.register(Update, UpdateAdmin)
