# -*- coding: utf-8 -*-

import requests
import json
import time
from bosys_api import bosys_server

class Constant:
    class DATA:
        class CRYCLE:
            TICK = 'tick'
            D_1M = '1m'
            D_1D = '1d'

        class SOURCE:
            DEFAULT = 'default'
            WIND = 'wind'
            ZHONGXING = 'zhongxin'
            XINGZHENG = 'xingzheng'
            ZHAOSHANG = 'zhaoshang'
            RUIDA = 'ruida'

    class ALGOID:
        # 每次按对方的买一/卖一价格报单，如果没有全部成交，则间隔interval秒后继续报单，直到全部成交
        MARKET = 1      # "interval:5.5"    间隔时间（单位秒, double)

        # 每次按我方的买一/卖一价格报单，每次拆单最多为split_volume手，直到全部成交
        # 如果报单在间隔interval秒内没全部成交，则重试加价，
        # 对买单在max(bid_1, 上一次报单价格)上加raise_price_unit个base_price，
        # 对卖单在min(ask_1, 上一次报单价格)上减raise_price_unit个base_price
        AUTOLIMIT = 2   # "split_volume:10,interval:5.5,raise_price_unit:1,base_price:0.01"
                        # spilt_volume: 拆单后最大下单数量 (int)
                        # interval: 重试间隔时间(单位秒, double)
                        # raise_price_unit: 重试加价单位(int)
                        # base_price: 标的最小交易单位(double)


class BtCommitReq:
    # 初始化为None的字段都为非必填字段

    class Order:
        def __init__(self):
            self.account_id = ''    # 账号id
            self.strategy_id = ''   # 策略id
            self.instrument = ''    # 标的格式: "标的代码.交易所"
            self.symbol = ''        # 标的的交易代码
            self.date = ''          # 交易日 yyyy-mm-dd
            self.time = ''          # 交易时间 hh:mm:ss
            self.real_time = 0      # 交易实际时间戳(微秒)
            self.oc = ''            # 开仓平仓: o/c(没有开仓平仓的标的统一填开仓)
            self.bs = ''            # 买卖: b/s
            self.volume = 0         # 量
            self.algo_id = 0        # 算法id 参考Constant.DATA.ALGOID
            self.algo_params = ''   # 算法参数 "k1:v1,k2:v2,k3:v3"

    class Head:
        class Account:
            def __int__(self):
                self.account_id = ''        # 账号id
                self.initial_amount = 0.0   # 账号初始金额

        class Instrument:
            def __int__(self):
                self.instrument = ''        # 标的格式: "标的代码.交易所"

                # 交易时间(非必填, 跨过零点要拆开成两个时间段)
                # 以cu为例: "210000-240000,000000-010000,090000-101500,103000-113000,133000-150000"
                # 使用建议: 如果标的使用了tick和分钟级别的数据，则该标的需要填写，避免撮合到非交易时间段的数据
                self.trading_time = None

        def __init__(self):
            self.name = None            # 回测名(非必填, 默认时间戳表示名字)
            self.begin_date = ''        # 开始日期 yyyy-mm-dd
            self.end_date = ''          # 结束日期 yyyy-mm-dd
            self.cycle = None           # 周期 参考Constant.DATA.CRYCLE(非必填, 默认Constant.DATA.CRYCLE.TICK)
            self.source = None          # tick数据源 参考Constant.DATA.SOURCE(非必填, 默认Constant.DATA.SOURCE.DEFAULT)
            self.priority = None        # 用户级别的优先级(非必填) 默认为0(中等优先级), 支持负数, 数值越大优先级越高, 支持运行时调整优先级
            self.is_continuous = None   # 回测记录上传时是否需要连续上传, 值为false时会覆盖策略名称一致的策略（非必填，默认false，每次按orders的交易日填的区间填写begin_time&end_time）
            self.is_raw = None          # 缓存是否保存原始tick数据(非必填，默认false，true时查看交易记录会输出对应成交的tick数据)
            self.accounts = []          # BtCommitReq.Head.Account
            self.instruments = []       # 标的信息 BtCommitReq.Head.Instrument

    def __init__(self):
        self.head = BtCommitReq.Head()
        self.orders = []            # BtCommitReq.Order


class BtCommitRsp:
    class Data:
        def __init__(self):
            self.task_id = 0

    def __init__(self, d):
        self.code = d['code']
        self.info = d['info']
        self.data = None

        if self.code == 0:
            self.data = BtCommitRsp.Data()
            self.data.task_id = d['data']['task_id']


# 回测提交
def backtest_commit(host, headers, req=None):
    url = host + '/backtest/commit'
    q = ''
    if req is None:
        q = '''
        {
            "head": {
                "name": "test",
                "begin_date": "2021-01-01",
                "end_date": "2021-01-31",
                "accounts" : [
                    {
                        "account_id": "test_A",
                        "initial_amount": 100000.0
                    },
                    {
                        "account_id": "test_B",
                        "initial_amount": 200000.0
                    },
                    {
                        "account_id": "test_C",
                        "initial_amount": 300000.0
                    }
                ],
                "instruments": [
                    {
                        "instrument": "CU2103.SHF",
                        "trading_time": "210000-240000,000000-010000,090000-101500,103000-113000,133000-150000"
                    }
                ]
            },

            "orders": [
                {
                    "account_id": "test_A",
                    "strategy_id": "test_strategy_A",
                    "instrument": "CU2103.SHF",
                    "symbol": "cu2103",
                    "date": "2021-01-07",
                    "time": "11:00:00",
                    "real_time": 1609988400000000,
                    "oc": "o",
                    "bs": "b",
                    "volume": 100,
                    "algo_id": 1,
                    "algo_params": "interval:2"
                },
                {
                    "account_id": "test_B",
                    "strategy_id": "test_strategy_B",
                    "instrument": "CU2103.SHF",
                    "symbol": "cu2103",
                    "date": "2021-01-08",
                    "time": "11:00:00",
                    "real_time": 1610074800000000,
                    "oc": "o",
                    "bs": "b",
                    "volume": 200,
                    "algo_id": 1,
                    "algo_params": "interval:0.5"
                },
                 {
                    "account_id": "test_C",
                    "strategy_id": "test_strategy_C",
                    "instrument": "CU2103.SHF",
                    "symbol": "cu2103",
                    "date": "2021-01-08",
                    "time": "11:00:00",
                    "real_time": 1610074800000000,
                    "oc": "o",
                    "bs": "b",
                    "volume": 300,
                    "algo_id": 1,
                    "algo_params": "interval:0.5"
                },
                {
                    "account_id": "test_A",
                    "strategy_id": "test_strategy_A",
                    "instrument": "CU2103.SHF",
                    "symbol": "cu2103",
                    "date": "2021-01-15",
                    "time": "11:00:00",
                    "real_time": 1610679600000000,
                    "oc": "c",
                    "bs": "b",
                    "volume": 100,
                    "algo_id": 1,
                    "algo_params": "interval:1"
                },
                {
                    "account_id": "test_B",
                    "strategy_id": "test_strategy_B",
                    "instrument": "CU2103.SHF",
                    "symbol": "cu2103",
                    "date": "2021-01-22",
                    "time": "11:00:00",
                    "real_time": 1611284400000000,
                    "oc": "c",
                    "bs": "s",
                    "volume": 200,
                    "algo_id": 1,
                    "algo_params": "interval:2"
                },
                {
                    "account_id": "test_C",
                    "strategy_id": "test_strategy_C",
                    "instrument": "CU2103.SHF",
                    "symbol": "cu2103",
                    "date": "2021-01-29",
                    "time": "11:00:00",
                    "real_time": 1611889200000000,
                    "oc": "c",
                    "bs": "s",
                    "volume": 300,
                    "algo_id": 1,
                    "algo_params": "interval:2"
                }
            ]
        }
        '''

        # 跌停板-卖
        # q = '''{"head": {"name": "test", "begin_date": "2020-01-01", "end_date": "2020-12-31", "cycle": null, "source": null, "priority": null, "accounts": [{"account_id": "test_A", "initial_amount": 100000.0}], "instruments": []}, "orders": [{"account_id": "test_A", "strategy_id": "test_strategy_A", "instrument": "P2005.DCE", "symbol": "p2005", "date": "2020-02-03", "time": "09:01:00", "real_time": 1580691660000000, "oc": "c", "bs": "s", "volume": 4, "algo_id": 1, "algo_params": "interval:2.5"}]}'''

        q = '''{"head": {"name": "2015-01-06", "begin_date": "2015-01-06", "end_date": "2015-01-06", "cycle": null, "source": null, "priority": null, "is_continuous": true, "is_raw": null, "accounts": [{"account_id": "RB_AI_basline00", "initial_amount": 1000000.0}], "instruments": []}, "orders": [{"account_id": "RB_AI_basline00", "strategy_id": "RB_AI_basline00_1OD", "instrument": "RB1505.SHF", "symbol": "RB1505", "date": "2015-01-06", "time": "21:05:00", "real_time": 1420549500000000, "oc": "c", "bs": "b", "volume": 39, "algo_id": 1, "algo_params": "interval:5"}]}'''
    else:
        q = json.dumps(obj=req, default=lambda x: x.__dict__)

    rsp = requests.get(url, params={'q': q}, headers=headers)
    print(rsp.json())
    return BtCommitRsp(rsp.json())


class BtControlReq:
    def __init__(self):
        self.task_id = 0    # 任务id
        self.cmd_key = ''   # cancel|priority|stop|run => 取消|调整优先级|暂停|运行
        self.cmd_val = 0    # priority时必填为调整的优先级，其他时候非必填


class BtControlRsp:
    def __init__(self, d):
        self.code = d['code']
        self.info = d['info']


# 回测任务控制
def backtest_control(host, headers, req=None):
    url = host + '/backtest/control'

    q = ''
    if req is None:
        q = '''
        {
            "task_id": 3303,
            "cmd_key": "cancel",
            "cmd_val": 10
        }
        '''
    else:
        q = json.dumps(obj=req, default=lambda x: x.__dict__)

    rsp = requests.get(url, params={'q': q}, headers=headers)
    print(rsp.json())
    return BtControlRsp(rsp.json())


def test_set_cycle_source(account):
    btCommitReq = BtCommitReq()
    btCommitReq.head.name = 'test'
    btCommitReq.head.begin_date = '2018-07-01'
    btCommitReq.head.end_date = '2018-12-31'
    btCommitReq.head.cycle = Constant.DATA.CRYCLE.TICK
    btCommitReq.head.source = Constant.DATA.SOURCE.RUIDA
    btCommitReq.head.accounts.append(account)

    o = BtCommitReq.Order()
    o.account_id = 'test_A'
    o.strategy_id = 'test_strategy_A'
    o.instrument = 'IH1812.CFE'
    o.symbol = 'IH1812'
    o.date = '2018-09-10'
    o.time = '11:00:00'
    o.real_time = 1536548400000000
    o.oc = 'o'
    o.bs = 'b'
    o.volume = 200
    o.algo_id = Constant.ALGOID.MARKET
    o.algo_params = 'interval:2.5'
    btCommitReq.orders.append(o)
    return btCommitReq


def test_future(account):
    btCommitReq = BtCommitReq()
    btCommitReq.head.name = 'test'
    btCommitReq.head.begin_date = '2017-01-01'
    btCommitReq.head.end_date = '2017-12-31'
    btCommitReq.head.accounts.append(account)

    o = BtCommitReq.Order()
    o.account_id = 'test_A'
    o.strategy_id = 'test_strategy_A'
    o.instrument = 'IC1701.CFE'
    o.symbol = 'IC1701'
    o.date = '2017-01-03'
    o.time = '11:00:00'
    o.real_time = 1483412400000000
    o.oc = 'o'
    o.bs = 'b'
    o.volume = 200
    o.algo_id = Constant.ALGOID.MARKET
    o.algo_params = 'interval:2.5'
    btCommitReq.orders.append(o)
    return btCommitReq


def test_index(account):
    btCommitReq = BtCommitReq()
    btCommitReq.head.name = 'test'
    btCommitReq.head.begin_date = '2020-01-01'
    btCommitReq.head.end_date = '2020-12-31'
    btCommitReq.head.accounts.append(account)

    o = BtCommitReq.Order()
    o.account_id = 'test_A'
    o.strategy_id = 'test_strategy_A'
    o.instrument = '000300.SH'
    o.symbol = '000300'
    o.date = '2020-12-31'
    o.time = '11:00:00'
    o.real_time = 1609383600000000
    o.oc = 'o'
    o.bs = 'b'
    o.volume = 200
    o.algo_id = Constant.ALGOID.MARKET
    o.algo_params = 'interval:2.5'
    btCommitReq.orders.append(o)
    return btCommitReq


def test_equity(account):
    btCommitReq = BtCommitReq()
    btCommitReq.head.name = 'test'
    btCommitReq.head.begin_date = '2020-01-01'
    btCommitReq.head.end_date = '2020-12-31'
    btCommitReq.head.accounts.append(account)

    o = BtCommitReq.Order()
    o.account_id = 'test_A'
    o.strategy_id = 'test_strategy_A'
    o.instrument = '600100.SH'
    o.symbol = '600100'
    o.date = '2020-12-31'
    o.time = '11:00:00'
    o.real_time = 1609383600000000
    o.oc = 'o'
    o.bs = 'b'
    o.volume = 200
    o.algo_id = Constant.ALGOID.MARKET
    o.algo_params = 'interval:2.5'
    btCommitReq.orders.append(o)
    return btCommitReq


def test_etf(account):
    btCommitReq = BtCommitReq()
    btCommitReq.head.name = 'test'
    btCommitReq.head.begin_date = '2020-01-01'
    btCommitReq.head.end_date = '2020-12-31'
    btCommitReq.head.accounts.append(account)

    o = BtCommitReq.Order()
    o.account_id = 'test_A'
    o.strategy_id = 'test_strategy_A'
    o.instrument = '510300.SH'
    o.symbol = '510300'
    o.date = '2020-12-31'
    o.time = '11:00:00'
    o.real_time = 1609383600000000
    o.oc = 'o'
    o.bs = 'b'
    o.volume = 200
    o.algo_id = Constant.ALGOID.MARKET
    o.algo_params = 'interval:2.5'
    btCommitReq.orders.append(o)
    return btCommitReq


def test_option(account):
    btCommitReq = BtCommitReq()
    btCommitReq.head.name = 'test'
    btCommitReq.head.begin_date = '2021-01-01'
    btCommitReq.head.end_date = '2021-12-31'
    btCommitReq.head.accounts.append(account)

    o = BtCommitReq.Order()
    o.account_id = 'test_A'
    o.strategy_id = 'test_strategy_A'
    #o.instrument = 'CU2106C58000.SHF'
    #o.symbol = 'cu2106C58000'
    o.instrument = 'IO2104-P-5000.CFE'
    o.symbol = 'IO2104-P-5000'
    o.date = '2021-04-12'
    o.time = '11:00:00'
    o.real_time = 1618196400000000
    o.oc = 'o'
    o.bs = 'b'
    o.volume = 200
    o.algo_id = Constant.ALGOID.MARKET
    o.algo_params = 'interval:2.5'
    btCommitReq.orders.append(o)
    return btCommitReq


def to_real_time(yyyy_mm_dd, hh_mm_ss):
    t = time.strptime(yyyy_mm_dd + ' ' + hh_mm_ss , "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(t)) * 1000 * 1000


class PositionDataRsp:
    class Data:
        class PositionData:
            def __init__(self):
                self.wind_code = ''
                self.qty = 0.0
                self.cost_price = 0.0
                self.cost_amount = 0.0

        def __init__(self):
            self.position_data = []     # 参考PositionDataRsp.Data.PositionData
            self.cash = 0.0

    def __init__(self, d):
        self.code = d['code']
        self.message = d['message']
        self.data = PositionDataRsp.Data()
        if self.code == 0:
            self.data.cash = d['data']['cash']
            for node in d['data']['position_data']:
                pd = PositionDataRsp.Data.PositionData()
                pd.wind_code = node['wind_code']
                pd.qty = node['qty']
                pd.cost_price = node['cost_price']
                pd.cost_amount = node['cost_amount']
                self.data.position_data.append(pd)


def fetch_position_data(host, task_id):
    url = host + '/position/backtest/position_data'
    headers = {'Content-Type': 'application/json'}
    rsp = requests.post(url, json={'task_id': task_id}, headers=headers)
    print(rsp.json())
    return PositionDataRsp(rsp.json())


class QueryTaskRsp:
    class Data:
        class STATE:
            CANNCEL = -2    # 取消回测
            RESTART = -1    # 重跑回测
            INIT = 0        # 初始化
            RUNNING = 1     # 回测中
            SUCCESS = 2     # 测回完成
            FAIL = 3        # 回测出错

        def __init__(self):
            self.task_id = 0
            self.user_id = 0
            self.state = 0     # 参考QueryTaskRsp.Data.STATE
            self.state_desc = ''
            self.proc_id = 0
            self.name = ''
            self.create_time = ''
            self.update_time = ''
            self.ct = 0
            self.ut = 0

    def __init__(self, d):
        self.code = d['code']
        self.info = d['info']
        if self.code == 0:
            self.data = QueryTaskRsp.Data()
            self.data.task_id = d['data']['id']
            self.data.user_id = d['data']['user_id']
            self.data.state = d['data']['state']
            self.data.state_desc = d['data']['state_desc']
            self.data.proc_id = d['data']['proc_id']
            self.data.name = d['data']['name']
            self.data.create_time = d['data']['create_time']
            self.data.update_time = d['data']['update_time']
            self.data.ct = d['data']['ct']
            self.data.ut = d['data']['ut']


def query_task(host, task_id):
    url = host + '/backtest/query/task'
    rsp = requests.get(url, params={'task_id': task_id})
    print(rsp.json())
    return QueryTaskRsp(rsp.json())


def busy_polling_sync(host, task_id):
    while True:
        queryTaskRsp = query_task(backtest_host, task_id)
        if queryTaskRsp.code != 0:
            print('query_task error, task_id={}, code={}, info={}'.format(
                task_id, queryTaskRsp.code, queryTaskRsp.info))
            return False
        if queryTaskRsp.data.state == QueryTaskRsp.Data.STATE.RUNNING:
            time.sleep(1)
        elif queryTaskRsp.data.state == QueryTaskRsp.Data.STATE.SUCCESS:
            print('backtest success')
            return True
        else:
            print('query_task state error, task_id={}, state={}'.format(task_id, queryTaskRsp.data.state))
            return False


def continue_demo(backtest_host, backtest_headers, position_host):
    bosys_server.login('lulu', 'lulu')
    account_id = 'test_A'
    strategy_id = 'test_strategy_A'

    account = BtCommitReq.Head.Account()
    account.account_id = account_id
    account.initial_amount = 1000 * 10000.0

    frist_backtest = True
    for trading_date in ['2021-01-07', '2021-01-08', '2021-01-15', '2021-01-22', '2021-01-29']:
        print('begin trading_date={}'.format(trading_date))
        btCommitReq = BtCommitReq()
        btCommitReq.head.name = 'test'
        btCommitReq.head.begin_date = trading_date
        btCommitReq.head.end_date = trading_date
        btCommitReq.head.accounts.append(account)

        if frist_backtest:
            # 策略第一次回测，有记录则覆盖，无记录则创建
            frist_backtest = False
        else:
            # 之后报单成交记录追加到之前的记录上
            btCommitReq.head.is_continuous = True

        o = BtCommitReq.Order()
        o.account_id = account_id
        o.strategy_id = strategy_id
        o.instrument = 'CU2103.SHF'
        o.symbol = 'cu2103'
        o.date = trading_date
        o.time = '11:00:00'
        o.real_time = to_real_time(o.date, o.time)
        o.oc = 'o'
        o.bs = 'b'
        o.volume = 2
        o.algo_id = Constant.ALGOID.MARKET
        o.algo_params = 'interval:2.5'
        btCommitReq.orders.append(o)

        btCommitRsp = backtest_commit(backtest_host, backtest_headers, btCommitReq)
        if btCommitRsp.code != 0:
            print("backtest_commit error")
            return False
        task_id = btCommitRsp.data.task_id
        print("backtest_commit success, task_id={}".format(task_id))

        # 获取持仓记录(可能阻塞一段时间，直到本次回测完毕后，回测服务把交易记录更新到持仓才会返回)
        res = bosys_server.get_position_data(account_id, strategy_id, '回测交易', trading_date, task_id)
        print(res)
        # if positionDataRsp.code != 0:
        #     print('fetch_position_data error, task_id={}'.format(task_id))
        #     return False

        print('end trading_date={}, task_id={}\n'.format(trading_date, task_id))

    print("continue_demo success")
    return True


if __name__ == '__main__':
    position_host = 'http://192.168.1.160:30100'    # 线上
    backtest_host = 'http://192.168.1.160:20200'    # 线上

    #develop = False
    develop = True
    if develop:
        position_host = 'http://192.168.1.252:30110'  # 开发
        backtest_host = 'http://192.168.1.160:20250'  # 开发

    token = 'f36373dddd25996c04dd5736096757bbf7355dce'
    backtest_headers = {'Authorization': token}

    account = BtCommitReq.Head.Account()
    account.account_id = 'test_A'
    account.initial_amount = 100000.0

    # 单次回测
    # btCommitReq = test_set_cycle_source(account)  # 指定cycle和source
    # btCommitReq = test_future(account)
    # btCommitReq = test_index(account)
    # btCommitReq = test_equity(account)
    # btCommitReq = test_etf(account)
    # btCommitReq = test_option(account)
    # btCommitRsp = backtest_commit(backtest_host, backtest_headers, btCommitReq)

    # 直接测试json
    btCommitRsp = backtest_commit(backtest_host, backtest_headers, None)
    pass
    # 任务控制
    # if btCommitRsp.code == 0:
    #     btControlReq = BtControlReq()
    #     btControlReq.task_id = btCommitRsp.data.task_id
    #     btControlReq.cmd_key = 'cancel'
    #     backtest_control(backtest_host, backtest_headers, btControlReq)

    # 连续回测
    #continue_demo(backtest_host, backtest_headers, position_host)

    '''
    查询:
        1.查看task信息，则在浏览器输入，填入返回的task_id
        eg: http://192.168.1.160:20200/backtest/query/task?task_id=123456
    
        2.查看task交易记录和对应撮合的数据，则在浏览器输入，填入返回的task_id
        eg: http://192.168.1.160:20200/backtest/query/trade?task_id=123456

        3.查看上传到BO_SYS_BACKEND的json，则在浏览器输入，填入返回的task_id
        eg: http://192.168.1.160:20200/backtest/query/upload_trade?task_id=123456
    '''
























