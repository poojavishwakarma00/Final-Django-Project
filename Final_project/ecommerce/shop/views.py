from django.shortcuts import render, redirect
from .models import Product, Cart
from django.contrib.auth.decorators import login_required

def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {"products": products})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("home")

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, "cart.html", {"cart_items": cart_items})

from .models import Product, Cart, Order, OrderItem
from django.db.models import Sum, F

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if request.method == "POST":
        if not cart_items.exists():
            return render(request, "checkout.html", {"error": "Your cart is empty."})

        # Calculate total
        total = cart_items.aggregate(total=Sum(F("product__price") * F("quantity")))["total"]

        # Create Order
        order = Order.objects.create(user=request.user, total_price=total)

        # Create Order Items
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

        # Clear Cart
        cart_items.delete()

        return render(request, "order_success.html", {"order": order})

    return render(request, "checkout.html", {"cart_items": cart_items})

