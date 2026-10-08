"""Config flow for Eigen SmartLife."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tuya_sharing import LoginControl
import requests
import voluptuous as vol

from homeassistant.config_entries import SOURCE_REAUTH, ConfigFlow, ConfigFlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_ENDPOINT,
    CONF_TERMINAL_ID,
    CONF_TOKEN_INFO,
    CONF_USER_CODE,
    DOMAIN,
    TUYA_CLIENT_ID,
    TUYA_RESPONSE_CODE,
    TUYA_RESPONSE_MSG,
    TUYA_RESPONSE_QR_CODE,
    TUYA_RESPONSE_RESULT,
    TUYA_RESPONSE_SUCCESS,
    TUYA_SCHEMA,
)


class EigenSmartLifeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure Eigen SmartLife using Tuya Device Sharing QR login."""

    VERSION = 1

    def __init__(self) -> None:
        self._login = LoginControl()
        self._user_code = ""
        self._qr_token = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the Smart Life user code and request a QR token."""
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}

        if user_input is not None:
            try:
                success, response = await self._async_get_qr_code(
                    user_input[CONF_USER_CODE]
                )
            except (requests.exceptions.RequestException, ValueError):
                errors["base"] = "cannot_connect"
            else:
                if success:
                    return await self.async_step_scan()

                errors["base"] = "login_error"
                placeholders = {
                    TUYA_RESPONSE_MSG: str(
                        response.get(TUYA_RESPONSE_MSG, "Unknown error")
                    ),
                    TUYA_RESPONSE_CODE: str(response.get(TUYA_RESPONSE_CODE, "0")),
                }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_USER_CODE): str}),
            errors=errors,
            description_placeholders=placeholders,
        )

    async def async_step_scan(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show and confirm the Tuya/Smart Life QR authorization."""
        if user_input is None:
            return self._show_scan_form()

        try:
            success, info = await self.hass.async_add_executor_job(
                self._login.login_result,
                self._qr_token,
                TUYA_CLIENT_ID,
                self._user_code,
            )
        except (requests.exceptions.RequestException, ValueError):
            return self._show_scan_form(errors={"base": "cannot_connect"})

        if not success:
            try:
                await self._async_get_qr_code(self._user_code)
            except (requests.exceptions.RequestException, ValueError):
                return self._show_scan_form(errors={"base": "cannot_connect"})
            return self._show_scan_form(
                errors={"base": "login_error"},
                placeholders={
                    TUYA_RESPONSE_MSG: str(info.get(TUYA_RESPONSE_MSG, "Unknown error")),
                    TUYA_RESPONSE_CODE: str(info.get(TUYA_RESPONSE_CODE, "0")),
                },
            )

        entry_data = {
            CONF_USER_CODE: self._user_code,
            CONF_TOKEN_INFO: {
                "t": info["t"],
                "uid": info["uid"],
                "expire_time": info["expire_time"],
                "access_token": info["access_token"],
                "refresh_token": info["refresh_token"],
            },
            CONF_TERMINAL_ID: info[CONF_TERMINAL_ID],
            CONF_ENDPOINT: info[CONF_ENDPOINT],
        }

        if self.source == SOURCE_REAUTH:
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(),
                data=entry_data,
            )

        await self.async_set_unique_id(str(info.get("uid", self._user_code)))
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=str(info.get("username") or "Smart Life"),
            data=entry_data,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Start reauthentication."""
        user_code = entry_data.get(CONF_USER_CODE)
        if isinstance(user_code, str):
            try:
                success, _ = await self._async_get_qr_code(user_code)
            except (requests.exceptions.RequestException, ValueError):
                success = False
            if success:
                return await self.async_step_scan()
        return await self.async_step_reauth_user_code()

    async def async_step_reauth_user_code(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for a new Smart Life user code during reauthentication."""
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}

        if user_input is not None:
            try:
                success, response = await self._async_get_qr_code(
                    user_input[CONF_USER_CODE]
                )
            except (requests.exceptions.RequestException, ValueError):
                errors["base"] = "cannot_connect"
            else:
                if success:
                    return await self.async_step_scan()
                errors["base"] = "login_error"
                placeholders = {
                    TUYA_RESPONSE_MSG: str(
                        response.get(TUYA_RESPONSE_MSG, "Unknown error")
                    ),
                    TUYA_RESPONSE_CODE: str(response.get(TUYA_RESPONSE_CODE, "0")),
                }

        return self.async_show_form(
            step_id="reauth_user_code",
            data_schema=vol.Schema({vol.Required(CONF_USER_CODE): str}),
            errors=errors,
            description_placeholders=placeholders,
        )

    def _show_scan_form(
        self,
        errors: dict[str, str] | None = None,
        placeholders: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        return self.async_show_form(
            step_id="scan",
            data_schema=vol.Schema(
                {
                    vol.Optional("QR"): selector.QrCodeSelector(
                        config=selector.QrCodeSelectorConfig(
                            data=f"tuyaSmart--qrLogin?token={self._qr_token}",
                            scale=5,
                            error_correction_level=selector.QrErrorCorrectionLevel.QUARTILE,
                        )
                    )
                }
            ),
            errors=errors,
            description_placeholders=placeholders,
        )

    async def _async_get_qr_code(self, user_code: str) -> tuple[bool, dict[str, Any]]:
        response = await self.hass.async_add_executor_job(
            self._login.qr_code,
            TUYA_CLIENT_ID,
            TUYA_SCHEMA,
            user_code,
        )
        success = bool(response.get(TUYA_RESPONSE_SUCCESS, False))
        if success:
            self._user_code = user_code
            self._qr_token = response[TUYA_RESPONSE_RESULT][TUYA_RESPONSE_QR_CODE]
        return success, response
