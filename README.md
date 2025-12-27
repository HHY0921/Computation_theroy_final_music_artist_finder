# 🎧 LLM Spotify Agent

An intelligent agent designed to assist a Large Language Model (LLM) by providing specific, up-to-date music information via the **Spotify Web API**. This agent acts as a specialized tool for the LLM, enabling it to answer music-related questions accurately.

---

## Features

* **Top Tracks Lookup:** Retrieve a specified artist's **top 10 most popular tracks** globally.
* **Artist Discovery:** Find the primary artist(s) of a given song name.
* **LLM Integration:** Designed to be easily integrated into any LLM Agent framework (e.g., LangChain, LlamaIndex) as a **tool** or **function**.

---

## Prerequisites

Before running the project, ensure you have the following installed and set up:

1.  A **Spotify Developer Account**.
2.  A registered Spotify Application to obtain a **Client ID** and **Client Secret**.
3.  An **Openweb Acount**

### Spotify API Setup

1.  Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2.  Click **"Create an App"** and fill in the details.
3.  Once created, find your **Client ID** and **Client Secret**. You will need these for the next step.

---

## Installation and Setup

* Add an empty tool inside the open webui (Workspace > Tools > + Create Tool)
* Copy the code from main.py to the tool code and save
* Once saved, look for the "Valves" or "Settings" icon next to your new tool.
* Enter your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET there.
* Start a new chat.
* Click the + (Tools) button and toggle the "Spotify" tool on.

## Example questions

1.  give me top tracks from ... 
2.  find me 5 newest songs from ...
3.  what songs are in the album ...
4.  who made the song ...
5.  find me some sad and slow songs for a rainy day
6.  what’s the release date of these songs