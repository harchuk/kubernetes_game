# Kubernetes Cluster Clash Online Platform

## Vision
Создать веб-платформу, где игроки могут играть в Kubernetes Cluster Clash (основной режим и junior) через браузер, с поддержкой онлайн-комнат, историй партий и современного UI.

## Key Requirements
- **Многопользовательский режим**: 2–4 игрока в одной комнате, наблюдатели.
- **Два режима игры**: Classic (полные правила) и Junior (6+).
- **Авторизация**: гостевой вход + регистрация (email/OAuth).
- **Истории партий**: запись результата, игроков, лога ходов.
- **Реалтайм**: синхронное обновление стола через WebSocket.
- **Современный UI**: Tailwind CSS + Headless UI, адаптивный дизайн.
- **Инфраструктура**: контейнеризация, CI/CD, подготовка к облачному деплою.

## Architecture Overview

### Frontend
- React + TypeScript.
- State management: Zustand или Redux Toolkit (решить на этапе имплементации).
- Routing: React Router.
- Styling: Tailwind CSS + Headless UI.
- WebSocket client (native или socket.io-client, если выберем совместимый сервер).

### Backend (API + Realtime)
- FastAPI (Python 3.11+).
- REST endpoints: аутентификация, управление пользователями/комнатами, получение истории партий.
- WebSocket endpoints: игровая шина (подключение к комнате, обмен действиями, обновления состояния).
- Background tasks: Redis для временных состояний (возможность).
- Data validation: Pydantic models.

### Storage
- PostgreSQL: пользователи, комнаты, истории партий, журналы.
- Redis (опционально): сессии/кэш/брокер событий.

### Infrastructure
- Docker + docker-compose для разработки.
- Poetry или uv для управления Python-зависимостями; pnpm/yarn для фронта.
- GitHub Actions: линтеры, pytest, frontend tests (Vitest/Playwright).
- Deploy target (по согласованию): Fly.io / Render / Railway / AWS.

## Roadmap (MVP)

1. **Project Setup**
   - Монорепо: корень с `frontend/`, `backend/`, `docker-compose.yml`, общими настройками.
   - Инструменты: форматирование (black/isort, prettier), lint (ruff/eslint), pre-commit.
   - CI: GitHub Actions с lint/test для двух частей.

2. **Backend Skeleton**
   - FastAPI приложение со схемой маршрутов.
   - Подключение к PostgreSQL через SQLModel/SQLAlchemy.
   - Базовые сущности: User, GameRoom, GameSession, TurnLog.
   - WebSocket endpoint с заглушкой (подключение/отключение, broadcast).

3. **Frontend Skeleton**
   - React + Vite + Tailwind setup.
   - Главное меню: выбор режима (Classic / Junior).
   - Лобби: список комнат, создание комнаты, присоединение.
   - Стол: базовый макет поля, панели игроков, журнал событий.

4. **Game Logic Integration**
   - Моделирование состояния игры на сервере: колода, рынок, руки, ресурсы, SLO.
   - Валидация ходов, рассылка состояния всем участникам.
   - Сохранение партий по итогам сессии.

5. **User Experience**
   - Авторизация (гость + email/OAuth).
   - Профиль пользователя с историей партий и статистикой.
   - Настройки стола (таймер хода, приватность комнаты).

6. **Testing & Launch**
   - Unit/Integration tests (backend, frontend).
   - E2E тесты (Playwright/Cypress).
   - Нагрузочные проверки WebSocket.
   - Деплой preview-версии.

## Initial Implementation Plan
- Создать каталоги `backend/`, `frontend/`, `infra/`.
- Подготовить `docker-compose.yml` со службами: fastapi, postgres, redis, frontend-dev.
- Backend: FastAPI + uvicorn, Poetry; базовые зависимости (fastapi, uvicorn, asyncpg, sqlmodel, redis, pydantic-settings).
- Frontend: Vite + React + Tailwind + Headless UI; ESLint/Prettier.
- CI: GitHub Actions workflow `ci.yml` (install, lint, test для обеих частей).
- Документировать локальный запуск в README.

## Open Questions
- Авторизация: запланирована через OAuth (GitHub/Google) или достаточно гостевого входа на MVP?
- Нужно ли поддерживать асинхронный режим (игра по переписке) или только синхронный?
- Как детально хранить историю: полный лог ходов/таймстамп каждой карты или сокращённый итог?

(Ответы на эти вопросы помогут уточнить архитектуру.)
