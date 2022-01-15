from rest_framework import serializers
from . import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class UserSerializer(serializers.ModelSerializer):
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = ("email", "password", "tokens")
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "tokens": {"read_only": True, },
        }

    def get_tokens(self, user):
        refresh = MyTokenObtainPairSerializer.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def create(self, validated_data):
        user = models.User.objects._create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            "email",
            "id",
        )
        depth = 1

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        profile_pic = obj.profile_pic.url
        return request.build_absolute_uri(profile_pic)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = models.UserProfile
        fields = "__all__"
        depth = 1

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        profile_pic = obj.profile_pic.url
        return request.build_absolute_uri(profile_pic)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Plans
        exclude = ("id",)


class UserPlanSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()

    class Meta:
        model = models.UserPlans
        exclude = ("id",)
