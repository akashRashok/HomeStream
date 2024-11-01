import os
import re
from flask import Flask, request, Response, render_template_string, abort
from tkinter import Tk, filedialog

# Function to select the media directory
def select_movie_directory():
    root = Tk()
    root.withdraw()
    movie_directory = filedialog.askdirectory(title="Select the Movie Directory")
    root.destroy()
    return movie_directory

#
app = Flask(__name__)

# Select the directory
MOVIE_DIRECTORY = select_movie_directory()

# Validate the selected directory; exit if it is invalid or contains no MP4 files
if not MOVIE_DIRECTORY or not os.path.isdir(MOVIE_DIRECTORY):
    print("No valid directory selected. Exiting.")
    exit(1)
if not any(file.endswith('.mp4') for _, _, files in os.walk(MOVIE_DIRECTORY) for file in files):
    print("No MP4 files found in the directory. Please select a directory with movies.")
    exit(1)

# Function to list all MP4 files in the selected movie directory
def list_files(directory):
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.mp4'):
                rel_dir = os.path.relpath(root, directory)
                rel_file = os.path.join(rel_dir, filename)
                files.append(rel_file)
    return files

# homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    movies = list_files(MOVIE_DIRECTORY)
    search_query = request.form.get('search', '').lower()
    if search_query:
        movies = [movie for movie in movies if search_query in movie.lower()]
    movies_list = '\n'.join(f'<li><a href="/watch/{movie}">{movie}</a></li>' for movie in movies)
    
    return render_template_string(f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Movie Server</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            margin: 0;
            padding: 20px;
          }}
          h1 {{
            text-align: center;
            color: #2c3e50;
          }}
          .movie-list {{
            max-width: 1000px;
            margin: 20px auto;
            padding: 20px;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          }}
          .search-container {{
            text-align: center;
            margin-bottom: 20px;
          }}
          ul {{
            list-style-type: none;
            padding: 0;
          }}
          li {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
          }}
          li a {{
            text-decoration: none;
            color: #2980b9;
          }}
          li a:hover {{
            color: #d35400;
          }}
          input[type="text"] {{
            padding: 8px;
            font-size: 16px;
            width: 60%;
            border: 1px solid #ccc;
            border-radius: 4px;
          }}
          button {{
            padding: 8px 16px;
            font-size: 16px;
            color: #fff;
            background-color: #2980b9;
            border: none;
            border-radius: 4px;
            cursor: pointer;
          }}
          button:hover {{
            background-color: #d35400;
          }}
        </style>
      </head>
      <body>
        <h1>Available Movies</h1>
        <div class="movie-list">
          <div class="search-container">
            <form method="post">
              <input type="text" name="search" placeholder="Search for a movie..." value="{search_query}">
              <button type="submit">Search</button>
            </form>
          </div>
          <ul>
            {movies_list}
          </ul>
        </div>
      </body>
    </html>
    """)

# video player
@app.route('/watch/<path:filename>')
def watch(filename):
    return render_template_string(f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Watching {filename}</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            margin: 0;
            padding: 20px;
          }}
          h1 {{
            text-align: center;
            color: #2c3e50;
          }}
          .video-container {{
            display: flex;
            justify-content: center;
            margin-top: 20px;
          }}
        </style>
      </head>
      <body>
        <h1>Watching {filename}</h1>
        <div class="video-container">
          <video width="80%" controls>
            <source src="/stream/{filename}" type="video/mp4">
            Your browser does not support the video tag.
          </video>
        </div>
      </body>
    </html>
    """)

@app.route('/stream/<path:filename>')
def stream(filename):
    file_path = os.path.join(MOVIE_DIRECTORY, filename)
    if not os.path.exists(file_path):
        abort(404)
    
    range_header = request.headers.get('Range', None)
    if range_header:
        return partial_response(file_path, range_header)
    else:
        return full_response(file_path)

# Function to send the full file if no range is requested
def full_response(file_path):
    """Send the entire file."""
    return Response(open(file_path, 'rb'), mimetype='video/mp4')

# Function to handle partial requests for HTTP 206
def partial_response(file_path, range_header):
    """Handle partial requests for HTTP 206."""
    size = os.path.getsize(file_path)
    byte_range = re.search(r'bytes=(\d+)-(\d*)', range_header)
    start = int(byte_range.group(1))
    end = byte_range.group(2)
    if end:
        end = int(end)
    else:
        end = size - 1

    length = end - start + 1
    with open(file_path, 'rb') as f:
        f.seek(start)
        data = f.read(length)

    response = Response(data, 206, mimetype='video/mp4')
    response.headers.add('Content-Range', f'bytes {start}-{end}/{size}')
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Content-Length', str(length))
    return response

# Start the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)