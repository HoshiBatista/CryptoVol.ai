import json
import joblib
import yfinance as yf
from pathlib import Path
from arch import arch_model
from statsmodels.tsa.arima.model import ARIMA

OUTPUT_DIR = Path("ml_models")
METADATA_FILE = OUTPUT_DIR / "models_metadata.json"

TICKERS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "TON", "AVAX", "LINK"]

MODEL_CONFIGS = [
    # GARCH: Моделирование волатильности
    {"type": "GARCH", "params": {"p": 1, "q": 1, "dist": "t"}},
    # ARIMA: Прогнозирование тренда цены
    {"type": "ARIMA", "params": {"order": (5, 1, 0)}},
]

START_DATE = "2020-01-01"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    metadata_list = []

    print(f" Starting local training for {len(TICKERS)} assets...")
    print(f" Output directory: {OUTPUT_DIR.absolute()}")

    for symbol in TICKERS:
        yf_ticker = f"{symbol}-USD"
        print(f"\nFetching data for {symbol} ({yf_ticker})...")

        try:
            df = yf.download(
                yf_ticker,
                start=START_DATE,
                interval="1d",
                progress=False,
                multi_level_index=False,
            )

            if df.empty:
                print(f"⚠️ No data found for {symbol}. Skipping.")
                continue

            prices = df["Close"].dropna()
            returns = prices.pct_change().dropna() * 100

            if len(prices) < 100:
                print(f"⚠️ Not enough data points ({len(prices)}). Skipping.")
                continue

        except Exception as e:
            print(f"❌ Error downloading {symbol}: {e}")
            continue

        for config in MODEL_CONFIGS:
            model_type = config["type"]
            params = config["params"]

            try:
                model_res = None

                if model_type == "GARCH":
                    print(f" Training GARCH {params}...")
                    am = arch_model(
                        returns,
                        vol="Garch",
                        p=params["p"],
                        q=params["q"],
                        dist=params.get("dist", "normal"),
                    )
                    model_res = am.fit(disp="off", show_warning=False)

                elif model_type == "ARIMA":
                    print(f" Training ARIMA {params['order']}...")
                    model = ARIMA(prices, order=params["order"])
                    model_res = model.fit()

                if model_res:
                    param_str = "_".join(
                        [f"{k}{v}" for k, v in params.items() if k != "order"]
                    )
                    if "order" in params:
                        param_str += f"_order_{params['order'][0]}{params['order'][1]}{params['order'][2]}"

                    filename = f"{symbol}_{model_type}_{param_str}.pkl"
                    filepath = OUTPUT_DIR / filename

                    joblib.dump(model_res, filepath)

                    metadata_list.append(
                        {
                            "symbol": symbol,
                            "model_type": model_type,
                            "parameters": params,
                            "filename": filename,
                            "relative_path": str(Path("ml_models") / filename),
                        }
                    )
                    print(f"   ✅ Saved: {filename}")

            except Exception as e:
                print(f"   ❌ Failed to train {model_type}: {e}")

    print(f"\nSaving metadata registry to {METADATA_FILE}...")
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=4)

    print("\n🎉 DONE! Models ready for deployment.")


if __name__ == "__main__":
    main()
