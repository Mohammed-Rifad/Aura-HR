from rest_framework.routers import DefaultRouter

from .views import LeaveBalanceViewSet, LeaveRequestViewSet, LeaveTypeViewSet

app_name = "leave"

router = DefaultRouter()
router.register("types", LeaveTypeViewSet, basename="leave-type")
router.register("balances", LeaveBalanceViewSet, basename="leave-balance")
router.register("requests", LeaveRequestViewSet, basename="leave-request")

urlpatterns = router.urls
