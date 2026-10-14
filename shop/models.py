from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self,username, password=None, **kwargs):
        if not username:
            raise ValueError("Username must be fill")
        user = self.model(username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,username,password=None,**kwargs):
        kwargs.setdefault("is_staff",True)
        kwargs.setdefault("is_superuser",True)

        if kwargs.get("is_staff") is not True:
            raise ValueError("Staff status must be True")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser status must be True")

        return self.create_user(username=username,password=password,**kwargs)

class User(AbstractUser):
    COUNTRY_CHOICES = [
        ("Uzbekistan","Uzbekistan"),
        ("Tajikistan","Tajikistan"),
        ("Kazakhistan","Kazakhistan"),
        ("Kyrgyzstan","Kyrgyzstan"),
        ("Turkmenistan","Turkmenistan"),
    ]
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=50)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, default="Uzbekistan")
    city = models.CharField(max_length=50, blank=True, null=True)
    region = models.CharField(max_length=50)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class Category(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class SubCategory(models.Model):
    title = models.CharField(max_length=50)
    info = models.TextField()
    image = models.ImageField(upload_to="images/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"

class Offer(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="images/")
    sale = models.IntegerField()

    def __str__(self):
        return self.title

class Brand(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.title

class Contact(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name

class Product(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    information = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return self.title

    def get_image(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return "https://png.pngtree.com/png-vector/20221125/ourlarge/pngtree-no-image-available-icon-flatvector-illustration-pic-design-profile-vector-png-image_40966566.jpg"
        return "https://png.pngtree.com/png-vector/20221125/ourlarge/pngtree-no-image-available-icon-flatvector-illustration-pic-design-profile-vector-png-image_40966566.jpg"
class ProductType(models.Model):
    SIZE_CHOICES = [
        ("xs","extra small"),
        ("s","small"),
        ("m","medium"),
        ("l","large"),
        ("xl","extra large"),
    ]
    COLOR_CHOICES = [
        ("black","black"),
        ("white","white"),
        ("red","red"),
        ("blue","blue"),
        ("green","green"),
    ]
    size = models.CharField(max_length=15, choices=SIZE_CHOICES, default="m")
    color = models.CharField(max_length=15, choices=COLOR_CHOICES, default="white")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="types")
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sale = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ("product",'size','color')

class ProductImage(models.Model):
    image = models.ImageField(upload_to="images/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

class Basket(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_sale(self):
        if self.product.types.first().sale:
            return self.product.types.first().sale * self.quantity
        return self.product.types.first().price * self.quantity

    def get_total_price(self):
        return self.product.types.first().price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

class Coupon(models.Model):
    DISCOUNT_TYPE = [
        ("percent","Percent"),
        ("amount", "amount"),
    ]
    code = models.CharField(max_length=10, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE, default="percent")
    discount_value = models.DecimalField(max_digits=6, decimal_places=2)
    min_order_price = models.DecimalField(max_digits=6, decimal_places=2)
    max_usage = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    allowed_categories = models.ManyToManyField("shop.Category",blank=True,related_name='coupons')
    active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return (self.active and self.valid_from <= now <= self.valid_to and self.used_count < self.max_usage)

    def __str__(self):
        return self.code

class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','coupon')

    def __str__(self):
        return f"{self.user.email} - {self.coupon.code}"
