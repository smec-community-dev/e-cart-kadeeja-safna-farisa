from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Reviews)
admin.site.register(Cart)
admin.site.register(WishList)
admin.site.register(Orders)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Address)



