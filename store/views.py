from django.db.models import Avg, Count
from delivery.models import DeliveryBoy

from django.http import HttpResponse
from .models import *
import razorpay,random
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse



def home(request):
    products = Product.objects.all()

    search = request.GET.get("search")
    category = request.GET.get("category")

    if search:
        products = products.filter(name__icontains=search)

    if category:
        products = products.filter(category=category)

    category_names = Product.objects.values_list(
        "category",
        flat=True
    ).distinct()

    categories = []

    for cat in category_names:
        first_product = Product.objects.filter(
            category=cat
        ).first()

        categories.append({
            "name": cat,
            "image": first_product.image_url
        })

    notification_count = 0

    if request.user.is_authenticated:
        notification_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        if request.user.is_authenticated:
            for product in products:
                cart_item = Cart.objects.filter(
                    user=request.user,
                    product=product
                ).first()

                product.quantity = cart_item.quantity if cart_item else 0
                product.cart_id = cart_item.id if cart_item else None

    return render(request, "home.html", {
        "products": products,
        "categories": categories,
        "notification_count": notification_count,
    })
def register(request):

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")

    return render(request, "register.html")

def user_login(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect("home")

    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("home")

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })

@login_required
def increase_quantity(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    item.quantity += 1
    item.save()

    return JsonResponse({
        "quantity": item.quantity
    })


@login_required
def decrease_quantity(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if item.quantity >=0:
        item.quantity -= 1
        item.save()

        return JsonResponse({
            "quantity": item.quantity
        })

    item.delete()

    return JsonResponse({
        "quantity": 0
    })


@login_required
def remove_cart_item(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    item.delete()
    return redirect("cart")

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items:
        return redirect("cart")

    total = sum(item.product.price * item.quantity for item in cart_items)

    discount = 0
    coupon_code = request.GET.get("coupon", "")

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            discount = coupon.discount
        except Coupon.DoesNotExist:
            discount = 0

    final_total = total - discount

    if final_total < 0:
        final_total = 0

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": final_total * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    if request.method == "POST":
        address = request.POST["address"]
        phone = request.POST["phone"]
        payment_method = request.POST["payment_method"]

        delivery_boy = DeliveryBoy.objects.annotate(
            active_orders=Count("order")
        ).order_by("active_orders").first()

        order = Order.objects.create(
            user=request.user,
            total_amount=final_total,
            address=address,
            phone=phone,
            payment_method=payment_method,
            assigned_delivery_boy=delivery_boy,
            delivery_boy=delivery_boy.name if delivery_boy else "Not Assigned",
            payment_status="Paid" if payment_method == "UPI" else "Pending",
            order_status="Placed",
            delivery_otp=str(random.randint(100000, 999999))
        )

        Notification.objects.create(
            user=request.user,
            message=f"Your Order #{order.id} has been placed successfully."
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )

        cart_items.delete()

        user_email = request.user.email

        if user_email:
            send_mail(
                "Instamart Order Placed & Delivery OTP",
                f"""
Hello {request.user.username},

Your Order #{order.id} has been placed successfully.

Total Amount: ₹{order.total_amount}
Payment Method: {order.payment_method}
Order Status: {order.order_status}
Delivery Partner: {order.delivery_boy}

------------------------------------
DELIVERY OTP: {order.delivery_otp}
------------------------------------

Please share this OTP only with the delivery partner.

Thank you for shopping with Instamart.
                """,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )

        return redirect("orders")

    return render(request, "checkout.html", {
        "total": total,
        "discount": discount,
        "final_total": final_total,
        "coupon_code": coupon_code,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"]
    })
@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")

    return render(request, "orders.html", {
        "orders": orders
    })
    

def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    reviews = Review.objects.filter(
        product=product
    )

    avg_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    )[:8]

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "related_products": related_products
        }
    )
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rating = request.POST["rating"]
        comment = request.POST["comment"]

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )

    return redirect("product_detail", product_id=product.id)
@login_required
@login_required
def track_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, "track_order.html", {
        "order": order
    })
@login_required
def add_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("home")


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, "wishlist.html", {"items": items})


@login_required
def remove_wishlist(request, wishlist_id):
    item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    item.delete()
    return redirect("wishlist")
@staff_member_required
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=5)

    total_revenue = 0
    for order in Order.objects.all():
        total_revenue += order.total_amount

    return render(request, "admin_dashboard.html", {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "low_stock_products": low_stock_products,
    })




@staff_member_required
def update_delivery_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.delivery_status = request.POST["delivery_status"]
        order.delivery_boy = request.POST["delivery_boy"]
        order.estimated_time = request.POST["estimated_time"]
        order.save()

    return redirect("delivery_panel")

from reportlab.pdfgen import canvas
from django.http import HttpResponse

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 800, "Swiggy Instamart Invoice")

    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f"Order ID: {order.id}")
    p.drawString(100, 730, f"Customer: {request.user.username}")
    p.drawString(100, 710, f"Phone: {order.phone}")
    p.drawString(100, 690, f"Address: {order.address}")
    p.drawString(100, 670, f"Payment Method: {order.payment_method}")
    p.drawString(100, 650, f"Payment Status: {order.payment_status}")
    p.drawString(100, 630, f"Order Status: {order.order_status}")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 590, "Products")

    y = 560
    items = OrderItem.objects.filter(order=order)

    p.setFont("Helvetica", 12)

    for item in items:
        p.drawString(
            100,
            y,
            f"{item.product_name}  x {item.quantity}  = Rs. {item.price * item.quantity}"
        )
        y -= 25

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y - 20, f"Total Amount: Rs. {order.total_amount}")

    p.showPage()
    p.save()

    return response

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.delivery_status != "Delivered":
        order.order_status = "Cancelled"
        order.delivery_status = "Cancelled"
        order.save()

        user_email = request.user.email

        if user_email:
            send_mail(
                "Instamart Order Cancelled",
                f"Your order #{order.id} has been cancelled successfully.\n\nRefund will be processed if payment was done online.",
                "instamart@example.com",
                [user_email],
                fail_silently=False,
            )

    return redirect("orders")
@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return render(
        request,
        "notifications.html",
        {"notifications": notifications}
    )


@login_required
def get_delivery_location(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return JsonResponse({
        "lat": order.delivery_lat,
        "lng": order.delivery_lng,
        "status": order.delivery_status
    })
@login_required
def get_location(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return JsonResponse({
        "lat": order.delivery_lat,
        "lng": order.delivery_lng,
        "status": order.delivery_status
    })