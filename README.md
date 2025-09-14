# E.V.A – Enhanced Virtual Assistant

EVA (Enhanced Virtual Assistant) is a Python-based personal AI assistant inspired by Jarvis from _Iron Man_.  
It combines wit, charm, and intelligence to help you manage tasks, run automations, and keep you entertained.

---

## ✨ Features

- **Conversational AI** – Helpful, witty, and self-aware dialogue.
- **Productivity Tools** – Calendar, reminders, task tracking, note-taking.
- **Knowledge & Search** – Query APIs, summarize documents, and answer questions.
- **Smart Integrations** – Connect to music, weather, IoT, or code assistants.
- **Error Handling with Humor** – EVA acknowledges mistakes gracefully.

---

## 📂 Project Structure

```

EVA/
├── main.py              # Entry point of the assistant
├── eva/                 # Core EVA package
│   ├── assistant.py     # Core assistant logic
│   ├── tools/           # Tool integrations (calendar, email, etc.)
└── README.md            # Documentation

```

---

## ⚙️ Setup Instructions

E.V.A uses [uv](https://docs.astral.sh/uv/) as its package manager.

### 1. Install uv

If you don’t have it already:

```bash
pip install uv
```

### 2. Create a Virtual Environment

```bash
uv venv
```

Activate it:

- **Linux/macOS**:

  ```bash
  source .venv/bin/activate
  ```

- **Windows (PowerShell)**:

  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

If you add new packages:

```bash
uv add <package-name>
```

---

## 🚀 Running EVA

Simply run the project’s entry point:

```bash
python main.py
```

---

## 🔧 Configuration

EVA can be customized via environment variables or a `.env` file.
Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_api_key_here
```

## Enabling TTS

On your `.env` add the following variable:

```
ENABLE_TTS=True
```

Download a voice sample for `piper-tts`

```sh
python3 -m piper.download_voices en_US-amy-medium
mkdir voices
mv en_US-amy-medium* voices/
```

---

## 🛠 Adding Tools

Tools are located in `eva/tools/`. Each tool is a Python module exposing a function EVA can call.
Example structure:

```python
# eva/tools/weather.py
def get_weather(city: str) -> str:
    # Call API and return weather data
    return f"Currently sunny in {city}, 26°C"
```

Register the tool in `assistant.py` to make EVA aware of it.

---

## 🤖 Example Interaction

```text
User: EVA, what’s on my agenda today?
EVA: Checking your calendar… You have a 10 AM meeting and, dare I say, a dangerously low number of coffee breaks scheduled.
```

---

## 📌 Roadmap

- [ ] Add voice support (TTS/STT).
- [ ] Expand tool library (email, system monitoring, IoT).
- [ ] GUI dashboard.
- [ ] Long-term memory with vector database.

---

## 🧑‍💻 Contributing

Contributions are welcome! Fork the repo, create a feature branch, and submit a PR.

---

## 📜 License

MIT License. Use EVA freely, but give credit where it’s due.
