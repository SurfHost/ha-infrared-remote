"""Constants for the Infrared Remote integration."""

DOMAIN = "infrared_remote"

CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_DEVICE_TYPE = "device_type"
CONF_DEVICE_NAME = "device_name"
CONF_ATTACH_TO_DEVICE = "attach_to_device"

DEVICE_TYPE_NEC_TV = "nec_tv"
DEVICE_TYPE_SAMSUNG_TV = "samsung_tv"
DEVICE_TYPE_SHARP_TV = "sharp_tv"
DEVICE_TYPE_DENON_AVR = "denon_avr"
DEVICE_TYPE_RAW_TEST = "raw_test"

DEVICE_TYPES = {
    DEVICE_TYPE_NEC_TV: "NEC TV (LG, most TVs)",
    DEVICE_TYPE_SAMSUNG_TV: "Samsung TV",
    DEVICE_TYPE_SHARP_TV: "Sharp TV (Aquos)",
    DEVICE_TYPE_DENON_AVR: "Denon AVR Receiver",
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

# Sharp Protocol
SHARP_FREQUENCY_KHZ = 38
SHARP_BIT_MARK_US = 320
SHARP_ONE_SPACE_US = 1680
SHARP_ZERO_SPACE_US = 680
SHARP_FRAME_GAP_US = 40000  # 40ms gap between first and second (inverted) frame

# Denon Protocol (different timing from Sharp despite similar structure)
# IRP: {38k,264}<1,-3|1,-7>(D:5,F:8,0:2,1,-165,D:5,~F:8,3:2,1,-165)+
# No header pulse. Time unit = 264us.
DENON_FREQUENCY_KHZ = 38
DENON_BIT_MARK_US = 264  # 1 unit
DENON_ONE_SPACE_US = 1848  # 7 units (264 * 7)
DENON_ZERO_SPACE_US = 792  # 3 units (264 * 3)
DENON_FRAME_GAP_US = 43560  # 165 units (264 * 165)

# Sharp TV codes (address 1) — Sharp Aquos LC series
SHARP_TV_ADDRESS = 0x01

SHARP_TV_COMMANDS = {
    "power": 22,
    "volume_up": 20,
    "volume_down": 21,
    "channel_up": 17,
    "channel_down": 18,
    "mute": 23,
    "input": 19,
    "menu": 32,
    "display": 27,
    "flashback": 47,
    "0": 10,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}

# Denon AVR codes (address 2) — Denon AV receivers
DENON_AVR_ADDRESS = 0x02

# Verified codes from actual Broadlink-learned AVR-2106 remote + IRDB
# Power/volume/mute confirmed by decoding real remote packets.
# Input/surround codes from IRDB, validated by matching pattern.
DENON_AVR_COMMANDS = {
    # Power (confirmed from real remote)
    "power_on": 225,
    "power_off": 226,
    # Volume (confirmed from real remote)
    "volume_up": 241,
    "volume_down": 242,
    "mute": 240,
    # Input selection (confirmed: tv_dbs=201, dvd=227 from real remote)
    "input_cd": 66,
    "input_dvd": 227,
    "input_tv_dbs": 201,
    "input_tuner": 197,
    "input_vcr": 205,
    "input_v_aux": 204,
    "input_cdr_tape": 210,
    # Surround modes (from IRDB)
    "pure_direct": 106,
    "stereo": 230,
    "standard": 228,
    "multi_channel": 219,
}
