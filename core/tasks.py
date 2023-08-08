from __future__ import absolute_import, unicode_literals
from celery import shared_task, current_task
from celery.utils.log import get_task_logger
import json
import os
import requests
from django.conf import settings
from .models import AudioFile, UserAction, User


logger = get_task_logger(__name__)
ELEVENLABS_API_KEY = settings.ELEVENLABS_API_KEY


@shared_task(name="convert_text_to_audio_task")
def convert_text_to_audio_task(user, text, audio_id):
    user = User.objects.get(id=user)
    CHUNK_SIZE = 1024
    current_task_id = current_task.request.id
    # Perform the conversion using the elevenlabs.io API (implementation not provided)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{audio_id}/stream?optimize_streaming_latency=0"

    payload = json.dumps({
        "text": f"{text}",
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0,
            "style": 0.5,
            "use_speaker_boost": True
        }
    })

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    logger.info(f"User {user} is converting text to audio.")
    response = requests.post(url, headers=headers, data=payload, stream=True)

    if response.status_code != 200:
        return

    logger.info(f"User {user} is converted text to audio.")
    with open(os.path.join(settings.MEDIA_ROOT + f'/audio/{current_task_id}.mp3'), "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    logger.info(f"{current_task_id}.mp3 saved successfully.")

    AudioFile.objects.create(
        user=user,
        text=text,
        audio_url=f'audio/{current_task_id}.mp3',
        audio_id=audio_id
    )
    # Deduct tokens from the user's balance
    user.tokens -= len(text)
    user.save()

    action = f"Converted text to audio: {text}"
    user_action = UserAction(user=user, action=action)
    user_action.save()

    # return current_task_id
