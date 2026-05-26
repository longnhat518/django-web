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

