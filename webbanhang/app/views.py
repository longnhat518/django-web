from django.shortcuts import render
from django.http import HttpResponse
from .models import *


# Create your views here.
def home(request):
    products = Product.objects.all()
    featured_products = Product.objects.filter(is_featured=True)
    sale_products = Product.objects.filter(is_on_sale=True)
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'sale_products': sale_products,
    }
    return render(request, "app/home.html", context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    context = {'items': items, 'order': order}
    return render(request, "app/cart.html", context)

def checkout(request):
    context = {}
    return render(request, "app/checkout.html", context)

def cartlist(request):
    context = {}
    return render(request, "app/cartlist.html", context)
