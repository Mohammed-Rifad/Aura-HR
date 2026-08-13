from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from common.permissions import IsHR, ReadOnly

from .models import Employee
from .serializers import (
    EmployeeDetailSerializer,
    EmployeeDocumentSerializer,
    EmployeeListSerializer,
    EmployeeWriteSerializer,
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Who sees which rows is decided in get_queryset(), not by a permission
    class. Permission classes answer "may you call this endpoint?" — they
    never see the rows.
    """

    # Never used at request time — get_queryset() replaces it entirely. It
    # exists so drf-spectacular and the router can find the model without
    # calling get_queryset(), which needs a real logged-in user.
    
    queryset = Employee.objects.none()
    permission_classes = [IsAuthenticated, IsHR | ReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department", "designation", "status", "employment_type"]
    search_fields = ["employee_id", "user__first_name", "user__last_name", "user__email"]
    ordering_fields = ["employee_id", "date_of_joining", "status"]

    def get_queryset(self):
        user = self.request.user

        qs = Employee.objects.select_related(
            "user",
            "department",
            "designation",
            "manager__user",
            "manager__department",
            "manager__designation",
        )

        Roles = user.Roles

        # Admin and HR can see everyone
        if user.role in (Roles.ADMIN, Roles.HR):
            return qs

        # Manager can see themselves + direct reports
        if user.role == Roles.MANAGER:
            return qs.filter(
                Q(user=user) |
                Q(manager__user=user)
            )

        # Employee can see only themselves
        return qs.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer

        if self.action == "documents":
            return EmployeeDocumentSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return EmployeeWriteSerializer

        
        return EmployeeDetailSerializer

    @action(
    detail=True,
    methods=["get", "post"],
    url_path="documents",
    parser_classes=[MultiPartParser, FormParser],
)
    def documents(self, request, pk=None):

        employee = self.get_object()

        if request.method == "GET":
            queryset = employee.documents.all()

            page = self.paginate_queryset(queryset)

            if page is not None:
                return self.get_paginated_response(
                    self.get_serializer(page, many=True).data
                )

            return Response(
                self.get_serializer(queryset, many=True).data
            )

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save(
            employee=employee,
            created_by=request.user,
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
    # 5. Record who deleted the employee
    def perform_destroy(self, instance):
        instance.delete(
            deleted_by=self.request.user
        )