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

# Register your models here.
admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(ProductImage)
admin.site.register(Category, CategoryAdmin)


