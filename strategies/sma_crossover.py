
import pandas as pd

class Strategy:
    name = "sma_crossover"
    params = {"fast": 9, "slow": 21}

    def generate(self, df: pd.DataFrame):
        df = df.copy()
        df["sma_fast"] = df["close"].rolling(self.params["fast"]).mean()
        df["sma_slow"] = df["close"].rolling(self.params["slow"]).mean()
        df["signal"] = 0
        df.loc[df["sma_fast"] > df["sma_slow"], "signal"] = 1
        df.loc[df["sma_fast"] < df["sma_slow"], "signal"] = -1
        return df
