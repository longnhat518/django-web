from django.contrib import admin
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_sub', 'sub_category')
    search_fields = ('name',)
    class Media:
        js = ('app/js/slugify.js',)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5  # Hiển thị sẵn 5 ô trống để upload 5 ảnh liền lúc

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'price', 'old_price', 'is_featured', 'is_on_sale', 'digital', 'sold_count', 'quantity')
    list_filter = ('is_featured', 'is_on_sale', 'digital')
    search_fields = ('name',)
    list_editable = ('is_featured', 'is_on_sale', 'digital', 'sold_count', 'quantity')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date_ordered', 'complete', 'transaction_id')
    list_filter = ('complete', 'date_ordered')
    search_fields = ('customer__name', 'transaction_id')
    list_editable = ('complete',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'date_added')
    list_filter = ('date_added',)
    search_fields = ('product__name', 'order__customer__name')
    list_editable = ('quantity',)

# Register your models here.
admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress)
admin.site.register(Category, CategoryAdmin)


