# Infrared Remote

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom Home Assistant integration that creates **button** and **media_player** entities to control IR devices (TVs, etc.) through the Home Assistant 2026.4 infrared platform.

## What does this do?

This is a **consumer integration** for the HA 2026.4 infrared platform. It sends IR commands through any available infrared emitter (like [Broadlink Infrared Emitter](https://github.com/SurfHost/ha-broadlink-infrared) or ESPHome IR proxy).

Set it up, pick your emitter, choose your device type, and you get:

- A **media_player** entity for your TV or receiver (power, volume, mute)
- **Button** entities for all remote functions
- Option to **attach IR buttons to an existing device** (like Battery Notes does)
- **Reconfigure** after setup — see and change the linked emitter
- Everything works through the new infrared platform with proper HA integration

## Supported devices

| Device Type | Protocol | Buttons | Media Player |
|-------------|----------|---------|--------------|
| LG TV | NEC (addr 0x04) | 18 | Yes (TV) |
| Samsung TV | NEC (addr 0x07) | 15 | Yes (TV) |
| Sharp TV (Aquos) | Sharp (addr 0x01) | 20 | Yes (TV) |
| Denon AVR Receiver | Denon (addr 0x02) | 16 | Yes (Receiver) |
| Philips RGBIC Lamp | NEC (addr 0x00) | 11 | No |
| Amino Kamai 7X STB | RC6 (raw learned) | 8 | No |
| Raw Test | Raw burst | 1 | No |

## Requirements

- Home Assistant **2026.4** or later
- An infrared emitter entity (e.g., Broadlink Infrared Emitter, ESPHome IR proxy)

## Installation via HACS

1. Open HACS in Home Assistant
2. Click the three dots in the top right and select **Custom repositories**
3. Add this repository URL and select **Integration** as category
4. Click **Download**
5. Restart Home Assistant

## Setup

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **Infrared Remote**
3. Select your infrared emitter
4. Choose the device type (e.g., "NEC TV (LG)")
5. Optionally give it a name (e.g., "Woonkamer TV")
6. Your TV now shows up as a media_player with button entities

## Testing

1. **Raw test first**: Set up with "Raw Test Signal". Press the button. If your IR blaster blinks, the chain works.
2. **TV test**: Set up with your TV type. Point the blaster at the TV and press Power.
3. **Dashboard**: Add the media_player entity for a proper TV control card.

## Adding more device types

Built-in protocol encoders: **NEC**, **Sharp**, and **Denon**. For unsupported protocols, Broadlink-learned codes can be stored as raw timings. PRs welcome!
