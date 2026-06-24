from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from store.models import *
from delivery.models import *

from datetime import date

def delivery_dashboard(request):

    if "delivery_boy_id" not in request.session:
        return redirect("delivery_login")

    delivery_boy_id = request.session.get("delivery_boy_id")

    delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)

    orders = Order.objects.filter(
        assigned_delivery_boy=delivery_boy
    ).order_by("-created_at")

    delivered_orders = orders.filter(
        delivery_status="Delivered"
    )

    today_orders = delivered_orders.filter(
        created_at__date=date.today()
    )

    total_earnings = delivered_orders.count() * 30
    today_earnings = today_orders.count() * 30

    return render(
        request,
        "delivery_dashboard.html",
        {
            "orders": orders,
            "delivered_orders": delivered_orders.count(),
            "today_orders": today_orders.count(),
            "total_earnings": total_earnings,
            "today_earnings": today_earnings,
            "delivery_boy": delivery_boy,
            "delivery_boy_name": delivery_boy.name,
        }
    )
@staff_member_required
def delivery_live(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "delivery_live.html", {"order": order})


@staff_member_required
def update_delivery_location(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.delivery_lat = request.POST.get("lat")
        order.delivery_lng = request.POST.get("lng")
        order.save()
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"})


@staff_member_required
def verify_delivery_otp(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        entered_otp = request.POST["otp"]

        if entered_otp == order.delivery_otp:
            order.delivery_status = "Delivered"
            order.order_status = "Delivered"
            order.save()
            return redirect("delivery_dashboard")

        return render(request, "verify_otp.html", {
            "order": order,
            "error": "Invalid OTP"
        })

    return render(request, "verify_otp.html", {"order": order})

@staff_member_required
def delivery_history(request):
    orders = Order.objects.filter(
        delivery_status="Delivered"
    ).order_by("-created_at")

    return render(request, "delivery_history.html", {
        "orders": orders
    })



def delivery_login(request):
    error = ""

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            boy = DeliveryBoy.objects.get(email=email, password=password)

            request.session["delivery_boy_id"] = boy.id
            request.session["delivery_boy_name"] = boy.name

            return redirect("delivery_dashboard")

        except DeliveryBoy.DoesNotExist:
            error = "Invalid email or password"

    return render(request, "delivery_login.html", {"error": error})


def delivery_logout(request):
    request.session.flush()
    return redirect("delivery_login")

@login_required
def update_delivery_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)

    allowed_status = [
        "Picked Up",
        "Out For Delivery",
        "Delivered"
    ]

    if status in allowed_status:

        if order.delivery_boy is None:
            order.delivery_boy = request.user

        order.delivery_status = status

        if status == "Delivered":
            order.order_status = "Delivered"
            order.payment_status = "Paid"

        order.save()

    return redirect("delivery_dashboard")

from django.shortcuts import render, redirect
from .models import DeliveryBoy


def delivery_register(request):
    if request.method == "POST":
        name = request.POST["name"]
        phone = request.POST["phone"]
        email = request.POST["email"]
        password = request.POST["password"]

        if DeliveryBoy.objects.filter(email=email).exists():
            return render(request, "delivery_register.html", {
                "error": "Email already registered"
            })

        DeliveryBoy.objects.create(
            name=name,
            phone=phone,
            email=email,
            password=password
        )

        return redirect("delivery_login")

    return render(request, "delivery_register.html")
def delivery_logout(request):
    request.session.flush()
    return redirect("delivery_login")

def toggle_availability(request):
    delivery_boy_id = request.session.get("delivery_boy_id")

    if delivery_boy_id:
        delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)
        delivery_boy.is_available = not delivery_boy.is_available
        delivery_boy.save()

    return redirect("delivery_dashboard")