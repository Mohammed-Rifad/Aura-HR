from django.utils import timezone
from rest_framework import serializers
from users.serializers import UserSerializer
from organizations.models import Department, Designation
from .models import Employee, EmployeeDocument
from .services import create_employee
from django.contrib.auth import get_user_model
from pathlib import Path
from .services import onboard_employee


MAX_DOCUMENT_SIZE = 5 * 1024 * 1024          # 5 MB
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}


User = get_user_model()


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )
    is_expiring_soon = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDocument
        fields = [
            "id",
            "document_type",
            "document_type_display",
            "document_number",
            "file",
            "issue_date",
            "expiry_date",
            "is_expiring_soon",
        ]

    def get_is_expiring_soon(self, obj) -> bool:
        if not obj.expiry_date:
            return False

        return (
            obj.expiry_date - timezone.now().date()
        ).days <= 30

    def validate_file(self, value):
        if value.size > MAX_DOCUMENT_SIZE:
            raise serializers.ValidationError(
                f"File is {value.size // 1024 // 1024} MB. The limit is 5 MB."
            )

        extension = Path(value.name).suffix.lower()
        if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise serializers.ValidationError(
                f"'{extension}' is not an accepted document type."
            )

        return value

    def validate(self, attrs):
        issue = attrs.get("issue_date")
        expiry = attrs.get("expiry_date")
        if issue and expiry and expiry < issue:
            raise serializers.ValidationError(
                {"expiry_date": "Expiry date cannot be before the issue date."}
            )
        return attrs



class DepartmentBriefSerializer(serializers.ModelSerializer):
    """Just enough to fill a dropdown."""

    class Meta:
        model = Department
        fields = ["id", "name", "code"]


class DesignationBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ["id", "title"]


class EmployeeListSerializer(serializers.ModelSerializer):
    """Small payload for the table view."""

    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    designation_title = serializers.CharField(source="designation.title", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "full_name",
            "email",
            "department_name",
            "designation_title",
            "status",
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Everything, for the profile page."""

    user = UserSerializer(read_only=True)
    department = DepartmentBriefSerializer(read_only=True)
    designation = DesignationBriefSerializer(read_only=True)


    manager = EmployeeListSerializer(read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "user",
            "department",
            "designation",
            "manager",
            "date_of_birth",
            "date_of_joining",
            "date_of_exit",
            "employment_type",
            "status",
            "documents",
            "created_at",
            "updated_at",
        ]


class EmployeeWriteSerializer(serializers.ModelSerializer):
    """HR creating or updating someone. Not used for reads."""

        # Account details. Used on create to make the login; ignored on update,
    # because an employee's account is not edited from this form.
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)


    class Meta:
        model = Employee
        fields = [
            "email", "first_name", "last_name", "phone",
            "department", "designation", "manager",
            "date_of_birth", "date_of_joining", "date_of_exit",
            "employment_type", "status",
            "department",
            "designation",
            "manager",
            "date_of_birth",
            "date_of_joining",
            "date_of_exit",
            "employment_type",
            "status",
        ]

    def update(self, instance, validated_data):
        # The user link is permanent. Without this, PATCH fails — the employee's
        # own user is excluded by the queryset above.
        validated_data.pop("user", None)

        validated_data["updated_by"] = self.context["request"].user

        return super().update(instance, validated_data)


    def validate(self, attrs):
        manager = attrs.get("manager")
        if manager and self.instance and manager.pk == self.instance.pk:
            raise serializers.ValidationError(
                {"manager": "An employee cannot be their own manager."}
            )

        joining = attrs.get("date_of_joining") or getattr(
            self.instance, "date_of_joining", None
        )
        exit_date = attrs.get("date_of_exit") or getattr(
    self.instance, "date_of_exit", None
)

        if joining and exit_date and exit_date < joining:
            raise serializers.ValidationError(
                {"date_of_exit": "Exit date cannot be before the joining date."}
            )

        return attrs
    def create(self, validated_data):
        if not validated_data.get("email"):
            raise serializers.ValidationError(
                {"email": "An email address is required to create an employee."}
            )

        return onboard_employee(
            created_by=self.context["request"].user,
            **validated_data,
        )
