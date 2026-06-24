from django.urls import path
from . import views

urlpatterns = [
    path("", views.delivery_dashboard, name="delivery_dashboard"),
    path("live/<int:order_id>/", views.delivery_live, name="delivery_live"),
    path("update-location/<int:order_id>/", views.update_delivery_location, name="update_delivery_location"),
    path("verify-otp/<int:order_id>/", views.verify_delivery_otp, name="verify_delivery_otp"),
    path("history/", views.delivery_history, name="delivery_history"),
    path("login/", views.delivery_login, name="delivery_login"),
    path("logout/", views.delivery_logout, name="delivery_logout"),
    path("update-delivery-status/<int:order_id>/<str:status>/",views.update_delivery_status,name="update_delivery_status"),
    path("register/", views.delivery_register, name="delivery_register"),
    path("logout/",views.delivery_logout,name="delivery_logout"),
    path("toggle-availability/",views.toggle_availability,name="toggle_availability"),
]