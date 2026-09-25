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
Реакция на распознавание **Car&Face**: по **сенсорам открытия** (MQTT-сенсоры Car&Face, `device_class: opening`) интеграция включает (открывает) выбранное устройство — реле шлагбаума, ворота или свет — **и/или нажимает выбранные кнопки** (например «открыть доступ» контроллера Болид С2000-2), с учётом расписания.

### Возможности
- **Сенсоры открытия** — выбор нескольких сенсоров (`binary_sensor`, класс `opening` / `garage_door` / `door` / `window`)
- **Исполняемое устройство** — реле шлагбаума/ворот (`switch`) или свет (`light`)
- **Импульс** — пауза 0: включить и сразу выключить (как кнопка шлагбаума); больше 0 — держать N минут
- **Расписание** — время начала/окончания
- **Кнопки-действия** — нажимаются при срабатывании (напр. кнопка «открыть доступ» Болид С2000-2 из интеграции SecurARM Sensor)
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
## Изменения 1.3.0 (25.09.2026)

- **Кнопки-действия** (`target_buttons`): мультивыбор `button.*` — кнопки нажимаются один раз на срабатывание (по фронту сенсора). Пример: `button.skif_pku_1_vkhod_otkryt_dostup` («открыть доступ» контроллера Болид С2000-2). Действуют **вместе** с исполняемым устройством; устройство теперь необязательно, если выбраны кнопки.
- **Убрана «Освещённость»**: поля «Освещённость: блок включен»/«датчик», сущности порогов/минимума/максимума освещённости, яркости и «Цвет» удалены из интеграции (платформа `select` больше не используется). Осталась «Задержка выключения».
- Миграция записи **v8 → v9**: из data/options убираются поля освещённости, добавляется `target_buttons`; исполняемое устройство и сенсоры сохраняются.
- Диагностический сенсор: «Текущая освещённость» заменён на **«Нажатые кнопки»**.

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
Home Assistant custom integration for **Car&Face**: turns on (opens) a target device — barrier relay, gate or light — and/or presses selected buttons (e.g. a Bolid C2000-2 «open access» button) based on **opening sensors** (Car&Face MQTT sensors, `device_class: opening`), with an optional schedule.

### Features
- Multiple **opening sensors** (`binary_sensor`, class `opening` / `garage_door` / `door` / `window`)
- Target device: relay/gate (`switch`) or light (`light`)
- Pulse mode (delay 0) or hold for N minutes
- Schedule (start/end time) and a button-action list
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
**Автор / Author:**
![Bezuglyj E.N.](logo-bezuglyj.png)
## License / Лицензия
MIT
