
import pandas as pd

class Strategy:
    name = "donchian_breakout"
    params = {"period":20}

    def generate(self, df: pd.DataFrame):
        df = df.copy()
        high = df["high"].rolling(self.params["period"]).max()
        low = df["low"].rolling(self.params["period"]).min()
        df["dc_high"] = high
        df["dc_low"] = low
        df["signal"] = 0
        df.loc[df["close"] > high.shift(1), "signal"] = 1
        df.loc[df["close"] < low.shift(1), "signal"] = -1
        return df
