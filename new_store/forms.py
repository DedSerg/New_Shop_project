from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Order



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')
    first_name = forms.CharField(max_length=150, required=True, label='Имя')
    last_name = forms.CharField(max_length=150, required=True, label='Фамилия')
    date_of_birth = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(1938, 2025)),
                                    label='Дата рождения')
    phone_number = forms.CharField(max_length=15, required=False, label='Номер телефона')
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'date_of_birth', 'phone_number']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError("Этот email уже зарегистрирован.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Храните пароль в зашифрованном виде
        if commit:
            user.save()

            # Создание UserProfile после сохранения пользователя
            UserProfile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'address', 'phone_number', 'email', 'additional_info']
        labels = {
            'full_name': 'Полное имя',
            'address': 'Адрес',
            'phone_number': 'Телефон',
            'email': 'Электронная почта',
            'additional_info': 'Дополнительная информация',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше полное имя'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш адрес'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш телефон'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'}),
            'additional_info': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Дополнительная информация', 'rows': 3}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'date_of_birth', 'phone_number', 'email', 'last_name', 'first_name']

