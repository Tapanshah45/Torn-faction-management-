import json
from channels.generic.websocket import AsyncWebsocketConsumer
class LiveUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'live_updates'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    async def send_update(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))
