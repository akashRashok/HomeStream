# HomeStream: Local Media Streaming Server

This project is a media streaming server built with Python and Flask. It allows users to select a local directory of media files in MP4 format and serves a searchable list of available movies/series through a web interface. Users can select a media file to watch and stream it directly in their browser, with seamless streaming enabled by partial content delivery.

## Features

- **File Selection**: Choose a movie directory with a Tkinter file dialogue at startup.
- **Movie List Display**: Shows a list of all available MP4 movies in the selected directory.
- **Search Functionality**: Users can search for a movie by title in real time.
- **In-Browser Playback**: Selected movies are streamed directly in the browser with an embedded video player.
- **Partial Content Streaming**: Implements HTTP 206 to allow smooth playback without buffering by handling byte-range requests.

## Getting Started

### Prerequisites

- **Python 3.x**: Make sure Python is installed.
- **Flask**: Install Flask for running the web server. To install Flask, use:
  ```bash
  pip install Flask

## Usage
- Homepage: Displays a searchable list of movies in the selected directory.
- Search: Type in the movie title to filter the list of movies in real-time.
- Watch a Movie: Click on a movie title to open the video player page and start streaming.
- Playback Control: Supports basic playback controls like play, pause, and seek within the embedded player.
