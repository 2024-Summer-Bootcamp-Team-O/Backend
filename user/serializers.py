from rest_framework import serializers
from user.models import user
from django.contrib.auth.hashers import make_password, check_password


class LoginSerializer(serializers.Serializer):
    user_email = serializers.EmailField()
    user_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user_email = data.get("user_email")
        user_password = data.get("user_password")

        try:
            user_instance = user.objects.get(user_email=user_email)
        except user.DoesNotExist:
            raise serializers.ValidationError("아이디 또는 비밀번호가 일치하지 않습니다.")

        if not check_password(user_password, user_instance.user_password):
            raise serializers.ValidationError("아이디 또는 비밀번호가 일치하지 않습니다.")

        data["user"] = user_instance
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField()
    user_password = serializers.CharField(write_only=True)
    user_name = serializers.CharField(max_length=100)

    class Meta:
        model = user
        fields = ("user_email", "user_password", "user_name")

    def create(self, validated_data):
        new_user = user.objects.create(
            user_email=validated_data["user_email"],
            user_password=make_password(validated_data["user_password"]),
            user_name=validated_data.get("user_name", ""),
        )
        return new_user
