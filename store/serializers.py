# File: store/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile

class SignupSerializer(serializers.ModelSerializer):
    # Add first and last name
    first_name    = serializers.CharField(write_only=True)
    last_name     = serializers.CharField(write_only=True)

    # Extra profile fields
    phone_number  = serializers.CharField(write_only=True)
    address_line1 = serializers.CharField(write_only=True)
    address_line2 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    city          = serializers.CharField(write_only=True)
    postal_code   = serializers.CharField(write_only=True)
    country       = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'phone_number', 'address_line1', 'address_line2',
            'city', 'postal_code', 'country',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Pop profile data
        prof_data = {
            'phone_number':  validated_data.pop('phone_number'),
            'address_line1': validated_data.pop('address_line1'),
            'address_line2': validated_data.pop('address_line2', ''),
            'city':          validated_data.pop('city'),
            'postal_code':   validated_data.pop('postal_code'),
            'country':       validated_data.pop('country'),
        }

        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )

        # Create or update profile
        profile, created = Profile.objects.get_or_create(user=user)
        for key, value in prof_data.items():
            setattr(profile, key, value)
        profile.save()

        Token.objects.get_or_create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token    = serializers.CharField(read_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
            
        token, _ = Token.objects.get_or_create(user=user)
        return {'username': user.username, 'token': token.key}