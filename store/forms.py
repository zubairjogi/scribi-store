# File: store/forms.py
# store/forms.py
from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=15)
    address_line1 = forms.CharField(max_length=255)
    address_line2 = forms.CharField(required=False)
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)



class ShippingForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)

    # Single address field for full delivery details
    complete_address = forms.CharField(
        max_length=300,
        label="Complete Delivery Address (Include House No, Street, Mohallah, Village/Area)"
    )

    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)