import json
import logging
import tracemalloc

from channels.generic.websocket import AsyncWebsocketConsumer
from pympler import asizeof
from pympler.classtracker import ClassTracker

logger = logging.getLogger("websocket-memory")
class_tracker = ClassTracker()
counter = 0

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_layer_tracker = False

    async def connect(self):
        global counter
        # snapshot = tracemalloc.take_snapshot()
        # top_stats = snapshot.statistics("lineno")
        # top_stats = [
        #     stat for stat in top_stats[:25] if "importlib._bootstrap_external" not in str(stat)
        # ]
        # for stat in top_stats[:25]:
        #     logger.error("[TRACE] " + str(stat))
        # print("diff")
        if not self.set_layer_tracker:
            class_tracker.track_object(self.channel_layer)
            self.set_layer_tracker = True
        counter += 1
        if counter % 10 == 0:
            print("================: Counter divisible by 10, snapshotting")
            class_tracker.create_snapshot(f'Handled {counter} connections')
        if counter % 50 == 0:
            print("================: Counter divisible by 50, printing stats")
            class_tracker.stats.print_stats()
            class_tracker.stats.print_summary()
            print("================: Done printing tracker stats")
            print(f"ChatConsumer size: {asizeof.asized(self.channel_layer).format()}")
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
        # issue1703: Attempted fix, seems to help, but a dirty solve
        self.channel_layer.receive_buffer.pop(self.channel_name, "")

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
