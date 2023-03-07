from mutagen.mp3 import MP3
import datetime
import os
import openai
from google.cloud import texttospeech
from google.oauth2 import service_account


from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
)

FRAME_SIZE = (1920, 1080)
credentials = service_account.Credentials.from_service_account_file(
    "faceless_youtube/dailyhoriscope-fa3c4c3373db.json"
)

client = texttospeech.TextToSpeechClient(credentials=credentials)


def convert_to_audio(sign, text):
    synthesis_input = texttospeech.SynthesisInput(ssml=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        name="en-US-Neural2-J",
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, pitch=-14.0, speaking_rate=1
    )
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(
        f'{sign}_{datetime.datetime.now().strftime("%Y-%m-%d")}.mp3', "wb"
    ) as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print(
            f'Audio content written to file "{sign}_{datetime.datetime.now().strftime("%Y-%m-%d")}.mp3"'
        )


def generate_horoscope(sign):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [
        {
            "role": "system",
            "content": "You are a professional astrologer",
        },
        {
            "role": "user",
            "content": f"Prompt: 300-500 word daily Astrological and Love Horoscope for {sign} with no pleasantries and mention the astrological sign first. Include small pauses between sentences. create the response in Speech Synthesis Markup Language (SSML) Please make sure to include appropriate SSML tags around the text, such as <speak>, <prosody>, <break>, and <emphasis> tags, as necessary. Do not include any newline characters in the response",
        },
    ]

    # messages =[
    #         {"role": "system", "content": "You are a professional astrologer."},
    #         {
    #             "role": "user",
    #             "content": f"Generate a personalized daily horoscope and love horoscope script for any astrology sign provided, the horoscope is for {datetime.datetime.now().strftime('%Y-%m-%d')} the script must start with the sign and not included any pleasantries.",
    #         },
    #         {
    #             "role": "assistant",
    #             "content": "Provide the astrology sign for which you would like to generate a horoscope.",
    #         },
    #         {"role": "user", "content": f"{sign}"},  # Replace with user's sign
    #     ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def main():
    # TODO: Move all configurations outside of the project
    # TODO: Move the source onto github
    # TODO: Cleanup mp3(s) as they are created
    # TODO: Change the text outcome from Open AI to ssml make line breaks pauses
    # TODO: Dockerize the project
    # TODO: Implement with YoutubeAPI
    signs = [
        "aquarius",
        "pisces",
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
    ]

    for sign in signs:
        horoscope = generate_horoscope(sign)
        convert_to_audio(sign, horoscope)

        video = VideoFileClip(
            f"faceless_youtube/videos/middle.mp4", target_resolution=(1080, 1920)
        )
        intro = VideoFileClip(f"faceless_youtube/videos/intro.mp4")
        outro = VideoFileClip(f"faceless_youtube/videos/outro.mp4")

        audio = AudioFileClip(
            f'{sign}_{datetime.datetime.now().strftime("%Y-%m-%d")}.mp3'
        )
        outputclip = video.set_audio(audio)
        outputclip = outputclip.subclip(0, audio.end)
        # Create the clip then concat the video
        composite_clip = concatenate_videoclips([intro, outputclip, outro])
        composite_clip.write_videofile(
            f'./faceless_youtube/output/{sign}_{datetime.datetime.now().strftime("%Y-%m-%d")}.mp4'
        )
        outputclip.close()
        video.close()


if __name__ == "__main__":
    main()
