# File: store/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (
    Category, Product,
    Cart, CartItem,
    Order, OrderItem,
    Profile, ProductImage,
    Announcement
)

# ——— CATEGORY & PRODUCT —————————————————————————————————————————

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display   = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields  = ('name',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('message', 'active')  # shows both fields in list view
    list_filter = ('active',)
    search_fields = ('message',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display   = ('name', 'category', 'price', 'stock', 'available','discount_percentage', 'created_at')
    list_filter    = ('available', 'category', 'created_at')
    list_editable = ('price', 'stock','discount_percentage', 'available')
    prepopulated_fields = {'slug': ('name',)}
    search_fields  = ('name', 'description')

# ——— CART & CART ITEM ————————————————————————————————————————————

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    readonly_fields = ('added_at',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display   = ('user', 'created_at')
    inlines        = [CartItemInline]
    search_fields  = ('user__username',)

# ——— ORDER & ORDER ITEM —————————————————————————————————————————

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ()

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ('id', 'full_name', 'status', 'total_price', 'created_at')
    list_filter    = ('status', 'created_at')
    search_fields  = ('full_name', 'email', 'phone_number')
    inlines        = [OrderItemInline]

# ——— PROFILE ————————————————————————————————————————————————

# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     inlines = [ProductImageInline]  # <-- Add this line
#     list_display   = ('name', 'category', 'price', 'stock', 'available', 'created_at')
#     list_filter    = ('available', 'category', 'created_at')
#     list_editable = ('price', 'stock', 'available')
#     prepopulated_fields = {'slug': ('name',)}
#     search_fields  = ('name', 'description')

# ——— OPTIONAL: Extend the built‑in User admin to show Profile inline ——————

User = get_user_model()

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


# unregister the default User admin, re‑register with the ProfileInline
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    inlines = [ProfileInline]


