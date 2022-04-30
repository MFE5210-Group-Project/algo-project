import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import pandas as pd
import numpy as np


# Data
df = pd.read_csv('/Users/wyb/Desktop/stratification_test_5.csv', index_col='trading_date')
cumulative_ret = df.iloc[:, 3]
x = np.array(df.index)
y = np.array(cumulative_ret)
data_plot = pd.DataFrame(y, x)
# print(data_plot)


# Plot Function
def display_gif(data_plot, xname, yname, picname, savename):
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
