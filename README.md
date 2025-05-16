# 🎬 YouTube Video Downloader (Ad-Free, Flask-Based)

A clean, fast, and ad-free **YouTube Video Downloader** built using **Python, Flask, and yt-dlp**. This tool allows you to paste any YouTube URL and download videos in your preferred resolution and format, complete with real-time download progress and smart merging of video and audio streams.

---

## 📌 Features

- 🔗 **URL-based YouTube video downloader**
- 🎞️ Lists all available resolutions with video/audio info and file size
- ⚡ **Real-time download progress** (speed, ETA, % complete, status)
- 📁 Auto-merges best video and audio formats (when required)
- 🧵 Multi-threaded architecture for smooth performance
- 🧠 Intelligent fallback for fragment-based downloads
- ❌ 100% ad-free, no redirects, no pop-ups
- 📦 Downloads saved locally in a `/downloads` directory

---

## 🚀 Demo
 
![image](https://github.com/user-attachments/assets/0c64d4d0-407d-461c-8d64-b4b7d949d834)
![screencapture-127-0-0-1-5000-download-process-2025-05-15-20_46_44](https://github.com/user-attachments/assets/96fb9776-de6f-47a8-bfb0-0de42d5a7c78)
![screencapture-127-0-0-1-5000-download-process-2025-05-15-20_46_56](https://github.com/user-attachments/assets/b8e4c00b-7e8b-4a18-b434-3c2aa663ef82)
![screencapture-127-0-0-1-5000-download-complete-2025-05-15-20_47_04](https://github.com/user-attachments/assets/fb095ac9-6370-4a78-9d04-3f010477a69f)


---

## 🛠️ Tech Stack

- **Python 3.x**
- **Flask** – lightweight web framework
- **yt-dlp** – YouTube download backend
- **HTML/CSS** – frontend templates (via `render_template`)
- **JavaScript (AJAX)** – for real-time progress updates
- **Threading** – background download tasks
- **UUID** – session management

---

## 🧪 How It Works

1. Paste a YouTube video link on the homepage.
2. The app fetches all available video/audio formats using `yt-dlp`.
3. Select your preferred resolution & format.
4. The download runs in the background using a thread.
5. Progress is tracked in real-time and displayed to the user.
6. File is saved to the local `downloads/` folder.

---

## 📥 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/youtube-video-downloader.git
cd youtube-video-downloader
````

### 2. Create a Virtual Environment (Optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** You must have `ffmpeg` installed and added to your system PATH for video/audio merging.

### 4. Run the Flask App

```bash
python app.py
```

* Open your browser and go to `http://127.0.0.1:5000/`

---

## 📂 Project Structure

```
youtube-video-downloader/
├── app.py                  # Main Flask app
├── templates/
│   ├── index.html
│   ├── download_process.html
│   ├── download_complete.html
│   └── error.html
├── downloads/              # Video downloads saved here
├── requirements.txt
```

---

## ⚠️ Requirements

* Python 3.7+
* `yt-dlp`
* `flask`
* `ffmpeg` (must be installed separately)

> Use the following command to install ffmpeg:
>
> * **Ubuntu/Debian**: `sudo apt install ffmpeg`
> * **Windows**: [Download from ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

---

## 📦 Dependencies

Flask
yt-dlp
---

## 🌐 Connect

* [LinkedIn](https://www.linkedin.com/in/ravikishan-s-48168033b/)

---

## 💡 Future Improvements

* Add support for playlist downloads
* Show download history
* Dockerize the app for easier deployment
* Add video preview before download

---

## 👤 Author

Developed by **RaviKishan Singh** – a faceless YouTube creator solving real-world problems through code.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---
