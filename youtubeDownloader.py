import pytube

# Replace with the YouTube video URL
video_url = "https://www.youtube.com/watch?v=2Vv-BfVoq4g"

# Create a YouTube object
yt = pytube.YouTube(video_url)

# Get the highest resolution stream (should be 4K)
stream = yt.streams.filter(res="480p").first()

# Download the video
stream.download(output_path="./video")

print("Video downloaded successfully!")