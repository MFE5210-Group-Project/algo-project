import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import quantstats as qs
import pandas as pd
import numpy as np


# Data for test the function
df = pd.read_csv('/Users/wyb/Desktop/stratification_test_5.csv', index_col='trading_date')
daily_ret = df.iloc[:, 6]
x = np.array(df.index)
y = np.array(daily_ret)
data_plot = pd.Series(daily_ret, x)
data_plot.index = pd.to_datetime(data_plot.index)


# Plot Function
def display_figure(stock, plot_full):
    """

    :param stock: Series; index is Time (Datetime); column is daily_return (Series, float32)
    :param plot_full: True: reports.full; False: reports.basic
    :return: Figures; Strategy performance
    """
    qs.extend_pandas()
    if plot_full is True:
        qs.reports.full(stock, benchmark=None, rf=0.03, grayscale=False, display=True, compounded=True)
    else:
        qs.reports.basic(stock, benchmark=None, rf=0.03, grayscale=False, display=True, compounded=True)


# display_figure(data_plot, False)


def display_gif(data_plot, xname, yname, picname, savename):
    """

    :param data_plot: DataFrame; index is Time
    :param xname: str; x label
    :param yname: str; y label
    :param picname: str; title
    :param savename: str; saving path
    :return: GIF
    """

    fig = plt.figure(figsize=(25, 15))
    plt.ylim(np.min(y), np.max(y))
    plt.xlabel(xname, fontsize=35)
    plt.xticks(range(0, data_plot.shape[0], 15))
    plt.ylabel(yname, fontsize=35)
    plt.title(picname, fontsize=50)

    def animate(i):
        data = data_plot.iloc[:int(i)]
        p = sns.lineplot(x=data.index, y=data.iloc[:, 0], data=data, color="r")
        p.tick_params(labelsize=data_plot.shape[0])
        plt.xticks(size=15)
        plt.yticks(size=15)
        plt.setp(p.lines, linewidth=3)

    ani = animation.FuncAnimation(fig, animate, frames=data_plot.shape[0])
    ani.save(savename, writer='pillow')
    plt.show()


# display_gif(data_plot, 'Time', 'Cumulative Return',
#         'Back-test: Cumulative Return',
#         'Back-test: Cumulative Return.gif')
