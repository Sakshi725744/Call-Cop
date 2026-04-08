# CallCop

**Real-time AI-powered phone call fraud detection.**

## Overview

CallCop detects fraudulent phone calls in real time. When an unknown caller contacts a user, a Twilio agent silently joins the call and streams the audio to a backend server. The server transcribes the audio in 10-second chunks and feeds each chunk to a Large Language Model trained to recognize common fraud patterns. If the LLM detects suspicious activity, it pushes an alert to Firebase, which the companion Flutter app picks up instantly — displaying the verdict on screen and reading it aloud via text-to-speech so the user is warned *during* the call.

### Fraud patterns detected

- Impersonation of telecom authorities (DoT / TRAI) threatening to block phone numbers
- SIM box / bypass fraud
- Fake relative impersonation with bogus payment transfers
- One-ring-and-cut (Wangiri) premium-rate scams
- Bank official impersonation requesting OTPs or KYC details

## Architecture

```
┌──────────┐    Twilio Media     ┌──────────────────┐    Firebase RT DB    ┌──────────────┐
│  Caller  │ ──── Stream ──────▶ │  Python Backend  │ ──── push ────────▶ │  Flutter App  │
│  (Phone) │                     │  (Flask + WS)    │                     │  (Mobile)     │
└──────────┘                     └──────┬───────────┘                     └──────┬────────┘
                                        │                                        │
                                  ┌─────▼─────┐                          ┌───────▼───────┐
                                  │  STT API   │                          │  TTS Engine   │
                                  │ (Whisper / │                          │  (on-device)  │
                                  │  Deepgram /│                          └───────────────┘
                                  │  Google)   │
                                  └─────┬──────┘
                                        │ transcript
                                  ┌─────▼──────┐
                                  │  LLM API   │
                                  │ (OpenAI /  │
                                  │  Claude)   │
                                  └────────────┘
```

**Flow:**

1. Twilio streams call audio over a WebSocket to the Flask server.
2. Audio is chunked into 10-second segments and transcribed via a speech-to-text provider.
3. Each transcript is sent to an LLM with a system prompt containing examples of known fraud patterns.
4. The LLM returns a structured response: `Decision` (fraud / not_fraud / need_more_time), `Reasoning`, and a recommended `Action`.
5. The response is pushed to Firebase Realtime Database.
6. The Flutter app listens for changes and immediately surfaces the alert — visually and via text-to-speech.

## Project Structure

```
CallCop-main/
├── app.py                 # Offline audio file processor (batch mode)
├── twilio.py              # Twilio + Google STT WebSocket server
├── twilio_live.py         # Twilio + OpenAI STT live WebSocket server
├── prompt.py              # LLM system prompt with fraud detection examples
├── config.ini             # Configuration file (not committed)
│
├── LLMOps/                # LLM & speech provider wrappers
│   ├── OpenAI.py          # OpenAI GPT (LLM) + Whisper (STT) + TTS handlers
│   ├── Anthropic.py       # Anthropic Claude LLM handler
│   ├── Deepgram.py        # Deepgram Nova-2 STT handler
│   ├── tools.py           # Function-calling tool definitions (OpenAI & Claude formats)
│   └── functions.py       # Tool implementations (weather, news, search, etc.)
│
├── DBOps/
│   └── firebase.py        # Firebase Realtime Database operations
│
└── Flutter App/           # Cross-platform mobile companion app
    ├── lib/
    │   └── main.dart      # App entry point — Firebase listener, TTS, UI
    ├── pubspec.yaml        # Flutter dependencies
    └── ...                 # Platform-specific files (iOS, Android, Web, etc.)
```

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Flutter SDK 3.5+**
- A [Twilio](https://www.twilio.com/) account with a phone number configured for media streams
- An [OpenAI](https://platform.openai.com/) API key (for GPT + Whisper)
- A [Firebase](https://firebase.google.com/) project with Realtime Database enabled
- Firebase Admin SDK service account JSON credentials
- *(Optional)* An [Anthropic](https://www.anthropic.com/) API key for Claude
- *(Optional)* A [Deepgram](https://deepgram.com/) API key for Nova-2 STT
- *(Optional)* A [Google Cloud](https://cloud.google.com/speech-to-text) service account for Google STT

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-org>/CallCop.git
   cd CallCop
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. **Create `config.ini`** in the project root (this file is gitignored):

   ```ini
   [OpenAI]
   api_key = sk-...

   [Models]
   llm = gpt-4o-2024-05-13
   stt = whisper-1

   [Twilio]
   account_sid = AC...
   auth_token = ...

   [Firebase]
   credentials_path = path/to/firebase-adminsdk.json
   database_url = https://<project-id>.firebaseio.com

   [API_Keys]
   openweather_key = ...
   serper_key = ...
   ```

4. **Place your Firebase Admin SDK JSON** at the path specified in `credentials_path`.

5. **Run the live server** (Twilio + OpenAI STT + LLM + Firebase):

   ```bash
   python twilio_live.py
   ```

   Or, to process an audio file offline:

   ```bash
   python app.py
   ```

   The server starts Flask on port `8080` and a WebSocket server on the same port for Twilio media streams.

6. **Expose the server** to the internet (Twilio needs a public URL). Use [ngrok](https://ngrok.com/) or a similar tunnel:

   ```bash
   ngrok http 8080
   ```

   Then configure your Twilio phone number's webhook to point to the ngrok URL.

### Flutter App Setup

1. **Navigate to the Flutter app directory**

   ```bash
   cd "Flutter App"
   ```

2. **Install dependencies**

   ```bash
   flutter pub get
   ```

3. **Configure Firebase** — ensure `GoogleService-Info.plist` (iOS) and `google-services.json` (Android) are in place for your Firebase project.

4. **Run the app**

   ```bash
   flutter run
   ```

   The app connects to Firebase Realtime Database and listens for updates at the `Response` key. When the backend pushes a new LLM response, the app:
   - Changes the background color to indicate status
   - Displays the decision (fraud / not_fraud / need_more_time)
   - Shows reasoning and recommended action
   - Reads the action aloud via text-to-speech

## How It Works

### LLM Fraud Analysis

The system prompt in `prompt.py` instructs the LLM to act as a call analyst. For every 10-second chunk of transcribed audio, the model returns a structured response:

```
Decision: [fraud / not_fraud / need_more_time]

Reasoning: [brief explanation]

Action: [one-line recommendation — prefixed with "Fraud!" if fraud is detected]
```

The prompt includes detailed examples of real-world scam patterns (telecom impersonation, bank official impersonation, Wangiri, etc.) so the model can recognize them in live conversation.

### Supported Providers

| Capability          | Provider Options                          |
| ------------------- | ----------------------------------------- |
| **LLM**             | OpenAI GPT-4o / GPT-4 / GPT-3.5, Anthropic Claude 3.5 Sonnet / Opus / Haiku |
| **Speech-to-Text**  | OpenAI Whisper, Deepgram Nova-2, Google Cloud Speech-to-Text |
| **Text-to-Speech**  | OpenAI TTS (backend), Flutter TTS (mobile app) |
| **Database**        | Firebase Realtime Database                |
| **Call Handling**    | Twilio Programmable Voice + Media Streams |

### Entry Points

| Script             | Description                                                                |
| ------------------ | -------------------------------------------------------------------------- |
| `twilio_live.py`   | Production server — Twilio media stream + OpenAI STT + LLM + Firebase     |
| `twilio.py`        | Alternative server using Google Cloud Speech-to-Text instead of Whisper    |
| `app.py`           | Offline batch processor — feed an audio file, get fraud analysis per chunk |

## Scope & Limitations

**In scope:**
- Real-time fraud detection during live phone calls
- Seamless Twilio integration for call interception and audio streaming
- Multi-provider STT transcription and LLM analysis
- Mobile alerts with visual and audible feedback

**Out of scope:**
- Post-call investigation or forensic analysis
- Multi-lingual support beyond what the STT provider handles
- Fraud detection in non-voice channels (SMS, email)
- Advanced UI beyond the alert interface

## Future Opportunities

- Expand language and dialect support
- Integrate voice biometrics for caller verification
- Ingest latest scam intelligence feeds to keep the LLM prompt current
- Extend to SMS and email fraud detection
- Build a web dashboard for call history and analytics

## License

This project was built as a hackathon prototype
