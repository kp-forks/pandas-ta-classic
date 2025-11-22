# -*- coding: utf-8 -*-
# Price Max (PMAX)
from pandas import Series
from pandas_ta_classic.overlap import ma
from pandas_ta_classic.volatility import atr
from pandas_ta_classic.utils import get_offset, verify_series


def pmax(
    high, low, close, length=None, multiplier=None, mamode=None, offset=None, **kwargs
):
    """Indicator: PMAX (Price Max)"""
    # Validate arguments
    length = int(length) if length and length > 0 else 10
    multiplier = float(multiplier) if multiplier and multiplier > 0 else 3.0
    mamode = mamode.lower() if mamode and isinstance(mamode, str) else "ema"
    high = verify_series(high, length)
    low = verify_series(low, length)
    close = verify_series(close, length)
    offset = get_offset(offset)

    if high is None or low is None or close is None:
        return

    # Calculate Result
    # Calculate ATR
    atr_value = atr(high, low, close, length=length)

    # Calculate moving average of close
    ma_value = ma(mamode, close, length=length)

    # Calculate PMAX bands
    pmax_up = ma_value - (multiplier * atr_value)
    pmax_down = ma_value + (multiplier * atr_value)

    # Initialize PMAX and trend
    pmax = Series(0.0, index=close.index)
    trend = Series(1, index=close.index)

    for i in range(1, len(close)):
        # Update upper band
        if close.iloc[i - 1] > pmax_up.iloc[i - 1]:
            pmax_up.iloc[i] = max(pmax_up.iloc[i], pmax_up.iloc[i - 1])

        # Update lower band
        if close.iloc[i - 1] < pmax_down.iloc[i - 1]:
            pmax_down.iloc[i] = min(pmax_down.iloc[i], pmax_down.iloc[i - 1])

        # Determine trend
        if close.iloc[i] > pmax_down.iloc[i - 1]:
            trend.iloc[i] = 1
        elif close.iloc[i] < pmax_up.iloc[i - 1]:
            trend.iloc[i] = -1
        else:
            trend.iloc[i] = trend.iloc[i - 1]

        # Set PMAX value based on trend
        if trend.iloc[i] == 1:
            pmax.iloc[i] = pmax_up.iloc[i]
        else:
            pmax.iloc[i] = pmax_down.iloc[i]

    # Offset
    if offset != 0:
        pmax = pmax.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        pmax.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        if kwargs["fill_method"] == "ffill":
            pmax.ffill(inplace=True)
        elif kwargs["fill_method"] == "bfill":
            pmax.bfill(inplace=True)

    # Name and Categorize it
    pmax.name = f"PMAX_{mamode[0].upper()}_{length}_{multiplier}"
    pmax.category = "trend"

    return pmax


pmax.__doc__ = """PMAX (Price Max)

PMAX is a trend-following indicator that combines moving averages with ATR
(Average True Range) to create adaptive support and resistance levels. It helps
identify trend direction and potential reversal points.

Sources:
    https://www.tradingview.com/script/sU9molfV/
    https://www.prorealcode.com/prorealtime-indicators/pmax/

Calculation:
    Default Inputs:
        length=10, multiplier=3.0, mamode='ema'

    ATR = ATR(high, low, close, length)
    MA = MA(close, length, mamode)

    PMAX_UP = MA - (multiplier * ATR)
    PMAX_DOWN = MA + (multiplier * ATR)

    If close > PMAX_DOWN[1]: trend = 1 (uptrend)
    If close < PMAX_UP[1]: trend = -1 (downtrend)

    PMAX = PMAX_UP if trend == 1 else PMAX_DOWN

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    length (int): ATR period. Default: 10
    multiplier (float): ATR multiplier. Default: 3.0
    mamode (str): Moving average mode. Default: 'ema'
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""
