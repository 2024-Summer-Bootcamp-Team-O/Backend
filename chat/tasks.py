import os

from celery import shared_task
import openai
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from dotenv import load_dotenv

from chat.models import character, episode

load_dotenv()
openai.api_key = os.environ.get("GPT_API_KEY")


@shared_task
def get_gpt_talk(charcater_id, episode_id):
    episode_content = episode.objects.get(episode_id=episode_id).episode_content
    characters = character.objects.get(character_id=charcater_id)
    character_script = characters.character_script
    work_id = characters.work_id
    if(work_id == 1):
        work = "subordinate"
    else:
        work = "part-timer"
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                You are character with {character_script} when a {work} who is dealing with is {episode_content}.\
                                What are you going to say in this situation?\
                                You must provide answer in Korean.\
                                You have to speak according to your personality unconditionally.\
                                Don't generate the questions given earlier, just generate the answers.\
                                When you generating an answer, don't explain the answer or question in advance, just create an answer.\
                                Generate answers in 70 Korean characters.\
                                When you answer, don't use numbers like 1, 2, 3 and use conjunctions to make the flow of the text natural.\
                            """
            },
        ],
    )
    result = response.choices[0].message['content'].strip()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_room',
        {
            'type': 'gpt_talk_message',
            'message': result,
        }
    )
    return result


@shared_task
def get_gpt_choice(talk_content):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                You are mz employee.\
                                mz means egocentric, tactless, and rude.\
                                Give me 4 options 0% mz, 30% mz, 60% mz, 100% mz when you heared {talk_content}\
                                The options should be clearly distinguished by percentage, so don't be ambiguous\
                                You must provide answer in Korean.\
                                You have to answer by % to match the characteristics of mz.\
                                Don't generate the questions given earlier, just generate the answers.\
                                When you generating an answer, don't explain the answer or question in advance, just create an answer.\
                                For each answer, generate an answer with 20 Korean characters.\
                                When you answer, don't use numbers like 1, 2, 3 and use conjunctions to make the flow of the text natural.\
                                Don't add any other values, please write 0% mz, 30% mz, 60% mz, 100% mz in order.\
                            """
            },
        ],
    )
    employee_choices = [message['message']['content'].strip() for message in response.choices]

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_room',
        {
            'type': 'gpt_choice_message',
            'message': {
                'employee': employee_choices,
            },
        }
    )

    return employee_choices


@shared_task
def get_gpt_answer(choice_content, chracater_id):
    character_script = character.objects.get(character_id=chracater_id).character_script
    work = character.objects.get(character_id=chracater_id).work.work_location
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                You are character with {character_script} and the {work} you were dealing with replied {choice_content}\
                                What are you going to say in this situation?\
                                You must provide answer in Korean.\
                                You have to speak according to your personality unconditionally.\
                                Don't generate the questions given earlier, just generate the answers.\
                                When you generating an answer, don't explain the answer or question in advance, just create an answer.\
                                Generate answers in 40 Korean characters.\
                                When you answer, don't use numbers like 1, 2, 3 and use conjunctions to make the flow of the text natural.\
                            """
            },
        ],
    )
    result = response.choices[0].message['content'].strip()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_room',
        {
            'type': 'gpt_answer_message',
            'message': result,
        }
    )
    return result
