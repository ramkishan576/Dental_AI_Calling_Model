FastAPI Telnyx Integration

This FastAPI app demonstrates how to integrate with the Telnyx API and OpenAI for handling call events, transcription, and generating responses during a phone call. The system is designed to answer calls, start transcription, process transcriptions, and respond back via Text-to-Speech (TTS) using Telnyx.

Features

Handle Incoming Call Events: Listen for Telnyx call events such as call.initiated, call.answered, and call.transcription.
Transcription Handling: Integrate with Telnyx's transcription service to transcribe the incoming call.
OpenAI Integration: Process transcriptions and generate responses using OpenAI GPT models.
Text-to-Speech: Send generated responses as voice outputs back to the caller via Telnyx.
Requirements

Python 3.8 or higher
FastAPI
Requests
OpenAI API Key
Telnyx API Key
HTTPX (for async HTTP requests)
