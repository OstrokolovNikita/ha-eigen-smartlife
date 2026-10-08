# Eigen SmartLife

Independent Home Assistant custom integration for supported **Eigen appliances and selected Smart Life / Tuya devices** through **Tuya Device Sharing**.

It does **not** depend on Home Assistant's official `tuya` integration, LocalTuya, Tuya Local, Xtend Tuya, or a Tuya IoT Developer cloud project.

> Status: **0.2.0 test release**. The Eigen Stark-R01A refrigerator and Smart Life Measure socket are supported. The Eigen BD/ED / Foss dishwasher remains discovery-only until real DP data is available while it is online.

## Supported devices

### Eigen Stark-R01A refrigerator

Product ID: `gagu2uqowgklirxz`

Current entities:

- Control lock (`child_lock`)
- Fresh zone (`switch_chiller`)
- Refrigerator target temperature (`cool_temp_set`)
- Freezer target temperature (`cold_temp_set`)

Temperature limits are read from the live Tuya specification when available, with verified profile values used only as fallback.

### Smart Life Measure socket

Product ID: `999hv2s5ckom5zw2`

Current entities:

- Outlet power (`switch_1`)
- Current power (`cur_power`)
- Voltage (`cur_voltage`)
- Current (`cur_current`)
- Total energy (`add_ele`)
- Fault/problem bitmap (`fault`)
- Child lock (`child_lock`)
- Power restore behavior (`relay_status`)
- Indicator mode (`light_mode`)
- Countdown timer in seconds (`countdown_1`)

Read-only electrical values use the scale reported by the live Tuya specification.

### Eigen BD/ED / Foss dishwasher

Product ID: `qrs7owpuzw8uwjxl`

The integration recognizes the product for sanitized diagnostics, but intentionally creates no control entities yet. Program/status DPs will be added only after they are observed from the Device Sharing API; UI screenshots are not used to guess DP mappings.

## Architecture

- UI-only setup with Smart Life **User Code + QR authorization**
- `tuya-device-sharing-sdk>=0.2.15` (0.2.15 is the current tested baseline)
- Cloud push through Tuya MQTT where supported
- Product-scoped entity loading: unsupported Smart Life devices are not imported into Home Assistant; they are visible only in sanitized diagnostics for profile development
- Stable HA device/entity identifiers
- Automatic Device Sharing token refresh persistence
- Sanitized diagnostics: no access token, refresh token, local key, UUID or IP address
- No `configuration.yaml` changes

## Installation

### HACS custom repository (during testing)

1. Add `https://github.com/OstrokolovNikita/ha-eigen-smartlife` as a HACS custom repository of type **Integration**.
2. Install **Eigen SmartLife**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration → Eigen SmartLife**.
5. In Smart Life open **Me → Settings → Account and Security → User Code** and copy the code.
6. Enter the User Code in Home Assistant.
7. Scan the QR code with Smart Life, approve access, return to Home Assistant and submit the QR step.

### Manual test install

Copy `custom_components/eigen_smartlife/` to:

`/config/custom_components/eigen_smartlife/`

Restart Home Assistant and add **Eigen SmartLife** from **Settings → Devices & services**.

## Clean migration from other Tuya/Eigen experiments

Eigen SmartLife is standalone. For a clean test environment, remove old Eigen-specific experiments such as `eigen_tuya_bridge`, `xtend_tuya`, `tuya_local`/Tuya Local entries used for these appliances, and the official Tuya entry if it was only being kept for Eigen. Restart Home Assistant before adding Eigen SmartLife.

Do not delete unrelated integrations or device entries you still use for other hardware.

## Diagnostics

Use **Settings → Devices & services → Eigen SmartLife → three dots → Download diagnostics**.

Diagnostics intentionally include product ID, DP status/specification and local strategy metadata needed to add appliance support, but exclude credentials and local secrets.

## Known limitations in 0.2.0

- The dishwasher does not yet expose entities because it was offline when its Device Sharing DP specification was captured.
- Adding/removing Smart Life devices after integration startup may require reloading the integration.
- Cloud availability depends on Smart Life/Tuya Device Sharing services.

## Development / validation

The repository is prepared for:

- HACS validation (`hacs/action`)
- Home Assistant hassfest validation
- Python compile checks

Every functional change should increment the integration version, update `CHANGELOG.md`, pass CI and be tagged as a GitHub release after device testing.

## License

MIT


## Release model

Development commits on `main` are validated by HACS, Home Assistant hassfest
and Python compile checks. Published versions use semantic versions from
`custom_components/eigen_smartlife/manifest.json`.

When the manifest version changes, GitHub Actions automatically creates the
matching GitHub Release and tag (for example `v0.2.0`). HACS then sees the
release as a normal versioned update instead of a raw commit.

During rapid development HACS may cache repository metadata for a short time;
a manual repository refresh can reveal a new release sooner.
