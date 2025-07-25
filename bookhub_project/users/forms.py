from .models import BookRating
from django import forms
from .models import UserProfile

class BookRatingForm(forms.ModelForm):
    class Meta:
        model = BookRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, '★' * i) for i in range(1, 6)]),
            'review': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ваш отзыв...'}),
        }

class AccountSettingsForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    email = forms.EmailField(label='Email', required=True)
    birth_date = forms.DateField(label='Дата рождения', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    city = forms.CharField(label='Город', required=False)
    country = forms.CharField(label='Страна', required=False)

    class Meta:
        model = UserProfile
        fields = ['avatar', 'birth_date', 'city', 'country']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
        self.fields['birth_date'].initial = self.instance.birth_date
        self.fields['city'].initial = self.instance.city
        self.fields['country'].initial = self.instance.country

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = self.instance.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()
        profile.birth_date = self.cleaned_data.get('birth_date')
        profile.city = self.cleaned_data.get('city')
        profile.country = self.cleaned_data.get('country')
        if commit:
            profile.save()
        return profile 