# -*- coding: utf-8 -*-
# Volume Flow Indicator (VFI)
from pandas_ta_classic.overlap import ma
from pandas_ta_classic.utils import get_offset, verify_series


def vfi(
    close,
    volume,
    length=None,
    coef=None,
    vcoef=None,
    mamode=None,
    offset=None,
    **kwargs,
):
    """Indicator: Volume Flow Indicator (VFI)"""
    # Validate arguments
    length = int(length) if length and length > 0 else 130
    coef = float(coef) if coef else 0.2
    vcoef = float(vcoef) if vcoef else 2.5
    mamode = mamode.lower() if mamode and isinstance(mamode, str) else "ema"
    _length = length
    close = verify_series(close, _length)
    volume = verify_series(volume, _length)
    offset = get_offset(offset)

    if close is None or volume is None:
        return

    # Calculate Result
    # Typical price
    typical = close

    # Volume cutoff
    vave = volume.rolling(length).mean().shift(1)
    vmax = vave * vcoef
    vc = volume.clip(upper=vmax)

    # Calculate MF (Money Flow)
    mf = typical - typical.shift(1)

    # VCP (Volume times Cutoff Price)
    vcp = vc * mf

    # Calculate VFI
    vfi = vcp.rolling(length).sum() / vave.rolling(length).mean()

    # Smooth VFI
    vfi = ma(mamode, vfi, length=3)

    # Offset
    if offset != 0:
        vfi = vfi.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        vfi.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        if kwargs["fill_method"] == "ffill":
            vfi.ffill(inplace=True)
        elif kwargs["fill_method"] == "bfill":
            vfi.bfill(inplace=True)

    # Name and Categorize it
    vfi.name = f"VFI_{length}"
    vfi.category = "volume"

    return vfi


vfi.__doc__ = """Volume Flow Indicator (VFI)

The Volume Flow Indicator (VFI) is a volume-based indicator that helps identify
the strength of bulls vs bears in the market. It combines price movement with
volume to show the flow of money into or out of a security.

Sources:
    https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/
    https://www.investopedia.com/terms/v/volume-analysis.asp

Calculation:
    Default Inputs:
        length=130, coef=0.2, vcoef=2.5, mamode='ema'

    typical = close
    inter = typical.diff() (handle zeros)
    vave = SMA(volume, length)
    vmax = vave * vcoef
    vc = min(volume, vmax)

    mf = typical - typical[1]
    vcp = vc * mf

    VFI = SUM(vcp, length) / SMA(vave, length)
    VFI = EMA(VFI, 3)

Args:
    close (pd.Series): Series of 'close's
    volume (pd.Series): Series of 'volume's
    length (int): The period. Default: 130
    coef (float): Calculation coefficient. Default: 0.2
    vcoef (float): Volume coefficient. Default: 2.5
    mamode (str): Moving average mode for smoothing. Default: 'ema'
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""
