import quantstats as qs
import sklearn
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# Process original data
data_index = pd.read_excel('/Users/wyb/PycharmProjects/algo-project/database/index_A.xlsx', index_col='交易日期')
data_index = data_index.iloc[::-1]  # 翻转数据， wind下载格式为时间由近及远
data_index = data_index.iloc[:, 5].shift(-1)/100  # wind 全A指数 涨跌幅(未来一天）;
data_index = data_index.dropna()
data_index.index = pd.to_datetime(data_index.index)

data_north = pd.read_excel('/Users/wyb/PycharmProjects/algo-project/database/北向资金.xlsx', index_col='日期')
data_north = data_north.dropna()
data_north = data_north.iloc[::-1]
data_north = data_north.iloc[:-1, [1, 3]]
data_north.index = pd.to_datetime(data_north.index)

data_balance = pd.read_excel('/Users/wyb/PycharmProjects/algo-project/database/融资余额.xlsx', index_col='指标名称')
finance_balance = data_balance.iloc[:, 0]
margin_balance = data_balance.iloc[:, 1]
# print(finance_balance)
# print(margin_balance)

data_currency = pd.read_excel('/Users/wyb/PycharmProjects/algo-project/database/中间价_美元兑人民币.xlsx', index_col='指标名称')
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

data[['finance_balance', 'margin_balance', 'currency', 'north_money', 'north_money_net', 'rate']] = \
    data[['finance_balance', 'margin_balance', 'currency', 'north_money', 'north_money_net', 'rate']].astype('float')

# # Correlation analysis
# print(data.corr())


# Factor analysis
# Create short-term and long-term ratio
short_length = 5
long_length = 22


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


signal = np.array(ma_ratio(data.iloc[:, 1], short_length, long_length, 'down'))
x = np.array(data.iloc[long_length-1:, -1])
y = signal*x
new_index = data.index[long_length-1:]


# Cumulative return
def cumulative(simple_ret):
    cumulative_ret = [simple_ret[0]+1]
    for i in range(1, len(list(simple_ret))):
        cumulative_ret.append(cumulative_ret[-1]*(1+simple_ret[i]))
    return cumulative_ret


# Plot
cumulative_y = cumulative(y)  # cumulative return after timing strategy
cumulative_x = cumulative(x)  # original index cumulative return
plt.plot(new_index, cumulative_x)
plt.plot(new_index, cumulative_y)
stock = pd.Series(y, new_index)
fig = plt.figure()
qs.extend_pandas()
qs.stats.sharpe(stock)
qs.reports.basic(stock, benchmark=None, rf=0, grayscale=False, display=True, compounded=True)
plt.show()

# # Future test with LogisticRegression, Bad performance not considered
# input_data = np.zeros((data.shape[0]-long_length+1, 2))
# for i in range(data.shape[0]-long_length+1):
#     input_data[i, 0] = np.mean(data.iloc[i: i+long_length+1, 1])
#     input_data[i, 1] = np.mean(data.iloc[i: i+short_length+1, 1])
# input_data = pd.DataFrame(input_data)
# input_label = []
# for i in range(data.shape[0]-long_length+1):
#     if data.iloc[i+long_length-1, -1] > 0:
#         input_label.append(1)
#     else:
#         input_label.append(0)
#
# # X_train, X_test, y_train, y_test = train_test_split(input_data, input_label, test_size=0.3, random_state=0)
# X_train = input_data.iloc[:750, :]
# X_test = input_data.iloc[750:, :]
# y_train = input_label[:750]
# y_test = input_label[750:]
#
# model = LogisticRegression(solver='saga', penalty='l1')
# model.fit(X_train, y_train)
# y_pred_test = model.predict(X_test)
# print(y_pred_test)
# # print(accuracy_score(y_test, y_pred_test))
#
# # Plot
# x = np.array(data.iloc[750+long_length-1:, -1])
# y = np.array(y_pred_test)*x
# cumulative_y = cumulative(y)  # cumulative return after timing strategy
# cumulative_x = cumulative(x)  # original index cumulative return
# plt.plot(data.index[750+long_length-1:], cumulative_x)
# plt.plot(data.index[750+long_length-1:], cumulative_y)
# plt.show()