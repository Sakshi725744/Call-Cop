from deepgram import DeepgramClient, PrerecordedOptions
import logging

class DeepgramSpeechHandler:
    '''
    This class handles the interaction with the OpenAI Speech API.
    '''

    nova_2_price = 0.0043 # $0.0043 per minute
    
    usd_to_inr = 85.00

    def __init__(self, api_key):
        '''
        Parameters:
        - api_key: The OpenAI API key
        '''
        self.api_key = api_key
        self.deepgram_client = DeepgramClient(api_key)

    def estimate_api_cost(self, model, amount):
        '''
        This function estimates the cost of the API call based on the model, input tokens and output tokens.

        Parameters:
        - model (str): Model used for the API call
        
        Returns:
        - float: Cost of the API call (in INR)
        '''
        
        if model == "nova-2":
            cost = (self.nova_2_price/60) * amount * self.usd_to_inr
        
        return cost

    def transcribe(self, audio_file, model="nova-2"):
        '''
        This method transcribes an audio file using the OpenAI API.

        Parameters:
        - audio_file: The name of the audio file
        - model: The model to use
            default: whisper-1

        Returns:
        - transcription: The transcription of the audio file
        - cost: The cost of the API call (In INR)
        - language: The language of the audio file
        '''

        if model=='nova-2':
            with open(audio_file, 'rb') as buffer_data:
                payload = { 'buffer': buffer_data }

                options = PrerecordedOptions(
                    smart_format=True, model="nova-2", language="en-IN"
                )

                response = self.deepgram_client.listen.prerecorded.v('1').transcribe_file(payload, options)
                text = response['results']['channels'][0]['alternatives'][0]['transcript']
                length = response['metadata']['duration']

                cost = self.estimate_api_cost(model, length)

                logging.info(f'Transcription: {text}')

        return text, cost, 'English'