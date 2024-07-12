from rest_framework import serializers
from user.models import user
from django.contrib.auth.hashers import make_password, check_password


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user_instance = user.objects.get(email=email)
        except user.DoesNotExist:
            raise serializers.ValidationError(
                "아이디 또는 비밀번호가 일치하지 않습니다."
            )

        if not check_password(password, user_instance.password):
            raise serializers.ValidationError(
                "아이디 또는 비밀번호가 일치하지 않습니다."
            )

        data["user"] = user_instance
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=100)

    class Meta:
        model = user
        fields = ("email", "password", "name")

    def create(self, validated_data):
        new_user = user.objects.create(
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            name=validated_data.get("name", ""),
        )
        return new_user
