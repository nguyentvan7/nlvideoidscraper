import os
from dotenv import load_dotenv
import json
import requests
from git import Repo
from shutil import copy2

load_dotenv()
API = os.getenv('YOUTUBE-APIKEY')
repoPath = os.getenv('REPOPATH')

videoDict = json.load(open('dict.json'))
videoArray = json.load(open('array.json'))
playlistId = "UU3tNpTOHsTnkmbwztCs30sA"

def loadVideos():
    pageCount = 0
    pageToken = ""
    done = False
    # Get all the pages of the uploads playlist
    while ((pageCount == 0 or pageToken != "") and not (done)):
        print(pageCount)
        pageCount += 1
        requestURL = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50\
&playlistId=" + playlistId + "&key=" + API
        if (pageToken != ""):
            requestURL += "&pageToken=" + pageToken
        
        playlistData = requests.get(requestURL)
        playlistJson = playlistData.json()
        if "nextPageToken" in playlistJson:
            pageToken = playlistJson["nextPageToken"]
        else:
            pageToken = ""

        for video in playlistJson["items"]:
            # If this video already exists, we have already loaded all the recent videos, don't waste quota
            videoId = video["snippet"]["resourceId"]["videoId"]
            if videoId in videoDict:
                done = True
                break
            videoDict[videoId] = 1
            videoArray.append({"videoId": videoId})
        
    with open("array.json", "w") as vid:
        json.dump(videoArray, vid)
    with open("dict.json", "w") as v:
        json.dump(videoDict, v)

def pushToRepo():
    print(repoPath)
    repo = Repo(repoPath)
    copy2("array.json", repoPath + "/videos.json")
    origin = repo.remote("origin")
    origin.pull()
    # Check if there are any changes first
    for item in repo.index.diff(None):
        if item.a_path == "videos.json":
            repo.index.add(["videos.json"])
            repo.index.commit("Update video array")
            origin.push()
            break

loadVideos()
pushToRepo()