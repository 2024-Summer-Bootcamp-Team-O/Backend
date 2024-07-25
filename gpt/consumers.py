import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from gpt.tasks import get_gpt_answer

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group if assigned
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            input_data = json.loads(text_data)
            token = input_data.get("token")
            message = input_data.get("message")
            
            if token:
                # Handle authentication
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                    self.user = await self.get_user(payload['user_id'])
                    
                    if self.user.is_authenticated:
                        self.room_group_name = f"chat_{self.user.id}"
                        # Join the room group
                        await self.channel_layer.group_add(
                            self.room_group_name,
                            self.channel_name
                        )
                    else:
                        await self.close()
                        return
                except (InvalidToken, TokenError):
                    self.user = AnonymousUser()
                    await self.close()
                    return
            
            if message:
                # Handle the message
                if hasattr(self, 'user') and self.user.is_authenticated:
                    get_gpt_answer.delay(message, self.user.email)
                else:
                    await self.close()

        except json.JSONDecodeError:
            # Handle JSON decode errors
            await self.close()

    async def gpt_talk_message(self, event):
        message = event["message"]
        await self.send(
            text_data=json.dumps({"message": message, "type": "gpt_talk_message"})
        )

    async def gpt_answer_message(self, event):
        message = event["message"]
        await self.send(
            text_data=json.dumps({"message": message, "type": "gpt_answer_message"})
        )

    async def gpt_feedback_message(self, event):
        message = event["message"]
        message_type = event["type"]
        await self.send(text_data=json.dumps({"message": message, "type": message_type}))

    async def gpt_audio(self, event):
        audio_chunk = event["audio_chunk"]
        await self.send(text_data=json.dumps({"audio_chunk": audio_chunk, "type": "audio"}))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
