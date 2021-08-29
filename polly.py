from contextlib import closing
from tempfile import gettempdir

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError


class Polly:
    # Section of the AWS credentials file (~/.aws/credentials).
    def __init__(self, profile):
        self.session = Session(profile_name=profile)
        self.polly = self.session.client('polly')

    def convert(self, text):
        try:
            # Request speech synthesis
            response = self.polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId='Joanna', Engine='neural')
        except (BotoCoreError, ClientError) as error:
            # The service returned an error
            return error

        # Access the audio stream from the response
        if 'AudioStream' in response:
            # Closing the stream is important because the service throttles on the number of parallel connections.
            # Use contextlib.closing to ensure the stream object will be closed automatically at the end.
            with closing(response['AudioStream']) as stream:
                # Save to temp file
                output = f'{gettempdir()}/speech.mp3'
                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, 'wb') as file:
                        file.write(stream.read())
                        return output
                except IOError as error:
                    # Could not write to file
                    return error
        else:
            # The response didn't contain audio data
            return 'Could not stream audio'
