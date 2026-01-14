import re

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from kanmind_app.models import Board, Comment, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for read operations.

    Used in nested representations (board owners, task assignees).
    """

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class RegistrationSerializer(serializers.ModelSerializer):
    """User registration with password confirmation and fullname validation.

    Input: email, password, repeated_password, fullname
    Validates: password match, fullname format (First Last exactly)
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "fullname", "password", "repeated_password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        # Password confirmation check
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )

        fullname = attrs["fullname"]
        if not fullname:
            raise serializers.ValidationError(
                {"fullname": "Fullname is required!"}
            )

        # Fullname format: exactly one space between two words, no digits
        stripped = fullname.strip()
        if not re.match(r"^[a-zA-Z]+ [a-zA-Z]+$", stripped):
            raise serializers.ValidationError(
                {"fullname": "Fullname is incorrect!"}
            )

        return attrs

    def create(self, validated_data):
        # Remove confirmation field before user creation
        validated_data.pop("repeated_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Custom login serializer using email/password authentication."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # Attempt authentication with email/password
        user = authenticate(
            email=attrs.get("email"), password=attrs.get("password")
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Store user for view access
        attrs["user"] = user
        return attrs


class BoardListSerializer(serializers.ModelSerializer):
    """Board listing serializer with summary statistics.

    Input: title, members (array of user IDs)
    Output: Includes counts for quick overview
    Prevents duplicate board titles per owner.
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
        """Prevent owner from creating multiple boards with same title."""
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
    """Task operations with dual input/output user representations.

    Input IDs: assignee_id, reviewer_id (write_only)
    Output objects: assignee, reviewer (read_only nested serializers)
    """

    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    created_by = UserSerializer(read_only=True)
    # Nested users for read operations
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "board",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "created_by",
            "comments_count",
        ]
        read_only_fields = ["created_by"]

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskDetailSerializer(TaskSerializer):
    """Extended task serializer for detail views.

    Inherits all TaskSerializer fields + additional read-only fields for updates.
    Prevents board changes after creation.
    """

    class Meta(TaskSerializer.Meta):
        # Inherits all fields from TaskSerializer
        read_only_fields = [
            "board",
            "created_by",
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Detailed board view with nested user representations.

    Output: Full owner/member user objects instead of IDs
    Prevents title conflicts on updates (excludes current instance).
    """

    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)

    def validate(self, attrs):
        """Title validation for updates (PATCH/PUT)."""
        owner = self.context["request"].user
        title = attrs.get("title")

        if title:  # Only validate if title is provided (PATCH might omit it)
            queryset = Board.objects.filter(owner=owner, title=title)

            # Exclude current instance on updates to allow same title
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
        fields = ["id", "title", "owner_data", "members_data"]


class EmailFilterSerializer(serializers.Serializer):
    """Simple serializer for validating email query parameters.

    Used in EmailCheckView for ?email=... queries.
    """

    email = serializers.EmailField()


class CommentSerializer(serializers.ModelSerializer):
    """Task comment serializer.

    Author shown as fullname only.
    Author, task, created_at are read-only.
    """

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content", "task"]
        read_only_fields = ["author", "task", "created_at"]

    def get_author(self, obj):
        """Return author's fullname instead of full user object."""
        return obj.author.fullname
