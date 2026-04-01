# Changelog

All notable changes to the Infrared Remote integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-01

### Added
- Integration icon in SVG, PNG, and PNG@2x formats
- Proper `DeviceInfo` on all entities so buttons and media_player group under one device
- Optional device name field in config flow (e.g., "Woonkamer TV")
- Icon (`mdi:television`) on the media_player entity

### Changed
- Renamed from `ir_test_remote` to `infrared_remote` (domain: `infrared_remote`)
- Integration display name changed from "IR Test Remote" to "Infrared Remote"
- Button entity class renamed from `IRTestButton` to `IRButton`
- Media player entity class renamed from `IRTestMediaPlayer` to `IRMediaPlayer`

### Fixed
- Entities not grouping under a device in the HA device registry

## [0.1.0] - 2026-04-01

### Added
- Initial release (as `ir_test_remote`)
- Consumer integration for the HA 2026.4 infrared entity platform
- Built-in NEC protocol encoder (no external dependencies)
  - Standard NEC frame: header (9000/4500 us), LSB-first data encoding, stop bit
  - 8-bit address with inverted complement, 8-bit command with inverted complement
  - 38 kHz carrier frequency, 560 us timing unit
- LG TV device type with 18 NEC commands (address 0x04):
  power, volume up/down, channel up/down, mute, input, OK, up/down/left/right, back, home, menu, play, pause, stop
- Samsung TV device type with 15 NEC commands (address 0x07):
  power, volume up/down, channel up/down, mute, input, OK, up/down/left/right, back, home, menu
- Raw Test Signal mode for verifying the IR chain works
- `media_player` entity with assumed state, supporting: turn on/off, volume up/down, mute
- `button` entities for each individual remote command with appropriate MDI icons
- Config flow with infrared emitter selection and device type dropdown
- English translations for the config flow
- Tested with Broadlink RM4 Pro as emitter and LG TV as target
