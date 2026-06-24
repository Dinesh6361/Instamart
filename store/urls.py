from django.urls import path
from . import views

urlpatterns = [
    path('', views.home,name='home'),
    path('register/', views.register, name="register"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name='logout'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/increase/<int:cart_id>/', views.cart_increase_quantity, name='cart_increase_quantity'),
    path('cart/decrease/<int:cart_id>/', views.cart_decrease_quantity, name='cart_decrease_quantity'),
    path('increase/<int:cart_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:cart_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:cart_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('product/<int:product_id>/', views.product_detail,name='product_detail'),
    path('review/<int:product_id>/', views.add_review, name='add_review'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('add-wishlist/<int:product_id>/', views.add_wishlist, name='add_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove-wishlist/<int:wishlist_id>/', views.remove_wishlist, name='remove_wishlist'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('notifications/', views.notifications, name='notifications'),
    path('get-location/<int:order_id>/', views.get_delivery_location, name='get_delivery_location'),
    path("get-location/<int:order_id>/", views.get_location, name="get_location"),
   
]