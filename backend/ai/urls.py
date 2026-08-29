from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ChatView, ConversationViewSet, PendingActionViewSet
from .views import ChatStreamView, ChatView, ConversationViewSet, PendingActionViewSet
from .views import (
    AIActivityViewSet,
    ApprovalLogViewSet,
    ChatStreamView,
    ChatView,
    ConversationViewSet,
    PendingActionViewSet,
)
from .views import ChatView, ConversationViewSet

app_name = "ai"

router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversation")
router.register("actions", PendingActionViewSet, basename="pending-action")
router.register("activity", AIActivityViewSet, basename="ai-activity")
router.register("approval-log", ApprovalLogViewSet, basename="ai-approval-log")


urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("chat/stream/", ChatStreamView.as_view(), name="chat-stream"),
] + router.urls
