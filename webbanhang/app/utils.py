import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            parts = str(i).split('_')
            product_id = int(parts[0])
            variant_id = int(parts[1]) if len(parts) > 1 else None
            
            product = Product.objects.get(id=product_id)
            variant = None
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                except ProductVariant.DoesNotExist:
                    pass
            
            price = variant.get_price if variant else product.price
            cartItems += cart[i]["quantity"]
            total = price * cart[i]["quantity"]
            
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            
            product_name = product.name
            if variant:
                attrs = []
                if variant.color: attrs.append(variant.color)
                if variant.size: attrs.append(variant.size)
                if attrs:
                    product_name += f" ({' - '.join(attrs)})"
            
            item = {
                'product':{
                    'id':product.id,
                    'name':product_name,
                    'price':price,
                    'old_price':product.old_price,
                    'imageURL':product.imageURL,
                    'format_price': "{:,.0f}".format(price).replace(',', '.') + '₫',
                    'format_old_price':product.format_old_price,
                    'category_names':product.category_names,
                },
                'variant': variant,
                'quantity':cart[i]["quantity"],
                'get_total':total,
                'format_get_total': "{:,.0f}".format(total).replace(',', '.') + '₫'
            }
            items.append(item)
        except Exception as e:
            print("Lỗi parse cookieCart:", str(e))
            pass
            
    def format_money(amount):
        return "{:,.0f}".format(amount).replace(",", ".") + "₫"
    
    order['format_get_cart_total'] = format_money(order['get_cart_total'])
    
    return {'cartItems': cartItems, 'order': order, 'items': items}

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_telegram_notification(order, shipping_address=None):
    if not getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or not getattr(settings, 'TELEGRAM_CHAT_ID', ''):
        return

    items = order.orderitem_set.all()
    item_list = ""
    for item in items:
        item_list += f"- {item.product.name} x {item.quantity}: {item.get_total:,.0f}đ\n"

    payment_stt = "Đã xác nhận" if order.complete else "Chưa hoàn tất"
    method = "Chuyển khoản" if order.payment_method == "transfer" else "COD"

    msg = (
        f"🚨 <b>CÓ ĐƠN HÀNG MỚI</b> 🚨\n\n"
        f"Mã đơn: #{order.id}\n"
        f"Phương thức: {method}\n"
        f"Trạng thái: {payment_stt}\n"
        f"Tổng tiền: <b>{order.get_cart_total:,.0f}đ</b>\n\n"
        f"<b>🛒 Sản phẩm:</b>\n"
        f"{item_list}\n"
    )

    if shipping_address:
        msg += (
            f"<b>📦 Giao hàng đến:</b>\n"
            f"- SĐT: {shipping_address.mobile}\n"
            f"- Địa chỉ: {shipping_address.address}, {shipping_address.city}\n"
        )

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

def send_order_email(order, customer_email, customer_name, shipping_address=None):
    if not customer_email:
        return
        
    items = order.orderitem_set.all()
    context = {
        'order': order,
        'items': items,
        'customer_name': customer_name,
        'shipping_address': shipping_address
    }
    
    html_content = render_to_string('app/email/order_confirmation.html', context)
    text_content = strip_tags(html_content)
    
    subject = f'Xác nhận đơn hàng #{order.id} từ Web Bán Hàng'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@webbanhang.com')
    
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [customer_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        print(f"Lỗi gửi Email: {e}")
