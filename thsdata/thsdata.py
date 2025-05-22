# -*- coding: utf-8 -*-
# File: thsdata.py
# Description: This module provides a wrapper for THS SDK to interact with stock market data,
#              including industry blocks, stock components, K-line data, and more.
# Author: bensema
# Date: 2025-05-15
# License: MIT
# Version: 1.0.0
# Note: This project is for personal research and study purposes only.
#       It is not intended for illegal use, and the author is not responsible for any issues caused by misuse.

import pytz
import json
import random
import inspect
import requests
import datetime
import pandas as pd
from thsdk import THS
from typing import Any, List, Optional, Tuple
from datetime import datetime, time

china_tz = pytz.timezone('Asia/Shanghai')


def _isdigit2code(code: str) -> str:
    """
    Convert a 6-digit stock code to a 10-character code with a market prefix.

    :param code: A 6-digit stock code (e.g., '600519').
    :return: A 10-character code with the market prefix (e.g., 'USHA600519').
    :raises ValueError: If the code is not 6 digits or does not match any known prefix.
    """
    if not code.isdigit() or len(code) != 6:
        raise ValueError("证券数字代码必须是6位数字")

    if code.startswith(("688", "60")):  # 沪
        market = "USHA"
    elif code.startswith(("300", "00")):  # 深
        market = "USZA"
    elif code.startswith(("8", "4", "9")):  # 京
        market = "USTM"
    elif code.startswith("11"):  # 深可转债
        market = "USZD"
    elif code.startswith("12"):  # 沪可转债
        market = "USHD"
    elif code.startswith("5"):  # 沪基金
        market = "USHJ"
    elif code.startswith("15"):  # 深基金
        market = "USZJ"
    else:
        raise ValueError("未知的证券代码前缀")

    return market + code


def _time_2_int(t: datetime) -> int:
    dst = (t.minute +
           (t.hour << 6) +
           (t.day << 11) +
           (t.month << 16) +
           (t.year << 20) -
           0x76c00000)
    return dst


class Adjust:
    """K线复权类型"""
    FORWARD = "Q"  # 前复权
    BACKWARD = "B"  # 后复权
    NONE = ""  # 不复权

    @classmethod
    def all_types(cls) -> List[str]:
        """返回所有复权类型"""
        return [cls.FORWARD, cls.BACKWARD, cls.NONE]


class Interval:
    """K线周期类型"""
    MIN_1 = 0x3001  # 1分钟K线
    MIN_5 = 0x3005  # 5分钟K线
    MIN_15 = 0x300f  # 15分钟K线
    MIN_30 = 0x301e  # 30分钟K线
    MIN_60 = 0x303c  # 60分钟K线
    MIN_120 = 0x3078  # 120分钟K线
    DAY = 0x4000  # 日K线
    WEEK = 0x5001  # 周K线
    MONTH = 0x6001  # 月K线
    QUARTER = 0x6003  # 季K线
    YEAR = 0x7001  # 年K线

    @classmethod
    def minute_intervals(cls) -> List[int]:
        """返回分钟级别周期"""
        return [cls.MIN_1, cls.MIN_5, cls.MIN_15, cls.MIN_30, cls.MIN_60, cls.MIN_120]

    @classmethod
    def day_and_above_intervals(cls) -> List[int]:
        """返回日及以上级别周期"""
        return [cls.DAY, cls.WEEK, cls.MONTH, cls.QUARTER, cls.YEAR]

    @classmethod
    def all_types(cls) -> List[int]:
        """返回所有周期类型"""
        return cls.minute_intervals() + cls.day_and_above_intervals()


class THSData:
    def __init__(self, ops: dict = None, ths_class: Optional[Any] = None):
        self.ops = ops
        self.hq = ths_class(self.ops) if ths_class else THS(self.ops)
        self.__share_instance = random.randint(6666666, 8888888)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @property
    def share_instance(self):
        self.__share_instance += 1  # Increment on access
        return self.__share_instance

    def connect(self):
        self.hq.connect()

    def disconnect(self):
        self.hq.disconnect()

    def about(self):
        about = "\n\nabout me: 本项目基于thsdk二次开发。仅用于个人对网络协议的研究和习作，不对外提供服务。请勿用于非法用途，对此造成的任何问题概不负责。 \n\n"

        if self.hq:
            thsdk_about = self.hq.about()
            about += "thsdk about:\n" + thsdk_about

        return about

    def query_data(self, req: str, query_type: str = "zhu") -> pd.DataFrame:
        try:
            response = self.hq.query_data(req, query_type)
            if response.code != 0:
                print(f"查询错误: {response.code}, 信息: {response.message}")
                return pd.DataFrame()  # Return an empty DataFrame on error
            df = pd.DataFrame(response.payload.data)
            return df

        except Exception as e:
            print(f"query_data exception occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on exception

    def _block_data(self, block_id: int):
        try:
            response = self.hq.get_block_data(block_id)
            if response.code != 0:
                print(f"查询错误: {response.code}, 信息: {response.message}")
                return pd.DataFrame()  # Return an empty DataFrame on error
            df = pd.DataFrame(response.payload.data)
            return df
        except Exception as e:
            print(f"An exception occurred: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on exception

    def _get_block_components(self, block_code: str) -> pd.DataFrame:
        try:
            response = self.hq.get_block_components(block_code)
            if response.code != 0:
                print(f"查询错误: {response.code}, 信息: {response.message}")
                return pd.DataFrame()  # Return an empty DataFrame on error
            df = pd.DataFrame(response.payload.data)
            return df
        except Exception as e:
            print(f"An exception occurred: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on exception

    def stock_codes(self) -> pd.DataFrame:
        """获取股票市场代码.

        :return: pandas.DataFrame

        Example::

            code        name
            USHA600519  贵州茅台
            USZA300750  宁德时代
            USTM832566    梓橦宫
        """
        return self._block_data(0xC6A6)

    def conbond_codes(self) -> pd.DataFrame:
        """获取可转债市场代码.

        :return: pandas.DataFrame

        Example::

            code        name
            USHD113037   紫银转债
            USZD123158   宙邦转债
            USHD110094   众和转债
        """
        return self._block_data(0xCE14)

    def etf_codes(self) -> pd.DataFrame:
        """获取ETF基金市场代码.

        :return: pandas.DataFrame

        Example::

            code        name
            USHJ589660       综指科创
            USZJ159201   自由现金流ETF
            USHJ510410      资源ETF
        """
        return self._block_data(0xCFF3)

    def security_bars(self, code: str, start: datetime, end: datetime, adjust: str, period: int) -> pd.DataFrame:
        """获取指定证券的K线数据.
        支持日k线、周k线、月k线，以及5分钟、15分钟、30分钟和60分钟k线数据.

        :param code: 证券代码，例如 'USHA600519'
        :type code: str
        :param start: 开始时间，格式为 datetime 对象
        :type start: datetime.datetime
        :param end: 结束时间，格式为 datetime 对象
        :type end: datetime.datetime
        :param adjust: 复权类型， :const:`Q`, :const:`B`, :const:``
        :type adjust: str
        :param period: 数据类型，
        :type period: int

        :return: pandas.DataFrame

        Example::

                time    close   volume    turnover     open     high      low
            2024-01-02  1685.01  3215644  5440082500  1715.00  1718.19  1678.10
            2024-01-03  1694.00  2022929  3411400700  1681.11  1695.22  1676.33
            2024-01-04  1669.00  2155107  3603970100  1693.00  1693.00  1662.93
        """
        m_period = {0x3001, 0x3005, 0x300f, 0x301e, 0x303c, 0x3078, }

        if period in m_period:
            start_int = _time_2_int(start)
            end_int = _time_2_int(end)
        else:
            if start.tzinfo is None:
                # If naive, localize to Beijing timezone
                start = china_tz.localize(start)
            else:
                # Convert to Beijing timezone
                start = start.astimezone(china_tz)

            if end.tzinfo is None:
                # If naive, localize to Beijing timezone
                end = china_tz.localize(end)
            else:
                # Convert to Beijing timezone
                end = end.astimezone(china_tz)

            start_int = int(start.strftime('%Y%m%d'))
            end_int = int(end.strftime('%Y%m%d'))

        response = self.hq.security_bars(code, start_int, end_int, adjust, period)
        if response.code != 0:
            func_name = inspect.currentframe().f_code.co_name
            raise ValueError(f"[{func_name}] 查询错误: {response.code}, 信息: {response.message}")
        return pd.DataFrame(response.payload.data)

    def ths_industry_block(self) -> pd.DataFrame:
        """获取行业板块.

        :return: pandas.DataFrame

        Example::

                      code   name
            0   URFI881165     综合
            1   URFI881171  自动化设备
            2   URFI881118   专用设备
            3   URFI881141     中药
            4   URFI881157     证券
            ..         ...    ...
            85  URFI881138   包装印刷
            86  URFI881121    半导体
            87  URFI881131   白色家电
            88  URFI881273     白酒
            89  URFI881271   IT服务
        """
        return self._block_data(0xCE5F)

    def ths_industry_sub_block(self) -> pd.DataFrame:
        """获取三级行业板块.

        :return: pandas.DataFrame

        Example::

                       code    name
            0    URFA884270  综合环境治理
            1    URFA884164    自然景点
            2    URFA884065    装饰园林
            3    URFA884161    专业连锁
            4    URFA884068    专业工程
            ..          ...     ...
            225  URFA884091   半导体材料
            226  URFA884160    百货零售
            227  URFA884294    安防设备
            228  URFA884045      氨纶
            229  URFA884095     LED
        """
        return self._block_data(0xc4b5)

    def ths_concept_block(self) -> pd.DataFrame:
        """获取概念板块.

        :return: pandas.DataFrame

        Example::

                       code       name
            0    URFI885580       足球概念
            1    URFI885758       租售同权
            2    URFI885764      自由贸易港
            3    URFI885760      装配式建筑
            4    URFI885877        转基因
            ..          ...        ...
            391  URFI886037       6G概念
            392  URFI885556         5G
            393  URFI885537       3D打印
            394  URFI886088  2024三季报预增
            395  URFI886097   2024年报预增
        """
        return self._block_data(0xCE5E)

    def ths_block_components(self, block_code: str) -> pd.DataFrame:
        """查询行业，行业三级，概念板块成分股.

        :param block_code: 板块代码，例如 'URFI881157'

        :return: pandas.DataFrame

        Example::

                      code   name
            0   USHA601375  中原证券
            1   USHA601696  中银证券
            2   USHA600030  中信证券
            ..          ...     ...
            46  USZA002939  长城证券
            47  USHA601108  财通证券
            48  USHA600906  财达证券
        """
        return self._get_block_components(block_code)

    def stock_cur_market_data(self, codes: List[str]) -> pd.DataFrame:
        """股票当前时刻市场数据

        :param codes: 证券代码，例如 'USHA600519, USHA600036' 注意只能同一市场
        :type codes: List[str]

        :return: pandas.DataFrame

        Example::
                price  deal_type   volume  volume_ratio  ...  limit_down    high    low   开盘涨幅
            0  669.54         21  4168728        0.5324  ...       541.6  677.31  663.1 -1.034


        """

        market = codes[0][:4]

        # 检查所有代码是否属于同一市场
        for code in codes:
            if len(code) != 10:
                raise ValueError("证券代码长度不足")
            if code[:4] != market:
                raise ValueError("只能同一市场的证券代码")

        short_codes = [code[4:] for code in codes]  # 剔除前4位
        short_code = ','.join(short_codes)  # 用逗号连接

        req = f"id=200&instance={self.share_instance}&zipversion=2&codelist={short_code}&market={market}&datatype=5,6,8,9,10,12,13,402,19,407,24,30,48,49,69,70,3250,920371,55,199112,264648,1968584,461256,1771976,3475914,3541450,526792,3153,592888,592890"

        data = self.query_data(req)

        return data

    def conbond_cur_market_data(self, codes: List[str]) -> pd.DataFrame:
        """可转债当前时刻市场数据

        :param codes: 证券代码，例如 'USHD600519, USHD600036' 注意只能同一市场
        :type codes: List[str]

        :return: pandas.DataFrame

        Example::
                price  deal_type   volume  volume_ratio  ...  limit_down    high    low   开盘涨幅
            0  669.54         21  4168728        0.5324  ...       541.6  677.31  663.1 -1.034


        """

        market = codes[0][:4]

        # 检查所有代码是否属于同一市场
        for code in codes:
            if len(code) != 10:
                raise ValueError("证券代码长度不足")
            if code[:4] != market:
                raise ValueError("只能同一市场的证券代码")

        short_codes = [code[4:] for code in codes]  # 剔除前4位
        short_code = ','.join(short_codes)  # 用逗号连接

        req = f"id=200&instance={self.share_instance}&zipversion=2&codelist={short_code}&market={market}&datatype=5,55,10,80,49,13,19,25,31,24,30,6,7,8,9,12,199112,264648,48,1771976,1968584,527527"

        data = self.query_data(req)

        return data

    def call_auction(self, code: str) -> pd.DataFrame:
        """集合竞价

        :param code: 证券代码，例如 'USHA600519'
        :type code: str

        :return: pandas.DataFrame

        Example::

                                    time    price    bid2_vol    ask2_vol  cur_volume
            0  2025-03-04 09:15:07+08:00  1487.02  2147483648  2147483648         500
            1  2025-03-04 09:15:10+08:00  1487.46         900  2147483648        1100
            2  2025-03-04 09:15:13+08:00  1487.46         997  2147483648        1203
            3  2025-03-04 09:15:16+08:00  1487.46         797  2147483648        1503
            4  2025-03-04 09:15:19+08:00  1487.46         697  2147483648        1603
            ..                       ...      ...         ...         ...         ...
            74 2025-03-04 09:24:46+08:00  1487.00         447  2147483648       11353
            75 2025-03-04 09:24:49+08:00  1487.00          47  2147483648       11953
            76 2025-03-04 09:24:52+08:00  1487.00         147  2147483648       12153
            77 2025-03-04 09:24:55+08:00  1487.00  2147483648         353       12300
            78 2025-03-04 09:24:58+08:00  1485.00  2147483648         253       13100

        """

        now = datetime.now()
        # 使用当前日期，构造当天的 9:15:00 和 9:25:00
        start = datetime.combine(now.date(), time(9, 15, 0))  # 9:15:00
        end = datetime.combine(now.date(), time(9, 25, 0))  # 9:25:00

        # 获取 Unix 时间戳（秒）
        start_unix = int(start.timestamp())
        end_unix = int(end.timestamp())
        market = code[:4]
        short_code = code[4:]
        req = f"id=204&instance={self.share_instance}&zipversion=2&code={short_code}&market={market}&datatype=1,10,27,33,49&start={start_unix}&end={end_unix}"

        data = self.query_data(req)
        data['time'] = pd.to_datetime(data['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(china_tz)

        return data

    def corporate_action(self, code: str) -> pd.DataFrame:
        """权息资料

        :param code: 证券代码，例如 'USHA600519'
        :type code: str

        :return: pandas.DataFrame

        Example::

                    time                                               权息资料
            0   20020725                   2002-07-25(每十股 转增1.00股 红利6.00元)$
            1   20030714                    2003-07-14(每十股 送1.00股 红利2.00元)$
            2   20040701                   2004-07-01(每十股 转增3.00股 红利3.00元)$
            3   20050805                   2005-08-05(每十股 转增2.00股 红利5.00元)$
            4   20060519                           2006-05-19(每十股 红利3.00元)$
            5   20060525  2006-05-25(  每10股对价现金41.3200元 ,每10股对价股票12.4000股)$
            6   20070713                           2007-07-13(每十股 红利7.00元)$
            7   20080616                           2008-06-16(每十股 红利8.36元)$
            8   20090701                          2009-07-01(每十股 红利11.56元)$
            9   20100705                          2010-07-05(每十股 红利11.85元)$
            10  20110701                   2011-07-01(每十股 送1.00股 红利23.00元)$
            11  20120705                          2012-07-05(每十股 红利39.97元)$
            12  20130607                          2013-06-07(每十股 红利64.19元)$
            13  20140625                   2014-06-25(每十股 送1.00股 红利43.74元)$
            14  20150717                   2015-07-17(每十股 送1.00股 红利43.74元)$
            15  20160701                          2016-07-01(每十股 红利61.71元)$
            16  20170707                          2017-07-07(每十股 红利67.87元)$
            17  20180615                         2018-06-15(每十股 红利109.99元)$
            18  20190628                         2019-06-28(每十股 红利145.39元)$
            19  20200624                         2020-06-24(每十股 红利170.25元)$
            20  20210625                         2021-06-25(每十股 红利192.93元)$
            21  20220630                         2022-06-30(每十股 红利216.75元)$
            22  20221227                         2022-12-27(每十股 红利219.10元)$
            23  20230630                         2023-06-30(每十股 红利259.11元)$
            24  20231220                         2023-12-20(每十股 红利191.06元)$
            25  20240619                         2024-06-19(每十股 红利308.76元)$
            26  20241220                         2024-12-20(每十股 红利238.82元)$
        """

        market = code[:4]
        short_code = code[4:]
        req = f"id=211&instance={self.share_instance}&zipversion=2&code={short_code}&market={market}&start=-36500&end=0&fuquan=Q&datatype=471&period=16384"

        data = self.query_data(req)

        return data

    def transaction_history(self, code: str, date: datetime) -> pd.DataFrame:
        """tick3秒l1快照数据

        :param code: 证券代码，例如 'USHA600519'
        :type code: str

        :param date: 指定日期
        :type date: datetime

        :return: pandas.DataFrame

        Example::

                                      time    price  ...  transaction_count  cur_volume
            0    2025-04-11 09:15:06+08:00  1544.00  ...                  0         100
            1    2025-04-11 09:15:09+08:00  1546.90  ...                  0         500
            2    2025-04-11 09:15:12+08:00  1546.90  ...                  0         700
            3    2025-04-11 09:15:15+08:00  1546.90  ...                  0         800
            4    2025-04-11 09:15:18+08:00  1550.98  ...                  0        5500
            ...                        ...      ...  ...                ...         ...
            4842 2025-04-11 14:59:51+08:00  1565.30  ...              23044           0
            4843 2025-04-11 14:59:54+08:00  1565.30  ...              23044           0
            4844 2025-04-11 14:59:57+08:00  1565.30  ...              23044           0
            4845 2025-04-11 15:00:00+08:00  1565.30  ...              23044           0
            4846 2025-04-11 15:00:03+08:00  1568.98  ...              23616      159400
        """
        # Ensure the date is in Beijing timezone
        if date.tzinfo is None:
            # If naive, localize to Beijing timezone
            date = china_tz.localize(date)
        else:
            # Convert to Beijing timezone
            date = date.astimezone(china_tz)

        # 构造当天的 09:15 和 15:30 时间
        start = datetime.combine(date.date(), time(9, 15, 0)).astimezone(china_tz)
        end = datetime.combine(date.date(), time(15, 30, 0)).astimezone(china_tz)

        # 转换为 Unix 时间戳（秒）
        start_unix = int(start.timestamp())
        end_unix = int(end.timestamp())

        market = code[:4]
        short_code = code[4:]
        req = f"id=205&instance={self.share_instance}&zipversion=2&code={short_code}&market={market}&start={start_unix}&end={end_unix}&datatype=1,5,10,12,18,49&TraceDetail=0"

        data = self.query_data(req)
        data['time'] = pd.to_datetime(data['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(china_tz)

        return data

    def order_book(self, code: str) -> dict:
        """5档盘口

        :param code: 证券代码，例如 'USHA600519'
        :type code: str

        :return: dict

        Example::
            {'bid4': 1585, 'bid4_vol': 1900, 'ask4': 1586.3, 'ask4_vol': 200, 'bid5': 1584.92, 'bid5_vol': 100, 'ask5': 1586.6, 'ask5_vol': 100, 'bid1': 1585.21, 'bid1_vol': 2, 'bid2': 1585.2, 'bid2_vol': 100, 'bid3': 1585.01, 'bid3_vol': 400, 'ask1': 1585.62, 'ask1_vol': 1100, 'ask2': 1585.65, 'ask2_vol': 100, 'ask3': 1586, 'ask3_vol': 1400, 'code': 'USHA600519'}


        """

        market = code[:4]
        short_code = code[4:]
        req = f"id=200&instance={self.share_instance}&zipversion=2&codelist={short_code}&market={market}&datatype=24,25,26,27,28,29,150,151,154,155,30,31,32,33,34,35,152,153,156,157"

        data = self.query_data(req)

        return data.iloc[0].to_dict()

    def moneyflow_major(self, code: str) -> pd.DataFrame:
        # todo  https://zx.10jqka.com.cn/marketinfo/moneyflow/graph/major?code=600519&start=20250101&end=20250314
        pass

    def wencai_select_codes(self, condition: str) -> Tuple[List[str], Exception]:
        """问财速查API.

        :param condition: 条件选股
        :return:
        """

        """
        <高定价权的绩优股>
        
        策略介绍
        公司具备良好的市场定价权，经营能力优秀，上市2年以上经过市场反复检验，业绩持续保持高速增长，具备持续盈利的能力，内在价值将不断提升。
        
        策略问句
        连续2年营业收入增长率大于16%，连续2年扣非净利润增长率大于15%，连续两年净资产收益率大于4，连续8个季度销售毛利率大于50%，连续8个季度净利润大于0，连续2年净利润增长率大于15%股价大于40，上市两年以上
        
        <主力资金做多中小盘>
        
        策略介绍
        跟踪主力资金动向选股往往可以让普通投资者一同喝汤吃肉，我们通过分析主力手法，提前在中盘股中精选主力看好个股。
        
        策略问句
        非st，非科创板，非退市，非停牌，流通市值大于5亿元，非同花顺，近1个月有>=1次的减持公告取反，今日曾涨停股且DDE排列前30位以内，主力持仓线上移，流通值<100亿元，大单净量翻红，剔除ST,流通值<100亿，股价<40元
        
        <触底反弹看涨股>
        
        策略介绍
        前期已经跌出黄金坑，形态上向上突破半年线，并且量能配合良好，上升通道已经打开，中线趋势向上，具备良好的投资价值
        
        策略问句
        昨天股价上穿120均线，前20个交易日跌幅大于4%，昨天放量上涨，今天高开大于0
        
        <问财高增长机构精选>
    
        策略介绍
        跟着机构选股思维选择好行业好股票，往往能让普通投资者实现超额收益。策略选取销售利润年年增长，营业净资产收益率和收入大幅增长的股票，实现远超大盘的收益。
        
        策略问句
        非st，非科创板，非退市，非停牌，流通市值大于5亿元，非同花顺，近1个月有>=1次的减持公告取反，销售毛利率连续3年大于65%，净资产收益率大于15％，营业收入同比增长10以上


        实用语句:
        wencai("涨停，非ST，上市时间大于3个月")
        wencai("涨停，非ST，上市时间大于3个月，连续涨停天数,首次涨停时间,最终涨停时间,涨停原因类别,涨停封单额,涨停封单量占流通a股比")
        wencai("近5日涨停次数排名前20，非ST，上市时间大于3个月")
        wencai("250日新高，非ST，沪深A，上市时间超过250天,股票代码,股票简称,最新价,最新涨跌幅,技术形态,买入信号inter")
        wencai("今年以来涨幅最大的前50名，非ST")
        wencai("今年以来跌幅最大的前10名，非ST")
        wencai("热门股 排名前200")
        wencai("2022-06-01人气榜排行前200名")
        wencai("概念板块近14日累计涨幅排名前5")
        wencai("脑机接口概念股")
        wencai("均线多头排列，MACD金叉，DIFF上穿中轴")
        wencai("股价大于10日均线，MACD金叉，换手率大于10%")
        wencai("黄金坑")
        wencai("营业收入增长率>10%;营业利润增长率>10%;加权净资产收益率>15%;总资产报酬率>5%")
        wencai("新股")
        wencai("2023-3-3 新股")
        wencai("上市时间不足一个月新股和次新股")
        wencai("5%<换手率<10%") 
        wencai("游资营业部连续3天买入") 
        wencai("股性极佳的自选股")
        wencai("距离机构目标价还有翻倍空间的股票")
        wencai("(vol5>vol20)且(vol5>vol60)，(最低价<120日均线)或(最低价<250日均线)或(最高价<upper和100日最高收盘价)") 
        wencai("macd金叉，成交额增长，(5日均线>20日均线)或(均价>EXPMA50)，最低价/EXPMA50<1.025，涨停价/63日最高收盘价<0.98，(10日均线>20日均线)或(5日均线>120日均线)或(60日均线<120日均线)")

        """

        url = "https://eq.10jqka.com.cn/dataQuery/query"

        # 定义请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://eq.10jqka.com.cn/",
            "Connection": "keep-alive"
        }

        # Prepare query parameters
        params = {"query": condition}

        try:
            # Make HTTP GET request
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise exception for bad status codes

            # Parse JSON response
            data = response.json()

            # Check status_msg
            if data.get("status_msg") != "success":
                return None, Exception(data.get("status_msg"))

            ret = []

            # Get stockList array
            stock_list = data.get("stockList", [])

            # Iterate through stockList
            for item in stock_list:
                stock_code = item.get("stock_code", "")
                market_id = item.get("marketid", "")

                d = stock_code
                if market_id == "17":
                    d = "USHA" + d
                    ret.append(d)
                elif market_id == "21":
                    d = "USHP" + d
                    ret.append(d)
                elif market_id == "22":
                    d = "USHT" + d
                    ret.append(d)
                elif market_id == "33":
                    d = "USZA" + d
                    ret.append(d)
                elif market_id == "37":
                    d = "USZP" + d
                    ret.append(d)
                elif market_id == "151":
                    d = "USTM" + d
                    ret.append(d)
                else:
                    d = "todo" + d
                    print(f"todo market {condition} {d}")

            return ret, None

        except requests.RequestException as e:
            return [], e
        except json.JSONDecodeError as e:
            return [], e

    def wencai_base(self, condition: str) -> pd.DataFrame:
        """问财base.

        :param condition: 条件选股
        :return:
        """
        response = self.hq.wencai_base(condition)
        if response.code != 0:
            func_name = inspect.currentframe().f_code.co_name
            raise ValueError(f"[{func_name}] 错误: {response.code}, 信息: {response.message}")

        return pd.DataFrame(response.payload.data)

    def wencai_nlp(self, condition: str) -> pd.DataFrame:
        """问财nlp.

        :param condition: 条件选股
        :return:
        """
        response = self.hq.wencai_nlp(condition)
        if response.code != 0:
            func_name = inspect.currentframe().f_code.co_name
            raise ValueError(f"[{func_name}] 错误: {response.code}, 信息: {response.message}")

        return pd.DataFrame(response.payload.data)

    def attention(self, code: str) -> pd.DataFrame:
        """舆情关注度.

        :param code: 6位股票代码 eg. 600519
        :return:
        """

        url = "https://ai.10jqka.com.cn/stockapi/yuqing/attention"

        # 定义请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://ai.10jqka.com.cn/",
            "Connection": "keep-alive"
        }

        # Prepare query parameters
        params = {"stockCode": code}

        try:
            # Make HTTP GET request
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise exception for bad status codes

            # Parse JSON response
            data = response.json()

            # Check status_msg
            if data.get("message") != "success":
                return pd.DataFrame()

            # Get stockList array
            data = data.get("data", [])

            return pd.DataFrame(data)



        except Exception as e:
            return pd.DataFrame()

    def getshape(self) -> pd.DataFrame:
        """k线策略形态.

        :param code: 6位股票代码 eg. 600519
        :return:
        """

        url = "https://ai.10jqka.com.cn/igroup/strategy/getshape/"

        # 定义请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://ai.10jqka.com.cn/",
            "Connection": "keep-alive"
        }

        # Prepare query parameters
        params = {}

        try:
            # Make HTTP GET request
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise exception for bad status codes

            # Parse JSON response
            data = response.json()

            # Check status_msg
            if data.get("errormsg") != "":
                return pd.DataFrame()

            # Get stockList array
            data = data.get("result", [])

            return pd.DataFrame(data)

        except Exception as e:
            return pd.DataFrame()

    def download(self, code: str, start: Optional[Any] = None, end: Optional[Any] = None, adjust: str = Adjust.NONE,
                 period: str = "max",
                 interval: int = Interval.DAY,
                 count: int = -1) -> pd.DataFrame:
        """获取历史k线数据。

       :param period:  str max
       :param code: 证券代码，支持格式
                    6位数字代码:600519;
                    8位缩写市场和数字代码:sh600519;
                    9位缩写尾部市场和数字代码:600519.sh
                    10个字符标准ths格式代码(前4位指定市场market，比如并以'USHA'或'USZA'开头):USHA600519
       :param count: 需要的数量，推荐使用此参数
       :param start: 开始时间，格式取决于周期。对于日级别，使用日期（例如，20241224）。对于分钟级别，datetime。
       :param end: 结束时间，格式取决于周期。对于日级别，使用日期（例如，20241224）。对于分钟级别，datetime。
       :param adjust: 复权类型，必须是有效的复权值之一。
       :param interval: 周期类型，必须是有效的周期值之一。
       :param count: 指定数量

       :return: pandas.DataFrame

        Example::

                time    close   volume    turnover     open     high      low
            2024-01-02  1685.01  3215644  5440082500  1715.00  1718.19  1678.10
            2024-01-03  1694.00  2022929  3411400700  1681.11  1695.22  1676.33
            2024-01-04  1669.00  2155107  3603970100  1693.00  1693.00  1662.93
        """

        code = code.upper()

        if len(code) == 6:
            code = _isdigit2code(code)
        elif len(code) == 8:
            if code.startswith(("SH", "SZ", "BJ")):
                code = _isdigit2code(code[2:])
            elif code.endswith(("SH", "SZ", "BJ")):
                code = _isdigit2code(code[:6])
            else:
                raise ValueError(
                    "8位代码必须以SH或SZ开头或者结尾，例如 'SH600519' 或 'SZ000001'， '600519SH' 或 '000001SZ'")
        elif len(code) == 9:
            if code.startswith(("SH.", "SZ.", "BJ.")):
                code = _isdigit2code(code[3:])
            elif code.endswith((".SH", ".SZ")):
                code = _isdigit2code(code[:6])
            else:
                raise ValueError("9位代码必须以.SH或.SZ结尾，例如 '600519.SH' 或 '000001.SZ'")

        if interval in Interval.minute_intervals() and isinstance(start, datetime) and isinstance(end, datetime):
            start, end = _time_2_int(start), _time_2_int(end)

        code = code.upper()

        response = self.hq.download(code, start, end, adjust, period, interval, count)
        data = pd.DataFrame(response.payload.data)
        if response.code != 0:
            func_name = inspect.currentframe().f_code.co_name
            raise ValueError(f"[{func_name}] 错误: {response.code}, 信息: {response.message}")

        # Check if data is not empty
        if data is not None and not data.empty:
            # Specify column order
            desired_columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            if all(col in data.columns for col in desired_columns):
                data = data[desired_columns]
        else:
            # Handle the case where no data is returned
            data = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])

        return data

    def dc(self):

        """
            东方财富 推送
            http://74.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=700&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|1|0|web&fid=f243&fs=b:MK0354&fields=f1,f5,f30,f152,f2,f3,f12,f13,f14,f227,f228,f229,f230,f231,f232,f233,f234,f235,f236,f237,f238,f239,f240,f241,f242,f26,f243&_=1686201469778
            https://push2.eastmoney.com/api/qt/stock/trends2/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58&ut=fa5fd1943c7b386f172d6893dbfba10b&ndays=1&iscr=1&secid=1.000001
            https://push2his.eastmoney.com/api/qt/stock/trends2/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58&ndays=1&secid=0.000422

            富途
            https://www.futunn.com/OpenAPI

            美股行情
            https://polygon.io/


        :return:
        """
