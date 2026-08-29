from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsHR, ReadOnly

from .models import Department, Designation
from .serializers import DepartmentSerializer, DesignationSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Reference data. Everyone reads it — the filter dropdowns need it.
    Only HR and Admin change it.

    No scoping: department names are not sensitive, and hiding them would
    break the filter dropdown for the people who need it most.
    """

    queryset = Department.objects.annotate(
        employee_count=Count("employees")
    ).order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsHR | ReadOnly]
    search_fields = ["name", "code"]


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.order_by("title")
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated, IsHR | ReadOnly]
    search_fields = ["title"]
