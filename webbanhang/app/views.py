from itertools import product
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import *
import json
from .utils import cookieCart
from .forms import CreateUserForm

# Create your views here.
def home(request):
    customer = None
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email})
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
    products = Product.objects.all()
    featured_products = Product.objects.filter(is_featured=True)
    sale_products = Product.objects.filter(is_on_sale=True)
    banners = Banner.objects.filter(is_active=True).order_by('order')[:5]
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'sale_products': sale_products,
        'banners': banners,
        'items': items,
        'order': order,
        'customer': customer,
    }
    return render(request, "app/home.html", context)

def cart(request):
    customer = None
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email})
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
    context = {'items': items, 'order': order, 'customer': customer}
    return render(request, "app/cart.html", context)

def checkout(request):
    customer = None
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email})
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
    context = {"items": items, "order": order, "customer": customer}
    return render(request, "app/checkout.html", context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer, created = Customer.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email})
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse("Item was added",safe=False)

def register(request):
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đăng ký thành công! Hãy đăng nhập.')
            return redirect('login')
    context = {'form': form}
    return render(request, "app/register.html", context)

def loginView(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method =="POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác.")
    
    return render(request, "app/login.html")

def logoutUser(request):
    logout(request)
    return redirect("login")