from django.urls import path
from .views import HomeView, BookListView, BookDetailView, ProfileView, AccountSettingsView, MyBooksView, AddToMyBooksView, RemoveFromMyBooksView, FriendsView, CommunityView, NotificationsView, MessagesView, BookRatingView, book_pdf_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/', BookListView.as_view(), name='catalog'),
    path('book/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/settings/', AccountSettingsView.as_view(), name='account_settings'),
    path('mybooks/', MyBooksView.as_view(), name='mybooks'),
    path('mybooks/add/', AddToMyBooksView.as_view(), name='add_to_mybooks'),
    path('mybooks/remove/', RemoveFromMyBooksView.as_view(), name='remove_from_mybooks'),
    path('book/<int:pk>/pdf/', book_pdf_view, name='book_pdf_view'),
]

urlpatterns += [
    path('search/', BookListView.as_view(template_name='catalog.html'), name='search'),
    path('friends/', FriendsView.as_view(), name='friends'),
    path('community/', CommunityView.as_view(), name='community'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('book/<int:pk>/rate/', BookRatingView.as_view(), name='rate_book'),
] 