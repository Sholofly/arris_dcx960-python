"""Python client for ArrisDCX960."""
from typing import List


class ArrisDCX960Session:
    """Represent a session."""

    householdId: str
    oespToken: str
    locationId: str
    username: str

    def __init__(self, houseHoldId, oespToken, locationId, username):
        """Initialize a session."""
        self.householdId = houseHoldId
        self.oespToken = oespToken
        self.locationId = locationId
        self.username = username


class ArrisDCX960PlayingInfo:
    """Represent current state of a box."""

    channelId: str
    title: str
    image: str
    sourceType: str
    paused: bool

    def __init__(self):
        """Initialize the playing info."""
        self.channelId = None
        self.title = None
        self.image = None
        self.sourceType = None
        self.paused = False
        self.channelTitle = None

    def setPaused(self, paused: bool):
        """Set pause state."""
        self.paused = paused

    def setChannel(self, channelId):
        """Set channel."""
        self.channelId = channelId

    def setTitle(self, title):
        """Set title."""
        self.title = title

    def setChannelTitle(self, title):
        """Set channel title."""
        self.channelTitle = title

    def setImage(self, image):
        """Set image."""
        self.image = image

    def setSourceType(self, sourceType):
        """Set sourfce type."""
        self.sourceType = sourceType


class ArrisDCX960Channel:
    """Represent a channel."""

    serviceId: str
    title: str
    streamImage: str
    logoImage: str
    channelNumber: str

    def __init__(self, serviceId, title, streamImage, logoImage, channelNumber):
        """Initialize a channel."""
        self.serviceId = serviceId
        self.title = title
        self.streamImage = streamImage
        self.logoImage = logoImage
        self.channelNumber = channelNumber


class ArrisDCX960RecordingSingle:
    """Reresent a single recording."""

    recording_id: str
    title: str
    image: str
    season: int
    episode: int

    def __init__(self, recording_id, title, image):
        """Init the single recording."""
        self.recording_id = recording_id
        self.title = title
        self.image = image
        self.season = None
        self.episode = None

    def set_season(self, season: int):
        """Set season."""
        self.season = season

    def set_episode(self, episode: int):
        """Set episode."""
        self.episode = episode


class ArrisDCX960RecordingShow:
    """Represent a recorderd show."""

    title: str
    media_group_id: str
    image: str
    children: List[ArrisDCX960RecordingSingle]
    episode_count: int

    def __init__(self, media_group_id, title, episode_count, image):
        """Init recorder show."""
        self.media_group_id = media_group_id
        self.title = title
        self.image = image
        self.episode_count = episode_count
        self.children = []

    def append_child(self, season_recording: ArrisDCX960RecordingSingle):
        """Append child."""
        self.children.append(season_recording)
