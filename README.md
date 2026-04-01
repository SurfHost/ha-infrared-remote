# Infrared Remote

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom Home Assistant integration that creates **button** and **media_player** entities to control IR devices (TVs, etc.) through the Home Assistant 2026.4 infrared platform.

## What does this do?

This is a **consumer integration** for the HA 2026.4 infrared platform. It sends IR commands through any available infrared emitter (like [Broadlink Infrared Emitter](https://github.com/your-repo/ha-broadlink-infrared) or ESPHome IR proxy).

Set it up, pick your emitter, choose your device type, and you get:

- A **media_player** entity for your TV (power, volume, mute) that works like any smart TV
- **Button** entities for all remote functions (18 for LG, 15 for Samsung)
- Everything works through the new infrared platform with proper HA integration

## Supported devices

| Device Type | Protocol | Buttons | Media Player |
|-------------|----------|---------|--------------|
| LG TV | NEC (addr 0x04) | 18 | Yes |
| Samsung TV | NEC (addr 0x07) | 15 | Yes |
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

The NEC protocol encoder is built-in. To add more devices, you only need to know the NEC address and command codes. PRs welcome!
