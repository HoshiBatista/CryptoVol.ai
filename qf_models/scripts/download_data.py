import yfinance as yf
import os
import datetime as dt

OUTPUT_DIR = "data"

CRYPTO_LIST = [
    "BTC-USD",  # Bitcoin
    "ETH-USD",  # Ethereum
    "SOL-USD",  # Solana
    "ADA-USD",  # Cardano
    "TON-USD",  # Toncoin
]

START_DATE = dt.datetime(2018, 1, 1)
END_DATE = dt.datetime.now()


def download_and_save_crypto_data(ticker, start, end, output_dir):
    """
    Загружает данные для одного тикера с Yahoo Finance и сохраняет их в CSV.

    Args:
        ticker (str): Тикер криптовалюты (например, 'BTC-USD').
        start (datetime): Дата начала периода.
        end (datetime): Дата окончания периода.
        output_dir (str): Директория для сохранения файла.
    """
    print(f"[*] Загрузка данных для тикера: {ticker}...")

    try:
        data = yf.download(ticker, start=start, end=end, progress=False)

        if data.empty:
            print(
                f"[!] Предупреждение: Для тикера {ticker} не найдено данных. Пропускаем."
            )
            return

        file_path = os.path.join(output_dir, f"{ticker}.csv")

        data.to_csv(file_path)
        print(f"[+] Успешно сохранено: {file_path}")

    except Exception as e:
        print(f"[!] Ошибка при обработке тикера {ticker}: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("Начало процесса загрузки исторических данных...")
    print("=" * 50)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Создана директория: {OUTPUT_DIR}")

    for crypto_ticker in CRYPTO_LIST:
        download_and_save_crypto_data(crypto_ticker, START_DATE, END_DATE, OUTPUT_DIR)
        print("-" * 20)

    print("=" * 50)
    print("Процесс загрузки данных завершен.")
    print("=" * 50)
