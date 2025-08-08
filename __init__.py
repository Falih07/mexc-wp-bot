from .sma_crossover import Strategy as sma_crossover
from .rsi import Strategy as rsi
from .macd import Strategy as macd
from .bbands_mean_revert import Strategy as bbands_mean_revert
from .donchian_breakout import Strategy as donchian_breakout

ALL = {
    "sma_crossover": sma_crossover,
    "rsi": rsi,
    "macd": macd,
    "bbands_mean_revert": bbands_mean_revert,
    "donchian_breakout": donchian_breakout,
}
