# File: store/urls.py
# from django.urls import path
# from . import views

# app_name = 'store'

# urlpatterns = [
#     path('',              views.home,            name='home'),
#     path('category/<slug:slug>/', views.category_detail, name='category_detail'),
#     path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
#     path('cart/',         views.cart,            name='cart'),
    
# ]
# store/urls.py
from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Product and category views
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Cart functionality
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    
    # Order functionality
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]