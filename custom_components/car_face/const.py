from __future__ import annotations

from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo

DOMAIN = "car_face"
PLATFORMS = ["binary_sensor", "number", "sensor", "time"]

CONF_NAME = "name"
CONF_ENABLED = "enabled"
CONF_TRIGGER_TYPE = "trigger_type"
CONF_ON_ENABLED = "on_enabled"
CONF_ON_SENSORS = "on_sensors"
CONF_OFF_ENABLED = "off_enabled"
CONF_OFF_SENSORS = "off_sensors"
CONF_TARGET_ENTITY = "target_entity"
# Переключатели: можно включать/выключать устройство и кнопки по отдельности.
CONF_DEVICE_ENABLED = "device_enabled"
CONF_BUTTONS_ENABLED = "buttons_enabled"
# Кнопки-действия: нажимаются при срабатывании сенсора (напр. кнопка
# «открыть доступ» контроллера Болид С2000-2 из интеграции SecurARM Sensor).
CONF_TARGET_BUTTONS = "target_buttons"
CONF_RESET_OPTIONS = "reset_options"
CONF_PULSE_SEC = "pulse_sec"

# legacy keys (только для миграции старых записей)
CONF_TRIGGER_SENSORS = "trigger_sensors"
CONF_MOTION_SENSORS = "motion_sensors"
CONF_LIGHT = "light"
CONF_USE_ILLUMINANCE = "use_illuminance"
CONF_ILLUMINANCE_SENSOR = "illuminance_sensor"

TRIGGER_MOTION = "motion"
TRIGGER_OPENING = "opening"
TRIGGER_ANY = "any"
TRIGGER_TYPE_OPTIONS = [TRIGGER_MOTION, TRIGGER_OPENING, TRIGGER_ANY]

# Сенсоры открытия: их предлагает селектор Car&Face (MQTT-сенсоры правил Car&Face
# приходят как binary_sensor с device_class=opening).
OPENING_DEVICE_CLASSES = ["opening", "garage_door", "door", "window"]

DEFAULT_NAME = "Car&Face: открытие"
DEFAULT_ENABLED = True
DEFAULT_ON_ENABLED = True
DEFAULT_OFF_ENABLED = True
DEFAULT_TRIGGER_TYPE = TRIGGER_OPENING
DEFAULT_OFF_DELAY_MIN = 1
DEFAULT_DEVICE_ENABLED = True
DEFAULT_BUTTONS_ENABLED = True
DEFAULT_PULSE_SEC = 0  # 0 = держать, пока активен сенсор; >0 = импульс, секунд
DEFAULT_START_TIME = "00:00:00"
DEFAULT_END_TIME = "23:59:59"

CTRL_OFF_DELAY_MIN = "off_delay_min"
CTRL_START_TIME = "start_time"
CTRL_END_TIME = "end_time"

DEFAULT_CTRL_VALUES = {
    CTRL_OFF_DELAY_MIN: DEFAULT_OFF_DELAY_MIN,
    CTRL_START_TIME: DEFAULT_START_TIME,
    CTRL_END_TIME: DEFAULT_END_TIME,
}

DATA_RUNTIME = "runtime"
EVENT_UPDATE = f"{DOMAIN}_update"

ATTR_STATUS = "status"
ATTR_LAST_REASON = "last_reason"
ATTR_LAST_ACTION = "last_action"
ATTR_LAST_ACTION_AT = "last_action_at"
ATTR_ACTIVE_ON_SENSORS = "active_on_sensors"
ATTR_ACTIVE_OFF_SENSORS = "active_off_sensors"
ATTR_TARGET_STATE = "target_state"
ATTR_TARGET_BUTTONS = "target_buttons"
ATTR_LAST_BUTTONS = "last_buttons"
ATTR_NEXT_OFF_AT = "next_off_at"

INTEGRATION_MANUFACTURER = "Bezuglyy"
INTEGRATION_MODEL = "Car&Face"
INTEGRATION_SW_VERSION = "1.3.0"

DIAG_ENTITY_CATEGORY = EntityCategory.DIAGNOSTIC


def build_device_info(entry_id: str, entry_title: str | None = None) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name=entry_title or DEFAULT_NAME,
        manufacturer=INTEGRATION_MANUFACTURER,
        model=INTEGRATION_MODEL,
        sw_version=INTEGRATION_SW_VERSION,
    )
