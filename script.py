import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
import calendar
import time
from datetime import datetime

def sinceEpoch(date):
    utc_dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds()
    return timestamp

def insertComment(youtube, channelId, videoId, text):
    insertResult = youtube.commentThreads().insert(
        part='snippet',
        body=dict(
            snippet=dict(
                channelId=channelId,
                videoId=videoId,
                topLevelComment=dict(
                    snippet=dict(
                        textOriginal=text
                    )
                )
            )
        )
    ).execute()

    comment = insertResult['snippet']['topLevelComment']
    author = comment['snippet']['authorDisplayName']
    text = comment['snippet']['textDisplay']
    print('Inserted comment for %s: %s' % (author, text))

CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.force-ssl']

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

check = 'channelid' #channelId to check for newest videos

request = youtube.channels().list(
    part='contentDetails',
    id=check
)
response = request.execute()
uploadsId = response['items'][0]['contentDetails']['relatedPlaylists']['uploads'] #getting information about channel


while (True):
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploadsId
    )
    response = request.execute() #checking all videos in their uploads playlist

    title = response['items'][0]['snippet']['title']
    desc = response['items'][0]['snippet']['description']
    vidId = response['items'][0]['snippet']['resourceId']['videoId']
    pub = sinceEpoch(response['items'][0]['snippet']['publishedAt'])
    now = calendar.timegm(time.gmtime())

    if (now-pub < 3600): #if video is from last hour
        print("\n\n\n'" + title + "' less than one hour old.")
        if (('leave a comment' in title.lower() and 'central' in title.lower()) or ('leave a comment' in desc.lower() and 'paypal' in desc.lower())): #if video has proper terms so we know it is the right video
            print('Contains correct strings.')
            youtube.videos().rate(rating='like', id=vidId).execute()
            print('Liked video.')
            insertComment(youtube, check, vidId, 'Very cool!')
            break
    else:
        print('No new video yet :(')
    time.sleep(30)
