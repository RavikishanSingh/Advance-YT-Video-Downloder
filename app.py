from flask import Flask, render_template, request, Response, jsonify
import yt_dlp
import os
import queue
import threading
import math
import json
import time
import uuid

app = Flask(__name__)
# Global dictionary to store download progress for each session
download_progress = {}

def format_size(bytes):
    if bytes is None:
        return 'Unknown size'
    size = float(bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def process_formats(formats):
    processed_formats = []
    video_formats = []
    
    # First collect all formats with both video and audio
    for f in formats:
        format_id = f.get('format_id', '')
        height = f.get('height')
        filesize = f.get('filesize') or f.get('filesize_approx')
        has_audio = f.get('acodec') != 'none'
        has_video = f.get('vcodec') != 'none'
        fps = f.get('fps', '')
        
        if height and has_video:
            format_info = {
                'format_id': format_id,
                'resolution': f'{height}p',
                'has_audio': has_audio,
                'filesize': format_size(filesize),
                'ext': f.get('ext', ''),
                'fps': f'{fps}fps' if fps else '',
                'display_str': f"{height}p {f'{fps}fps ' if fps else ''}- {format_size(filesize)}"
            }
            video_formats.append(format_info)

    # Sort by resolution
    video_formats.sort(key=lambda x: int(x['resolution'][:-1]), reverse=True)
    
    # Add formats with best available audio
    for format in video_formats:
        if format['has_audio']:
            processed_formats.append(format)
        else:
            # Create a format that will combine this video with best audio
            combined_format = format.copy()
            combined_format['format_id'] = f"{format['format_id']}+bestaudio"
            combined_format['display_str'] = f"{format['display_str']} (with audio)"
            processed_formats.append(combined_format)
    
    return processed_formats

def progress_hook(d, session_id):
    if d['status'] == 'downloading':
        try:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            filename = d.get('filename', '').split('/')[-1] if d.get('filename') else 'file'
            
            # Calculate percentage if total is known, otherwise use downloaded bytes for fragment-based progress
            if total > 0:
                percentage = (downloaded / total) * 100
                is_fragment_download = False
            else:
                # For unknown size files, we'll use a fragment-based approach
                percentage = -1  # Special value to indicate unknown total
                is_fragment_download = True
                
            speed_str = f"{speed/1024/1024:.1f} MB/s" if speed else "N/A"
            
            # Format ETA to be more user-friendly
            if eta:
                if eta > 60:
                    minutes = eta // 60
                    seconds = eta % 60
                    eta_str = f"{minutes}m {seconds}s"
                else:
                    eta_str = f"{eta}s"
            else:
                eta_str = "calculating..."
                
            download_progress[session_id] = {
                'percentage': percentage,
                'speed': speed_str,
                'eta': eta_str,
                'downloaded': format_size(downloaded),
                'total': format_size(total) if total > 0 else "Unknown",
                'status': 'Downloading...',
                'timestamp': time.time(),
                'filename': filename,
                'fragment_based': is_fragment_download,
                'downloaded_bytes': downloaded
            }
        except Exception as e:
            download_progress[session_id] = {
                'percentage': -1,
                'speed': 'N/A',
                'eta': 'unknown',
                'status': 'Calculating...',
                'downloaded': 'N/A',
                'total': 'Unknown',
                'timestamp': time.time(),
                'error': str(e),
                'fragment_based': True
            }
    elif d['status'] == 'finished':
        download_progress[session_id] = {
            'percentage': 100,
            'speed': 'N/A',
            'eta': '0',
            'status': 'Processing the downloaded file...',
            'timestamp': time.time()
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download_process', methods=['POST'])
def download_process():
    url = request.form['url']
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = process_formats(info_dict.get('formats', []))
            thumbnail = info_dict.get('thumbnail', '')
            title = info_dict.get('title', 'Video')

            # Generate a unique session ID
            session_id = str(uuid.uuid4())
            download_progress[session_id] = {
                'percentage': 0,
                'speed': 'N/A',
                'eta': 'N/A',
                'status': 'Ready to download',
                'timestamp': time.time()
            }

            return render_template('download_process.html',
                                url=url,
                                formats=formats,
                                thumbnail=thumbnail,
                                title=title,
                                session_id=session_id)
    except Exception as e:
        return render_template('error.html', error_message=str(e))

@app.route('/get_progress/<session_id>')
def get_progress(session_id):
    progress_data = download_progress.get(session_id, {
        'percentage': 0,
        'speed': 'N/A',
        'eta': 'N/A',
        'status': 'No data available',
        'timestamp': time.time(),
        'fragment_based': False
    })
    
    # Clean up old session data (older than 30 minutes)
    current_time = time.time()
    for sid in list(download_progress.keys()):
        if current_time - download_progress[sid].get('timestamp', 0) > 1800:  # 30 minutes
            del download_progress[sid]
    
    return jsonify(progress_data)

def download_video_task(url, format_id, session_id, downloads_dir):
    try:
        # Create a custom progress hook that includes the session ID
        def session_progress_hook(d):
            progress_hook(d, session_id)
        
        # Additional options to help with difficult formats
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'noplaylist': True,
            'progress_hooks': [session_progress_hook],
            'fragment_retries': 10,       # Retry fragments 10 times
            'retries': 10,                # Retry the whole download 10 times
            'file_access_retries': 5,     # Retry on file access issues
            'ignoreerrors': False,        # Don't ignore errors
            'continue': True,             # Resume downloads if possible
            'noprogress': False,          # Show progress
            'quiet': False,               # Print messages to stdout
            'verbose': False,             # Don't print debug information
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
            # Mark download as complete
            download_progress[session_id] = {
                'percentage': 100,
                'speed': 'Complete',
                'eta': '0',
                'status': 'Complete',
                'timestamp': time.time()
            }
    except Exception as e:
        download_progress[session_id] = {
            'percentage': 0,
            'speed': 'N/A',
            'eta': 'N/A',
            'status': f'Error: {str(e)}',
            'timestamp': time.time()
        }

@app.route('/download_complete', methods=['POST'])
def download_complete():
    url = request.form['url']
    format_id = request.form['format_id']
    session_id = request.form['session_id']
    downloads_dir = os.path.abspath('downloads')

    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)

    try:
        # Start download in a separate thread
        download_thread = threading.Thread(
            target=download_video_task,
            args=(url, format_id, session_id, downloads_dir)
        )
        download_thread.daemon = True
        download_thread.start()
        
        # Return the download status page immediately
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return render_template(
                'download_complete.html',
                title=info.get('title', 'Unknown'),
                thumbnail=info.get('thumbnail', ''),
                session_id=session_id
            )
            
    except Exception as e:
        return render_template('error.html', error_message=str(e))

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True, threaded=True)