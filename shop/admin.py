from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Offer)
admin.site.register(Brand)
admin.site.register(Contact)
admin.site.register(Like)
admin.site.register(Basket)
admin.site.register(Coupon)
admin.site.register(CouponUsage)




class ProductTypeInline(admin.TabularInline):
    model = ProductType
    fk_name = "product"
    extra = 2

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fk_name = "product"
    extra = 2

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','title']
    inlines = [ProductTypeInline, ProductImageInline]

admin.site.register(Product, ProductAdmin)