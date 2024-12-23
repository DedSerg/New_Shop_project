from django.test import TestCase
from django.contrib.auth.models import User
from .models import Order, UserProfile
from django.core.exceptions import ValidationError
from .models import Product, Category, Cart, CartItem
from django.core.files.uploadedfile import SimpleUploadedFile


class OrderModelTest(TestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Убедитесь, что профиль пользователя создается корректно
        self.user_profile, _ = UserProfile.objects.get_or_create(user=self.user)

        # Создаем тестовый заказ
        self.order = Order.objects.create(
            user=self.user,
            full_name='Test User',
            address='123 Test Street',
            phone_number='1234567890',
            email='test@example.com',
            status='pending'
        )

    def test_order_creation(self):
        """Тестируем создание заказа"""
        self.assertEqual(self.order.full_name, 'Test User')
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(str(self.order), f'Заказ #{self.order.id} от {self.user.username}')

    def test_order_status_display(self):
        """Тестируем отображение статуса заказа"""
        self.assertEqual(self.order.get_status_display(), 'В ожидании')

    def test_order_status_choices(self):
        """Тестируем корректность выбора статусов"""
        self.assertEqual(Order.STATUS_CHOICES, [
            ('pending', 'В ожидании'),
            ('completed', 'Завершён'),
            ('canceled', 'Отменён'),
        ])

class ProductModelTest(TestCase):

    def setUp(self):
        # Создаем категорию для тестов
        self.category = Category.objects.create(name='Тестовая категория')
        # Создаем пользователя для тестов
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Создаем продукт с категорией
        self.product = Product.objects.create(
            name='Тестовый продукт',
            description='Описание тестового продукта',
            price=10.00,
            stock=5,
            category=self.category  # Указываем категорию
        )
        # Создаем корзину для пользователя
        self.cart = Cart.objects.create(user=self.user)

    def test_total_price(self):
        # Тестируем вычисление общей цены
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(cart_item.total_price, 30.00)  # 3 * 10.00

class CartModelTest(TestCase):

    def setUp(self):
        # Создаем пользователя для тестов
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Создаем продукт для тестов
        self.product = Product.objects.create(
            name='Тестовый продукт',
            description='Описание тестового продукта',
            price=10.00,
            stock=5,
            category=None  # Укажите нужную категорию, если у вас она есть
        )
        # Создаем корзину для пользователя
        self.cart = Cart.objects.create(user=self.user)

    def test_create_cart(self):
        # Тестируем создание корзины
        self.assertEqual(self.cart.user, self.user)
        self.assertIsNotNone(self.cart.created_at)

    def test_add_cart_item(self):
        # Тестируем добавление товара в корзину
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)

    def test_clean_quantity_exceeds_stock(self):
        # Тестируем валидацию на превышение количества
        cart_item = CartItem(cart=self.cart, product=self.product, quantity=10)  # 10 больше, чем в наличии
        with self.assertRaises(ValidationError):
            cart_item.clean()  # Вызываем валидацию

    def test_increase_quantity(self):
        # Тестируем увеличение количества товара
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        cart_item.increase_quantity()
        self.assertEqual(cart_item.quantity, 3)

    def test_decrease_quantity(self):
        # Тестируем уменьшение количества товара
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        cart_item.decrease_quantity()
        self.assertEqual(cart_item.quantity, 1)

        # Уменьшаем количество до 1, проверяем, что уменьшение не произошло
        cart_item.decrease_quantity()
        self.assertEqual(cart_item.quantity, 1)  # Количество не должно стать меньше 1

    def test_total_price(self):
        # Тестируем вычисление общей цены
        cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(cart_item.total_price, 30.00)  # 3 * 10.00


class UserProfileModelTest(TestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Создаем тестовое изображение
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'file_content',  # Можете оставить содержимое пустым для теста
            content_type='image/jpeg'
        )

        # Создаем профиль пользователя с изображением
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            profile_picture=self.test_image,  # Используем тестовое изображение
            date_of_birth='1990-01-01',
            phone_number='1234567890',
            email='test@example.com',
            last_name='Test',
            first_name='User'
        )

    def test_user_profile_creation(self):
        """Тестируем создание профиля пользователя"""
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.date_of_birth, '1990-01-01')
        self.assertEqual(self.user_profile.phone_number, '1234567890')
        self.assertEqual(self.user_profile.email, 'test@example.com')
        self.assertEqual(self.user_profile.last_name, 'Test')
        self.assertEqual(self.user_profile.first_name, 'User')
        self.assertIsNotNone(self.user_profile.profile_picture)  # Проверяем, что изображение установлено

    def test_user_profile_string_representation(self):
        """Тестируем строковое представление профиля пользователя"""
        self.assertEqual(str(self.user_profile), "testuser's Profile")

    def test_user_profile_blank_fields(self):
        """Тестируем создание профиля с пустыми полями"""
        user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        user_profile2 = UserProfile.objects.create(user=user2)

        # Проверяем, что поля действительно равны None
        self.assertEqual(user_profile2.profile_picture, None)
        self.assertEqual(user_profile2.date_of_birth, None)
        self.assertEqual(user_profile2.phone_number, None)
        self.assertEqual(user_profile2.email, None)
        self.assertEqual(user_profile2.last_name, None)
        self.assertEqual(user_profile2.first_name, None)

    def test_user_profile_update(self):
        """Тестируем обновление профиля пользователя"""
        self.user_profile.phone_number = '0987654321'
        self.user_profile.save()
        self.assertEqual(self.user_profile.phone_number, '0987654321')