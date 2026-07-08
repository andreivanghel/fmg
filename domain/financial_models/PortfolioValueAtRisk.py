from typing import Any

import yaml
import numpy as np
import pandas as pd
import yfinance as yf
from domain.financial_model_executor import FinancialModelExecutor

yf.set_tz_cache_location("/tmp/py-yfinance-cache")

class PortfolioVaR(FinancialModelExecutor):

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
        with open("domain/financial_models/portfolio_var_config.yaml") as f:
            return yaml.safe_load(f)

    def _fetch_data(self, tickers: list[str], lookback_days: int) -> pd.DataFrame:
        PRICE_TYPE = "Close"

        raw_prices = yf.download(tickers, period=f"{lookback_days}d", auto_adjust=True, progress=False)
        prices = raw_prices[PRICE_TYPE]
        if prices.isnull().values.any():
            prices = prices.ffill().dropna()

        return prices

    def _compute_portfolio_returns(
            self,
            prices: pd.DataFrame,
            weights: np.ndarray
    ) -> np.ndarray:
        asset_returns = prices.pct_change().dropna().values
        portfolio_returns = asset_returns @ weights
        portfolio_log_returns = np.log1p(portfolio_returns)

        return portfolio_log_returns

    def _compute_var(
            self, 
            portfolio_returns: np.ndarray, 
            confidence_levels: list[float]
    ) -> list[dict]:
        var_table = []

        for cl in confidence_levels:
            percentile = (1 - cl) * 100                          # es. 95% → 5°percentile
            var_return = np.percentile(portfolio_returns, percentile)
            var_value = -var_return                              # convenzione: perdita positiva

            # CVaR (Expected Shortfall): media delle perdite oltre il VaR
            # risponde a: "se supero il VaR, quanto perdo in media?"
            tail_returns = portfolio_returns[portfolio_returns <= var_return]
            cvar_value = -np.mean(tail_returns) if len(tail_returns) > 0 else var_value

            var_table.append({
                "confidence_level": float(cl),
                "var_1d":  round(float(var_value),  6),   # perdita max in 1 giorno
                "cvar_1d": round(float(cvar_value), 6),   # perdita attesa oltre VaR
                "var_10d": round(float(var_value * np.sqrt(10)), 6),  # scaling √t a 10gg
            })

        return var_table
    


    def _specific_checks(self):
        return super()._specific_checks()
