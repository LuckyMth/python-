# -*- coding: utf-8 -*-

"""
邻道干扰统计脚本
版本号：2.2.2.220115
更新内容：
使用步骤：
    1、修改配置文件日志数量、路径、正则式格式等
    2、执行程序
"""

import os
import re
import copy
import configparser
import chardet


class ConfFile:
    def __init__(self, conf_path=os.getcwd() + "\\nei.ini"):
        # 存储日志数量，所有日志的绝对路径
        self.fil_log = list()
        self.conf = configparser.ConfigParser()
        self.time_fmt = list()
        self.b2_fmt = list()
        try:
            try:
                self.conf.read(conf_path, encoding="utf8")
            except UnicodeDecodeError:
                exit("Error：配置文件编码错误")
            self.fil_log.append(self.conf.getint("日志", "fil_num"))
            if self.fil_log[0] % 2 != 0:
                exit("Error：日志数量不为偶数")
            for log_num in range(self.fil_log[0]):
                filn = self.conf.get("日志", "fil" + str(log_num + 1))
                self.fil_log.append(filn)
            self.prov = self.conf.get("基本配置", "prov")
            print("启用配置："+self.prov)
            # 默认统计10s邻道率
            try:
                self.sec_diff = int(self.conf.get("基本配置", "sec_diff"))
            except ValueError:
                self.sec_diff = 10
            # 所有时间格式
            time_fmt_num = int(self.conf.get("时间格式", "time_fmt_num"))
            for time_fmti in range(1, time_fmt_num+1):
                find_time = self.conf.get("时间格式", "find_time_"+str(time_fmti))
                time_hh = int(self.conf.get("时间格式", "time_hh_"+str(time_fmti)))
                time_minh = int(self.conf.get("时间格式", "time_minh_"+str(time_fmti)))
                time_sh = int(self.conf.get("时间格式", "time_sh_"+str(time_fmti)))
                self.time_fmt.append([find_time, time_hh, time_minh, time_sh])
            # 所有B2格式
            b2_fmt_num = int(self.conf.get(self.prov, "b2_fmt_num"))
            for b2_fmti in range(1, b2_fmt_num+1):
                len_obu = int(self.conf.get(self.prov, "len_obu_"+str(b2_fmti)))
                find_b2 = self.conf.get(self.prov, "find_b2_"+str(b2_fmti))
                self.b2_fmt.append([len_obu, find_b2])
        except configparser.NoOptionError:
            exit("Error：配置文件读取失败")


class LogData:
    def __init__(self, path, time_fmt, b2_fmt):
        # 日志路径
        self.log_path = path
        self.fil_fmt_detect(time_fmt, b2_fmt)
        self.rgl_exp_time = time_fmt[0][0]
        self.time_hh = int(time_fmt[0][1])
        self.time_minh = int(time_fmt[0][2])
        self.time_sh = int(time_fmt[0][3])
        self.rgl_exp_b2 = b2_fmt[0][1]
        self.b2_all = list()
        self.b2_rmv = list()
        self.coding = fil_coding_detect(self.log_path)

        # 从日志提取所有B2帧obuid及time，obuid长度默认为8，也有的日志是11（含有空格）
        with open(self.log_path, "r", encoding=self.coding, errors="ignore") as fil:
            fo = fil.read()
            lst_tem = re.findall(self.rgl_exp_b2, fo, re.M)
            fo1 = "\n".join(lst_tem)
            # time截取范围
            exp_time_start = re.search(self.rgl_exp_time, fo1).start()
            exp_time_end = re.search(self.rgl_exp_time, fo1).end()

            # 从包含B2和时间的正则表达式搜索结果中提取obuid及time，len_obu为obuid长度，默认为8，也有的日志是11
            # 截取obuid及时间，计算秒数，用列表保存
            len_b2 = len(lst_tem[0])
            for i in range(len(lst_tem)):
                b2_obuid = lst_tem[i][len_b2-b2_fmt[0][0]:]
                b2_time = lst_tem[i][exp_time_start:exp_time_end]
                lst_time_sec = 10 * int(b2_time[self.time_hh]) + int(b2_time[self.time_hh + 1])
                lst_time_sec = (60 * lst_time_sec + 10 * int(b2_time[self.time_minh]) + int(b2_time[self.time_minh + 1]))
                lst_time_sec = (60 * lst_time_sec + 10 * int(b2_time[self.time_sh]) + int(b2_time[self.time_sh + 1]))
                rec_tem = [b2_time, b2_obuid, lst_time_sec]
                self.b2_all.append(rec_tem)
            duplicate_obuid_remove(self.b2_all, self.b2_rmv)
            fil.close()

    # 检测日志格式（待开发）
    def fil_fmt_detect(self, time_fmt, b2_fmt):
        pass
        # print(time_fmt, b2_fmt)
        # print(self.log_path)


# 对从日志中提取出的B2帧obuid及time进行去重
# 去重逻辑：比较一个 obuid 与它后面的2000个（或者一直到列表最后），如果时间30分钟内且 obuid 相同，则去重
# obu_all：B2帧 obuid 及时间，元素内容依次为时间、obuid、秒数
# obu_rmv：去重结果，元素内容依次为时间、obuid、秒数
def duplicate_obuid_remove(obu_all, obu_rmv):
    rec_copy = copy.deepcopy(obu_all)
    i = 0
    while i != len(rec_copy):
        if rec_copy[i][1] != "":
            obu_rmv.append(rec_copy[i])
            j = i + 1
            while j != min(i + 2000, len(rec_copy)):
                if (
                    rec_copy[i][1] == rec_copy[j][1]
                    and abs(rec_copy[i][2] - rec_copy[j][2]) < 1800
                ):
                    rec_copy[j][1] = ""
                j = j + 1
        i = i + 1


# 统计邻道干扰率：先对所有b2进行邻道统计，再去重
# 输出邻道统计结果，默认阈值为10秒
def calculate_nei_interference_rate(log_self, log_nei, sec_diff):
    # 邻道干扰数
    inf_num = int()
    # 邻道干扰obuid
    inf_obu_tem = []
    inf_obu = []
    # 邻道干扰统计
    for i in range(len(log_self.b2_all)):
        for j in range(len(log_nei.b2_all)):
            if abs(log_self.b2_all[i][2] - log_nei.b2_all[j][2]) < sec_diff and log_self.b2_all[i][1] == log_nei.b2_all[j][1]:
                inf_tem = [log_self.b2_all[i][0], log_self.b2_all[i][1], log_self.b2_all[i][2], log_nei.b2_all[j][0],]
                inf_obu_tem.append(inf_tem)
    # 邻道统计结果去重（注意参数列表的元素顺序）
    # inf_obu元素顺序为本道时间、obuid、本道秒数、邻道时间
    duplicate_obuid_remove(inf_obu_tem, inf_obu)
    if len(inf_obu) != 0:
        inf_num = len(inf_obu)
    # 计算邻道干扰率
    inf_gate_self = 100 * inf_num / len(log_self.b2_rmv)
    inf_gate_nei = 100 * inf_num / len(log_nei.b2_rmv)
    # 输出结果
    print("邻道干扰obuid：")
    print("本道时间---OBUID---本道秒数---邻道时间")
    for obuid_tem in inf_obu:
        print(obuid_tem)
    print("%d秒邻道数：%d" % (sec_diff, inf_num))
    print("本道obu数：%d，去重后：%d，邻道率为：%.2f%%" % (len(log_self.b2_all), len(log_self.b2_rmv), inf_gate_self))
    print("邻道obu数：%d，去重后：%d，邻道率为：%.2f%%\n\n" % (len(log_nei.b2_all), len(log_nei.b2_rmv), inf_gate_nei))


# 检测源文件编码并返回
def fil_coding_detect(src_file):
    char_detect = str()
    with open(src_file, "rb") as fi:
        for row in fi:
            tmp = chardet.detect(row)
            code = tmp.get("encoding")
            if code == "utf-8":
                char_detect = "utf-8"
            else:
                char_detect = "gb18030"
            break
        fi.close()
    return char_detect


if __name__ == "__main__":
    conf = ConfFile()
    for log_SN in range(int(conf.fil_log[0] / 2)):
        log1 = LogData(conf.fil_log[2 * log_SN + 1], conf.time_fmt, conf.b2_fmt)
        log2 = LogData(conf.fil_log[2 * log_SN + 2], conf.time_fmt, conf.b2_fmt)
        print("第%d组统计：" % (log_SN + 1))
        # 邻道干扰统计
        calculate_nei_interference_rate(log1, log2, sec_diff=conf.sec_diff)
    # os.system('pause')

