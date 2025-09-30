```
// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs
// Schema for the CryptoVol.ai project

// --- Модуль Пользователей ---

Table users {
  id uuid [pk, default: `uuid_generate_v4()`, note: 'Первичный ключ']
  email varchar [unique, not null, note: 'Уникальный email']
  password_hash varchar [not null]
  created_at timestamp [not null, default: `now()`]
}

Table user_profiles {
  user_id uuid [pk, note: 'Составной ключ, внешний ключ к users']
  full_name varchar
  avatar_url varchar
  settings jsonb [note: 'Настройки пользователя (тема, уведомления)']
}

Table roles {
  id int [pk]
  name varchar [unique, not null, note: 'Название роли (admin, user, premium)']
}

Table user_roles {
  user_id uuid [pk]
  role_id int [pk]
}


// --- Модуль Криптовалют и Моделей ---

Table cryptocurrencies {
  id int [pk]
  symbol varchar(16) [unique, not null, note: 'Символ (BTC, ETH)']
  name varchar(100) [not null, note: 'Полное название (Bitcoin, Ethereum)']
  description text
}

Table cryptocurrency_data {
  id uuid [pk, default: `uuid_generate_v4()`]
  crypto_id int [not null]
  timestamp timestamp [not null]
  price_usd decimal(18, 8) [not null]
  daily_return float

  indexes {
    (crypto_id, timestamp) [unique]
  }
}

Table trained_models {
  id uuid [pk, default: `uuid_generate_v4()`]
  crypto_id int [not null]
  model_type varchar [not null, note: 'Тип модели (GARCH, ARIMA)']
  parameters jsonb [note: 'Параметры обученной модели']
  trained_at timestamp [not null, default: `now()`]
  version int [not null]
}


// --- Модуль Портфелей и Симуляций ---

Table portfolios {
  id uuid [pk, default: `uuid_generate_v4()`]
  user_id uuid [not null]
  name varchar [not null, note: 'Название портфеля (e.g., "Долгосрок")']
  created_at timestamp [not null, default: `now()`]
}

Table portfolio_assets {
  id uuid [pk, default: `uuid_generate_v4()`]
  portfolio_id uuid [not null]
  crypto_id int [not null]
  amount decimal(24, 12) [not null, note: 'Количество актива с высокой точностью']
}

Table simulation_jobs {
  id uuid [pk, default: `uuid_generate_v4()`]
  user_id uuid [not null]
  portfolio_id uuid [note: 'Может быть NULL, если симуляция не для портфеля']
  status varchar [not null, default: 'pending', note: 'pending, running, completed, failed']
  created_at timestamp [not null, default: `now()`]
  completed_at timestamp
}

Table simulation_results {
  job_id uuid [pk]
  results jsonb [not null, note: 'Результаты симуляции (распределение цен, VaR)']
  model_id uuid [not null]
}


// --- Определение связей ---

// Связи модуля Пользователей
Ref: user_profiles.user_id - users.id // Один-к-одному
Ref: user_roles.user_id > users.id // Многие-ко-многим (часть 1)
Ref: user_roles.role_id > roles.id // Многие-ко-многим (часть 2)
Ref: portfolios.user_id > users.id
Ref: simulation_jobs.user_id > users.id

// Связи модуля Криптовалют
Ref: cryptocurrency_data.crypto_id > cryptocurrencies.id
Ref: trained_models.crypto_id > cryptocurrencies.id
Ref: portfolio_assets.crypto_id > cryptocurrencies.id

// Связи модуля Портфелей и Симуляций
Ref: portfolio_assets.portfolio_id > portfolios.id
Ref: simulation_jobs.portfolio_id > portfolios.id
Ref: simulation_results.job_id - simulation_jobs.id // Один-к-одному
Ref: simulation_results.model_id > trained_models.id
```
