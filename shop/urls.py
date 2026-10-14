from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="home"),
    path("products/<int:pk>/", detail, name="detail"),
    path("contact/", contact, name="contact"),
    path("likes/", likes, name="likes"),
    path("likes/<int:pk>/", user_like, name="like"),
    path("basket/", basket, name="basket"),
    path("basket_add/<int:pk>/", basket_add, name="basket_add"),
    path("basket_update/<int:pk>/", basket_update, name="basket_update"),
    path("basket_delete/<int:pk>/", basket_delete, name="basket_delete"),
    path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),
    path("coupon/", coupon, name="coupon"),
    path("search/", search, name="search"),
    path("category/<int:pk>/", category, name="category"),
    path("signup/", SignUp.as_view(), name="signup"),
    path("signin/", SignIn.as_view(), name="signin"),
    path("signout/", SignOut.as_view(), name="signout"),
]