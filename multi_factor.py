import numpy as np
import math
import pandas as pd
import statsmodels.api as sm


def mid_cap(cap):
    """

    :param cap: stock cap, DataFrame(n , 1)
    :return: mid_cap, series(n)
    """
    ln_cap = np.log(cap)
    ln_cap_cube = ln_cap**3
    ln_cap = sm.add_constant(ln_cap)
    ols = sm.OLS(ln_cap_cube, ln_cap)
    model = ols.fit()
    re = model.resid
    #  Winsorized
    re_max = np.std(re)*3
    re_min = np.std(re)*(-3)
    re[re > re_max] = re_max
    re[re < re_min] = re_min
    #  Standardized
    mu = np.mean(re)
    sigma = np.std(re)
    return (re-mu)/sigma


# Short Term Reversal
def STDREV(ret):
    """

    :param ret: stock simple return, DataFrame(n , 1)
    :return: stdrev, , DataFrame(n-21 , 1)
    """
    window = 21
    half_life = 5
    half_factor = 0.5**(1/half_life)
    ln_ret = np.log(1 + ret)
    w = np.zeros((window, 1))
    for i in range(window):
        w[i, 0] = half_factor**i
    rev = np.zeros((window, ln_ret.shape[0]-window))
    for i in range(ln_ret.shape[0]-window):
        rev[:, i] = ln_ret.iloc[i:i+window]
    result = pd.DataFrame(np.dot(rev.T, w))
    result.index = ret.index[window:]
    return result


# BTOP
def BTOP(book_value, cap):
    """

    :param book_value: DataFrame(n , 1)
    :param cap: DataFrame(n , 1)
    :return: book_to_price, DataFrame(n , 1)
    """
    return book_value/cap


# CETOP
def CETOP(PCF_OCF_TTM):
    """

    :param PCF_OCF_TTM: Wind中的PCF_OCF_TTM因子, DataFrame(n , 1)
    :return: Wind中的PCF_OCF_TTM因子的倒数, DataFrame(n , 1)
    """
    return 1/PCF_OCF_TTM


# STOM
def STOM(turnover):
    """

    :param turnover: 最近21个交易日的换手率, DataFrame(n , 1)
    :return: share turnover one month, DataFrame(n-21 , 1)
    """
    st = np.zeros((turnover.shape[0]-21, 1))
    for i in range(21, turnover.shape[0]):
        st[i-21, 0] = sum(turnover.iloc[i-21:i, 0])
    ln_st = np.log(st)
    ln_st = pd.DataFrame(ln_st)
    ln_st.index = turnover.index[21:]
    return ln_st




