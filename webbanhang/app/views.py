from .models import Product, Order, OrderItem, Category, Banner, News, ShippingAddress, CustomerProfile, ProductVariant, Review, Wishlist
from itertools import product
from .utils import cookieCart, send_telegram_notification, send_order_email
from .forms import CreateUserForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
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
    quantity = int(data.get('quantity', 1))
    variantId = data.get('variantId')
    
    customer = request.user
    product = Product.objects.get(id=productId)
    
    variant = None
    if variantId:
        try:
            variant = ProductVariant.objects.get(id=variantId)
        except ProductVariant.DoesNotExist:
            pass
            
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product, variant=variant)
    
    if action == 'add':
        orderItem.quantity += quantity
    elif action == 'remove':
        orderItem.quantity -= quantity
    elif action == 'delete':
        orderItem.quantity = 0
        
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
        
    # Get updated cart total and items
    cart_items_count = order.get_cart_items
    cart_total = order.format_get_cart_total
    
    items_list = []
    for item in order.orderitem_set.all():
        variant_title = ""
        if item.variant:
            variant_title = f"Phân loại: {item.variant.color or ''}"
            if item.variant.color and item.variant.size:
                variant_title += f" - {item.variant.size}"
            elif item.variant.size:
                variant_title = f"Phân loại: {item.variant.size}"
                
        items_list.append({
            'product_id': item.product.id,
            'product_name': item.product.name,
            'product_image': item.product.imageURL,
            'product_price': item.product.format_price,
            'product_old_price': item.product.format_old_price if item.product.old_price else "",
            'quantity': item.quantity,
            'variant_title': variant_title,
            'variant_id': item.variant.id if item.variant else None,
            'total': item.format_get_total
        })
        
    return JsonResponse({
        'status': 'success',
        'cart_items_count': cart_items_count,
        'cart_total': cart_total,
        'items': items_list
    })

def get_cart_data(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items_count = order.get_cart_items
        cart_total = order.format_get_cart_total
        
        items_list = []
        for item in items:
            variant_title = ""
            if item.variant:
                variant_title = f"Phân loại: {item.variant.color or ''}"
                if item.variant.color and item.variant.size:
                    variant_title += f" - {item.variant.size}"
                elif item.variant.size:
                    variant_title = f"Phân loại: {item.variant.size}"
            
            items_list.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_image': item.product.imageURL,
                'product_price': item.product.format_price,
                'product_old_price': item.product.format_old_price if item.product.old_price else "",
                'quantity': item.quantity,
                'variant_title': variant_title,
                'variant_id': item.variant.id if item.variant else None,
                'total': item.format_get_total
            })
    else:
        cookieData = cookieCart(request)
        cart_items_count = cookieData['cartItems']
        cart_total = cookieData['order']['format_get_cart_total']
        
        items_list = []
        for item in cookieData['items']:
            variant_title = ""
            if item.get('variant'):
                variant = item['variant']
                variant_title = f"Phân loại: {variant.color or ''}"
                if variant.color and variant.size:
                    variant_title += f" - {variant.size}"
                elif variant.size:
                    variant_title = f"Phân loại: {variant.size}"
                    
            items_list.append({
                'product_id': item['product']['id'],
                'product_name': item['product']['name'],
                'product_image': item['product']['imageURL'],
                'product_price': item['product']['format_price'],
                'product_old_price': item['product']['format_old_price'] or "",
                'quantity': item['quantity'],
                'variant_title': variant_title,
                'variant_id': item['variant'].id if item.get('variant') else None,
                'total': item['format_get_total']
            })
            
    return JsonResponse({
        'status': 'success',
        'cart_items_count': cart_items_count,
        'cart_total': cart_total,
        'items': items_list
    })


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
    
    username = ""
    if request.method =="POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác.")
    
    return render(request, "app/login.html", {"username": username})

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
    in_wishlist = False
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        in_wishlist = Wishlist.objects.filter(user=customer, product__slug=slug).exists()
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
    
    product = Product.objects.get(slug=slug)
    categories = Category.objects.filter(is_sub=False)
    reviews = product.reviews.all().order_by('-date_added')
    variants = product.variants.all()
    colors = product.variants.exclude(color__isnull=True).exclude(color='').values_list('color', flat=True).distinct()
    sizes = product.variants.exclude(size__isnull=True).exclude(size='').values_list('size', flat=True).distinct()
    
    context = {
        'product': product,
        'categories': categories,
        'items': items,
        'order': order,
        'customer': customer,
        'reviews': reviews,
        'variants': variants,
        'colors': colors,
        'sizes': sizes,
        'in_wishlist': in_wishlist,
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
        
        # Phone validation (required)
        if not data.get('form', {}).get('phone', '').strip():
            return JsonResponse({'error': 'Số điện thoại nhận hàng là bắt buộc!'}, status=400)
        
        # Check if cart is empty
        customer = None
        if request.user.is_authenticated:
            customer = request.user
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
        else:
            cookieData = cookieCart(request)
            items = cookieData['items']
            
        if not items:
            return JsonResponse({'error': 'Giỏ hàng của bạn đang trống! Không thể thực hiện đặt hàng.'}, status=400)
            
        # Re-get or create order object
        if request.user.is_authenticated:
            # order already retrieved/created above
            pass
        else:
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
            order.status = 'chờ xác nhận'
            order.complete = True
        
        order.save()
        
        shipping_address = ShippingAddress.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            order=order,
            address=data['form'].get('address', ''),
            city=data['form'].get('city', ''),
            mobile=data['form'].get('phone', ''),
        )
        
        if payment_method == 'cod':
            send_telegram_notification(order, shipping_address)
            customer_name = data['form'].get('name', 'Quý khách')
            customer_email = data['form'].get('email', '')
            if request.user.is_authenticated and request.user.email:
                customer_email = request.user.email
                customer_name = request.user.first_name or request.user.username
            send_order_email(order, customer_email, customer_name, shipping_address)
        
        if payment_method == 'transfer':
            # Check if PayOS is configured, fallback to manual bank transfer if empty
            if not getattr(settings, 'PAYOS_CLIENT_ID', '') or not getattr(settings, 'PAYOS_API_KEY', '') or not getattr(settings, 'PAYOS_CHECKSUM_KEY', ''):
                order.status = 'chờ xác nhận'
                order.complete = True
                order.save()
                return JsonResponse({'checkoutUrl': reverse('payment_success') + f'?payment_method=transfer&order_id={order.id}'})

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
        return JsonResponse({'checkoutUrl': reverse('payment_success') + f'?payment_method={payment_method}&order_id={order.id}'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def payment_success(request):
    customer = None
    if request.user.is_authenticated:
        customer = request.user
        # Ở môi trường thực tế, việc này nên được làm ở webhook.
        try:
            order = Order.objects.get(customer=customer, complete=False)
            order.complete = True
            order.status = 'chuẩn bị hàng'
            order.save()
            
            try:
                shipping_address = order.shippingaddress_set.first()
            except:
                shipping_address = None
                
            send_telegram_notification(order, shipping_address)
            customer_name = customer.first_name or customer.username
            if customer.email:
                send_order_email(order, customer.email, customer_name, shipping_address)
                
        except:
            pass
        # Reset cart info for view
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        items = []
    else:
        # Nếu guest, xóa giỏ hàng từ cookie
        # Xóa giỏ hàng trên trình duyệt bằng cách trả về một response yêu cầu xóa cookie
        pass
    
    order_id = request.GET.get('order_id', '')
    payment_method = request.GET.get('payment_method', '')
    
    order_total = 0
    half_total = 0
    if order_id:
        try:
            order_obj = Order.objects.get(id=order_id)
            order_total = order_obj.get_cart_total
            half_total = order_total * 0.5
        except Order.DoesNotExist:
            pass
            
    format_order_total = "{:,.0f}".format(order_total).replace(',', '.') + '₫'
    format_half_total = "{:,.0f}".format(half_total).replace(',', '.') + '₫'
    
    categories = Category.objects.filter(is_sub=False)
    context = {
        'customer': customer,
        'categories': categories,
        'payment_method': payment_method,
        'order_total': format_order_total,
        'half_total': format_half_total
    }
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

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    categories = Category.objects.filter(is_sub=False)
    
    profile_obj, created = CustomerProfile.objects.get_or_create(user=customer)
    addresses = ShippingAddress.objects.filter(customer=customer).order_by('-date_added')
    
    password_form = PasswordChangeForm(request.user)
    active_tab = request.GET.get('tab', 'profile')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'change_password':
            active_tab = 'password'
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Đổi mật khẩu thành công!')
                return redirect('/profile/?tab=password')
            else:
                for field in password_form:
                    for error in field.errors:
                        messages.error(request, f"{field.label}: {error}")
                for error in password_form.non_field_errors():
                    messages.error(request, error)
        else:
            active_tab = 'profile'
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            avatar = request.FILES.get('avatar')
            
            if not email:
                messages.error(request, 'Email không được để trống.')
            else:
                customer.first_name = first_name
                customer.last_name = last_name
                customer.email = email
                customer.save()
                
                profile_obj.phone = phone
                if avatar:
                    # Clean up old file
                    if profile_obj.avatar:
                        try:
                            if os.path.exists(profile_obj.avatar.path):
                                os.remove(profile_obj.avatar.path)
                        except Exception as e:
                            print("Lỗi xóa avatar cũ:", str(e))
                    profile_obj.avatar = avatar
                profile_obj.save()
                messages.success(request, 'Cập nhật thông tin tài khoản thành công!')
                return redirect('profile')
                
    context = {
        'items': items,
        'order': order,
        'customer': customer,
        'profile': profile_obj,
        'addresses': addresses,
        'categories': categories,
        'password_form': password_form,
        'active_tab': active_tab,
    }
    return render(request, "app/profile.html", context)

def add_review(request, slug):
    if request.method == "POST":
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
        
        if not request.user.is_authenticated:
            if is_ajax:
                return JsonResponse({'status': 'login_required', 'message': 'Bạn cần đăng nhập để gửi đánh giá.'}, status=401)
            messages.error(request, "Bạn cần đăng nhập để gửi đánh giá.")
            return redirect('login')
        
        try:
            product = Product.objects.get(slug=slug)
            
            # Đọc tham số dựa trên Content-Type
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                rating = int(data.get('rating', 5))
                comment = data.get('comment', '').strip()
            else:
                rating = int(request.POST.get('rating', 5))
                comment = request.POST.get('comment', '').strip()
            
            if rating < 1 or rating > 5:
                rating = 5
                
            if not comment:
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': 'Bình luận không được để trống.'}, status=400)
                messages.error(request, "Bình luận không được để trống.")
            else:
                review = Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=rating,
                    comment=comment
                )
                
                if is_ajax:
                    stars_full = len(product.get_rating_stars['full'])
                    stars_half = len(product.get_rating_stars['half'])
                    stars_empty = len(product.get_rating_stars['empty'])
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Cảm ơn bạn đã gửi đánh giá!',
                        'review': {
                            'username': review.user.username,
                            'rating': review.rating,
                            'comment': review.comment,
                            'date_added': review.date_added.strftime("%d/%m/%Y %H:%M")
                        },
                        'average_rating': product.get_average_rating,
                        'review_count': product.get_review_count,
                        'rating_stars': {
                            'full': stars_full,
                            'half': stars_half,
                            'empty': stars_empty
                        }
                    })
                messages.success(request, "Cảm ơn bạn đã gửi đánh giá!")
        except Product.DoesNotExist:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Sản phẩm không tồn tại.'}, status=404)
            messages.error(request, "Sản phẩm không tồn tại.")
        except Exception as e:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            messages.error(request, f"Lỗi: {str(e)}")
            
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)
    return redirect('detail', slug=slug)

def wishlist(request):
    customer = None
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        wishlisted_items = Wishlist.objects.filter(user=customer).select_related('product')
    else:
        return redirect('login')
        
    categories = Category.objects.filter(is_sub=False)
    
    context = {
        'items': items,
        'order': order,
        'customer': customer,
        'categories': categories,
        'wishlist': wishlisted_items
    }
    return render(request, "app/wishlist.html", context)

def toggle_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required', 'message': 'Vui lòng đăng nhập để thực hiện.'}, status=401)
        
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get('productId')
            product = Product.objects.get(id=product_id)
            
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
            
            if not created:
                wishlist_item.delete()
                action = 'removed'
                message = 'Đã xóa khỏi danh sách yêu thích.'
            else:
                action = 'added'
                message = 'Đã thêm vào danh sách yêu thích.'
                
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            return JsonResponse({'status': 'success', 'action': action, 'message': message, 'count': wishlist_count})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sản phẩm không tồn tại.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


