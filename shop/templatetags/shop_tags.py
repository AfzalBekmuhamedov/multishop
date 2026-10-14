from django import template
from ..models import Category, Like,Basket

register = template.Library()

@register.simple_tag()
def get_categories():
    return Category.objects.all()

@register.simple_tag()
def get_likes(user):
    products =  Like.objects.filter(user=user)
    return [item.product for item in products]

@register.simple_tag()
def get_likes_count(user):
    products =  Like.objects.filter(user=user)
    return len([item.product for item in products])

@register.simple_tag()
def get_basket_count(user):
    products =  Basket.objects.filter(user=user)
    return len([item.product for item in products])
