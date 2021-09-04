"""Python client for ArrisDCX960."""
from typing import List


class ArrisDCX960Session:
    householdId: str
    oespToken: str
    locationId: str
    username: str
    def __init__(self, houseHoldId, oespToken, locationId, username):
        self.householdId = houseHoldId
        self.oespToken = oespToken
        self.locationId = locationId
        self.username = username

class ArrisDCX960PlayingInfo:
    channelId: str
    title: str
    image: str
    sourceType: str
    paused: bool

    def __init__(self):
        self.channelId = None
        self.title = None
        self.image = None
        self.sourceType = None
        self.paused = False
        self.channelTitle = None

    def setPaused(self, paused: bool):
        self.paused = paused

    def setChannel(self, channelId):
        self.channelId = channelId

    def setTitle(self, title):
        self.title = title

    def setChannelTitle(self, title):
        self.channelTitle = title

    def setImage(self, image):
        self.image = image

    def setSourceType(self, sourceType):
        self.sourceType = sourceType

class ArrisDCX960Channel:
    serviceId: str
    title: str
    streamImage: str
    logoImage: str
    channelNumber: str

    def __init__(self, serviceId, title, streamImage, logoImage, channelNumber):
        self.serviceId = serviceId
        self.title = title
        self.streamImage = streamImage
        self.logoImage = logoImage
        self.channelNumber = channelNumber

class ArrisDCX960RecordingSingle:
    recording_id: str
    title: str
    image: str
    season: int
    episode: int

    def __init__(self, recording_id, title, image):
        self.recording_id = recording_id
        self.title = title
        self.image = image
        self.season = None
        self.episode = None

    def set_season(self, season:int):
        self.season = season
        
    def set_episode(self, episode:int):
        self.episode = episode


class ArrisDCX960RecordingShow:
    title: str
    media_group_id: str
    image: str
    children: List[ArrisDCX960RecordingSingle]
    episode_count: int

    def __init__(self, media_group_id, title, episode_count, image):
        self.media_group_id = media_group_id
        self.title = title
        self.image = image
        self.episode_count = episode_count
        self.children = []
    
    def append_child(self, season_recording:ArrisDCX960RecordingSingle):
        self.children.append(season_recording)

