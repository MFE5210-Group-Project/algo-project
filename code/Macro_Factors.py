import quantstats as qs
import sklearn
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Process original data
data_index = pd.read_excel('/Users/wyb/Downloads/CUHK/second term/5210 Algorithm Trading/project/index_A.xlsx', index_col='交易日期')
data_index = data_index.iloc[::-1]  # 翻转数据， wind下载格式为时间由近及远
data_index = data_index.iloc[:, 5].shift(-1)/100  # wind 全A指数 涨跌幅(未来一天）;
data_index = data_index.dropna()
data_index.index = pd.to_datetime(data_index.index)

data_north = pd.read_excel('/Users/wyb/Downloads/CUHK/second term/5210 Algorithm Trading/project/北向资金.xlsx', index_col='日期')
data_north = data_north.dropna()
data_north = data_north.iloc[::-1]
data_north = data_north.iloc[:-1, [1, 3]]
data_north.index = pd.to_datetime(data_north.index)

data_balance = pd.read_excel('/Users/wyb/Downloads/CUHK/second term/5210 Algorithm Trading/project/融资余额.xlsx', index_col='指标名称')
finance_balance = data_balance.iloc[:, 0]
margin_balance = data_balance.iloc[:, 1]
# print(finance_balance)
# print(margin_balance)

data_currency = pd.read_excel('/Users/wyb/Downloads/CUHK/second term/5210 Algorithm Trading/project/中间价_美元兑人民币.xlsx', index_col='指标名称')
data_currency = data_currency.iloc[::-1]
data_currency = data_currency.dropna()
# print(data_currency)

data_sheet = pd.concat([finance_balance, margin_balance, data_currency], axis=1)
data_sheet.index = pd.to_datetime(data_sheet.index)
data = pd.merge(data_sheet, data_north, how='inner', left_index=True, right_index=True)
data = pd.merge(data, data_index, how='inner', left_index=True, right_index=True)
data.columns = ['finance_balance', 'margin_balance', 'currency', 'north_money', 'north_money_net', 'rate']
data.to_csv('/Users/wyb/PycharmProjects/algo-project/database/macro_factor.csv')
# print(data)


# Correlation analysis
# sns.heatmap(data.corr())
# plt.show()


# Factor analysis
# Create short-term and long-term ratio
# short_l = 5
# long_l = 22
# trend = 'up'
# indicator = data.iloc[:, 0]


def ma_ratio(indicator, short_l, long_l, trend):
    s = []
    for i in range(long_l-1, indicator.shape[0]):
        a = np.mean(indicator[i+1-long_l: i+1])
        b = np.mean(indicator[i+1-short_l: i+1])
        if trend == 'up':
            if b/a > 1:
                s.append(1)
            else:
                s.append(0)
        if trend == 'down':
            if b/a > 1:
                s.append(0)
            else:
                s.append(1)
    return s


signal = np.array(ma_ratio(data.iloc[:, 4], 5, 22, 'up'))
x = np.array(data.iloc[21:, -1])
y = signal*x
new_index = data.index[21:]
stock = pd.Series(y, new_index)
fig = plt.figure()
qs.extend_pandas()
qs.stats.sharpe(stock)
qs.reports.basic(stock, benchmark=None, rf=0, grayscale=False, display=True, compounded=True)
plt.show()