from django.urls import path
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    home, register, CustomLoginView, category_list, category_detail_view, product_list, product_detail,
    CategoryListAPIView, CategoryDetailAPIView, ProductListAPIView, ProductDetailAPIView, add_to_cart, remove_from_cart,
    update_cart, cart_view, checkout_view, order_complete, UserProfileListCreateView, UserProfileDetailView)


urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/profile/edit/', views.edit_profile, name='edit_profile'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('profiles/', UserProfileListCreateView.as_view(), name='userprofile-list-create'),
    path('profiles/<int:pk>/', UserProfileDetailView.as_view(), name='userprofile-detail'),
    path('categories/', category_list, name='category_list'),
    path('category/<int:category_id>/', category_detail_view, name='category_detail'),
    path('products/', product_list, name='product_list'),  # Изменено на product_list
    path('products/<int:pk>/', product_detail, name='product_detail'),
    path('api/categories/', CategoryListAPIView.as_view(), name='category_list_api'),
    path('api/categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category_detail_api'),
    path('api/products/', ProductListAPIView.as_view(), name='product_list_api'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail_api'),
    path('cart/add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', update_cart, name='update_cart'),  # новый маршрут
    path('cart/', cart_view, name='cart_view'),
    path('checkout/', checkout_view, name='checkout'),
    path('order/complete/<int:order_id>/',order_complete, name='order_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)