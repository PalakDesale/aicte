from django.contrib import admin
from .models import Cook, Dish, Order, OrderItem, UserProxy
from django.contrib.auth.admin import UserAdmin

# Register your models here.
@admin.register(UserProxy)
class UserProxyAdmin(UserAdmin):
    pass

# Custom Admin Site Headers
admin.site.site_header = "HomeCook Connect Administration"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to User & Marketplace Management"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('cost',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'total_cost', 'created_at', 'user')
    list_filter = ('status', 'created_at', 'payment_method', 'payment_status')
    search_fields = ('customer_name', 'customer_phone', 'customer_address')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Cook)
class CookAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'location')
    search_fields = ('name', 'specialty', 'location')

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('title', 'cook', 'price', 'is_available')
    list_filter = ('is_available', 'cook')
    search_fields = ('title', 'description')
