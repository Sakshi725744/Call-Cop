import configparser
import logging
from datetime import datetime, timezone
from LLMOps.OpenAI import OpenAILLMHandler, OpenAISpeechHandler
from DBOps.firebase import FirebaseOps
from prompt import system_prompt
import io
import time
from pydub import AudioSegment

# Set Log Level
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# Define Config Object
config = configparser.ConfigParser()
config.read('config.ini')

# Read OpenAI API key from config
openai_api_key = config['OpenAI']['api_key']

llm_model = config['Models']['llm']
stt_model = config['Models']['stt']

# Create OpenAI Handlers
llm_handler = OpenAILLMHandler(openai_api_key)

# Create Speech to text handler Handler
speech_to_text_handler = OpenAISpeechHandler(openai_api_key)

# Create Firebase Handler
firebase_handler = FirebaseOps(config['Firebase']['credentials_path'], config['Firebase']['database_url'])

# create messages and insert system prompt
messages = [
    {
        "role": "system",
        "content": [
            {
                "type": "text", 
                "text": system_prompt
            }
        ]
    }
]

def process_audio_file(audio_file_path):
    # Load the audio file
    audio = AudioSegment.from_mp3(audio_file_path)
    
    # Process the audio in 10-second chunks
    chunk_length_ms = 10 * 1000  # 10 seconds in milliseconds
    for i, chunk_start in enumerate(range(0, len(audio), chunk_length_ms)):
        chunk = audio[chunk_start:chunk_start + chunk_length_ms]
        
        # Export the chunk to a temporary file
        buffer = io.BytesIO()
        buffer.name = f"chunk_{i+1}.wav"
        chunk.export(buffer, format="wav")
        buffer.seek(0)
        
        # Transcribe the chunk
        transcription, cost, language = speech_to_text_handler.transcribe_buffer(buffer)

        # if the length of the transcription is less than 10 words, then skip the chunk
        if len(transcription.split()) < 10:
            continue
        
        # Send transcription to LLM handler
        messages.append({"role": "user", "content": f"Chunk {i+1}: {transcription}"})
        response_message, cost, role, model, completion_tokens, prompt_tokens = llm_handler.send_text(
            messages,
            model=llm_model
        )

        # Update Firebase with the LLM response
        # firebase_handler.add_data({
        #     f"CallCop/chunks/{i+1}": {
        #         "transcription": transcription,
        #         "response": response_message,
        #         "time": time.time()
        #     }
        # })
        firebase_handler.update_value(key='Response', value=response_message)
        
        # Add LLM response to messages
        messages.append({"role": role, "content": response_message})
        
        print(f"Chunk {i+1} processed:")
        print(f"Transcription: {transcription}")
        print(f"LLM Response: {response_message}")
        print("----------------------------------")
        print()

# Use the MP3 file
audio_file_path = "/Users/sakshambhutani/PycharmProjects/MachineLearning/Projects/GHack/CallCop_py/debt_collection.wav"
process_audio_file(audio_file_path)