import logging
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import TemplateView
from .models import Cart, CartItem, Order, OrderItem, Product, Category, UserProfile
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm, OrderForm, UserProfileForm
from .serializers import CategorySerializer, ProductSerializer, UserProfileSerializer
from rest_framework import generics, permissions
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db import transaction


logger = logging.getLogger(__name__)

def home(request):
    categories = Category.objects.all()  # Получаем все категории
    return render(request, 'new_store/home.html', {'categories': categories})

class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

def category_detail_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)  # Получаем категорию по ID
    products = Product.objects.filter(category=category).all()
    if not products.exists():
        print("Продукты не найдены для этой категории.")  # Вывод в консоль для отладки

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')  # Получаем номер страницы из параметров запроса
    page_obj = paginator.get_page(page_number)

    return render(request, 'new_store/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
    })


class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Доступ только для аутентифицированных пользователей

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Устанавливаем текущего пользователя как владельца профиля


class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Доступ только для аутентифицированных пользователей

    def get_queryset(self):
        # Фильтрация профиля по текущему пользователю
        return self.queryset.filter(user=self.request.user)

def category_list(request):
    categories = Category.objects.all()  # Извлечение всех категорий из базы данных
    return render(request, 'new_store/category_list.html', {'categories': categories})

class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def product_list(request):
    product_list = Product.objects.all()  # Получаем все продукты
    paginator = Paginator(product_list, 6)  # Показывать 6 продуктов на странице
    page_number = request.GET.get('page')  # Получаем номер страницы
    page_obj = paginator.get_page(page_number)  # Получаем объекты для текущей страницы

    return render(request, 'new_store/product_list.html', {
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)  # Получаем продукт по первичному ключу
    return render(request, 'new_store/product_detail.html', {'product': product})

def cart_view(request):
    if request.user.is_authenticated:
        # Получаем или создаем корзину текущего пользователя
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Получаем все элементы корзины для текущей корзины
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')  # Оптимизация запросов
        total_price = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart_items = []
        total_price = 0

    return render(request, 'new_store/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)  # Получаем или создаем корзину
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        quantity = request.POST.get('quantity', 1)
        try:
            quantity = float(quantity)
        except ValueError:
            quantity = 1  # Установить по умолчанию
        if not created:   # Если товар уже в корзине, увеличиваем количество на введенное значение
            cart_item.quantity += quantity
        else:    # Если товар только что добавлен, устанавливаем количество на введенное значение
            cart_item.quantity = quantity
        cart_item.save()  # Сохраняем изменения

    return redirect('cart_view')  # Перенаправляем на страницу корзины

def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity', 1)  # Установить значение по умолчанию
        try:
            quantity = int(quantity)  # Преобразуем в целое число
        except ValueError:
            quantity = 1  # Установить по умолчанию, если не удалось преобразовать

        # Получаем корзину текущего пользователя
        cart = get_object_or_404(Cart, user=request.user)

        # Попробуем получить CartItem, связанный с продуктом и корзиной
        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

        if cart_item:  # Если CartItem найден
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество товара обновлено.')  # Сообщение об успешном обновлении
        else:
            messages.error(request, 'Товар не найден в вашей корзине.')  # Сообщение об ошибке

    return redirect('cart_view')  # Перенаправление на страницу корзины

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)# Получаем CartItem по его ID
    if request.user.is_authenticated:
        if cart_item.cart.user == request.user:# Проверяем, принадлежит ли товар текущему пользователю
           cart_item.delete()  # Удаляем товар из корзины
           messages.success(request, 'Товар успешно удален из корзины.')  # Сообщение об успешном удалении
        else:
            messages.error(request, 'Вы не можете удалить этот товар из корзины.')  # Если товар не принадлежит пользователю
    else:
        messages.error(request, 'Пожалуйста, войдите в систему, чтобы удалить товар из корзины.')

    return redirect('cart_view')  # Перенаправляем обратно на страницу корзины

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()  # Сохраняем пользователя
            login(request, user)  # Автоматически входим в систему после регистрации

            # Приветственное сообщение
            messages.success(request, f'Добро пожаловать, {user.first_name} {user.last_name}!')
            return redirect('home')  # Перенаправляем на главную страницу
    else:
        form = UserRegistrationForm()  # Создаем пустую форму, если это GET-запрос

    # Рендерим страницу регистрации с формой
    return render(request, 'new_store/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Входим в систему
                messages.success(request, f'Добро пожаловать, {username}!')  # Приветственное сообщение
                return redirect('home')  # Перенаправление на главную страницу после входа
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'new_store/login.html', {'form': form})  # Указываем путь к шаблону логина

class CustomLoginView(LoginView):
    template_name = 'new_store/login.html'
    success_url = reverse_lazy('profile')  #  Имя URL для перенаправления

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'new_store/profile.html'  # Укажите ваш шаблон для профиля

@login_required
def profile_view(request):
    # Получаем профиль пользователя
    profile = request.user.profile  # Доступ через related_name='profile'

    # Проверяем наличие изображения профиля
    profile_picture_url = profile.profile_picture.url if profile.profile_picture and profile.profile_picture.name else 'default_image_url'  # URL изображения по умолчанию

    return render(request, 'new_store/profile.html', {
        'profile': profile,
        'profile_picture_url': profile_picture_url,
    })

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'new_store/edit_profile.html', {'form': form})

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['user'] = self.request.user  # Добавляем текущего пользователя в контекст
    return context


@login_required
def checkout_view(request):
    user = request.user

    # Получаем корзину пользователя
    try:
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all()

    except Cart.DoesNotExist:
        messages.error(request, 'У вас нет товаров в корзине.')
        return redirect('product_list')

    # Вычисляем общую стоимость
    total_price = sum(item.total_price for item in cart_items)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.total_price = total_price
                order.save()

                for item in cart_items:
                    total_item_price = item.quantity * item.product.price  # Вычисляем общую цену для данного элемента
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                        total_price=total_item_price  # Устанавливаем общую цену
                    )

                    # Уменьшаем количество на складе
                    item.product.stock -= item.quantity
                    item.product.save()

                # Очистка корзины
                cart.items.all().delete()

            messages.success(request, 'Ваш заказ успешно оформлен!')
            return redirect('order_complete', order_id=order.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = OrderForm()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    }

    return render(request, 'new_store/checkout.html', context)

@login_required
def order_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Суммируем total_price всех связанных OrderItem
    total_price = sum(item.total_price for item in order.items.all())

    context = {
        'order': order,
        'total_price': total_price,
    }
    return render(request, 'new_store/order_complete.html', context)

