# Car&Face
![Release](https://img.shields.io/github/v/release/bezuglyy/car_face?label=Release&style=flat-square) ![HACS](https://img.shields.io/badge/HACS-Custom%20Repository-purple?style=flat-square) ![License](https://img.shields.io/github/license/bezuglyy/car_face?style=flat-square) ![HA](https://img.shields.io/badge/HA-2025.1%2B-2ea44f?style=flat-square)

Кастомная интеграция для [Home Assistant](https://www.home-assistant.io) · версия **1.1.0**.

![icon](custom_components/car_face/brand/icon.png)

| | |
|---|---|
| Домен | `car_face` |
| Версия | 1.1.0 |
| Тип | custom integration |

## Описание
Реакция на распознавание **Car&Face**: по **сенсорам открытия** (MQTT-сенсоры Car&Face, `device_class: opening`) интеграция включает (открывает) выбранное устройство — реле шлагбаума, ворота или свет — с учётом расписания и (опционально) освещённости.

### Возможности
- **Сенсоры открытия** — выбор нескольких сенсоров (`binary_sensor`, класс `opening` / `garage_door` / `door` / `window`)
- **Исполняемое устройство** — реле шлагбаума/ворот (`switch`) или свет (`light`)
- **Импульс** — пауза 0: включить и сразу выключить (как кнопка шлагбаума); больше 0 — держать N минут
- **Расписание** — время начала/окончания, блок «только при низкой освещённости»
- **Несколько записей на одно устройство** — например Post2 / Post3 / Post5 на одно реле
- **Редактирование** — любая запись меняется через «Настройки» (Options)
- **Диагностика** — статус, последнее действие и его время, причина решения, запланированное выключение, статус сценария
- Русская и английская локализация, фирменные иконки

### Установка
1. Скопируйте папку `custom_components/car_face/` в каталог `custom_components/` конфигурации Home Assistant.
2. Перезапустите Home Assistant.
3. Настройки → Устройства и службы → Добавить интеграцию → **Car&Face**.

> Установка через HACS: добавьте репозиторий `https://github.com/bezuglyy/car_face` как Custom repository (категория Integration).

### Пример (шлагбаум по распознаванию номера)
| Поле | Значение |
|---|---|
| Сенсоры открытия (MQTT) | `binary_sensor.car_face_mqtt_shlagbaum_post2_svoi_nomera` |
| Исполняемое устройство | `switch.usb_power2_switch_1` (реле шлагбаума) |
| Пауза до выключения, мин | `0` (импульс) |

---
## Изменения 1.1.0 (23.09.2026)
- Первый выпуск Car&Face на базе логики `motion_control` (**сама логика не менялась**).
- Селектор сенсоров ограничен **сенсорами открытия** (`binary_sensor` + `device_class: opening/garage_door/door/window`).
- Тип срабатывания по умолчанию — «Открытие (шлагбаум/ворота/дверь)».
- **На одно устройство можно добавить несколько записей** (уникальность «название + устройство») — Post2/Post3/Post5 на одно реле.
- Русские подписи («Сенсоры открытия (MQTT)», «Исполняемое устройство»), локализация RU/EN, фирменные иконки Car&Face.
- Исправлены 4 дефекта базовой логики (актуальны для `motion_control` 1.0.1):
  1. настройки записи затирались значениями по умолчанию при пустом `options` (в диагностике `status = missing_target`);
  2. падение `datetime.now(hass.config.time_zone)` (в современных версиях HA `time_zone` — строка) → `dt_util.now()`;
  3. окно настроек (Options) не открывалось — `AttributeError: property 'config_entry' has no setter` (HA 2024.11+);
  4. диагностические сенсоры с `device_class: timestamp` падали (получали строку) → `datetime`.
- `AbortFlow` больше не проглатывается общим `except` — повторное добавление записи корректно отбрасывается.

> В проекте-источнике добавлены HA-тесты (10 проверок): форма и селектор открытия, добавление двух записей
> на одно реле, дубль → abort, валидация, редактирование через Options, логика вкл/выкл и паузы, регрессии дефектов.

---
## Description
Home Assistant custom integration for **Car&Face**: turns on (opens) a target device — barrier relay, gate or light — based on **opening sensors** (Car&Face MQTT sensors, `device_class: opening`), with optional schedule and illuminance condition.

### Features
- Multiple **opening sensors** (`binary_sensor`, class `opening` / `garage_door` / `door` / `window`)
- Target device: relay/gate (`switch`) or light (`light`)
- Pulse mode (delay 0) or hold for N minutes
- Schedule (start/end time) and optional illuminance threshold
- Several entries for the same device (Post2 / Post3 / Post5 → one relay)
- Edit any entry via Options; diagnostics sensors and scenario status
- Russian and English localization, Car&Face brand icons

### Installation
1. Copy the `custom_components/car_face/` folder into the `custom_components/` directory of your Home Assistant configuration.
2. Restart Home Assistant.
3. Settings → Devices & Services → Add Integration → **Car&Face**.

> HACS: add `https://github.com/bezuglyy/car_face` as a Custom repository (category Integration).

### Changes 1.1.0
First release built on `motion_control` logic (logic itself unchanged): opening-sensor selector, multiple entries per
device, RU/EN labels, Car&Face branding, plus 4 bug fixes (settings overwritten by defaults when `options` was empty;
`datetime.now(config.time_zone)` `TypeError`; options dialog failing on HA 2024.11+; timestamp diagnostic sensors
crashing) and correct `AbortFlow` handling.

---
## Изменения 1.2.0 (24.09.2026)
- **Режим «Импульс, сек»** (`pulse_sec`): реле включается и **выключается через N секунд**, даже если сенсор
  открытия остаётся активным — как кнопка шлагбаума. `0` — прежнее поведение (держать, пока сенсор активен).
  Повторное срабатывание по тому же событию не происходит, пока сенсор не отпустят.
- Поле «Импульс, сек» в форме добавления и в «Настройках» (0…1200, шаг 1).
- HA-тесты: 13 проверок (добавлены импульс, `pulse_sec=0` и наличие поля).

### Changes 1.2.0
- **Pulse mode** (`pulse_sec`): the relay turns on and off after N seconds even if the opening sensor stays active
  (barrier button behaviour). `0` = previous behaviour (hold while the sensor is active). No re-trigger while the
  sensor remains active. New field in the config and options flows; 13 HA tests.

---
**Автор / Author:**
![Bezuglyj E.N.](logo-bezuglyj.png)
## License / Лицензия
MIT
