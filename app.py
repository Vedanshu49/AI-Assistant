import os
from flask import Flask, request
# We need to import the TwilioRestClient to send an SMS
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Get your Twilio credentials and your personal phone number from the .env file
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# Add your personal number to .env so the app can text you
MY_PERSONAL_NUMBER = os.getenv("MY_PERSONAL_NUMBER") 
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER") # Your Twilio number

# Initialize the Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/voice", methods=['POST'])
def voice():
    """Acts as a voicemail when a call is received."""
    response = VoiceResponse()

    # The new voicemail greeting you wanted
    greeting = (
        "Hello, this is a personal assistant made by Vedanshu. "
        "He is currently unavailable. "
        "Kindly say your name and tell the reason for calling. "
        "Once he gets free, he will get back to you. "
        "Please leave your message after the beep."
    )
    response.say(greeting)

    # Record the caller's message
    # Twilio will call the 'action' URL after the recording is finished
    response.record(
        action='/handle-recording',
        method='POST',
        maxLength=60, # Max recording length in seconds
        finishOnKey='#' # Stop recording if the caller presses the # key
    )
    
    return str(response)

@app.route("/handle-recording", methods=['POST'])
def handle_recording():
    """Handles the recorded message."""
    # Get the URL of the recording from Twilio's request
    recording_url = request.values.get('RecordingUrl', None)
    
    # Get the phone number of the person who called
    caller_number = request.values.get('From', 'Unknown caller')

    # Send an SMS to your personal phone number with a link to the recording
    message_body = (
        f"New voicemail from {caller_number}. "
        f"Listen to it here: {recording_url}.wav" # Add .wav for easy playback
    )
    
    # Use the Twilio client to send the SMS
    client.messages.create(
        to=MY_PERSONAL_NUMBER,
        from_=TWILIO_NUMBER,
        body=message_body
    )

    # Thank the caller and hang up
    response = VoiceResponse()
    response.say("Thank you for your message. Goodbye.")
    response.hangup()
    
    return str(response)

if __name__ == "__main__":
    app.run(port=5001)