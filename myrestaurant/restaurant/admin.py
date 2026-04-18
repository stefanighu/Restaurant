from django.contrib import admin

from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Dish)
admin.site.register(MediaFile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)