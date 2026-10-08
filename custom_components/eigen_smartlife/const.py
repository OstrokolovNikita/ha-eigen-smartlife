"""Constants for Eigen SmartLife."""

from __future__ import annotations

import logging

from homeassistant.const import Platform

DOMAIN = "eigen_smartlife"
LOGGER = logging.getLogger(__package__)

CONF_ENDPOINT = "endpoint"
CONF_TERMINAL_ID = "terminal_id"
CONF_TOKEN_INFO = "token_info"
CONF_USER_CODE = "user_code"

# Tuya's Device Sharing credentials used by the Home Assistant QR authorization flow.
# No Tuya IoT Developer project, Access ID or Access Secret is required.
TUYA_CLIENT_ID = "HA_3y9q4ak7g4ephrvke"
TUYA_SCHEMA = "haauthorize"

TUYA_RESPONSE_CODE = "code"
TUYA_RESPONSE_MSG = "msg"
TUYA_RESPONSE_QR_CODE = "qrcode"
TUYA_RESPONSE_RESULT = "result"
TUYA_RESPONSE_SUCCESS = "success"

PLATFORMS: list[Platform] = [
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
    Platform.LOCK,
]

SIGNAL_UPDATE = f"{DOMAIN}_update_{{}}"
SIGNAL_NEW_DEVICE = f"{DOMAIN}_new_device"
SIGNAL_REMOVE_DEVICE = f"{DOMAIN}_remove_device_{{}}"

PRODUCT_ID_REFRIGERATOR_STARK_R01A = "gagu2uqowgklirxz"
PRODUCT_ID_DISHWASHER_BD_ED = "qrs7owpuzw8uwjxl"
PRODUCT_ID_MEASURE_SOCKET = "999hv2s5ckom5zw2"
