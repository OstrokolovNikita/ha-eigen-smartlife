# Changelog

## 0.2.0 - 2026-10-08

Smart plug support.

- Add Smart Life Measure socket profile for product ID `999hv2s5ckom5zw2`.
- Add outlet control, current power, voltage, current and total energy entities.
- Add fault/problem diagnostic, child lock, power restore behavior and indicator mode.
- Add configurable countdown timer.
- Electrical sensor scaling is taken from the live Tuya Device Sharing specification.
- Keep unsupported Smart Life products diagnostics-only.

## 0.1.1 - 2026-10-08

Device discovery update.

- Keep Home Assistant entities strictly limited to explicitly supported profiles.
- Passively enumerate and enrich all devices in the authorized Smart Life account for sanitized diagnostics.
- Add a `supported` marker to each diagnostic device.
- This enables accurate profile development for new devices from real Device Sharing `status`, `function`, `status_range` and local DP strategy data without guessing codes.

## 0.1.0 - 2026-10-08

Initial test release.

- Independent Smart Life/Tuya Device Sharing QR authorization.
- No dependency on Home Assistant's official Tuya integration.
- Eigen-only product filtering.
- Eigen Stark-R01A support for `child_lock`, `switch_chiller`, `cool_temp_set`, and `cold_temp_set`.
- Cloud push subscription and token refresh persistence.
- Sanitized diagnostics for supported Eigen products.
- Eigen BD/ED / Foss dishwasher recognized in diagnostics without guessed entities.
- HACS metadata, RU/EN translations and CI validation workflow.
