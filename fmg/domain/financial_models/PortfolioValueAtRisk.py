from typing import Any, cast

import numpy as np
import pandas as pd
import yaml
import yfinance as yf
from numpy.typing import NDArray
from typing_extensions import override

from fmg.domain.financial_model_executor import FinancialModelExecutor

yf.set_tz_cache_location("/tmp/py-yfinance-cache")


class PortfolioVaR(FinancialModelExecutor):
    @override
    def _run(self, params: dict) -> dict:

        confidence_levels = params["confidence_levels"]
        lookback_days = params["lookback_days"]

        # CONFIGURATION (to be better parametrized!)
        config = self._load_config()
        tickers = config["tickers"]
        weights = np.array(config["weights"])

        # DATA FETCH (this implementation makes the run not reproducible!!)
        prices = self._fetch_data(tickers, lookback_days)

        # RETURNS CALCULATION
        portfolio_returns = self._compute_portfolio_returns(prices, weights)

        # VAR CALCULATION
        var_table = self._compute_var(portfolio_returns, confidence_levels)

        return {
            "tickers": list(tickers),
            "weights": [float(w) for w in config["weights"]],
            "lookback_days": int(lookback_days),
            "n_observations": len(portfolio_returns),
            "var_table": var_table,
        }

    def _load_config(self) -> Any:
        with open("fmg/domain/financial_models/portfolio_var_config.yaml") as f:
            return yaml.safe_load(f)

    def _fetch_data(self, tickers: list[str], lookback_days: int) -> pd.DataFrame:
        PRICE_TYPE = "Close"

        raw_prices: pd.DataFrame = cast(
            pd.DataFrame,
            yf.download(tickers, period=f"{lookback_days}d", auto_adjust=True, progress=False),
        )

        if raw_prices is None or raw_prices.empty:
            return pd.DataFrame()  # Return an empty DataFrame if no data is fetched

        prices = raw_prices[PRICE_TYPE]

        if isinstance(prices, pd.Series):
            prices_df = prices.to_frame()
        else:
            prices_df = prices

        if prices_df.isnull().to_numpy().any():
            prices_df = prices_df.ffill().dropna()

        return prices_df

    def _compute_portfolio_returns(
        self, prices: pd.DataFrame, weights: NDArray[np.float64]
    ) -> np.ndarray:
        asset_returns: NDArray[np.float64] = prices.pct_change().dropna().to_numpy(dtype=np.float64)
        portfolio_returns = asset_returns @ weights

        return cast(NDArray[np.float64], np.log1p(portfolio_returns))

    def _compute_var(
        self, portfolio_returns: np.ndarray, confidence_levels: list[float]
    ) -> list[dict]:
        var_table = []

        for cl in confidence_levels:
            percentile = (1 - cl) * 100  # es. 95% → 5°percentile
            var_return = np.percentile(portfolio_returns, percentile)
            var_value = -var_return  # convenzione: perdita positiva

            # CVaR (Expected Shortfall): media delle perdite oltre il VaR
            # risponde a: "se supero il VaR, quanto perdo in media?"
            tail_returns = portfolio_returns[portfolio_returns <= var_return]
            cvar_value = -np.mean(tail_returns) if len(tail_returns) > 0 else var_value

            var_table.append(
                {
                    "confidence_level": float(cl),
                    "var_1d": round(float(var_value), 6),  # perdita max in 1 giorno
                    "cvar_1d": round(float(cvar_value), 6),  # perdita attesa oltre VaR
                    "var_10d": round(float(var_value * np.sqrt(10)), 6),  # scaling √t a 10gg
                }
            )

        return var_table

    @override
    def _specific_checks(self):
        return super()._specific_checks()
