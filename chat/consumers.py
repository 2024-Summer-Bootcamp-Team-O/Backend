from channels.generic.websocket import AsyncWebsocketConsumer
import json

from chat.tasks import get_gpt_choice


class ChatConsumer(AsyncWebsocketConsumer):
    count = {
        'feedback': 1
    }

    async def connect(self):
        self.room_group_name = 'chat_room'

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

        # Redis 연결 닫기
        self.redis.close()
        await self.redis.wait_closed()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        message_type = text_data_json.get('message_type')

        if message_type == 'gpt_talk_message':
            await get_gpt_choice(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # WebSocket으로 메시지 전송
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def save_to_redis(self, key, value):
        # Redis에 데이터 저장
        async with self.redis.get() as conn:
            await conn.set(key, json.dumps(value))
