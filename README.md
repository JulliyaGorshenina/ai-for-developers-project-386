# Календарь звонков

[![hexlet-check](https://github.com/JulliyaGorshenina/ai-for-developers-project-386/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/JulliyaGorshenina/ai-for-developers-project-386/actions)

Сервис бронирования звонков по мотивам [cal.com](https://cal.com): владелец
календаря публикует свободные слоты, а гость выбирает удобное время и
записывается на звонок.

Учебный проект Хекслета: https://ru.hexlet.io/programs/ai-for-developers
Как это должно работать: https://files.hexlet.app/a/2ipc5m

## Возможности

- Слоты по 30 минут, сгенерированные из недельного расписания владельца.
- Гость выбирает день и время и оставляет заявку (имя, email, комментарий).
- Владелец задаёт недельное расписание, видит список предстоящих встреч и
  может отменить запись (слот снова становится свободным).
- Без регистрации, личных кабинетов и синхронизации с внешними календарями.

## Стек

- **Backend:** Python, FastAPI, SQLite (стандартный `sqlite3`).
- **Frontend:** TypeScript, Vite (vanilla TS).
- **Тесты/линтеры:** pytest, ruff; vitest, eslint, tsc.
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

### Frontend

```bash
cd frontend
npm install
cd ..
```

## Использование

Запустите backend (и, при необходимости, frontend dev-сервер):

```powershell
# API + отдача собранного фронтенда: http://127.0.0.1:8000
backend\.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir backend

# dev-режим фронтенда: http://127.0.0.1:5173 (проксирует /api на :8000)
cd frontend; npm run dev
```

- Страница записи: `/`
- Страница владельца: `/admin.html` (токен из `ADMIN_TOKEN`, по умолчанию
  `dev-admin-token`)

### Переменные окружения

| Переменная     | По умолчанию        | Назначение                     |
| -------------- | ------------------- | ------------------------------ |
| `ADMIN_TOKEN`  | `dev-admin-token`   | Токен доступа к API владельца  |
| `BOOKING_TZ`   | `Europe/Moscow`     | Часовой пояс для отображения   |
| `SLOT_MINUTES` | `30`                | Длина слота в минутах          |
| `DB_PATH`      | `backend/bookings.db` | Файл базы данных SQLite      |

## Тесты и линтеры

```powershell
# backend
backend\.venv\Scripts\python -m pytest backend
backend\.venv\Scripts\python -m ruff check backend

# frontend
cd frontend; npm run lint; npm run typecheck; npm test
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
