from rest_framework import serializers
from .models import Category, Product, UserProfile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Вложенный сериализатор
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'category', 'image', 'stock']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id',  # Добавьте поле id, если нужно
            'user',  # Ссылка на пользователя
            'profile_picture',  # Изображение профиля
            'date_of_birth',  # Дата рождения
            'phone_number',  # Номер телефона
            'email',  # Электронная почта
            'last_name',  # Фамилия
            'first_name',  # Имя
        ]