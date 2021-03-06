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

    channel_id: str
    title: str
    image: str
    source_type: str
    paused: bool
    channel_title: str

    def __init__(self):
        """Initialize the playing info."""
        self.channel_id = None
        self.title = None
        self.image = None
        self.source_type = None
        self.paused = False
        self.channel_title = None

    def set_paused(self, paused: bool):
        """Set pause state."""
        self.paused = paused

    def set_channel(self, channel_id):
        """Set channel."""
        self.channel_id = channel_id

    def set_title(self, title):
        """Set title."""
        self.title = title

    def set_channel_title(self, title):
        """Set channel title."""
        self.channel_title = title

    def set_image(self, image):
        """Set image."""
        self.image = image

    def set_source_type(self, source_type):
        """Set sourfce type."""
        self.source_type = source_type


class ArrisDCX960Channel:
    """Represent a channel."""

    service_id: str
    title: str
    stream_image: str
    logo_image: str
    channel_number: str

    def __init__(self, service_id, title, stream_image, logo_image, channel_number):
        """Initialize a channel."""
        self.service_id = service_id
        self.title = title
        self.stream_image = stream_image
        self.logo_image = logo_image
        self.channel_number = channel_number


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
