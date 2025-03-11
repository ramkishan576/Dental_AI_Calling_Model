from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
#import openai
import uvicorn
import os
import nest_asyncio
from openai import OpenAI
import uuid
client = OpenAI()
import httpx
nest_asyncio.apply()
import time
 
# Initialize FastAPI app
app = FastAPI()
 
# Telnyx and OpenAI API keys
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")  # Ensure these are set in the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
 
# Store conversation history
conversation_history = [
    {"role": "system", "content": "Today you work at Telnyx. Sell Telnyx as best as you can."}
]
 
@app.post("/webhook")
async def telnyx_webhook(request: Request):
    try:
        # Await the json method to parse the incoming JSON data
        incoming_data = await request.json()
 
        # Log the entire incoming payload for debugging
        print(f"Incoming data: {incoming_data}")
 
        # Extract `event_type` and validate its presence
        event_type = incoming_data.get('data', {}).get('event_type')
        if not event_type:
            return JSONResponse(
                content={"status": "error", "message": "'event_type' key is missing"},
                status_code=400
            )
 
        if event_type == 'call.initiated':
            print(f'Event Type : {event_type}')
            print(f'Incomming data keys : {incoming_data.keys()}')
            return answer_call(incoming_data['data']['payload']['call_control_id'])
        # elif event_type == 'call.answered':
        #     print(f'Event Type : {event_type}')
        #     return send_greeting(incoming_data['data']['payload']['call_control_id'])
        elif event_type == 'call.answered':
            print(f'Event Type : {event_type}')
            print("Transcript started ...")
            #return send_greeting(incoming_data['data']['payload']['call_control_id'])
            return start_transcription(incoming_data['data']['payload']['call_control_id'])
        elif event_type == 'call.transcription':
            print(f'Event Type : {event_type}')
            return handle_transcription(incoming_data['data']['payload']['call_control_id'] , incoming_data['data']['payload']['transcription_data']['transcript'])
 
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )
 
# Handler for 'call.initiated' event
async def handle_call_initiated(call_control_id):
    # if not payload:
    #     return JSONResponse(
    #         content={"status": "error", "message": "'payload' is missing or invalid"},
    #         status_code=400
    #     )
 
    # call_control_id = payload.get('call_control_id')
    if not call_control_id:
        return JSONResponse(
            content={"status": "error", "message": "'call_control_id' is missing"},
            status_code=400
        )
 
    # Answer the call
    response = await answer_call(call_control_id)
    return JSONResponse(content=response, status_code=200 if response['status'] == 'answered' else 500)
 
# Handler for 'call.hangup' event
async def handle_call_hangup(call_control_id):
    # if not payload:
    #     return JSONResponse(
    #         content={"status": "error", "message": "'payload' is missing or invalid"},
    #         status_code=400
    #     )
 
    # call_control_id = payload.get('call_control_id')
    if not call_control_id:
        return JSONResponse(
            content={"status": "error", "message": "'call_control_id' is missing"},
            status_code=400
        )
 
    # Process hangup logic here (if needed)
    return JSONResponse(
        content={"status": "success", "message": "Call hangup handled successfully"},
        status_code=200
    )
 
def answer_call(call_control_id):
    url = f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/answer"
    headers = {"Authorization": f"Bearer {TELNYX_API_KEY}"}
    response = requests.post(url, headers=headers)
    return JSONResponse({"status": "answered" , "Message":response.text})
 
def start_transcription(call_control_id):
    url = f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/transcription_start"
    headers = {
    'Content-Type': 'multipart/form-data',
    'Accept': 'application/json',
    'Authorization': f"Bearer {TELNYX_API_KEY}"}
    
    data = {
        "language": "en-US",
        "transcription_engine": "B",
        "transcription_tracks": "inbound"
    }
 
    # payload = {
    #     "language": "en",  # Adjust as needed
    #     "model": "openai/whisper-large-v3-turbo"  # Replace with the correct model name per Telnyx docs
    # }
    response = requests.post(url, json=data, headers=headers)
    print(f"start transdd : {response.text}")
    return JSONResponse({"status": "transcription_started" , "Message":response.text})
 
#conversation_history = [{"role": "system", "content": "Today you work at Telnyx. Sell Telnyx as best as you can."}]
 
def handle_transcription(call_control_id , transcript):
    #transcript = data['payload']['text']
    #conversation_history.append({"role": "user", "content": transcript})
 
    # Send to OpenAI for response
    # completion = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=conversation_history
    #     )
 
    
    # Add AI response to history
    # response_text = completion.choices[0].message
    # print(f'Model response : {response_text}')
    # conversation_history.append({"role": "assistant", "content": response_text})
 
    url = "http://127.0.0.1:8080/v1/msg-servive"
 
    headers = {
        "X-API-KEY": "SK9a64e98330fae2399ff2cbcb5729cd46" , #os.getenv("X-API-KEY") ,#"your_api_key_here",  # Replace with your actual API key
        "Content-Type": "application/json",
    }
    print(headers)
    params = {
        "clinic_id": "6752cdd6cbb054b3e56e01ad" , #os.getenv("CLINIC-ID"),
        "patient_number": "19876543459" , #os.getenv("PHONE-NUMBER"),
        "session_id": "test_session_id112",
    }
    print(params)
    if not transcript:
        return JSONResponse({"status": "no_speech_detected", "message": "No speech detected, waiting for input."})
    print(f"User input message : {transcript}")
    data = {
            "human": transcript,
            }
    try:
        #response = httpx.get(url=url)
        start_time = time.time()
        response = httpx.post(url=url, headers=headers, params=params, json=data)
        end_time = time.time()
        print(f"API call took {end_time - start_time} seconds")
        response.raise_for_status()
        print("API Connected Successfully ...!")
        # Parse the response JSON
        response_data = response.json()
        print(response_data)
 
        # Safely access the model_response from the JSON
        response_text = response_data.get('model_response', 'No response available')
        
        return send_tts_response(call_control_id, response_text)
 
    except httpx.HTTPError as e:
        print(f"Failed to initiate API: {e}")
        return None
    
 
def send_tts_response(call_control_id , text):
    url = f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/speak"
    headers = {"Authorization": f"Bearer {TELNYX_API_KEY}"}
    data = {"payload" : text,
            "stop":"current",
            "voice":"female",
            "language":"en-US",}
    print(f'Greetings : {data}')
    
    # Send the greeting via Telnyx API
    response = requests.post(url, json=data, headers=headers)
 
    print(f"Greeting response : {response}")
    
    if response.status_code == 200:
        print(f'On Greeting : {response.text}')
        return JSONResponse({"status": "greeting_sent", "Message": response.text})
    else:
        print(f'Error on Greeting : {response.status_code}')
        return JSONResponse({"status": "failed", "error": response.text})
 
 
def send_greeting(call_control_id):
    url = f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/speak"
    headers = {"Authorization": f"Bearer {TELNYX_API_KEY}"}
    data = {"payload" : "Hello! Thank you for calling. How can we assist you today?",
            "stop":"current",
            "voice":"female",
            "language":"arb",}
    print(f'Greetings : {data}')
    
    # Send the greeting via Telnyx API
    response = requests.post(url, json=data, headers=headers)
 
    print(f"Greeting response : {response}")
    
    if response.status_code == 200:
        print(f'On Greeting : {response.text}')
        return JSONResponse({"status": "greeting_sent", "Message": response.text})
    else:
        print(f'Error on Greeting : {response.status_code}')
        return JSONResponse({"status": "failed", "error": response.text})
 
 
# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
 