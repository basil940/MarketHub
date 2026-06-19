from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_dashboard(event_type, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'dashboard',
        {
            'type': 'dashboard_update',
            'data': {
                'event': event_type,
                **data
            }
        }
    )