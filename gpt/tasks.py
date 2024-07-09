import os

import redis
from celery import shared_task
import openai
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from dotenv import load_dotenv

from chat.models import character, episode

load_dotenv()
openai.api_key = os.environ.get("GPT_API_KEY")
feedback_count = 1


# 대사 제공과 동시에 선택지 제공
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
    r = redis.Redis(host='redis', port=6379, db=0)
    get_gpt_choice.delay(result, episode_id)
    redis_key = "talk_content"
    if r.exists(redis_key):
        r.delete(redis_key)
    r.set(redis_key, result.encode('utf-8'))

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
def get_gpt_choice(talk_content, episode_id):
    episode_content = episode.objects.get(episode_id=episode_id).episode_content
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                You are mz employee.\
                                mz means egocentric, tactless, and rude.\
                                If {episode_content}, Give me 4 options 0% mz, 30% mz, 60% mz, 100% mz when you heared {talk_content}\
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

# 답변과 동시에 피드백 제공
@shared_task
def get_gpt_answer(choice_content, chracater_id, episode_id, talk_content, mz_percent):
    character_script = character.objects.get(character_id=chracater_id).character_script
    episode_content = episode.objects.get(episode_id=episode_id).episode_content
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                You are character with {character_script}. In this {episode_content}, you said {talk_content}, but the employee you were dealing with answered {choice_content}
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
    get_gpt_feedback.delay(choice_content, episode_id, talk_content, mz_percent)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_room',
        {
            'type': 'gpt_answer_message',
            'message': result,
        }
    )
    return result


@shared_task
def get_gpt_feedback(choice_content, episode_id, talk_content, mz_percent):
    global feedback_count
    episode_content = episode.objects.get(episode_id=episode_id).episode_content
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                You're the kind of guy that grandfathers say, "예끼 이놈아 무슨소리냐"\
                                You must speak in that way.\
                                You are the one who looks at what the self-centered, tactless and rude mz employee said and points out what went wrong.\
                                In {episode_content}, the mz employee who heard {talk_content} said {choice_content}.\
                                Give me feedback on the answer\
                                You must give feedback only to mz employee's answer.\
                                Feedback means scolding a person for what he or she did well and what he or she didn't do in his or her answer and telling him or her how to say it.\
                                You must provide answer in Korean.\
                                Don't generate the questions given earlier, just generate the answers.\
                                When you generating an answer, don't explain the answer or question in advance, just create an answer.\
                                Generate answers in 50 Korean characters.\
                                When you answer, don't use numbers like 1, 2, 3 and use conjunctions to make the flow of the text natural.\
                            """
            },
        ],
    )
    result = response.choices[0].message['content'].strip()
    r = redis.Redis(host='redis', port=6379, db=0)
    redis_key = f"feedback{feedback_count}"
    r.set(redis_key, result.encode('utf-8'))

    if r.exists("mz_percent"):
        existing_value = float(r.get(redis_key))
        count_key = 'count'
        conversation_count = int(r.get(count_key))
        mz_percent = (existing_value * conversation_count + mz_percent) / (conversation_count + 1)

    r.set(redis_key, mz_percent)
    feedback_count += 1

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_room',
        {
            'type': 'gpt_feedback_message',
            'message': result,
        }
    )
    return result
