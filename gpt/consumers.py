from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from gpt.tasks import get_gpt_answer


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_group_name = "chat_room"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        input_data = json.loads(text_data)
        get_gpt_answer.delay(input_data["message"])

    def gpt_talk_message(self, event):
        message = event["message"]
        self.send(
            text_data=json.dumps({"message": message, "type": "gpt_talk_message"})
        )

    def gpt_answer_message(self, event):
        message = event["message"]
        self.send(
            text_data=json.dumps({"message": message, "type": "gpt_answer_message"})
        )

    def gpt_feedback_message(self, event):
        message = event["message"]
        message_type = event["type"]
        self.send(text_data=json.dumps({"message": message, "type": message_type}))

    def gpt_audio(self, event):
        audio_chunk = event["audio_chunk"]
        self.send(text_data=json.dumps({"audio_chunk": audio_chunk, "type": "audio"}))
