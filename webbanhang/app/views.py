from itertools import product
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils.text import slugify
from .models import *
import json
from .utils import cookieCart
from .forms import CreateUserForm

# Create your views here.
def home(request):
    customer = None
    if request.user.is_authenticated:
        customer = request.user
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
    categories = Category.objects.filter(is_sub=False)
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'sale_products': sale_products,
        'banners': banners,
        'items': items,
        'order': order,
        'customer': customer,
        'categories': categories,
    }
    return render(request, "app/home.html", context)

def cart(request):
    customer = None
    if request.user.is_authenticated:
        customer = request.user
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
        customer = request.user
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
    quantity = data.get('quantity', 1)
    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity += quantity
    elif action == 'remove':
        orderItem.quantity -= quantity
    elif action == 'delete':
        orderItem.quantity = 0
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

def search(request):
    customer = None
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
    if request.method == "POST":
        search_query = request.POST.get("search")
        search_slug = slugify(search_query)
        if search_slug:
            products = Product.objects.filter(Q(name__icontains=search_query) | Q(slug__icontains=search_slug))
        else:
            products = Product.objects.filter(name__icontains=search_query)
        context = {'search':search_query,'products': products, 'items': items, 'order': order, 'customer': customer}
        return render(request, "app/search.html", context)

def category(request):
    customer = None
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category','')
    products = None
    if active_category:
        products = Product.objects.filter(category__slug=active_category)
    context = {'products': products, 'categories': categories, 'active_category': active_category, 'items': items, 'order': order, 'customer': customer}
    return render(request, "app/category.html", context)

def detail(request, slug):
    customer = None
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
    
    product = Product.objects.get(slug=slug)
    categories = Category.objects.filter(is_sub=False)
    
    context = {
        'product': product,
        'categories': categories,
        'items': items,
        'order': order,
        'customer': customer
    }
    return render(request, "app/detail.html", context)