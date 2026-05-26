import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from tinymce.models import HTMLField
# Create your models here.

def image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"app/static/app/images/{filename}"

def banner_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"app/static/app/images/banners/{filename}"

def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"app/static/app/images/avatars/{filename}"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Số điện thoại")
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True, verbose_name="Ảnh đại diện")

    def __str__(self):
        return self.user.username
        
    @property
    def avatarURL(self):
        try:
            url = self.avatar.url
            url = url.replace('\\', '/')
            if '/app/static/' in url:
                url = url.replace('/app/static/', '/static/')
            elif url.startswith('app/static/'):
                url = url.replace('app/static/', '/static/')
        except:
            url = ''
        return url

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.customerprofile.save()
    except:
        pass


class Category(models.Model):
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, null=True, verbose_name="Tên sản phẩm")
    category = models.ManyToManyField(Category, blank=True, verbose_name="Danh mục")
    price = models.FloatField(verbose_name="Giá bán")
    old_price = models.FloatField(null=True, blank=True, verbose_name="Giá gốc (chưa giảm)")
    is_featured = models.BooleanField(default=False, verbose_name="Sản phẩm Best Seller")
    is_on_sale = models.BooleanField(default=False, verbose_name="Sản phẩm đang Sale")
    digital = models.BooleanField(default=False, null=True, blank=False, verbose_name="Sản phẩm Kỹ thuật số (Không ship)")
    sold_count = models.IntegerField(default=0, null=True, blank=True, verbose_name="Đã bán được")
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="Số lượng")
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True, verbose_name="Đường dẫn (Slug)")
    sku = models.CharField(max_length=50, null=True, blank=True, verbose_name="Mã SKU")
    description = HTMLField(null=True, blank=True, verbose_name="Mô tả sản phẩm")
    size_info = models.TextField(null=True, blank=True, verbose_name="Thông tin kích thước")
    material_info = models.TextField(null=True, blank=True, verbose_name="Thông tin chất liệu")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách Sản phẩm"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def category_names(self):
        return ", ".join([c.name for c in self.category.all() if c.name])

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

    @property
    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum([r.rating for r in reviews])
            return round(total / reviews.count(), 1)
        return 0.0

    @property
    def get_review_count(self):
        return self.reviews.count()
        
    @property
    def get_rating_stars(self):
        avg = self.get_average_rating
        full_stars = int(avg)
        half_star = 1 if (avg - full_stars) >= 0.25 else 0
        empty_stars = 5 - full_stars - half_star
        return {
            'full': range(full_stars),
            'half': range(half_star),
            'empty': range(empty_stars)
        }

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
    STATUS_CHOICES = (
        ('chờ xác nhận', 'Chờ xác nhận'),
        ('chuẩn bị hàng', 'Chuẩn bị hàng'),
        ('đang giao', 'Đang giao'),
        ('đã giao', 'Đã giao'),
    )
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, blank=True)
    transaction_id = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='chờ xác nhận', verbose_name='Trạng thái đơn hàng')
    payment_method = models.CharField(max_length=50, null=True, blank=True, verbose_name='Phương thức thanh toán')

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
    variant = models.ForeignKey('ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = self.product.name if self.product else "OrderItem"
        if self.variant:
            attrs = []
            if self.variant.color: attrs.append(self.variant.color)
            if self.variant.size: attrs.append(self.variant.size)
            if attrs:
                name += f" ({' - '.join(attrs)})"
        return name

    @property
    def get_total(self):
        price = self.variant.get_price if self.variant else self.product.price
        total = price * self.quantity
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
            price = self.variant.get_price if self.variant else self.product.price
            old_price = self.product.old_price if self.product.old_price else price
            sale_after_discount = (old_price * self.quantity) - (price * self.quantity)
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

class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, verbose_name="Đường dẫn (Slug)")
    short_description = models.TextField(null=True, blank=True, verbose_name="Mô tả ngắn")
    content = HTMLField(verbose_name="Nội dung bài viết")
    image = models.ImageField(upload_to=image_upload_path, null=True, blank=True, verbose_name="Hình ảnh đại diện")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng")
    is_published = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        verbose_name = "Tin tức"
        verbose_name_plural = "Quản lý Tin tức"
        ordering = ['-date_added']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

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

@receiver(post_delete, sender=News)
def auto_delete_news_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=50, null=True, blank=True, verbose_name="Màu sắc")
    size = models.CharField(max_length=50, null=True, blank=True, verbose_name="Kích thước")
    price = models.FloatField(null=True, blank=True, verbose_name="Giá bán riêng (nếu khác giá gốc)")
    quantity = models.IntegerField(default=0, verbose_name="Số lượng tồn kho")

    def __str__(self):
        attrs = []
        if self.color: attrs.append(f"Màu: {self.color}")
        if self.size: attrs.append(f"Size: {self.size}")
        desc = " - ".join(attrs) if attrs else "Mặc định"
        return f"{self.product.name} ({desc})"

    @property
    def get_price(self):
        if self.price is not None:
            return self.price
        return self.product.price

    @property
    def format_price(self):
        try:
            return "{:,.0f}".format(self.get_price).replace(',', '.') + '₫'
        except:
            return '0₫'

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5, verbose_name="Đánh giá (1-5 sao)")
    comment = models.TextField(verbose_name="Bình luận")
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} sao)"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.user.username} thích {self.product.name}"
