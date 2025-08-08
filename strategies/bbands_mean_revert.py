
import pandas as pd

class Strategy:
    name = "bbands_mean_revert"
    params = {"period":20,"stddev":2.0}

    def generate(self, df: pd.DataFrame):
        df = df.copy()
        ma = df["close"].rolling(self.params["period"]).mean()
        std = df["close"].rolling(self.params["period"]).std()
        upper = ma + self.params["stddev"]*std
        lower = ma - self.params["stddev"]*std
        df["bb_mid"] = ma
        df["bb_up"] = upper
        df["bb_lo"] = lower
        df["signal"] = 0
        df.loc[df["close"] < lower, "signal"] = 1   # revert up
        df.loc[df["close"] > upper, "signal"] = -1  # revert down
        return df
