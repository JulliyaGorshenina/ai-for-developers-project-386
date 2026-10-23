# Календарь звонков

[![hexlet-check](https://github.com/JulliyaGorshenina/ai-for-developers-project-386/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/JulliyaGorshenina/ai-for-developers-project-386/actions)

Сервис бронирования звонков по мотивам [cal.com](https://cal.com): владелец
публикует типы встреч и своё расписание, а гость выбирает тип, свободный слот и
записывается на звонок.

Учебный проект Хекслета: https://ru.hexlet.io/programs/ai-for-developers
Как это должно работать: https://files.hexlet.app/a/2ipc5m

## Возможности

- Владелец задаёт **типы встреч** (название, описание, длительность) и **недельное
  расписание** (окна доступности).
- Гость выбирает тип встречи, видит свободные слоты в окне 14 дней и оставляет
  заявку (имя, email, комментарий).
- Слоты строятся с шагом, равным длительности типа; занятый слот не предлагается,
  а повторная запись (в том числе на другой тип, пересекающийся по времени)
  отклоняется сервером.
- Владелец видит список предстоящих встреч **всех типов** и может отменить запись
  (слот снова становится свободным).
- Без регистрации, личных кабинетов и синхронизации с внешними календарями.

## Контракт

API описан по принципу **Design First**: источник правды — TypeSpec в `spec/`. Из
него генерируются OpenAPI 3.1, клиентский TS-SDK и серверные Pydantic-модели.
Порядок изменений: правка TypeSpec → генерация → код обеих сторон.
Дрейф ловится в CI (`git diff` после перегенерации).

## Стек

- **Backend:** Python, FastAPI, SQLite (стандартный `sqlite3`).
- **Frontend:** TypeScript, Vite (vanilla TS), сгенерированный клиент
  (`@hey-api/openapi-ts`).
- **Контракт:** TypeSpec → OpenAPI 3.1; серверные модели —
  `datamodel-code-generator`.
- **Тесты/линтеры:** pytest, ruff; vitest, eslint, tsc; Playwright (e2e).
- **CI/CD:** GitHub Actions, release-please.

## Установка

```bash
git clone https://github.com/JulliyaGorshenina/ai-for-developers-project-386.git
cd ai-for-developers-project-386
```

### Backend

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python -m pip install -r backend\requirements.txt
```

### Frontend и контракт

```bash
cd spec; npm ci; cd ..            # инструменты TypeSpec
cd frontend; npm ci; cd ..        # фронтенд + генератор SDK
```

## Использование

```powershell
# API + отдача собранного фронтенда: http://127.0.0.1:8000
backend\.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir backend

# dev-режим фронтенда: http://127.0.0.1:5173 (проксирует /api на :8000)
cd frontend; npm run dev
```

- Главная страница: `/`
- Запись: `/booking.html`
- Кабинет владельца: `/admin.html`

### Переменные окружения

| Переменная          | По умолчанию          | Назначение                     |
| ------------------- | --------------------- | ------------------------------ |
| `BOOKING_TZ`        | `Europe/Moscow`       | Часовой пояс для генерации слотов |
| `AVAILABILITY_DAYS` | `14`                  | Длина окна записи в днях       |
| `DB_PATH`           | `backend/bookings.db` | Файл базы данных SQLite        |

## Генерация контракта

```powershell
cd spec; npx tsp compile .                        # -> spec/openapi/openapi.json
cd ..\frontend; npm run gen:api                    # -> src/api/generated/
cd ..; backend\.venv\Scripts\python -m datamodel_code_generator `
  --input spec\openapi\openapi.json --input-file-type openapi `
  --output-model-type pydantic_v2.BaseModel --openapi-scopes schemas `
  --target-python-version 3.12 --disable-timestamp `
  --output backend\app\generated\models.py
```

## Тесты и линтеры

```powershell
# backend
backend\.venv\Scripts\python -m pytest backend
backend\.venv\Scripts\python -m ruff check backend
backend\.venv\Scripts\python -m ruff format --check backend

# frontend
cd frontend; npm run lint; npm run typecheck; npm test; npm run build

# e2e (нужен собранный фронтенд и Chromium)
cd ..; npm install; npx playwright install chromium; npx playwright test
```

## Коммиты и релизы

Коммиты — по [Conventional Commits](https://www.conventionalcommits.org/).
[release-please](https://github.com/googleapis/release-please) на каждый push в
`main` читает историю коммитов, собирает `CHANGELOG.md` и открывает release-PR с
новой версией по правилам семантического версионирования. Подробнее — в
[AGENTS.md](AGENTS.md).

---

<details>
<summary>Автоматические тесты Хекслета</summary>

Тесты запускаются на каждый коммит. За запуск отвечает файл `.github/workflows/hexlet-check.yml` — не удаляйте и не переименовывайте ни его, ни репозиторий.

</details>

## О Хекслете

[Хекслет](https://ru.hexlet.io/) — школа программирования: авторские программы обучения с практикой, поддержкой наставников и реальными проектами, которые остаются в резюме. Этот репозиторий — один из таких проектов.
