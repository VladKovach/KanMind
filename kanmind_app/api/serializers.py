from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(max_length=150)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"email": "User with this email already exists."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("repeated_password")

        # create user; use email as username or generate something simple
        username = validated_data["email"]  # or any other scheme

        user = User(username=username, **validated_data)
        user.set_password(password)
        user.save()

        return user


class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Invalid email or password."})

        # authenticate by username + password
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError({"email": "Invalid email or password."})

        attrs["user"] = user
        return attrs


# class RegistrationSerializer(serializers.ModelSerializer):
#     repeated_password = serializers.CharField(write_only=True)
#     fullname = serializers.CharField(max_length=150)

#     class Meta:
#         model = User
#         fields = ["fullname", "email", "password", "repeated_password"]
#         extra_kwargs = {
#             "password": {"write_only": True},
#         }

#     def validate(self, attrs):
#         if attrs["password"] != attrs["repeated_password"]:
#             raise serializers.ValidationError("Passwords do not match.")
#         elif User.objects.filter(email=attrs["email"]).exists():
#             raise serializers.ValidationError("User with such email already exists.")
#         elif User.objects.filter(username=attrs["fullname"]).exists():
#             raise serializers.ValidationError("User with such fullname already exists.")
#         return attrs

#     def create(self, validated_data):
#         password = validated_data.pop("password")
#         validated_data.pop("repeated_password")
#         fullname = validated_data.pop("fullname")
#         user = User(**validated_data, username=fullname)
#         user.set_password(password)  # hash password
#         user.save()
#         return user
