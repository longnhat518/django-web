from django.contrib import admin
from django.utils.html import mark_safe
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
    list_display = ('id','name', 'price', 'old_price', 'is_featured', 'is_on_sale', 'digital', 'sold_count', 'quantity')
    list_filter = ('is_featured', 'is_on_sale', 'digital')
    search_fields = ('name',)
    list_editable = ('is_featured', 'is_on_sale', 'digital', 'sold_count', 'quantity')
    class Media:
        js = ('app/js/slugify.js',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','customer', 'date_ordered', 'complete', 'transaction_id')
    list_filter = ('complete', 'date_ordered')
    search_fields = ('customer__username', 'transaction_id')
    list_editable = ('complete',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'order', 'quantity', 'date_added')
    list_filter = ('date_added',)
    search_fields = ('product__name', 'order__customer__username')
    list_editable = ('quantity',)

class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "subtitle", "image_preview", "is_active", "order")
    list_editable = ("is_active", "order")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        from django.utils.html import mark_safe

        if obj.imageURL:
            return mark_safe(
                f'<img src="{obj.imageURL}" style="max-height: 100px; border-radius: 5px; border: 1px solid #ccc" />'
            )
        return "Chưa có ảnh"

    image_preview.short_description = "Ảnh xem trước"

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Banner, BannerAdmin)

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'image_preview', 'date_added', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = ('is_published', 'date_added')
    readonly_fields = ('image_preview',)
    class Media:
        js = ('app/js/slugify.js',)

    def image_preview(self, obj):
        from django.utils.html import mark_safe
        if obj.imageURL:
            return mark_safe(f'<img src="{obj.imageURL}" style="max-height: 50px; border-radius: 5px; border: 1px solid #ccc" />')
        return "Chưa có ảnh"
    image_preview.short_description = "Ảnh đại diện"

admin.site.register(News, NewsAdmin)



