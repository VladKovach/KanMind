from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from kanmind_app.models import Board, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "fullname", "password", "repeated_password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        # Check password match
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        return User.objects.create_user(**validated_data)


from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs.get("email"), password=attrs.get("password"))

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer description
    """

    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def validate(self, attrs):
        owner = self.context["request"].user
        title = attrs.get("title")

        if Board.objects.filter(owner=owner, title=title).exists():
            raise serializers.ValidationError(
                {
                    "detail": f"Owner {owner.id} already has a board with title '{title}'."
                }
            )
        return attrs

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="todo").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer description
    """

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"


class BoardDetailSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    # Custom representation for members on output
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Replace plain member IDs with full UserSerializer objects
        if instance.members.exists():
            data["members"] = UserSerializer(instance.members.all(), many=True).data
        return data

    def validate(self, attrs):
        owner = self.context["request"].user
        title = attrs.get("title")

        if title:  # Only validate if title is provided (PATCH might omit it)
            queryset = Board.objects.filter(owner=owner, title=title)

            # Exclude current instance on updates (PUT/PATCH)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "title": f"Owner {owner.id} already has a board with title '{title}'."
                    }
                )

        return attrs

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class EmailFilterSerializer(serializers.Serializer):
    email = serializers.EmailField()
