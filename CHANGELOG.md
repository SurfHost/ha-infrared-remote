# Changelog

All notable changes to the Infrared Remote integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-04-03

### Added
- **Sharp TV (Aquos)** device type with Sharp protocol encoder (address 1, 20 commands)
- **Denon AVR Receiver** device type with Sharp/Denon protocol encoder (address 2, 12 commands including discrete power on/off and input selection)
- New `sharp.py` protocol encoder supporting the Sharp/Denon IR protocol family (5-bit address + 8-bit command, two-frame transmission with inversion check)
- Denon AVR media player entity shows as "Receiver" with discrete power on/off commands
- Button icons for number keys, Denon inputs (CD, DVD, Tuner, Phono), surround modes

## [0.4.0] - 2026-04-02

### Added
- **Attach to existing device** option in config flow — IR button entities merge into an existing device (e.g., your LG WebOS TV) instead of creating a separate device
- Media player entity is skipped in attach mode (the target device already has one)
- New config flow with setup mode choice: "Create new device" or "Attach to existing device"

## [0.3.3] - 2026-04-02

### Fixed
- Added icon URL to hacs.json so HACS displays the integration icon

## [0.3.2] - 2026-04-02

### Fixed
- Added error handling around IR send calls in button and media_player platforms (logs and re-raises `HomeAssistantError`)
- Fixed `sw_version` mismatch in button and media_player `DeviceInfo` (was `0.3.0`, now matches manifest)

## [0.3.1] - 2026-04-02

### Fixed
- Fixed repository link in README (`your-repo` → `SurfHost`)

## [0.3.0] - 2026-04-02

### Added
- Support for the official `infrared-protocols` library (`home-assistant-libs/infrared-protocols`)
  - Uses `make_lg_tv_command()` from the library for LG TV commands when available
  - Automatic fallback to built-in NEC encoder if the library is not installed
- New `ir_commands.py` module as unified command factory layer

### Fixed
- Brand icons now in `brand/` directory with both `icon.png` and `logo.png` (HA 2026.3+ requirement)
- Removed SVG from brand folder (HA only supports PNG)

### Changed
- Button and media_player platforms now use `ir_commands` factory instead of directly instantiating NEC commands
- Updated documentation URL to GitHub repository
- Added `@SurfHost` as codeowner

## [0.2.0] - 2026-04-01

### Added
- Integration icon in PNG and PNG@2x formats
- Proper `DeviceInfo` on all entities so buttons and media_player group under one device
- Optional device name field in config flow (e.g., "Woonkamer TV")

### Changed
- Renamed from `ir_test_remote` to `infrared_remote`

### Fixed
- Entities not grouping under a device in the HA device registry

## [0.1.0] - 2026-04-01

### Added
- Initial release (as `ir_test_remote`)
- Built-in NEC protocol encoder (no external dependencies)
- LG TV device type with 18 NEC commands (address 0x04)
- Samsung TV device type with 15 NEC commands (address 0x07)
- Raw Test Signal mode for verifying the IR chain
- `media_player` entity with assumed state (turn on/off, volume, mute)
- `button` entities for each remote command with MDI icons
- Config flow with emitter selection and device type dropdown
- Tested with Broadlink RM4 Pro as emitter and LG TV as target
