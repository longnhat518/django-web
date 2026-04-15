from itertools import product
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import *
import json


# Create your views here.
def home(request):
    customer = None
    if request.user.is_authenticated:
        customer = getattr(request.user, "customer", None)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0}
    products = Product.objects.all()
    featured_products = Product.objects.filter(is_featured=True)
    sale_products = Product.objects.filter(is_on_sale=True)
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'sale_products': sale_products,
        'items': items,
        'order': order,
        'customer': customer,
    }
    return render(request, "app/home.html", context)

def cart(request):
    customer = None
    if request.user.is_authenticated:
        customer = getattr(request.user, "customer", None)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    context = {'items': items, 'order': order, 'customer': customer}
    return render(request, "app/cart.html", context)

def checkout(request):
    customer = None
    if request.user.is_authenticated:
        customer = getattr(request.user, "customer", None)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0}
    context = {"items": items, "order": order, "customer": customer}
    return render(request, "app/checkout.html", context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity += 1
        product.quantity -= 1
    elif action == 'remove':
        orderItem.quantity -= 1
        product.quantity += 1
    orderItem.save()
    product.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse("Item was added",safe=False)