from pytube import Playlist
from dadjokes import Dadjoke
import random

''' Returns a random dad joke '''
def dad_jokes():
    return(Dadjoke().joke)

''' Returns a random dank video from a playlist on youtube '''
def dank():
    playlist = Playlist('https://www.youtube.com/watch?v=q6EoRBvdVPQ&list=PLFsQleAWXsj_4yDeebiIADdH5FMayBiJo')
    yt = random.choice(playlist.videos)
    return("https://www.youtube.com/watch?v="+yt.video_id+"&list=PLFsQleAWXsj_4yDeebiIADdH5FMayBiJo")