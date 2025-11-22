# -*- coding: utf-8 -*-
# Laguerre Relative Strength Index (Laguerre RSI)
from pandas_ta_classic.utils import get_offset, verify_series


def lrsi(close, length=None, gamma=None, offset=None, **kwargs):
    """Indicator: Laguerre RSI (LRSI)"""
    # Validate arguments
    length = int(length) if length and length > 0 else 14
    gamma = float(gamma) if gamma and 0 < gamma < 1 else 0.5
    close = verify_series(close, length)
    offset = get_offset(offset)

    if close is None:
        return

    # Calculate Result
    # Initialize Laguerre filter components
    l0 = close.copy()
    l1 = close.copy()
    l2 = close.copy()
    l3 = close.copy()

    # Apply Laguerre filter
    for i in range(1, len(close)):
        l0.iloc[i] = (1 - gamma) * close.iloc[i] + gamma * l0.iloc[i - 1]
        l1.iloc[i] = -gamma * l0.iloc[i] + l0.iloc[i - 1] + gamma * l1.iloc[i - 1]
        l2.iloc[i] = -gamma * l1.iloc[i] + l1.iloc[i - 1] + gamma * l2.iloc[i - 1]
        l3.iloc[i] = -gamma * l2.iloc[i] + l2.iloc[i - 1] + gamma * l3.iloc[i - 1]

    # Calculate Laguerre RSI
    cu = 0 * close
    cd = 0 * close

    for i in range(len(close)):
        if l0.iloc[i] >= l1.iloc[i]:
            cu.iloc[i] = l0.iloc[i] - l1.iloc[i]
        else:
            cd.iloc[i] = l1.iloc[i] - l0.iloc[i]

        if l1.iloc[i] >= l2.iloc[i]:
            cu.iloc[i] += l1.iloc[i] - l2.iloc[i]
        else:
            cd.iloc[i] += l2.iloc[i] - l1.iloc[i]

        if l2.iloc[i] >= l3.iloc[i]:
            cu.iloc[i] += l2.iloc[i] - l3.iloc[i]
        else:
            cd.iloc[i] += l3.iloc[i] - l2.iloc[i]

    lrsi = 100 * cu / (cu + cd)

    # Offset
    if offset != 0:
        lrsi = lrsi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        lrsi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        if kwargs["fill_method"] == "ffill":
            lrsi.ffill(inplace=True)
        elif kwargs["fill_method"] == "bfill":
            lrsi.bfill(inplace=True)

    # Name and Categorize it
    lrsi.name = f"LRSI_{length}"
    lrsi.category = "momentum"

    return lrsi


lrsi.__doc__ = """Laguerre RSI (LRSI)

The Laguerre RSI is a modified RSI indicator that uses Laguerre polynomials to
reduce lag and provide earlier signals. It adapts to price changes more quickly
than the standard RSI while maintaining smooth oscillations.

Sources:
    https://www.tradingview.com/script/3p0QrN5C-Laguerre-RSI/
    https://www.mesasoftware.com/papers/LaguerreFilters.pdf

Calculation:
    Default Inputs:
        length=14, gamma=0.5
    
    Apply Laguerre filter with gamma coefficient:
    L0 = (1 - gamma) * Close + gamma * L0[1]
    L1 = -gamma * L0 + L0[1] + gamma * L1[1]
    L2 = -gamma * L1 + L1[1] + gamma * L2[1]
    L3 = -gamma * L2 + L2[1] + gamma * L3[1]
    
    Calculate ups and downs:
    CU = sum of (L0-L1, L1-L2, L2-L3) when positive
    CD = sum of (L0-L1, L1-L2, L2-L3) when negative (absolute)
    
    LRSI = 100 * CU / (CU + CD)

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period. Default: 14
    gamma (float): Laguerre filter coefficient (0 to 1). Default: 0.5
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""
