
import pandas as pd

class Strategy:
    name = "macd"
    params = {"fast":12,"slow":26,"signal":9}

    def generate(self, df: pd.DataFrame):
        df = df.copy()
        ema_fast = df["close"].ewm(span=self.params["fast"], adjust=False).mean()
        ema_slow = df["close"].ewm(span=self.params["slow"], adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=self.params["signal"], adjust=False).mean()
        df["macd"] = macd
        df["macd_signal"] = macd_signal
        df["signal"] = 0
        df.loc[macd > macd_signal, "signal"] = 1
        df.loc[macd < macd_signal, "signal"] = -1
        return df
