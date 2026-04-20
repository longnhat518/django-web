import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
# Create your models here.

def image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"app/static/app/images/{filename}"

def banner_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"app/static/app/images/banners/{filename}"

class Category(models.Model):
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, null=True, verbose_name="Tên sản phẩm")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh mục")
    price = models.FloatField(verbose_name="Giá bán")
    old_price = models.FloatField(null=True, blank=True, verbose_name="Giá gốc (chưa giảm)")
    is_featured = models.BooleanField(default=False, verbose_name="Sản phẩm Best Seller")
    is_on_sale = models.BooleanField(default=False, verbose_name="Sản phẩm đang Sale")
    digital = models.BooleanField(default=False, null=True, blank=False, verbose_name="Sản phẩm Kỹ thuật số (Không ship)")
    sold_count = models.IntegerField(default=0, null=True, blank=True, verbose_name="Đã bán được")
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="Số lượng")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách Sản phẩm"

    def __str__(self):
        return self.name

    @property
    def short_name(self):
        return self.name[:40] + "..."
    @property
    def discount_percentage(self):
        try:
            if self.old_price:
                return int(((self.old_price - self.price) / self.old_price) * 100)
            return 0
        except:
            return 0

    @property
    def format_price(self):
        try:
            return "{:,.0f}".format(self.price).replace(',', '.') + '₫'
        except:
            return '0₫'
            
    @property
    def format_old_price(self):
        try:
            if self.old_price:
                return "{:,.0f}".format(self.old_price).replace(',', '.') + '₫'
            return ''
        except:
            return ''


    @property
    def imageURL(self):
        images = self.images.all()
        if images.exists():
            return images.first().imageURL
        return ''
    
    @property
    def hover_imageURL(self):
        images = self.images.all()
        if images.count() > 1:
            return images[1].imageURL
        return self.imageURL

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=image_upload_path, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} Image"
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
            url = url.replace('\\', '/')
            if '/app/static/' in url:
                url = url.replace('/app/static/', '/static/')
            elif url.startswith('app/static/'):
                url = url.replace('app/static/', '/static/')
        except:
            url = ''
        return url

@receiver(post_delete, sender=ProductImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, blank=True)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def format_get_cart_total(self):
        try:
            return "{:,.0f}".format(self.get_cart_total).replace(',', '.') + '₫'
        except:
            return '0₫'

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product and i.product.digital == False:
                shipping = True
        return shipping
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name if self.product else "OrderItem"

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    @property
    def format_get_total(self):
        try:
            return "{:,.0f}".format(self.get_total).replace(',', '.') + '₫'
        except:
            return '0₫'

    @property
    def sale_after_discount(self):
        try:
            sale_after_discount = (self.product.old_price * self.quantity) - (self.product.price * self.quantity)
            return "{:,.0f}".format(sale_after_discount).replace(",", ".") + "₫"
        except:
            return '0₫'

class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

class Banner(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name="Tiêu đề nhỏ (h2)")
    subtitle = models.CharField(max_length=200, null=True, blank=True, verbose_name="Tiêu đề chính (h1)")
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name="Mô tả (p)")
    image = models.ImageField(upload_to=banner_upload_path, null=True, blank=True, verbose_name="Hình nền Banner")
    button_text = models.CharField(max_length=50, default="Xem chi tiết", verbose_name="Chữ nút bấm")
    button_link = models.CharField(max_length=200, default="#", verbose_name="Link nút bấm")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Quản lý Banner"
        ordering = ['order', '-id']

    def __str__(self):
        return str(self.subtitle) if self.subtitle else "Banner"
        
    @property
    def imageURL(self):
        try:
            url = self.image.url
            url = url.replace('\\', '/')
            if '/app/static/' in url:
                url = url.replace('/app/static/', '/static/')
            elif url.startswith('app/static/'):
                url = url.replace('app/static/', '/static/')
        except:
            url = ''
        return url

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.is_active:
            # Kiểm tra xem nếu thêm banner này thì có vượt quá 5 không
            active_banners = Banner.objects.filter(is_active=True)
            if self.pk:
                active_banners = active_banners.exclude(pk=self.pk)
            if active_banners.count() >= 5:
                raise ValidationError("Chỉ được phép thiết lập tối đa 5 Banner được hiển thị (is_active=True).")

@receiver(post_delete, sender=Banner)
def auto_delete_banner_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
