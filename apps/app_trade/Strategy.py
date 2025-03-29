import numpy as np

class BaseStrategy:
    def __init__(self, open_price, close_price, low, high, volume, current_price, **kwargs):
        """
        open_price, close_price, low, high, volume: списки данных для каждого периода (свечные данные)
        current_price: текущая цена актива
        kwargs: дополнительные параметры (например, для новостной стратегии)
        """
        self.open_price = open_price
        self.close_price = close_price
        self.low = low
        self.high = high
        self.volume = volume
        self.current_price = current_price
        self.params = kwargs

    def calculate_sma(self, period=20):
        if len(self.close_price) < period:
            return None
        return sum(self.close_price[-period:]) / period

    def calculate_rsi(self, period=14):
        if len(self.close_price) < period + 1:
            return None
        deltas = np.diff(self.close_price)
        seed = deltas[:period]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = 100 - 100 / (1 + rs)
        for delta in deltas[period:]:
            if delta > 0:
                up_val = delta
                down_val = 0
            else:
                up_val = 0
                down_val = -delta
            up = (up * (period - 1) + up_val) / period
            down = (down * (period - 1) + down_val) / period
            rs = up / down if down != 0 else 0
            rsi = 100 - 100 / (1 + rs)
        return rsi

    def calculate_macd(self, fast=12, slow=26, signal=9):
        if len(self.close_price) < slow:
            return None, None, None
        prices = np.array(self.close_price)
        ema_fast = self._ema(prices, fast)
        ema_slow = self._ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self._ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line[-1], signal_line[-1], histogram[-1]

    def _ema(self, prices, period):
        ema = []
        k = 2 / (period + 1)
        for i, price in enumerate(prices):
            if i == 0:
                ema.append(price)
            else:
                ema.append(price * k + ema[-1] * (1 - k))
        return np.array(ema)

    def candle_trend(self):
        """
        Анализ последней свечи.
        Если последнее закрытие > открытие, возвращает 1 (бычья свеча);
        если <, возвращает -1 (медвежья);
        иначе 0.
        """
        if not self.open_price or not self.close_price:
            return 0
        last_open = self.open_price[-1]
        last_close = self.close_price[-1]
        if last_close > last_open:
            return 1
        elif last_close < last_open:
            return -1
        else:
            return 0

    def candle_volume_factor(self):
        """
        Возвращает отношение последнего объёма к среднему объёму.
        """
        if not self.volume:
            return 1
        avg_vol = sum(self.volume) / len(self.volume)
        last_vol = self.volume[-1]
        return last_vol / avg_vol if avg_vol != 0 else 1

    def signal(self):
        raise NotImplementedError("Subclasses must implement signal() method.")

# 1. Дневная торговля (Day Trading)
class DayTradingStrategy(BaseStrategy):
    def signal(self):
        sma = self.calculate_sma(period=20)
        rsi = self.calculate_rsi(period=14)
        trend = self.candle_trend()
        if sma is None or rsi is None:
            return "hold"
        # Если цена ниже SMA, RSI ниже 30 и последняя свеча бычья – сигнал на покупку.
        if self.current_price < sma and rsi < 30 and trend == 1:
            return "buy"
        # Если цена выше SMA, RSI выше 70 и последняя свеча медвежья – сигнал на продажу.
        elif self.current_price > sma and rsi > 70 and trend == -1:
            return "sell"
        else:
            return "hold"

# 2. Скальпинг
class ScalpingStrategy(BaseStrategy):
    def signal(self):
        sma = self.calculate_sma(period=5)
        trend = self.candle_trend()
        if sma is None:
            return "hold"
        diff = (self.current_price - sma) / sma
        vol_factor = self.candle_volume_factor()
        # При высокой объемной активность сигналы усиливаются
        if diff < -0.005 * vol_factor and trend == 1:
            return "buy"
        elif diff > 0.005 * vol_factor and trend == -1:
            return "sell"
        else:
            return "hold"

# 3. Свинг-трейдинг
class SwingTradingStrategy(BaseStrategy):
    def signal(self):
        long_sma = self.calculate_sma(period=50)
        rsi = self.calculate_rsi(period=14)
        trend = self.candle_trend()
        if long_sma is None or rsi is None:
            return "hold"
        # Если цена ниже long_sma, RSI умеренный и последняя свеча бычья, ожидаем разворот – покупаем.
        if self.current_price < long_sma and rsi < 50 and trend == 1:
            return "buy"
        # Если цена выше long_sma, RSI высок и последняя свеча медвежья – сигнал на продажу.
        elif self.current_price > long_sma and rsi > 60 and trend == -1:
            return "sell"
        else:
            return "hold"

# 4. Позиционная торговля
class PositionTradingStrategy(BaseStrategy):
    def signal(self):
        long_sma = self.calculate_sma(period=200)
        trend = self.candle_trend()
        if long_sma is None:
            return "hold"
        # Если цена выше длинного SMA и последняя свеча бычья – долгосрочная покупка.
        if self.current_price > long_sma and trend == 1:
            return "buy"
        # Если цена ниже длинного SMA и последняя свеча медвежья – продажа или шорт.
        elif self.current_price < long_sma and trend == -1:
            return "sell"
        else:
            return "hold"

# 5. Арбитраж
class ArbitrageStrategy(BaseStrategy):
    def signal(self):
        sma = self.calculate_sma(period=20)
        if sma is None:
            return "hold"
        diff = (self.current_price - sma) / sma
        # Используем данные свечи для дополнительной проверки.
        trend = self.candle_trend()
        if diff < -0.02 and trend == 1:
            return "buy"
        elif diff > 0.02 and trend == -1:
            return "sell"
        else:
            return "hold"

# 6. Трендовая торговля (Trend Following)
class TrendFollowingStrategy(BaseStrategy):
    def signal(self):
        sma = self.calculate_sma(period=20)
        trend = self.candle_trend()
        if sma is None:
            return "hold"
        # Если цена выше SMA и последняя свеча подтверждает тренд (бычья) – покупаем.
        if self.current_price > sma and trend == 1:
            return "buy"
        # Если цена ниже SMA и свеча медвежья – продаём.
        elif self.current_price < sma and trend == -1:
            return "sell"
        else:
            return "hold"

# 7. Контртрендовая торговля (Counter-Trend Trading)
class CounterTrendStrategy(BaseStrategy):
    def signal(self):
        rsi = self.calculate_rsi(period=14)
        trend = self.candle_trend()
        if rsi is None:
            return "hold"
        # При перепроданности RSI и бычьей свече – сигнал на покупку.
        if rsi < 30 and trend == 1:
            return "buy"
        # При перекупленности RSI и медвежьей свече – сигнал на продажу.
        elif rsi > 70 and trend == -1:
            return "sell"
        else:
            return "hold"

# 8. Grid-трейдинг
class GridTradingStrategy(BaseStrategy):
    def signal(self):
        if not self.close_price:
            return "hold"
        grid_lower = min(self.low)
        grid_upper = max(self.high)
        range_grid = grid_upper - grid_lower
        # Используем данные последней свечи для уточнения границ.
        last_low = self.low[-1]
        last_high = self.high[-1]
        # Если текущая цена близка к нижней границе свечного диапазона – покупаем.
        if self.current_price <= grid_lower + 0.05 * range_grid or last_low <= grid_lower + 0.05 * range_grid:
            return "buy"
        # Если текущая цена близка к верхней границе – продаём.
        elif self.current_price >= grid_upper - 0.05 * range_grid or last_high >= grid_upper - 0.05 * range_grid:
            return "sell"
        else:
            return "hold"

# 9. DCA (Dollar Cost Averaging)
class DCAStrategy(BaseStrategy):
    def signal(self):
        avg_price = sum(self.close_price) / len(self.close_price) if self.close_price else None
        trend = self.candle_trend()
        if avg_price is None:
            return "hold"
        # Если текущая цена ниже среднего и последняя свеча бычья – покупка.
        if self.current_price < avg_price and trend == 1:
            return "buy"
        else:
            return "hold"

# 10. Торговля на новостях (News Trading)
class NewsTradingStrategy(BaseStrategy):
    def signal(self):
        sentiment = self.params.get("news_sentiment", 0)  # -1 до +1
        # Дополнительно учитываем, что последняя свеча подтверждает новостной фон.
        trend = self.candle_trend()
        if sentiment > 0.5 and trend == 1:
            return "buy"
        elif sentiment < -0.5 and trend == -1:
            return "sell"
        else:
            return "hold"

# 11. Алгоритмический/бот-трейдинг
class AlgoBotTradingStrategy(BaseStrategy):
    def signal(self):
        macd_line, signal_line, histogram = self.calculate_macd()
        rsi = self.calculate_rsi(period=14)
        trend = self.candle_trend()
        if macd_line is None or rsi is None:
            return "hold"
        # Комбинируем индикаторы и данные свечи:
        if histogram > 0 and 40 < rsi < 60 and trend == 1:
            return "buy"
        elif histogram < 0 and 40 < rsi < 60 and trend == -1:
            return "sell"
        else:
            return "hold"

# 12. Высокочастотная торговля (HFT)
class HighFrequencyTradingStrategy(BaseStrategy):
    def signal(self):
        if not self.close_price:
            return "hold"
        last_price = self.close_price[-1]
        diff = (self.current_price - last_price) / last_price
        # Используем данные последней свечи для микродвижений.
        trend = self.candle_trend()
        if abs(diff) < 0.001:
            return "hold"
        elif diff > 0 and trend == -1:
            return "sell"
        elif diff < 0 and trend == 1:
            return "buy"
        else:
            return "hold"

# 13. Управление капиталом и риск-менеджмент
class CapitalManagementStrategy(BaseStrategy):
    def signal(self):
        if len(self.close_price) < 2:
            return "hold"
        volatility = np.std(self.close_price)
        trend = self.candle_trend()
        # Если волатильность высока (относительно средней цены) и свеча нейтральна, предлагается удерживать позиции
        if volatility > np.mean(self.close_price) * 0.05 and trend == 0:
            return "hold"
        else:
            return "buy"

# Пример использования:
if __name__ == "__main__":
    # Пример исторических данных (закрытия)
    prices = [100, 102, 101, 103, 104, 105, 104, 106, 107, 108,
              107, 109, 110, 111, 112, 111, 113, 114, 115, 116,
              115, 117, 118, 119, 120]
    # Для open, close, low, high и volume используем списки одинаковой длины
    open_prices = [99, 101, 100, 102, 103, 104, 103, 105, 106, 107,
                   106, 108, 109, 110, 111, 110, 112, 113, 114, 115,
                   114, 116, 117, 118, 119]
    close_prices = prices  # Используем список цен закрытия, как есть
    lows = [98, 100, 99, 101, 102, 103, 102, 104, 105, 106,
            105, 107, 108, 109, 110, 109, 111, 112, 113, 114,
            113, 115, 116, 117, 118]
    highs = [101, 103, 102, 104, 105, 106, 105, 107, 108, 109,
             108, 110, 111, 112, 113, 112, 114, 115, 116, 117,
             116, 118, 119, 120, 121]
    volumes = [10000, 10500, 9800, 11000, 11500, 12000, 11800, 12500, 13000, 13500,
               13200, 14000, 14500, 15000, 14800, 14200, 15500, 16000, 16500, 17000,
               16800, 17500, 18000, 18500, 19000]
    current_price = 116

    strategies = {
        "DayTrading": DayTradingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "Scalping": ScalpingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "SwingTrading": SwingTradingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "PositionTrading": PositionTradingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "Arbitrage": ArbitrageStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "TrendFollowing": TrendFollowingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "CounterTrend": CounterTrendStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "GridTrading": GridTradingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "DCA": DCAStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "NewsTrading": NewsTradingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price, news_sentiment=0.7),
        "AlgoBot": AlgoBotTradingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "HFT": HighFrequencyTradingStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price),
        "CapitalManagement": CapitalManagementStrategy(prices, open_prices, close_prices, lows, highs, volumes, current_price)
    }

    for name, strat in strategies.items():
        print(f"{name} signal: {strat.signal()}")