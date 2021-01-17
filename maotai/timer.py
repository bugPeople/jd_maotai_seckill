# -*- coding:utf-8 -*-
import time
import requests
import json

from datetime import datetime
from maotai.jd_logger import logger
from maotai.config import global_config


class Timer(object):
    def __init__(self, sleep_interval=0.5):
        # '2018-09-28 22:45:50.000'
        # buy_time = 2020-12-22 09:59:59.500
        localtime = time.localtime(time.time())
        buy_time_everyday = global_config.getRaw(
            'config', 'buy_time').__str__()
        last_purchase_time_everyday = global_config.getRaw(
            'config', 'last_purchase_time').__str__()
        relogin_time_everyday = global_config.getRaw(
            'config', 'relogin_time').__str__()

        # 最后购买时间
        self.last_purchase_time = datetime.strptime(
            localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__() + ' ' + last_purchase_time_everyday,
            "%Y-%m-%d %H:%M:%S.%f")
        logger.info("最后购买时间：%s" % self.last_purchase_time)

        buy_time_config = datetime.strptime(
            localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__() + ' ' + buy_time_everyday,
            "%Y-%m-%d %H:%M:%S.%f")
        relogin_time_config = datetime.strptime(
            localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__() + ' ' + relogin_time_everyday,
            "%Y-%m-%d %H:%M:%S.%f")

        if time.mktime(localtime) < time.mktime(buy_time_config.timetuple()):
            # 取正确的购买时间
            self.buy_time = buy_time_config
            self.relogin_time = relogin_time_config
        # elif time.mktime(localtime) > time.mktime(self.last_purchase_time.timetuple()):
        #     # 取明天的时间 购买时间
        #     self.buy_time = datetime.strptime(
        #         localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + (
        #                 localtime.tm_mday + 1).__str__() + ' ' + buy_time_everyday,
        #         "%Y-%m-%d %H:%M:%S.%f")
        else:
            self.buy_time = datetime.strptime(
                localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + (
                        localtime.tm_mday + 1).__str__() + ' ' + buy_time_everyday,
                "%Y-%m-%d %H:%M:%S.%f")
            self.relogin_time = datetime.strptime(
                localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + (
                        localtime.tm_mday + 1).__str__() + ' ' + relogin_time_everyday,
                "%Y-%m-%d %H:%M:%S.%f")

        # self.buy_time = buy_time_config
        logger.info("开始购买时间：{}".format(self.buy_time))
        logger.info("重新登陆时间：{}".format(self.relogin_time))

        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)
        self.relogin_ms = int(time.mktime(self.relogin_time.timetuple()) * 1000.0 + self.relogin_time.microsecond / 1000)

        self.sleep_interval = sleep_interval

        self.diff_time = self.local_jd_time_diff()

        seckill_duration_ms = int(global_config.getRaw(
            'config', 'seckill_duration_ms'))
        self.buy_endtime_ms = self.buy_time_ms + seckill_duration_ms
        logger.info("抢购结束时间ms: {}".format(self.buy_endtime_ms))

    def jd_time(self):
        """
        从京东服务器获取时间毫秒
        :return:
        """
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)
        return int(js["serverTime"])

    def local_time(self):
        """
        获取本地毫秒时间
        :return:
        """
        return int(round(time.time() * 1000))

    def local_jd_time_diff(self):
        """
        计算本地与京东服务器时间差
        :return:
        """
        return self.local_time() - self.jd_time()

    def start(self):
        logger.info('正在等待到达设定时间:{}，检测本地时间与京东服务器时间误差为【{}】毫秒'.format(self.buy_time, self.diff_time))
        while True:
            # 本地时间减去与京东的时间差，能够将时间误差提升到0.1秒附近
            # 具体精度依赖获取京东服务器时间的网络时间损耗
            if self.local_time() - self.diff_time >= self.buy_time_ms:
                logger.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)

    def is_end(self):
        """
        计算秒杀是否结束
        """
        return self.local_time() - self.diff_time >= self.buy_endtime_ms

    def need_relogin(self):
        """计算是否需要重新登陆"""
        while True:
            if self.local_time() >= self.relogin_ms:
                logger.info("时间到达，验证是否需要重新登陆......")
                break
            else:
                time.sleep(self.sleep_interval)
