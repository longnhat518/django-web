from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("register/", views.register, name="register"),
    path("login/", views.loginView, name="login"), 
    path("logout/", views.logoutUser, name="logout"),
    path("search/", views.search, name="search"),
    path("category/", views.category, name="category"),
    path("product/<slug:slug>/", views.detail, name="detail"),
    path("all-product/", views.all_product, name="all_product"),
    path("guarantee/", views.guarantee, name="guarantee"),
    path('about/', views.about, name='about'),
    path('tinymce_upload/', views.tinymce_upload, name='tinymce_upload'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('process_order/', views.process_order, name='process_order'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),
    path('order-history/', views.order_history, name='order_history'),
    path('profile/', views.profile, name='profile'),
]
