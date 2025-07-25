from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Book, UserBookList, UserProfile, BookRating
from .models import Trend, Interview, Update, BookOfTheYear
from .forms import BookRatingForm, AccountSettingsForm
import random
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, FormView
from django.urls import reverse_lazy
import os
from django.db import models
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
try:
    from django.contrib.postgres.search import TrigramSimilarity
    HAS_TRIGRAM = True
except ImportError:
    HAS_TRIGRAM = False
from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt

# Create your views here.

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = list(Book.objects.all())
        context['popular_books'] = random.sample(books, min(6, len(books))) if books else []
        context['now'] = datetime.now()
        context['trends'] = Trend.objects.order_by('-published_at')[:5]
        context['interviews'] = Interview.objects.order_by('-published_at')[:3]
        context['updates'] = Update.objects.order_by('-published_at')[:3]
        # Самая читаемая книга года (BookOfTheYear)
        year = datetime.now().year
        book_of_year = BookOfTheYear.objects.filter(year=year).first()
        context['book_of_year'] = book_of_year
        return context

class BookListView(ListView):
    model = Book
    template_name = 'catalog.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search') or self.request.GET.get('q')
        use_trigram = False
        if hasattr(settings, 'DATABASES'):
            db_engine = settings.DATABASES['default']['ENGINE']
            if 'postgresql' in db_engine and HAS_TRIGRAM:
                use_trigram = True
        genre = self.request.GET.get('genre')
        author = self.request.GET.get('author')
        if genre:
            queryset = queryset.filter(genre=genre)
        if author:
            queryset = queryset.filter(author=author)
        if search:
            if use_trigram:
                # Fuzzy search with trigram similarity (PostgreSQL)
                return queryset.annotate(
                    sim_title=TrigramSimilarity('title', search),
                    sim_author=TrigramSimilarity('author', search),
                    sim_desc=TrigramSimilarity('description', search),
                ).filter(
                    Q(sim_title__gt=0.2) | Q(sim_author__gt=0.2) | Q(sim_desc__gt=0.2)
                ).order_by('-sim_title', '-sim_author', '-sim_desc')
            else:
                words = search.split()
                q = Q()
                for word in words:
                    q |= Q(title__icontains=word) | Q(author__icontains=word) | Q(description__icontains=word)
                    q |= Q(author__iexact=word)
                q |= Q(author__icontains=search) | Q(author__iexact=search)
                queryset = queryset.filter(q)
        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '') or self.request.GET.get('q', '')
        context['genres'] = Book.objects.values_list('genre', flat=True).distinct().order_by('genre')
        context['authors'] = Book.objects.values_list('author', flat=True).distinct().order_by('author')
        context['selected_genre'] = self.request.GET.get('genre', '')
        context['selected_author'] = self.request.GET.get('author', '')
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        is_pdf = is_txt = is_epub = False
        txt_content = None
        if book.file:
            ext = os.path.splitext(book.file.name)[1].lower()
            if ext == '.pdf':
                is_pdf = True
            elif ext == '.txt':
                is_txt = True
                try:
                    with book.file.open('r', encoding='utf-8') as f:
                        txt_content = f.read()
                except Exception:
                    txt_content = 'Ошибка чтения файла.'
            elif ext == '.epub':
                is_epub = True
        context['is_pdf'] = is_pdf
        context['is_txt'] = is_txt
        context['is_epub'] = is_epub
        context['txt_content'] = txt_content
        # --- рейтинги и отзывы ---
        context['ratings'] = book.ratings.select_related('user').order_by('-created_at')
        context['avg_rating'] = book.ratings.aggregate(models.Avg('rating'))['rating__avg']
        context['user_rating'] = None
        if self.request.user.is_authenticated:
            context['user_rating'] = book.ratings.filter(user=self.request.user).first()
        context['rating_form'] = BookRatingForm()
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from .models import UserBookList, UserProfile
        context['reading_books'] = UserBookList.objects.filter(user=user, list_type='reading').select_related('book')
        context['read_books'] = UserBookList.objects.filter(user=user, list_type='read').select_related('book')
        # профиль, закладки, прогресс
        profile, _ = UserProfile.objects.get_or_create(user=user)
        context['profile'] = profile
        context['bookmarks'] = profile.bookmarks.all()
        context['progress'] = profile.progress or {}
        return context

class AccountSettingsView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'account_settings.html'
    form_class = AccountSettingsForm
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class MyBooksView(LoginRequiredMixin, ListView):
    template_name = 'mybooks.html'
    context_object_name = 'mybooks'
    paginate_by = 12

    def get_queryset(self):
        from .models import UserBookList
        return UserBookList.objects.filter(user=self.request.user, list_type='reading').select_related('book')

@method_decorator(require_POST, name='dispatch')
class AddToMyBooksView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, pk=book_id)
        UserBookList.objects.get_or_create(user=request.user, book=book, list_type='reading')
        return redirect('mybooks')

@method_decorator(require_POST, name='dispatch')
class RemoveFromMyBooksView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        UserBookList.objects.filter(user=request.user, book_id=book_id, list_type='reading').delete()
        return redirect('mybooks')

class FriendsView(TemplateView):
    template_name = 'friends.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Заглушки для друзей и заявок
        context['friends'] = []
        friends_data = [
            {'name': 'Анна Иванова', 'avatar': '/media/avatars/anna.jpg', 'status': 'online'},
            {'name': 'Иван Петров', 'avatar': '', 'status': 'offline'},
        ]
        for f in friends_data:
            avatar_path = f.get('avatar', '')
            # Проверяем существование файла (относительно MEDIA_ROOT)
            has_avatar = False
            if avatar_path:
                avatar_file = avatar_path.replace('/media/', '')
                media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
                full_path = os.path.join(media_root, avatar_file)
                has_avatar = os.path.isfile(full_path)
            if not avatar_path or not has_avatar:
                initial = (f['name'].strip()[0].upper() if f['name'] else '?')
                f['initial'] = initial
                f['avatar'] = ''
            context['friends'].append(f)
        context['requests'] = []
        requests_data = [
            {'name': 'Мария Смирнова', 'avatar': ''},
        ]
        for r in requests_data:
            avatar_path = r.get('avatar', '')
            has_avatar = False
            if avatar_path:
                avatar_file = avatar_path.replace('/media/', '')
                media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
                full_path = os.path.join(media_root, avatar_file)
                has_avatar = os.path.isfile(full_path)
            if not avatar_path or not has_avatar:
                initial = (r['name'].strip()[0].upper() if r['name'] else '?')
                r['initial'] = initial
                r['avatar'] = ''
            context['requests'].append(r)
        return context

class CommunityView(TemplateView):
    template_name = 'community.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Заглушки для обсуждений
        context['topics'] = [
            {'title': 'Любимые книги 2024 года', 'author': 'Анна Иванова', 'replies': 12, 'last_post': '5 минут назад', 'last_user': 'Иван Петров'},
            {'title': 'Что вы читаете сейчас?', 'author': 'Мария Смирнова', 'replies': 34, 'last_post': '10 минут назад', 'last_user': 'Анна Иванова'},
            {'title': 'Обсуждение новинок', 'author': 'Иван Петров', 'replies': 7, 'last_post': '1 час назад', 'last_user': 'Мария Смирнова'},
        ]
        return context

class NotificationsView(TemplateView):
    template_name = 'notifications.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Заглушки для уведомлений
        notifications_data = [
            {'type': 'friend_request', 'text': 'Анна Иванова отправила вам заявку в друзья', 'time': '2 минуты назад', 'avatar': '/media/avatars/anna.jpg'},
            {'type': 'comment', 'text': 'Иван Петров прокомментировал вашу книгу', 'time': '10 минут назад', 'avatar': '/media/avatars/ivan.jpg'},
            {'type': 'message', 'text': 'Новое сообщение от Марии Смирновой', 'time': '1 час назад', 'avatar': '/media/avatars/maria.jpg'},
        ]
        context['notifications'] = []
        for n in notifications_data:
            avatar_path = n.get('avatar', '')
            has_avatar = False
            if avatar_path:
                avatar_file = avatar_path.replace('/media/', '')
                media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
                full_path = os.path.join(media_root, avatar_file)
                has_avatar = os.path.isfile(full_path)
            if not avatar_path or not has_avatar:
                # Попробуем взять первую букву имени из текста уведомления
                import re
                match = re.match(r'(\w+)', n.get('text', ''))
                initial = match.group(1)[0].upper() if match else '?'
                n['initial'] = initial
                n['avatar'] = ''
            context['notifications'].append(n)
        return context

class MessagesView(LoginRequiredMixin, TemplateView):
    template_name = 'messages.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dialogs_data = [
            {
                'name': 'Анна Иванова',
                'avatar': '/media/avatars/anna.jpg',
                'last_message': 'Привет! Как дела?',
                'time': '5 мин назад',
                'unread': True,
            },
            {
                'name': 'Иван Петров',
                'avatar': '/media/avatars/ivan.jpg',
                'last_message': 'Спасибо за рекомендацию!',
                'time': '1 ч назад',
                'unread': False,
            },
        ]
        context['dialogs'] = []
        for d in dialogs_data:
            avatar_path = d.get('avatar', '')
            has_avatar = False
            if avatar_path:
                avatar_file = avatar_path.replace('/media/', '')
                media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
                full_path = os.path.join(media_root, avatar_file)
                has_avatar = os.path.isfile(full_path)
            if not avatar_path or not has_avatar:
                initial = (d['name'].strip()[0].upper() if d['name'] else '?')
                d['initial'] = initial
                d['avatar'] = ''
            context['dialogs'].append(d)
        return context

class BookRatingView(LoginRequiredMixin, FormView):
    form_class = BookRatingForm
    def form_valid(self, form):
        book = Book.objects.get(pk=self.kwargs['pk'])
        BookRating.objects.update_or_create(
            book=book, user=self.request.user,
            defaults={'rating': form.cleaned_data['rating'], 'review': form.cleaned_data['review']}
        )
        return redirect('book_detail', pk=book.pk)

@xframe_options_exempt
def book_pdf_view(request, pk):
    from .models import Book
    try:
        book = Book.objects.get(pk=pk)
        if not book.file or not book.file.name.lower().endswith('.pdf'):
            raise Http404()
        return FileResponse(book.file.open('rb'), content_type='application/pdf')
    except Book.DoesNotExist:
        raise Http404()
