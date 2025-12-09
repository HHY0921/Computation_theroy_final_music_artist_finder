# 🎧 LLM Spotify Agent

An intelligent agent designed to assist a Large Language Model (LLM) by providing specific, up-to-date music information via the **Spotify Web API**. This agent acts as a specialized tool for the LLM, enabling it to answer music-related questions accurately.

---

## ✨ Features

* **Top Tracks Lookup:** Retrieve a specified artist's **top 10 most popular tracks** globally.
* **Artist Discovery:** Find the primary artist(s) of a given song name.
* **LLM Integration:** Designed to be easily integrated into any LLM Agent framework (e.g., LangChain, LlamaIndex) as a **tool** or **function**.

---

## 🛠️ Prerequisites

Before running the project, ensure you have the following installed and set up:

1.  **Python 3.8+**
2.  A **Spotify Developer Account**.
3.  A registered Spotify Application to obtain a **Client ID** and **Client Secret**.

### Spotify API Setup

1.  Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2.  Click **"Create an App"** and fill in the details.
3.  Once created, find your **Client ID** and **Client Secret**. You will need these for the next step.

---

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone [https://github.com/yourusername/llm-spotify-agent.git](https://github.com/yourusername/llm-spotify-agent.git)
cd llm-spotify-agent
```

### 2. Create and activate a virtual environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate      # On Windows
```

### 3. Install dependencies
This project uses the spotipy library for interacting with the Spotify API and python-dotenv for environment variable managemen
```bash
pip install -r requirements.txt
```
### 4. Configure Environment Variables
Create a file named .env in the root directory of the project and add your Spotify credentials:

```
# .env file
SPOTIPY_CLIENT_ID="YOUR_SPOTIFY_CLIENT_ID"
SPOTIPY_CLIENT_SECRET="YOUR_SPOTIFY_CLIENT_SECRET"
```
