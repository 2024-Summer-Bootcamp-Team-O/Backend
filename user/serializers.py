from rest_framework import serializers
from user.models import member
from django.contrib.auth.hashers import make_password, check_password


class LoginSerializer(serializers.Serializer):
    member_email = serializers.EmailField()
    member_password = serializers.CharField(write_only=True)

    def validate(self, data):
        member_email = data.get("member_email")
        member_password = data.get("member_password")

        try:
            member_instance = member.objects.get(member_email=member_email)
        except member.DoesNotExist:
            raise serializers.ValidationError("아이디 또는 비밀번호가 일치하지 않습니다.")

        if not check_password(member_password, member_instance.member_password):
            raise serializers.ValidationError("아이디 또는 비밀번호가 일치하지 않습니다.")

        data["member"] = member_instance
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    member_email = serializers.EmailField()
    member_password = serializers.CharField(write_only=True)
    member_name = serializers.CharField(max_length=100)

    class Meta:
        model = member
        fields = ("member_email", "member_password", "member_name")

    def create(self, validated_data):
        new_member = member.objects.create(
            member_email=validated_data["member_email"],
            member_password=make_password(validated_data["member_password"]),
            member_name=validated_data.get("member_name", ""),
        )
        return new_member
