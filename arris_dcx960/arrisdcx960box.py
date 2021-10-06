"""ArrisDCX960Box."""
from paho.mqtt.client import Client
import json
import requests
import logging
from .models import ArrisDCX960PlayingInfo, ArrisDCX960Channel
from .const import (
    BOX_PLAY_STATE_BUFFER,
    BOX_PLAY_STATE_CHANNEL,
    BOX_PLAY_STATE_DVR,
    BOX_PLAY_STATE_REPLAY,
    BOX_PLAY_STATE_APP,
    BOX_PLAY_STATE_VOD,
    ONLINE_STANDBY,
    UNKNOWN,
    COUNTRY_SETTINGS,
)
from .helpers import make_id

DEFAULT_PORT = 443
_logger = logging.getLogger(__name__)


class ArrisDCX960Box:
    """Represent a single settop box."""

    box_id: str
    name: str
    state: str = UNKNOWN
    info: ArrisDCX960PlayingInfo
    available: bool = False
    channels: ArrisDCX960Channel = {}

    def __init__(
        self,
        box_id: str,
        name: str,
        householdId: str,
        token: str,
        country_code: str,
        mqttClient: Client,
        client_id: str,
    ):
        """Initialize a single settop box."""
        self._country_config = COUNTRY_SETTINGS[country_code]
        self.box_id = box_id
        self.name = name
        self._householdId = householdId
        self._token = token
        self.info = ArrisDCX960PlayingInfo()
        self._mqttClientConnected = False
        self._createUrls(country_code)
        self.mqttClientId = client_id
        self.mqttClient = mqttClient
        self._change_callback = None
        self._message_stamp = None

    def _createUrls(self, country_code: str):
        """Create some urls."""
        baseUrl = self._country_config["api_url"]
        self._api_url_listing_format = baseUrl + "/listings/{id}"
        self._api_url_mediagroup_format = baseUrl + "/mediagroups/{id}"
        self._mqtt_broker = self._country_config["mqtt_url"]

    def register(self):
        """Register a settop box."""
        payload = {
            "source": self.mqttClientId,
            "state": "ONLINE_RUNNING",
            "deviceType": "HGO",
        }
        register_topic = self._householdId + "/" + self.mqttClientId + "/status"
        self.mqttClient.publish(register_topic, json.dumps(payload))

    def set_callback(self, callback):
        """Set callback function."""
        self._change_callback = callback

    def _do_subscribe(self, topic):
        """Subscribe to mqtt topic."""
        self.mqttClient.subscribe(topic)
        _logger.debug("subscribed to topic: {topic}".format(topic=topic))

    def update_settopbox_state(self, payload):
        """Register a new settop box."""
        state = payload["state"]
        if self.state == state:
            return

        self.state = state

        if state == ONLINE_STANDBY:
            self.info = ArrisDCX960PlayingInfo()
            if self._change_callback:
                _logger.debug(f"Callback called from box {self.box_id}")
                self._change_callback(self.box_id)
        else:
            self._request_settop_box_state()

    def _request_settop_box_state(self):
        """Send mqtt message to receive state from settop box."""
        _logger.debug("Request box state for box " + self.name)
        topic = self._householdId + "/" + self.box_id
        payload = {
            "id": make_id(8),
            "type": "CPE.getUiStatus",
            "source": self.mqttClientId,
        }
        self.mqttClient.publish(topic, json.dumps(payload))

    def update_settop_box(self, payload):
        """Update settopbox state."""
        deviceId = payload["source"]
        if deviceId != self.box_id:
            return
        _logger.debug(f"Updating box {self.box_id} with payload")
        statusPayload = payload["status"]
        if "uiStatus" not in statusPayload:
            _logger.warning("Unexpected statusPayload: ")
            _logger.warning(statusPayload)
            return
        message_stamp = payload["messageTimeStamp"]
        if self._message_stamp and self._message_stamp > message_stamp:
            return
        self._message_stamp = message_stamp
        uiStatus = statusPayload["uiStatus"]
        if uiStatus == "mainUI":
            playerState = statusPayload["playerState"]
            if "sourceType" not in playerState or "source" not in playerState:
                _logger.warning(
                    "No sourceType or stateSource in playerState. State update was skipped"
                )
                return
            sourceType = playerState["sourceType"]
            stateSource = playerState["source"]
            speed = playerState["speed"]
            if self.info is None:
                self.info = ArrisDCX960PlayingInfo()
            if sourceType == BOX_PLAY_STATE_REPLAY:
                self.info.setSourceType(BOX_PLAY_STATE_REPLAY)
                if stateSource is None or "eventId" not in stateSource:
                    _logger.warning("No eventId in stateSource")
                    _logger.warning("State update was skipped ")
                    return
                eventId = stateSource["eventId"]
                listing = self._get_listing(eventId)
                channel_id = self._get_listing_channel_id(listing)
                if channel_id is not None and channel_id in self.channels.keys():
                    self.info.setChannel(channel_id)
                    channel = self.channels[channel_id]
                    self.info.setTitle("ReplayTV: " + self._get_listing_title(listing))
                    self.info.setImage(self._get_listing_image(listing))
                else:
                    self._set_unknown_channel_info()
            elif sourceType == BOX_PLAY_STATE_DVR:
                self.info.setSourceType(BOX_PLAY_STATE_DVR)
                if stateSource is None or "recordingId" not in stateSource:
                    _logger.warning(
                        "No recordingId in stateSource,State update was skipped."
                    )
                    return
                recordingId = stateSource["recordingId"]
                listing = self._get_listing(recordingId)
                channel_id = self._get_listing_channel_id(listing)
                if channel_id is not None and channel_id in self.channels.keys():
                    self.info.setChannel(channel_id)
                    channel = self.channels[channel_id]
                    self.info.setTitle("Recording: " + self._get_listing_title(listing))
                    self.info.setImage(self._get_listing_image(listing))
                else:
                    self._set_unknown_channel_info()
            elif sourceType == BOX_PLAY_STATE_BUFFER:
                self.info.setSourceType(BOX_PLAY_STATE_BUFFER)
                if stateSource is None or "channelId" not in stateSource:
                    _logger.warning(
                        "No channelId in stateSource. State update was skipped."
                    )
                    return
                channelId = stateSource["channelId"]
                if channelId is not None and channelId in self.channels.keys():
                    self.info.setChannel(channelId)
                    channel = self.channels[channelId]
                    self.info.setChannelTitle(channel.title)
                    eventId = stateSource["eventId"]
                    listing = self._get_listing(eventId)
                    self.info.setTitle("Delayed: " + self._get_listing_title(listing))
                    self.info.setImage(channel.streamImage)
                else:
                    self._set_unknown_channel_info()
            elif sourceType == BOX_PLAY_STATE_CHANNEL:
                self.info.setSourceType(BOX_PLAY_STATE_CHANNEL)
                if stateSource is None or "channelId" not in stateSource:
                    _logger.warning(
                        "No channelId in stateSource. State update was skipped."
                    )
                    return
                channelId = stateSource["channelId"]
                eventId = stateSource["eventId"]
                if channelId is not None and channelId in self.channels.keys():
                    channel = self.channels[channelId]
                    listing = self._get_listing(eventId)
                    self.info.setChannel(channelId)
                    self.info.setChannelTitle(channel.title)
                    self.info.setTitle(self._get_listing_title(listing))
                    self.info.setImage(channel.streamImage)
                else:
                    self._set_unknown_channel_info()
            elif sourceType == BOX_PLAY_STATE_VOD:
                self.info.setSourceType(BOX_PLAY_STATE_VOD)
                title_id = stateSource["titleId"]
                mediagroup_content = self._get_mediagroup(title_id)
                self.info.setChannel(None)
                self.info.setChannelTitle("VOD")
                self.info.setTitle(self._get_mediagroup_title(mediagroup_content))
                self.info.setImage(self._get_mediagroup_image(mediagroup_content))
            else:
                self._set_unknown_channel_info()
            self.info.setPaused(speed == 0)
        elif uiStatus == "apps":
            appsState = statusPayload["appsState"]
            logoPath = appsState["logoPath"]
            if not logoPath.startswith("http:"):
                logoPath = "https:" + logoPath
            self.info.setSourceType(BOX_PLAY_STATE_APP)
            self.info.setChannel(None)
            self.info.setChannelTitle(appsState["appName"])
            self.info.setTitle(appsState["appName"])
            self.info.setImage(logoPath)
            self.info.setPaused(False)

        if self._change_callback:
            _logger.debug(f"Callback called from box {self.box_id}")
            self._change_callback(self.box_id)

    def _set_unknown_channel_info(self):
        """Set unknown channel info."""
        _logger.warning("Couldn't set channel. Channel info set to unknown...")
        self.info.setSourceType(BOX_PLAY_STATE_CHANNEL)
        self.info.setChannel(None)
        self.info.setTitle("No information available")
        self.info.setImage(None)
        self.info.setPaused(False)

    def _get_listing_title(self, listing_content):
        """Get listing title."""
        if listing_content is None:
            return ""
        return listing_content["program"]["title"]

    def _get_listing_image(self, listing_content):
        """Get listing image."""
        if (
            "program" in listing_content
            and "images" in listing_content["program"]
            and len(listing_content["program"]["images"]) > 0
        ):
            return listing_content["program"]["images"][0]["url"]
        else:
            _logger.debug(
                f"No image found. Listing content was: {str(listing_content)}"
            )
        return None

    def _get_listing_channel_id(self, listing_content):
        """Get listing channelId."""
        if "stationId" not in listing_content:
            return None
        return (
            listing_content["stationId"]
            .replace("lgi-nl-prod-master:", "")
            .replace("lgi-be-prod-master:", "")
            .replace("lgi-at-prod-master:", "")
            .replace("lgi-ch-prod-master:", "")
            .replace("lgi-hu-prod-master:", "")
            .replace("lgi-cz-prod-master:", "")
            .replace("lgi-ie-prod-master:", "")
            .replace("lgi-pl-prod-master:", "")
            .replace("lgi-de-prod-master:", "")
            .replace("lgi-sk-prod-master:", "")
            .replace("lgi-ro-prod-master:", "")
        )

    def _get_listing(self, listing_id):
        """Get listing."""
        response = requests.get(self._api_url_listing_format.format(id=listing_id))
        if response.status_code == 200:
            return response.json()
        return None

    def _get_mediagroup(self, title_id):
        """Get media group."""
        response = requests.get(self._api_url_mediagroup_format.format(id=title_id))
        if response.status_code == 200:
            return response.json()
        return None

    def _get_mediagroup_title(self, mediagroup_content):
        """Get media group title."""
        if mediagroup_content is None:
            return "Video on demand"
        else:
            return mediagroup_content["title"]

    def _get_mediagroup_image(self, mediagroup_content):
        """Get media group image."""
        if mediagroup_content is None:
            return None
        else:
            return mediagroup_content["images"][0]["url"]

    def send_key_to_box(self, key: str):
        """Send emulated (remote) key press to settopbox."""
        payload = (
            '{"type":"CPE.KeyEvent","status":{"w3cKey":"'
            + key
            + '","eventType":"keyDownUp"}}'
        )
        self.mqttClient.publish(self._householdId + "/" + self.box_id, payload)

    def set_channel(self, serviceId):
        """Set channel."""
        payload = (
            '{"id":"'
            + make_id(8)
            + '","type":"CPE.pushToTV","source":{"clientId":"'
            + self.mqttClientId
            + '","friendlyDeviceName":"Home Assistant"},'
            + '"status":{"sourceType":"linear","source":{"channelId":"'
            + serviceId
            + '"},"relativePosition":0,"speed":1}}'
        )

        self.mqttClient.publish(self._householdId + "/" + self.box_id, payload)

    def play_recording(self, recordingId):
        """Play recording."""
        payload = (
            '{"id":"'
            + make_id(8)
            + '","type":"CPE.pushToTV","source":{"clientId":"'
            + self.mqttClientId
            + '","friendlyDeviceName":"Home Assistant"},'
            + '"status":{"sourceType":"nDVR","source":{"recordingId":"'
            + recordingId
            + '"},"relativePosition":0}}'
        )

        self.mqttClient.publish(self._householdId + "/" + self.box_id, payload)

    def turn_off(self):
        """Turn off."""
        self.info = ArrisDCX960PlayingInfo()
