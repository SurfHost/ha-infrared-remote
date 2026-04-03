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
DEVICE_TYPE_PHILIPS_LAMP = "philips_lamp"
DEVICE_TYPE_AMINO_STB = "amino_stb"
DEVICE_TYPE_RAW_TEST = "raw_test"

DEVICE_TYPES = {
    DEVICE_TYPE_NEC_TV: "NEC TV (LG, most TVs)",
    DEVICE_TYPE_SAMSUNG_TV: "Samsung TV",
    DEVICE_TYPE_SHARP_TV: "Sharp TV (Aquos)",
    DEVICE_TYPE_DENON_AVR: "Denon AVR Receiver",
    DEVICE_TYPE_PHILIPS_LAMP: "Philips RGBIC Lamp",
    DEVICE_TYPE_AMINO_STB: "Amino Kamai Set-top Box",
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

# Philips RGBIC Ambient Floor Lamp — NEC protocol (address 0x00)
PHILIPS_LAMP_ADDRESS = 0x00

PHILIPS_LAMP_COMMANDS = {
    "on": 0x03,
    "off": 0x02,
    "brightness_up": 0x00,
    "brightness_down": 0x01,
    "red": 0x04,
    "green": 0x05,
    "blue": 0x06,
    "white": 0x07,
    "orange": 0x08,
    "night_mode": 0x0B,
    "yellow": 0x0C,
}

# Amino Kamai 7X Set-top Box — RC6 protocol (raw Broadlink-learned codes)
# RC6 is too complex to encode from scratch, so we store the base64
# Broadlink packets and decode them to raw timings at runtime.
AMINO_STB_BROADLINK_CODES = {
    "power": "JgCEAFQdDRAODw0dDR4qHA4QDg4ODw0PDg8NDxseDg4ODw0PHQ4ODw0dDg4dHQ4PGw8OHQ4ODg8NDw4PHA8OHA4ODgAIs1UdDg8ODw0dDh0qHQ0QDRANDw4ODg8ODhwdDg8NDw4OHQ8NDw4cDg8cHQ4PGw8OHQ4PDQ8ODw0PHA8OHA4PDQANBQ==",
    "channel_up": "JgBCAFQdDRAODg4dDR4qHA4QDQ8ODw0PDg4ODxseDQ8ODw0PHA8ODw0PDh0cHQ4OHA8NHg0PDg8cHA4PDg8ODw0PDgANBQ==",
    "channel_down": "JgBaAFUcDhAMEA4cDh0qHQ4PDRANDw4PDQ8ODhwdDg8NDw4PHA8NDw4PDR4bHg0PGw8OHQ4PDQ8cHQ4ODg8ODh0ACLtVHA4QDBAOHA4dKxwODw0QDg4ODwwSCgANBQ==",
    "forward": "JgCAAFQdDg8NDw4dDhwqHg4ODg8NDw4PDQ8ODh0cDhANDw4PGw8NDw4dDg8cHA4PHA8OHA4QDQ8bHhseDQ8ODw0ACLNUHg4ODg8NHg4cKh4NDw4ODg8ODg4PDQ8cHQ4PDg8NDxwODg8NHg4OHRwODxwPDR0NEA4PGx0cHQ4PDQ8OAA0F",
    "rewind": "JgB8AFUdDRAODw0dDR4qHA4QDg4ODw0PDg8NDxseDg4ODw0PHQ4ODw0PDh0cHQ4PGw8NHg4ODg8cHRwcDhAbAAi8VRwODw0PDh0OHSscDg4ODw4PDRANDw4PGx0ODw4ODg8cDw4ODg8NHRweDQ8cDg4dDg8ODh0cHRwODxwADQU=",
    "play": "JgCAAFQcDg8ODw4cDh4qHA4QDBAODg4PDg4ODxseDQ8ODg4PHA8ODg4dDRAbHg0PHA4OHg0PDg4dHB0ODh0NEA4ACLJUHg4ODg8NHg4cKh4NDw4ODg8ODg4PDQ8dHQ4ODg8ODhwODhANHQ4OHRwODxwPDh0ODg4PGx4bEA0dDg4OAA0F",
    "pause": "JgCEAFQdDw4NDw4dDhwrHQ4ODg8ODg4PDQ8ODxwdDg8ODg4PGw8ODg4QDR0cHQ0PHA8OHQ4PDQ8cDg4dDg8ODg4PDgAIs1QeDQ8ODw0eDR0qHQ4PDg4ODw0PDg8NDxwdDg8NEA0PHA4ODw0PDh0dHA4PHA8NHQ4ODhAbDw4dDg4ODw4ODgANBQ==",
    "stop": "JgCAAFQeDg4ODw0eDhwqHg0PDg4ODw4ODg8NDx0cDg8ODw4OHA4ODw4dDg4dHA4PHA8OHA4PDg8bDw4dDg8NDxsACLxVHQ4ODg8OHQ4cKh4NDw4PDQ8ODw0PDg4dHA4QDBAODhwPDQ8OHQ4PHBwODxwPDhwOEAwQGw8OHQ4PDQ8cAA0F",
}
