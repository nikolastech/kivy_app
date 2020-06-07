from pytube import *
import sys
link = "https://youtu.be/Q0OL4RnVBR8"


def progress_function(stream, chunk, bytes_remaining):
    size = video.filesize
    p = (abs(1-(float(bytes_remaining) / float(size))) * float(100))
    a = str(round(p)) + "%"
    sys.stdout.write('\r' + a)
    sys.stdout.flush()


yt = YouTube(link)
yt.register_on_progress_callback(progress_function)
print(yt.title)
stream_opt = yt.streams
#print(stream_opt)
video = stream_opt.filter(res="1080p").first()
print(video.title)
#video.download()


