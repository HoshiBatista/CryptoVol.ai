# CryptoVol.ai

[![Bot Code Quality Check](https://github.com/HoshiBatista/CryptoVol.ai/actions/workflows/CI.yml/badge.svg?branch=main)](https://github.com/HoshiBatista/CryptoVol.ai/actions/workflows/CI.yml)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)
![Ruff](https://img.shields.io/badge/Linter-Ruff-yellow.svg)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-lightgrey.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/HoshiBatista/CryptoVol.ai/branch/main/graph/badge.svg)](https://codecov.io/gh/HoshiBatista/CryptoVol.ai)
[![codestyle](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub last commit](https://img.shields.io/github/last-commit/HoshiBatista/CryptoVol.ai.svg)](https://github.com/HoshiBatista/CryptoVol.ai/commits/main)
![Contributions](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)

[![GitHub stars](https://img.shields.io/github/stars/HoshiBatista/CryptoVol.ai?style=social)](https://github.com/HoshiBatista/CryptoVol.ai/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/HoshiBatista/CryptoVol.ai?style=social)](https://github.com/HoshiBatista/CryptoVol.ai/network/members)

CryptoVol.ai is a web platform for advanced cryptocurrency market volatility analysis and forecasting. The system uses econometric GARCH models to model volatility clustering and Monte Carlo simulations to generate probabilistic price forecasts.


erDiagram
    users {
        UUID id PK "Первичный ключ"
        VARCHAR email UK "Уникальный email"
        VARCHAR password_hash "Хеш пароля"
        TIMESTAMP created_at "Время создания"
    }

    cryptocurrency_data {
        UUID id PK "Первичный ключ"
        VARCHAR symbol "Символ (e.g., BTC, ETH)"
        TIMESTAMP timestamp UK "Временная метка"
        DECIMAL price_usd "Цена в USD"
        FLOAT daily_return "Дневная доходность"
    }

    portfolio_and_simulations {
        UUID id PK "Первичный ключ"
        UUID user_id FK "Внешний ключ к users"
        VARCHAR symbol "Символ актива в портфеле"
        DECIMAL amount "Количество актива"
        JSONB projected_value "Результаты симуляции"
    }

    users ||--o{ portfolio_and_simulations : "владеет"


    cryptovol.ai/
├── backend/                  # Бэкенд на FastAPI
│   ├── app/
│   │   ├── api/              # API эндпойнты
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── crypto_data.py
│   │   │   │   └── portfolio.py
│   │   │   └── __init__.py
│   │   ├── core/             # Конфигурация, безопасность
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── crud/             # Функции для работы с базой (Create, Read, Update, Delete)
│   │   ├── db/               # Настройки и сессии базы данных
│   │   ├── models/           # Модели SQLAlchemy
│   │   ├── schemas/          # Схемы Pydantic
│   │   └── services/         # Бизнес-логика, интеграция с ИИ
│   │       ├── data_collection_service.py
│   │       └── simulation_service.py
│   │   ├── __init__.py
│   │   └── main.py           # Главный файл приложения FastAPI
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                 # Фронтенд на React/TypeScript
│   ├── public/
│   ├── src/
│   │   ├── api/              # Функции для запросов к API
│   │   ├── components/       # Переиспользуемые компоненты (графики, кнопки и т.д.)
│   │   ├── pages/            # Страницы приложения (Login, Dashboard, Portfolio)
│   │   ├── store/            # Управление состоянием (Redux, Zustand)
│   │   ├── types/            # TypeScript типы
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── qf_models/                # Количественные финансы и ИИ
│   ├── models/
│   │   ├── garch_model.py
│   │   └── monte_carlo.py
│   ├── notebooks/            # Jupyter notebooks для исследований
│   └── scripts/              # Скрипты для обучения и обработки данных
│
├── logs/                     # Директория для хранения лог-файлов
│   ├── app.log
│   └── data_collection.log
│
├── docker-compose.yml        # Файл для оркестрации контейнеров (FastAPI, React, PostgreSQL, Redis)
└── README.md                 # Описание проекта
