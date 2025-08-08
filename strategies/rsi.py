
import pandas as pd
import numpy as np

class Strategy:
    name = "rsi"
    params = {"period": 14, "oversold": 30, "overbought": 70}

    def generate(self, df: pd.DataFrame):
        df = df.copy()
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0.0)).rolling(self.params["period"]).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(self.params["period"]).mean()
        rs = gain / (loss.replace(0, np.nan))
        df["rsi"] = 100 - (100 / (1 + rs))
        df["signal"] = 0
        df.loc[df["rsi"] < self.params["oversold"], "signal"] = 1
        df.loc[df["rsi"] > self.params["overbought"], "signal"] = -1
        return df
