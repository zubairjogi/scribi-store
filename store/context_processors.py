from .models import Cart, Announcement
from django.db import models  # <-- Add this line

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.items.aggregate(total=models.Sum('quantity'))['total'] or 0
        except Cart.DoesNotExist:
            count = 0
    return {'cart_count': count}

def active_announcement(request):
    return {
        'announcement': Announcement.objects.filter(active=True).first()
    }