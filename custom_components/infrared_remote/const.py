"""Constants for the Infrared Remote integration."""

DOMAIN = "infrared_remote"

CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_DEVICE_TYPE = "device_type"
CONF_DEVICE_NAME = "device_name"
CONF_ATTACH_TO_DEVICE = "attach_to_device"

DEVICE_TYPE_NEC_TV = "nec_tv"
DEVICE_TYPE_SAMSUNG_TV = "samsung_tv"
DEVICE_TYPE_RAW_TEST = "raw_test"

DEVICE_TYPES = {
    DEVICE_TYPE_NEC_TV: "NEC TV (LG, most TVs)",
    DEVICE_TYPE_SAMSUNG_TV: "Samsung TV",
    DEVICE_TYPE_RAW_TEST: "Raw Test Signal (just a burst)",
}

# NEC Protocol
NEC_FREQUENCY_KHZ = 38
NEC_UNIT_US = 560
NEC_HEADER_MARK_US = 9000
NEC_HEADER_SPACE_US = 4500
NEC_ONE_MARK_US = NEC_UNIT_US
NEC_ONE_SPACE_US = 1690
NEC_ZERO_MARK_US = NEC_UNIT_US
NEC_ZERO_SPACE_US = NEC_UNIT_US
NEC_STOP_MARK_US = NEC_UNIT_US
NEC_STOP_SPACE_US = NEC_UNIT_US

# LG TV NEC codes (address 0x04)
LG_TV_ADDRESS = 0x04

LG_TV_COMMANDS = {
    "power": 0x08,
    "volume_up": 0x02,
    "volume_down": 0x03,
    "channel_up": 0x00,
    "channel_down": 0x01,
    "mute": 0x09,
    "input": 0x0B,
    "ok": 0x44,
    "up": 0x40,
    "down": 0x41,
    "left": 0x07,
    "right": 0x06,
    "back": 0x28,
    "home": 0xC4,
    "menu": 0x43,
    "play": 0xB0,
    "pause": 0xBA,
    "stop": 0xB1,
}

# Samsung TV NEC codes (address 0x07)
SAMSUNG_TV_ADDRESS = 0x07

SAMSUNG_TV_COMMANDS = {
    "power": 0x02,
    "volume_up": 0x07,
    "volume_down": 0x0B,
    "channel_up": 0x12,
    "channel_down": 0x10,
    "mute": 0x0F,
    "input": 0x01,
    "ok": 0x68,
    "up": 0x60,
    "down": 0x61,
    "left": 0x65,
    "right": 0x62,
    "back": 0x58,
    "home": 0x79,
    "menu": 0x1A,
}
