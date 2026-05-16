from .models import Product, Order, OrderItem, Category, Banner, News, ShippingAddress
from itertools import product
from .utils import cookieCart
from .forms import CreateUserForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import os
import uuid
import json


from django.conf import settings
from django.urls import reverse
from payos import PayOS
from payos.types import CreatePaymentLinkRequest, ItemData
import datetime

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
    news_list = News.objects.filter(is_published=True).order_by('-date_added')[:7]
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'sale_products': sale_products,
        'banners': banners,
        'items': items,
        'order': order,
        'customer': customer,
        'categories': categories,
        'news_list': news_list,
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
    categories = Category.objects.filter(is_sub=False)
    context = {'items': items, 'order': order, 'customer': customer, 'categories': categories}
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
    categories = Category.objects.filter(is_sub=False)
    context = {"items": items, "order": order, "customer": customer, 'categories': categories}
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

def all_product(request):
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
    
    # 1. Search Query
    query = request.GET.get('q', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(slug__icontains=slugify(query)))
        
    # 2. Category Filter
    category_slugs = request.GET.getlist('category')
    if category_slugs:
        products = products.filter(category__slug__in=category_slugs).distinct()
        
    # 3. Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=min_price)
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=max_price)
        
    # 4. Status Filter
    in_stock = request.GET.get('in_stock')
    if in_stock:
        products = products.filter(quantity__gt=0)
        
    is_sale = request.GET.get('is_sale')
    if is_sale:
        products = products.filter(is_on_sale=True)
        
    is_featured = request.GET.get('is_featured')
    if is_featured:
        products = products.filter(is_featured=True)
        
    # 5. Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price', '-id')
    elif sort_by == 'price_desc':
        products = products.order_by('-price', '-id')
    elif sort_by == 'bestseller':
        products = products.order_by('-sold_count', '-id')
    else: # newest
        products = products.order_by('-id')
        
    # 6. Pagination
    paginator = Paginator(products, 12) # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    categories = Category.objects.filter(is_sub=False)
    
    context = {
        'products': page_obj.object_list, # Current items for the page
        'page_obj': page_obj,
        'categories': categories,
        'items': items,
        'order': order,
        'customer': customer,
        
        # Pass back values for preserving filter states in UI
        'query': query,
        'selected_categories': category_slugs,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
        'is_sale': is_sale,
        'is_featured': is_featured,
        'sort_by': sort_by,
    }
    return render(request, "app/all_product.html", context)

def guarantee(request):
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
    
    context = {
        'items': items,
        'order': order,
        'customer': customer,
        'categories': categories
    }
    
    return render(request, "app/guarantee.html", context)

def about(request):
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
    
    context = {
        'items': items,
        'order': order,
        'customer': customer,
        'categories': categories
    }
    
    return render(request, "app/about.html", context)

@csrf_exempt
def tinymce_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        ext = file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        
        # Save to static directory matching the project's logic
        save_dir = os.path.join('app', 'static', 'app', 'images', 'tinymce')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        # URL matching STATIC_URL logic in this project
        file_url = f"/static/app/images/tinymce/{filename}"
        return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def news_list(request):
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
    news = News.objects.filter(is_published=True).order_by('-date_added')
    latest_news = News.objects.filter(is_published=True).order_by('-date_added')[:5]
    
    paginator = Paginator(news, 6) # 6 bài trên 1 trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'items': items,
        'order': order,
        'customer': customer,
        'categories': categories,
        'page_obj': page_obj,
        'latest_news': latest_news,
    }
    return render(request, "app/news_list.html", context)

def news_detail(request, slug):
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
    try:
        news_item = News.objects.get(slug=slug, is_published=True)
    except News.DoesNotExist:
        return redirect("news_list")
        
    latest_news = News.objects.filter(is_published=True).exclude(id=news_item.id).order_by('-date_added')[:5]
    
    context = {
        'items': items,
        'order': order,
        'customer': customer,
        'categories': categories,
        'news_item': news_item,
        'latest_news': latest_news,
    }
    return render(request, "app/news_detail.html", context)

@csrf_exempt
def process_order(request):
    if request.method == 'POST':
        transaction_id = int(datetime.datetime.now().timestamp())
        data = json.loads(request.body)
        
        customer = None
        if request.user.is_authenticated:
            customer = request.user
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            cookieData = cookieCart(request)
            items = cookieData['items']
            order = Order.objects.create(complete=False)
            for item in items:
                try:
                    product = Product.objects.get(id=item['product']['id'])
                    OrderItem.objects.create(
                        product=product,
                        order=order,
                        quantity=item['quantity']
                    )
                except:
                    pass
                
        order.transaction_id = str(transaction_id)
        # Nếu thanh toán chuyển khoản, chưa hoàn tất đơn hàng vội. Nếu COD thì coi như xong bước đặt hàng.
        payment_method = data.get('pay', 'cod')
        order.payment_method = payment_method
        if payment_method == 'cod':
            order.status = 'chuẩn bị hàng'
            order.complete = True
        
        order.save()
        
        ShippingAddress.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            order=order,
            address=data['form'].get('address', ''),
            city=data['form'].get('city', ''),
            mobile=data['form'].get('phone', ''),
        )
        
        if payment_method == 'transfer':
            # Initialize PayOS
            try:
                client = PayOS(
                    client_id=settings.PAYOS_CLIENT_ID,
                    api_key=settings.PAYOS_API_KEY,
                    checksum_key=settings.PAYOS_CHECKSUM_KEY
                )
                
                domain = request.build_absolute_uri('/')[:-1]
                return_url = domain + reverse('payment_success')
                cancel_url = domain + reverse('payment_cancel')
                
                amount = int(order.get_cart_total)
                if amount > 0:
                    # Tạo danh sách ItemData nếu cần (tuỳ chọn)
                    items_data = []
                    for item in order.orderitem_set.all():
                        items_data.append(ItemData(name=item.product.name, quantity=item.quantity, price=int(item.product.price)))

                    payment_data = CreatePaymentLinkRequest(
                        order_code=transaction_id,
                        amount=amount,
                        description=f"Thanh toan DH {order.id}",
                        items=items_data,
                        cancel_url=cancel_url,
                        return_url=return_url,
                    )
                    
                    response = client.payment_requests.create(payment_data=payment_data)
                    return JsonResponse({'checkoutUrl': response.checkout_url})
            except Exception as e:
                print("Lỗi PayOS:", str(e))
                return JsonResponse({'error': str(e)}, status=400)
                
        # For COD and others
        return JsonResponse({'checkoutUrl': reverse('payment_success')})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def payment_success(request):
    customer = None
    if request.user.is_authenticated:
        customer = request.user
        # Khi thành công, nếu có đơn hàng đang chờ thì đánh dấu hoàn tất.
        # Ở môi trường thực tế, việc này nên được làm ở webhook.
        try:
            order = Order.objects.get(customer=customer, complete=False)
            order.complete = True
            order.status = 'chuẩn bị hàng'
            order.save()
        except:
            pass
        # Reset cart info for view
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        items = []
    else:
        # Nếu guest, xóa giỏ hàng từ cookie
        # Xóa giỏ hàng trên trình duyệt bằng cách trả về một response yêu cầu xóa cookie
        pass
    categories = Category.objects.filter(is_sub=False)
    context = {'customer': customer, 'categories': categories}
    response = render(request, "app/payment_success.html", context)
    if not request.user.is_authenticated:
        response.delete_cookie('cart')
    return response

def payment_cancel(request):
    context = {}
    return render(request, "app/payment_cancel.html", context)

def order_history(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    customer = request.user
    # Active cart for navbar
    order_cart, created = Order.objects.get_or_create(customer=customer, complete=False)
    cart_items = order_cart.orderitem_set.all()
    
    # Completed orders
    past_orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_ordered')
    
    categories = Category.objects.filter(is_sub=False)
    
    context = {
        'items': cart_items,
        'order': order_cart,
        'customer': customer,
        'categories': categories,
        'past_orders': past_orders,
    }
    return render(request, "app/order_history.html", context)
