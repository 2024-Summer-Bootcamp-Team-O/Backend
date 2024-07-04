from rest_framework import serializers
from rest_framework.authtoken.admin import User
from user.models import member
from django.contrib.auth.hashers import make_password

from user.models import user


class LoginSerializer(serializers.Serializer):
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'password', 'user_name']
        model = member
        fields = ("member_email", "member_password", "member_name")

    def create(self, validated_data):
        new_member = member.objects.create(
            member_email=validated_data["member_email"],
            member_password=make_password(validated_data["member_password"]),
            member_name=validated_data.get("member_name", ""),
        )
        return new_member
