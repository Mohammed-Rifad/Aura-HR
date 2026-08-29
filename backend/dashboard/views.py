from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import summary


class DashboardView(APIView):
    """
    GET /api/v1/dashboard/

    One request instead of five. Everything is scoped by the caller's role,
    so an employee sees their own numbers and HR sees the company's.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(summary(request.user))
