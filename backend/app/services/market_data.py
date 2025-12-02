import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.crypto_data import Cryptocurrency, CryptocurrencyData
from app.core.logging_config import logger

DEFAULT_TICKERS = [
    {"symbol": "BTC", "name": "Bitcoin", "description": "Market Leader"},
    {"symbol": "ETH", "name": "Ethereum", "description": "Smart Contracts"},
    {"symbol": "SOL", "name": "Solana", "description": "High Performance L1"},
    {"symbol": "BNB", "name": "Binance Coin", "description": "Exchange Token"},
    {"symbol": "XRP", "name": "XRP", "description": "Payments"},
    {"symbol": "ADA", "name": "Cardano", "description": "Scientific Blockchain"},
    {"symbol": "DOGE", "name": "Dogecoin", "description": "Meme Coin"},
    {"symbol": "TON", "name": "Toncoin", "description": "The Open Network"},
    {"symbol": "AVAX", "name": "Avalanche", "description": "DApp Platform"},
    {"symbol": "LINK", "name": "Chainlink", "description": "Oracle"},
    {"symbol": "DOT", "name": "Polkadot", "description": "Interoperability"},
    {"symbol": "MATIC", "name": "Polygon", "description": "ETH Scaling"},
    {"symbol": "LTC", "name": "Litecoin", "description": "Payments"},
    {"symbol": "UNI", "name": "Uniswap", "description": "DeFi"},
    {"symbol": "ATOM", "name": "Cosmos", "description": "Internet of Blockchains"},
]


async def init_supported_cryptos(db: AsyncSession):
    logger.info("Checking supported cryptocurrencies...")

    stmt = select(Cryptocurrency.symbol)
    result = await db.execute(stmt)
    existing_symbols = set(result.scalars().all())

    new_cryptos = []

    for ticker in DEFAULT_TICKERS:
        if ticker["symbol"] in existing_symbols:
            continue

        logger.info(f" Preparing to add: {ticker['symbol']}")
        new_crypto = Cryptocurrency(
            symbol=ticker["symbol"],
            name=ticker["name"],
            description=ticker["description"],
        )
        new_cryptos.append(new_crypto)

    if new_cryptos:
        db.add_all(new_cryptos)
        await db.commit()
        logger.info(f" Successfully added {len(new_cryptos)} new cryptocurrencies.")
    else:
        logger.info(" All cryptocurrencies already exist in DB.")


async def sync_market_data(db: AsyncSession):
    logger.info("🔄 Starting market data sync...")

    await init_supported_cryptos(db)

    result = await db.execute(select(Cryptocurrency))
    cryptos = result.scalars().all()

    if not cryptos:
        logger.warning("⚠️ Still no cryptocurrencies found even after initialization.")
        return

    for crypto in cryptos:
        await process_single_crypto(db, crypto)

    logger.info("✅ Market data sync completed.")


async def process_single_crypto(db: AsyncSession, crypto: Cryptocurrency):
    ticker_yf = f"{crypto.symbol}-USD"

    stmt = (
        select(CryptocurrencyData.timestamp)
        .where(CryptocurrencyData.crypto_id == crypto.id)
        .order_by(desc(CryptocurrencyData.timestamp))
        .limit(1)
    )

    last_date_res = await db.execute(stmt)
    last_date = last_date_res.scalars().first()

    start_date = "2020-01-01"
    if last_date:
        start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")

    if pd.to_datetime(start_date) >= datetime.now():
        logger.info(f"⏳ {crypto.symbol} is up to date.")
        return

    logger.info(f"📥 Downloading {ticker_yf} from {start_date}...")

    try:
        df = yf.download(
            ticker_yf,
            start=start_date,
            interval="1d",
            progress=False,
            multi_level_index=False,
        )

        if df.empty:
            logger.warning(f"No new data for {ticker_yf}")
            return

        df.reset_index(inplace=True)

        if "Date" in df.columns:
            df.rename(columns={"Date": "Timestamp"}, inplace=True)

        df["Close"] = df["Close"].astype(float)
        df["daily_return"] = df["Close"].pct_change()
        df["daily_return"].fillna(0, inplace=True)

        new_records = []
        for _, row in df.iterrows():
            ts = row["Timestamp"]

            if ts.tzinfo is None:
                ts = ts.tz_localize("UTC")
            else:
                ts = ts.tz_convert("UTC")

            record = CryptocurrencyData(
                crypto_id=crypto.id,
                timestamp=ts,
                price_usd=float(row["Close"]),
                daily_return=float(row["daily_return"]),
            )
            new_records.append(record)

        if new_records:
            db.add_all(new_records)
            await db.commit()
            logger.info(f"💾 Saved {len(new_records)} records for {crypto.symbol}")

    except Exception as e:
        logger.error(f"❌ Error updating {crypto.symbol}: {e}")
        await db.rollback()
