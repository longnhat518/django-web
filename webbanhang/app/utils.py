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
            cartItems += cart[i]["quantity"]
            product = Product.objects.get(id=i)
            total = product.price * cart[i]["quantity"]
            
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            
            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'old_price':product.old_price,
                    'imageURL':product.imageURL,
                    'format_price':product.format_price,
                    'format_old_price':product.format_old_price,
                    'category':product.category,
                },
                'quantity':cart[i]["quantity"],
                'get_total':total,
                'format_get_total': "{:,.0f}".format(total).replace(',', '.') + '₫'
            }
            items.append(item)
        except:
            # Bỏ qua nếu sản phẩm không tồn tại
            pass
            
    # Thêm format_get_cart_total để template có thể hiển thị như ở authenticated
    def format_money(amount):
        return "{:,.0f}".format(amount).replace(",", ".") + "₫"
    
    order['format_get_cart_total'] = format_money(order['get_cart_total'])
    
    return {'cartItems': cartItems, 'order': order, 'items': items}

