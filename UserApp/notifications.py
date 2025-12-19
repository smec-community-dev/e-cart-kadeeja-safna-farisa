from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.timezone import now
from .models import Notification


def send_notification(user, message, notification_type="system"):
    # 1️⃣ Save notification in DB
    notification = Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        is_read=False
    )

    # 2️⃣ Send via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",   # ✅ MATCHES consumer
        {
            "type": "send_notification",  # ✅ MATCHES method name
            "message": notification.message,  # ✅ STRING
            "created": now().strftime("%d %b %Y %I:%M %p"),  # ✅ REQUIRED
        }
    )
