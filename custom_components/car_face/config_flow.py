from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from homeassistant.helpers import selector

from .const import (
    CONF_BUTTONS_ENABLED,
    CONF_DEVICE_ENABLED,
    CONF_ENABLED,
    CONF_LIGHT,
    CONF_MOTION_SENSORS,
    CONF_NAME,
    CONF_OFF_ENABLED,
    CONF_OFF_SENSORS,
    CONF_ON_ENABLED,
    CONF_ON_SENSORS,
    CONF_PULSE_SEC,
    CONF_RESET_OPTIONS,
    CONF_TARGET_BUTTONS,
    CONF_TARGET_ENTITY,
    CONF_TRIGGER_SENSORS,
    CONF_TRIGGER_TYPE,
    CTRL_OFF_DELAY_MIN,
    DEFAULT_BUTTONS_ENABLED,
    DEFAULT_DEVICE_ENABLED,
    DEFAULT_ENABLED,
    DEFAULT_NAME,
    DEFAULT_OFF_DELAY_MIN,
    DEFAULT_OFF_ENABLED,
    DEFAULT_ON_ENABLED,
    DEFAULT_PULSE_SEC,
    DEFAULT_TRIGGER_TYPE,
    DOMAIN,
    OPENING_DEVICE_CLASSES,
    TRIGGER_TYPE_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


def _clean_entity(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    value = value.strip()
    if not value or value.lower() == "none":
        return ""
    return value


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = value.strip()
        if not value or value.lower() == "none":
            return []
        return [value]
    if isinstance(value, (list, tuple, set)):
        result: list[str] = []
        for item in value:
            ent = _clean_entity(item)
            if ent:
                result.append(ent)
        return result
    return []


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_entry_payload(data: dict | None) -> dict:
    """Смапить payload записи в канонический вид (с дефолтами).

    ВНИМАНИЕ: результат всегда полный (все ключи). Для слияния data+options
    использовать ``merge_entry_payload`` — иначе дефолты затирают настройки.
    """
    data = dict(data or {})
    on_sensors = data.get(CONF_ON_SENSORS)
    if on_sensors is None:
        on_sensors = data.get(CONF_TRIGGER_SENSORS)
    if on_sensors is None:
        on_sensors = data.get(CONF_MOTION_SENSORS)

    return {
        CONF_NAME: str(data.get(CONF_NAME) or DEFAULT_NAME),
        CONF_ENABLED: _as_bool(data.get(CONF_ENABLED), DEFAULT_ENABLED),
        CONF_TRIGGER_TYPE: str(data.get(CONF_TRIGGER_TYPE) or DEFAULT_TRIGGER_TYPE),
        CONF_ON_ENABLED: _as_bool(data.get(CONF_ON_ENABLED), DEFAULT_ON_ENABLED),
        CONF_ON_SENSORS: _as_list(on_sensors),
        CONF_OFF_ENABLED: _as_bool(data.get(CONF_OFF_ENABLED), DEFAULT_OFF_ENABLED),
        CONF_OFF_SENSORS: _as_list(data.get(CONF_OFF_SENSORS)),
        CONF_TARGET_ENTITY: _clean_entity(
            data.get(CONF_TARGET_ENTITY) or data.get(CONF_LIGHT)
        ),
        CONF_TARGET_BUTTONS: _as_list(data.get(CONF_TARGET_BUTTONS)),
        CONF_DEVICE_ENABLED: _as_bool(
            data.get(CONF_DEVICE_ENABLED), DEFAULT_DEVICE_ENABLED
        ),
        CONF_BUTTONS_ENABLED: _as_bool(
            data.get(CONF_BUTTONS_ENABLED), DEFAULT_BUTTONS_ENABLED
        ),
        CTRL_OFF_DELAY_MIN: _as_int(
            data.get(CTRL_OFF_DELAY_MIN), DEFAULT_OFF_DELAY_MIN
        ),
        CONF_PULSE_SEC: _as_int(data.get(CONF_PULSE_SEC), DEFAULT_PULSE_SEC),
    }


def merge_entry_payload(data: dict | None, options: dict | None) -> dict:
    """Слить data и options записи.

    Options применяются только если реально заданы: пустой options не должен
    затирать data дефолтами (иначе запись «теряет» устройство и сенсоры).
    """
    merged = normalize_entry_payload(data)
    if options:
        merged.update(normalize_entry_payload(options))
    return merged


def _validate(data: dict) -> dict[str, str]:
    errors: dict[str, str] = {}
    # Должно быть активно хотя бы одно действие: устройство ИЛИ кнопки.
    device_on = _as_bool(
        data.get(CONF_DEVICE_ENABLED), DEFAULT_DEVICE_ENABLED
    ) and bool(data.get(CONF_TARGET_ENTITY))
    buttons_on = _as_bool(
        data.get(CONF_BUTTONS_ENABLED), DEFAULT_BUTTONS_ENABLED
    ) and bool(data.get(CONF_TARGET_BUTTONS))
    if not device_on and not buttons_on:
        errors["base"] = "nothing_enabled"
        return errors
    if (
        data.get(CONF_ENABLED, DEFAULT_ENABLED)
        and data.get(CONF_ON_ENABLED, DEFAULT_ON_ENABLED)
        and not data.get(CONF_ON_SENSORS)
    ):
        errors["base"] = "need_on_sensors"
        return errors
    return errors


def _multi_binary_sensor_selector() -> selector.EntitySelector:
    """Селектор сенсоров открытия.

    Car&Face (и его MQTT-правила) публикуют сенсоры как binary_sensor с
    device_class=opening, поэтому список ограничен сенсорами открытия:
    opening / garage_door / door / window.
    """
    return selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain=["binary_sensor"],
            device_class=OPENING_DEVICE_CLASSES,
            multiple=True,
        )
    )


def _target_buttons_selector() -> selector.EntitySelector:
    """Мультивыбор кнопок-действий (нажимаются при срабатывании).

    Пример: кнопки «открыть доступ» контроллеров доступа Болид (С2000-2) из
    интеграции SecurARM Sensor (`button.skif_pku_1_vkhod_otkryt_dostup`).
    """
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain=["button"], multiple=True)
    )


def _single_target_selector() -> selector.EntitySelector:
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain=["light", "switch"], multiple=False)
    )


def build_schema(data: dict, *, include_reset: bool) -> vol.Schema:
    data = normalize_entry_payload(data)
    fields: dict[Any, Any] = {
        vol.Required(CONF_NAME, default=data[CONF_NAME]): str,
        vol.Optional(
            CONF_ENABLED, default=data[CONF_ENABLED]
        ): selector.BooleanSelector(),
        vol.Optional(
            CONF_TRIGGER_TYPE, default=data[CONF_TRIGGER_TYPE]
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=TRIGGER_TYPE_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
                translation_key=CONF_TRIGGER_TYPE,
            )
        ),
        vol.Optional(
            CONF_ON_ENABLED, default=data[CONF_ON_ENABLED]
        ): selector.BooleanSelector(),
        vol.Optional(
            CONF_ON_SENSORS, default=data[CONF_ON_SENSORS]
        ): _multi_binary_sensor_selector(),
        vol.Optional(
            CONF_OFF_ENABLED, default=data[CONF_OFF_ENABLED]
        ): selector.BooleanSelector(),
        vol.Optional(
            CONF_OFF_SENSORS, default=data[CONF_OFF_SENSORS]
        ): _multi_binary_sensor_selector(),
        vol.Optional(
            CONF_PULSE_SEC, default=data[CONF_PULSE_SEC]
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0, max=1200, step=1, mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Optional(
            CTRL_OFF_DELAY_MIN, default=data[CTRL_OFF_DELAY_MIN]
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0, max=240, step=1, mode=selector.NumberSelectorMode.BOX
            )
        ),
        # Устройство НЕобязательно: у селектора в UI появляется крестик (✕),
        # очистка убирает ключ -> запись «только кнопки». Дефолт НЕ задаём,
        # когда устройства нет: селектор не принимает пустое значение.
        vol.Optional(
            CONF_DEVICE_ENABLED, default=data[CONF_DEVICE_ENABLED]
        ): selector.BooleanSelector(),
        # Крестик очистки присылает null -> vol.Any(None, селектор) принимает и
        # сериализуется корректно (важно: порядок именно такой).
        (
            vol.Optional(CONF_TARGET_ENTITY, default=data[CONF_TARGET_ENTITY])
            if data[CONF_TARGET_ENTITY]
            else vol.Optional(CONF_TARGET_ENTITY)
        ): vol.Any(None, _single_target_selector()),
        vol.Optional(
            CONF_BUTTONS_ENABLED, default=data[CONF_BUTTONS_ENABLED]
        ): selector.BooleanSelector(),
        vol.Optional(
            CONF_TARGET_BUTTONS, default=data[CONF_TARGET_BUTTONS]
        ): _target_buttons_selector(),
    }
    if include_reset:
        fields[vol.Optional(CONF_RESET_OPTIONS, default=False)] = (
            selector.BooleanSelector()
        )
    return vol.Schema(fields)


class CarFaceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 9

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                cleaned = normalize_entry_payload(user_input)
                errors = _validate(cleaned)
                if not errors:
                    # Уникальность — по названию + устройству: на одно и то же
                    # устройство (реле шлагбаума) можно добавить несколько записей
                    # (Post2 / Post3 / Post5), а точный дубль блокируется.
                    await self.async_set_unique_id(
                        f"{DOMAIN}:{cleaned[CONF_NAME]}:{cleaned[CONF_TARGET_ENTITY]}"
                    )
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=cleaned[CONF_NAME], data=cleaned
                    )
                user_input = cleaned
            except data_entry_flow.AbortFlow:
                # AbortFlow — управляющее исключение Home Assistant, его нельзя
                # глотать общим except (иначе форма просто показывается заново).
                raise
            except Exception:
                _LOGGER.exception("Config flow validation failed")
                errors["base"] = "internal_error"
        return self.async_show_form(
            step_id="user",
            data_schema=build_schema(user_input or {}, include_reset=False),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return CarFaceOptionsFlow()


class CarFaceOptionsFlow(config_entries.OptionsFlow):
    # ``config_entry`` — свойство базового класса (HA 2024.11+), задавать его
    # в __init__ нельзя: у свойства нет сеттера (options flow падал).
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                reset = bool(user_input.pop(CONF_RESET_OPTIONS, False))
                if reset:
                    self.hass.config_entries.async_update_entry(
                        self.config_entry, title=self.config_entry.title
                    )
                    await self.hass.config_entries.async_reload(
                        self.config_entry.entry_id
                    )
                    return self.async_create_entry(title="", data={})

                cleaned = normalize_entry_payload(user_input)
                errors = _validate(cleaned)
                if not errors:
                    self.hass.config_entries.async_update_entry(
                        self.config_entry, title=cleaned[CONF_NAME]
                    )
                    return self.async_create_entry(title="", data=cleaned)
                user_input = cleaned
            except Exception:
                _LOGGER.exception("Options flow validation failed")
                errors["base"] = "internal_error"

        merged = merge_entry_payload(
            self.config_entry.data, self.config_entry.options
        )
        if user_input:
            merged.update(normalize_entry_payload(user_input))
        return self.async_show_form(
            step_id="init",
            data_schema=build_schema(merged, include_reset=True),
            errors=errors,
        )
