from dis import disco
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Min, Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from config.settings import STRIPE_SECRET_KEY
from shop.forms import SignUpForm, SignInForm
from shop.models import *
import stripe

# Create your views here.
def index(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    offers = Offer.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all()
    context = {
        "categories":categories,
        "subcategories":subcategories,
        "offers":offers,
        "brands":brands,
        "featured_products": products[:8],
        "recent_products": products.order_by('-id')[:8],
    }
    return render(request, "shop/index.html",context)

def detail(request,pk):
    products = Product.objects.all()
    data = []
    while len(data) < 5:
        from random import randint
        num = randint(1,len(products) - 1)
        if not products[num] in data:
            data.append(products[num])

    context ={
        "product":Product.objects.get(pk=pk),
        "products":data
    }
    return render(request,"shop/detail.html",context)

def likes(request):
    user = request.user  if request.user.is_authenticated else None
    likes = Like.objects.filter(user=user)
    products = [item.product for item in likes]
    context = {
        "products":products
    }
    return render(request, "shop/likes.html",context)

def user_like(request,pk):
    user = request.user  if request.user.is_authenticated else None
    product = Product.objects.get(pk=pk)
    if product:
        liked_products = Like.objects.filter(user=user)
        if product in [item.product for item in liked_products]:
            liked_product = Like.objects.filter(user=user,product=product)
            liked_product.delete()
        else:
            Like.objects.create(user=user,product=product)
    next_page = request.META.get("HTTP_REFERER","home")
    return redirect(next_page)

def basket(request):
    user = request.user if request.user.is_authenticated else None
    products = Basket.objects.filter(user=user)
    total_sale = sum([item.get_total_sale() for item in products])
    total_price = sum([item.get_total_price() for item in products])
    benefit = total_price - total_sale
    total_quantity = sum([item.quantity for item in products])
    coupon_id = request.session.get("coupon_id")
    discount = 0
    coupon = None
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if coupon.discount_type == "percent":
                discount = total_sale * (coupon.discount_value / 100)
            else:
                discount = coupon.discount_value
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    final_total = total_sale - discount

    if request.method == "POST":
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            line_items = [
                {
                    "price_data":{
                        "currency": "usd",
                        "product_data":{
                            "name":"Multishop products"
                        },
                        "unit_amount":int(final_total)
                    },
                    "quantity":1
               }
            ],
            mode="payment",
            success_url = request.build_absolute_uri(reverse("success")),
            cancel_url=request.build_absolute_uri(reverse("cancel"))
        )
        return redirect(session.url)

    context = {
        "products":products,
        "total_sale": total_sale,
        "total_price": total_price,
        "benefit": benefit,
        "total_quantity":total_quantity,
        "coupon": coupon,
        "final_total": final_total

    }
    return render(request,"shop/basket.html",context)

def basket_add(request,pk):
    product = Product.objects.get(pk=pk)
    quantity = request.POST.get('quantity')
    if quantity:
        quantity = int(quantity)
    else:
        quantity = 1
    basket_product, created = Basket.objects.get_or_create(product=product,user=request.user)
    if not created:
        basket_product.quantity += quantity
        basket_product.save()
    else:
        basket_product.quantity = quantity
        basket_product.save()
    next_page = request.META.get("HTTP_REFERER","home")
    return redirect(next_page)


def basket_update(request,pk):
    product = Basket.objects.get(pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "+":
            product.quantity += 1
        elif action == "-":
            if product.quantity > 1:
                product.quantity -= 1
            else:
                product.delete()
                return redirect("basket")
        product.save()
    return redirect("basket")

def basket_delete(request,pk):
    product = Basket.objects.get(pk=pk)
    product.delete()
    return redirect("basket")

def success(request):
    coupon_id = request.session.get('coupon_id')
    if request.user.is_authenticated:
        with transaction.atomic():
            if coupon_id:
                try:
                    coupon = Coupon.objects.select_for_update().get(id=coupon_id)
                    if coupon.is_valid():
                        CouponUsage.objects.create(
                            user = request.user,
                            coupon=coupon
                        )
                        coupon.used_count += 1
                        coupon.save()
                except Coupon.DoesNotExist:
                    pass
                if "coupon_id" in request.session:
                    del request.session['coupon_id']
            Basket.objects.filter(user=request.user).delete()
    return render(request,"shop/success.html")

def cancel(request):
    return render(request,"shop/cancel.html")

def coupon(request):
    user = request.user if request.user.is_authenticated else None
    if request.method == "POST":
        code = request.POST.get('code').upper()
        try:
            coupon = Coupon.objects.get(code__iexact=code)
            if not coupon.is_valid():
                return redirect('basket')
            if CouponUsage.objects.filter(user=user, coupon=coupon).exists():
                return redirect("basket")
            products = Basket.objects.filter(user=user)
            total_sale = sum([item.get_total_sale() for item in products])
            if total_sale < coupon.min_order_price:
                return redirect("basket")
            if coupon.allowed_categories.exists():
                basket_categories = set(item.product.category for item in products)
                allowed = set(coupon.allowed_categories.all())
                if not basket_categories & allowed:
                    return redirect('basket')
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            return redirect("basket")
    return redirect("basket")


def search(request):
    word = request.GET.get('q')
    products = Product.objects.filter(Q(title__icontains=word))
    context = {
        "products":products
    }
    return render(request,"shop/search.html",context)




def contact(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        Contact.objects.create(full_name=full_name,email=email,subject=subject,message=message)
    return render(request, "shop/contact.html")

def category(request,pk):
    cat = Category.objects.get(pk=pk)
    products = Product.objects.filter(category=cat)
    sort_fields = request.GET.get("sort")
    color_fields = request.GET.getlist("color")
    size_fields = request.GET.getlist("size")
    price_fields = request.GET.getlist("price")
    if sort_fields:
        products = products.annotate(price=Min("types__price")).order_by(sort_fields)
    if color_fields:
        products = products.filter(types__color__in=color_fields)
    if size_fields:
        products = products.filter(types__size__in=color_fields)
    if price_fields:
        price_list = {
            "0-100":(0,100),
            "100-200": (100, 200),
            "200-300": (200, 300),
            "300-400": (300, 400),
            "400-500": (400, 500),
        }
        query = Q()
        for key in price_fields:
            if key in price_list:
                low,high = price_list[key]
                query |= Q(types__price__gte=low,types__price__lte=high)
        if query:
            products = products.filter(query).distinct()
    paginator = Paginator(products,9)
    page_number = request.GET.get("page")
    page_list = paginator.get_page(page_number)
    context = {
        "products":page_list
    }
    return  render(request,"shop/category.html",context)
# def signup(request):
#     form = SignUpForm(data=request.POST or None)
#     if request.method == "POST":
#         if form.is_valid():
#             user = form.save()
#             return redirect("signin")
#     context = {
#         "form":form
#     }
#     return render(request, "shop/signup.html", context)
class SignUp(CreateView):
    template_name = "shop/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("signin")

    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)

# def signin(request):
#     form = SignInForm(data=request.POST or None)
#     if request.method == "POST":
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect("home")
#     context = {
#         "form": form
#     }
#     return render(request, "shop/signin.html", context)
class SignIn(LoginView):
    template_name = "shop/signin.html"
    authentication_form = SignInForm
    def get_success_url(self):
        return reverse_lazy("home")

# def signout(request):
#     logout(request)
#     return redirect("signin")
class SignOut(LogoutView):
    next_page = reverse_lazy("signin")

