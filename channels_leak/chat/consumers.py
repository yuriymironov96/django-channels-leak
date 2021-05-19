import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer

import tracemalloc
import logging


logger = logging.getLogger("websocket-memory")


from pympler import tracker, summary, muppy
tr = tracker.SummaryTracker()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connect")
        # snapshot = tracemalloc.take_snapshot()
        # top_stats = snapshot.statistics("lineno")
        # top_stats = [
        #     stat for stat in top_stats[:25] if "importlib._bootstrap_external" not in str(stat)
        # ]
        # for stat in top_stats[:25]:
        #     logger.error("[TRACE] " + str(stat))
        from pympler import asizeof

        # print("diff")
        # tr.print_diff()
        # print("total")
        # summary.print_(summary.summarize(muppy.get_objects()))

        # print("ChatConsumer size:")
        # print(asizeof.asized(self, detail=10).format())

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("disconnect")
        # raise StopConsumer

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
