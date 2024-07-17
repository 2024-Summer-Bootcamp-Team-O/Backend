import os

import redis
from celery import shared_task
import openai
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory

from chat.models import character, episode, voice

from io import BytesIO
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from django.shortcuts import get_object_or_404

memory = ConversationBufferMemory()
load_dotenv()

# 환경 변수에서 API 키를 가져옴.
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ElevenLabs 클라이언트를 초기화.
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

openai.api_key = os.environ.get("GPT_API_KEY")
feedback_count = 1
r = redis.Redis(host="redis", port=6379, db=0)


# 대사 제공과 동시에 선택지 제공
@shared_task
def get_gpt_message(charcater_id, episode_id):
    load_memory()
    memory.chat_memory.messages = []
    episode_content = episode.objects.get(id=episode_id).content
    characters = character.objects.get(id=charcater_id)
    character_script = characters.script
    stream = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                You are character with {character_script} when a subordinate who is dealing with is {episode_content}.\
                                What are you going to say in this situation?\
                                You must provide answer in Korean.\
                                You have to speak according to your personality unconditionally.\
                                Don't generate the questions given earlier, just generate the answers.\
                                When you generating an answer, don't explain the answer or question in advance, just create an answer.\
                                Generate answers in 70 Korean characters.\
                                When you answer, don't use numbers like 1, 2, 3 and use conjunctions to make the flow of the text natural.\
                            """,
            },
        ],
        stream=True,
    )
    if r.exists("episode_id"):
        r.delete("episode_id")
    r.set("episode_id", episode_id)
    if r.exists("talk_content"):
        r.delete("talk_content")
    full_response = ""
    for response in stream:
        if "delta" in response.choices[0] and "content" in response.choices[0]["delta"]:
            result = response.choices[0]["delta"]["content"]
            full_response += result

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "chat_room",
                {
                    "type": "gpt_talk_message",
                    "message": result,
                },
            )
    memory.chat_memory.messages.append({"role": "assistant", "content": full_response})
    r.set("talk_content", full_response.encode("utf-8"))
    conversation_history = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in memory.chat_memory.messages]
    )
    r.set("conversation_history", conversation_history.encode("utf-8"))

    text_to_speech_file(full_response, charcater_id)

    return full_response


# 답변과 동시에 피드백 제공
@shared_task
def get_gpt_answer(user_message):
    load_memory()
    episode_id = r.get("episode_id").decode("utf-8")
    character_id = r.get("character_id").decode("utf-8")
    character_script = character.objects.get(id=character_id).script
    episode_content = episode.objects.get(id=episode_id).content
    memory.chat_memory.messages.append({"role": "user", "content": user_message})
    messages = memory.buffer_as_messages
    stream = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                conversation : {messages}
                                You are character with {character_script}. In this {episode_content}, What would you say after watching this conversation?\
                                You must answer in context of the conversation.\
                                You must provide answer in Korean.\
                                You have to speak according to your personality unconditionally.\
                                Don't generate the questions given earlier, just generate the answers.\
                                When you generating an answer, don't explain the answer or question in advance, just create an answer.\
                                Generate answers in 40 Korean characters.\
                                When you answer, don't use numbers like 1, 2, 3 and use conjunctions to make the flow of the text natural.\
                            """,
            },
        ],
        stream=True,
    )
    full_response = ""
    for response in stream:
        if "delta" in response.choices[0] and "content" in response.choices[0]["delta"]:
            result = response.choices[0]["delta"]["content"].strip()
            full_response += result
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "chat_room",
                {
                    "type": "gpt_answer_message",
                    "message": result,
                },
            )
    memory.chat_memory.messages.append({"role": "assistant", "content": full_response})
    conversation_history = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in memory.chat_memory.messages]
    )
    r.set("conversation_history", conversation_history.encode("utf-8"))

    text_to_speech_file(full_response, character_id)

    return full_response


@shared_task
def get_gpt_feedback():
    global feedback_count
    episode_id = r.get("episode_id").decode("utf-8")
    episode_content = episode.objects.get(id=episode_id).content
    character_id = 6  # 김수미로 고정
    character_script = character.objects.get(id=character_id).script
    messages = memory.buffer_as_messages
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                conversation : {messages}
                                You are character with {character_script}. In {episode_content}, Look at this conversation and give the feedback.\
                                Give me feedback on the answer\
                                You must give feedback only to user's answer.\
                                Feedback means scolding a person for what he or she did well and what he or she didn't do in his or her answer and telling him or her how to say it.\
                                You must provide answer in Korean.\
                                Don't generate the questions given earlier, just generate the answers.\
                                When you generating an answer, don't explain the answer or question in advance, just create an answer.\
                                Generate answers in 50 Korean characters.\
                                When you answer, don't use numbers like 1, 2, 3 and use conjunctions to make the flow of the text natural.\
                            """,
            },
        ],
    )

    result = response.choices[0].message["content"].strip()
    redis_key = f"feedback{feedback_count}"
    r.set(redis_key, result.encode("utf-8"))

    feedback_count += 1

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat_room",
        {
            "type": "gpt_feedback_message",
            "message": result,
        },
    )

    text_to_speech_file(result, character_id)

    return result


@shared_task
def get_gpt_result():
    feedback_keys = r.keys("feedback*")
    feedback_values = [r.get(key).decode("utf-8") for key in feedback_keys]
    feedback_values_str = ", ".join(feedback_values)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""
                                    You're the kind of guy that grandfathers say, "예끼 이놈아 무슨소리냐"\
                                    You must speak in that way.\
                                    You are the one who looks at what the self-centered, tactless and rude mz employee said and points out what went wrong.\
                                    {feedback_values_str}, Look at those feedbacks and write the final feedback.\
                                    Feedback means scolding a person for what he or she did well and what he or she didn't do in his or her answer and telling him or her how to say it.\
                                    You must provide answer in Korean.\
                                    Don't generate the questions given earlier, just generate the answers.\
                                    When you generating an answer, don't explain the answer or question in advance, just create an answer.\
                                    Generate answers in 300 Korean characters.\
                                    When you answer, don't use numbers like 1, 2, 3 and use conjunctions to make the flow of the text natural.\
                                """,
            },
        ],
    )

    result = response.choices[0].message["content"].strip()
    return result


def load_memory():
    history = r.get("conversation_history")
    if history:
        # Redis에서 가져온 문자열을 줄 단위로 분리하고, 각 줄을 메시지 형식으로 변환
        messages = history.decode("utf-8").splitlines()
        formatted_messages = []

        for msg in messages:
            role, content = msg.split(
                ": ", 1
            )  # 첫 번째 부분을 역할로, 나머지를 내용으로
            formatted_messages.append(
                {"role": role.strip(), "content": content.strip()}
            )

        # 메모리에 메시지 추가
        memory.chat_memory.messages.extend(formatted_messages)


@shared_task
def text_to_speech_file(text: str, character_id: int) -> None:
    from base64 import b64encode

    # 해당 캐릭터의 음성세팅을 가져옴
    voice_settings = get_object_or_404(voice, character_id=character_id)

    # 텍스트를 음성으로 변환
    response = client.text_to_speech.convert(
        voice_id=f"{voice_settings.code}",
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=voice_settings.stability,
            similarity_boost=voice_settings.similarity,
            style=voice_settings.style,
            use_speaker_boost=True,
        ),
    )

    # 오디오 데이터를 메모리에 저장하기 위한 BytesIO 객체 생성
    audio_stream = BytesIO()

    # 각 오디오 데이터 청크를 스트림에 씀
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)

    # 스트림 위치를 처음으로 재설정
    audio_stream.seek(0)

    # 오디오 데이터를 base64로 인코딩
    encoded_audio = b64encode(audio_stream.read()).decode("utf-8")

    # 음성 데이터를 WebSocket을 통해 전송
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat_room",
        {
            "type": "gpt_audio",
            "audio_chunk": encoded_audio,
        },
    )
