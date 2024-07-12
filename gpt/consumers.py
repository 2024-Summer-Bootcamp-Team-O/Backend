# consumers.py
import redis
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from gpt.tasks import get_gpt_answer


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_group_name = 'chat_room'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        input_data = json.loads(text_data)
        get_gpt_answer.delay(input_data['message'])

    def gpt_talk_message(self, event):
        message = event['message']
        message_type = event['type']
        self.send(text_data=json.dumps({
            'message': message,
            'type': message_type
        }))

    def gpt_choice_message(self, event):
        message_type = event['type']
        messages = event['message']['employee']
        employee_choices = {}
        for message in messages:
            choices = message.split('\n')
            for choice in choices:
                mz_split = choice.split('mz:')
                if len(mz_split) > 1:
                    percentage = mz_split[0].strip()
                    employee_choices[percentage] = mz_split[1].strip()

        message = {
            'message': employee_choices,
            'type': type
        }
        self.send(text_data=json.dumps({
            'message': message['message'],
            'type': message_type
        }))

    def gpt_answer_message(self, event):
        message = event['message']
        message_type = event['type']
        self.send(text_data=json.dumps({
            'message': message,
            'type': message_type
        }))

    def gpt_feedback_message(self, event):
        message = event['message']
        message_type = event['type']
        self.send(text_data=json.dumps({
            'message': message,
            'type': message_type
        }))
