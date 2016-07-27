#!/usr/bin/ python
# coding:utf-8

# python lib
import urllib
import urllib2
import langid
import json
import os


def check_language(TransStr):
    '''
    :Info: 检测输入文字的语言
    :param TransStr: 文字
    :return: 返回输入文字的语言
    :rtype: str
    '''
    LangId = langid.classify(TransStr.decode("utf-8", "ignore"))
    return LangId


def to_language(LangId):
    '''
    :Info: 获取语言的对应关系
    :param LangId: 输入文字的语言
    :return: 语言的对应关系（中 to 英文,英文 to 中）
    :rtype: dict
    '''
    if "zh" == LangId[0]:
        ToLangid = {"zh": "en"}
    elif "en" == LangId[0]:
        ToLangid = {"en": "zh"}
    else:
        ToLangid = ""

    return ToLangid


def tanslate(TransStr, ToLangid):
    '''
    :Info: 向百度请求数据，获得文字的释义
    :param TransStr: 输入的文字
    :param ToLangid: 语言的对应关系
    :return: 释义
    '''
    # 百度查询网址
    BAIDU_DICT = "http://fanyi.baidu.com/v2transapi"
    # 定义释义
    means_detail_fromlang = TransStr
    means_detail_tolang = ""
    for ori_langid, to_langid in ToLangid.items():
        # Post百度翻译接口
        POST_DATA = urllib.urlencode({"from": ori_langid, "to": to_langid, "query": TransStr, "transtype": "translang", "simple_means_flag": "3"})
        req = urllib2.Request(BAIDU_DICT, POST_DATA)
        response = urllib2.urlopen(req)
        # 获取返回的json数据
        the_json_str = response.read()
        # 解析json数据
        the_json_dict = json.loads(the_json_str)
        if "en" == to_langid:
            # zh to en : 采集汉英大词典
            word_mean = the_json_dict["dict_result"]["synthesize_means"]["symbols"][0]["cys"][0]["means"][0]["word_mean"]
            means_detail_tolang = "[zh]" + os.linesep + TransStr.decode("utf-8") + os.linesep + "[en]" + os.linesep + word_mean + os.linesep + "[Example]" + os.linesep
            for means in the_json_dict["dict_result"]["synthesize_means"]["symbols"][0]["cys"][0]["means"][0]["ljs"]:
                means_detail_tolang = means_detail_tolang + means["ls"] + means["ly"] + os.linesep
        elif "zh" == to_langid:
            # en to zh
            # 发音
            word_read_am = "美式发音".decode("utf-8") + "[%s]" % the_json_dict["dict_result"]["simple_means"]["symbols"][0]["ph_am"]
            word_read_en = "英式发音".decode("utf-8") + "[%s]" % the_json_dict["dict_result"]["simple_means"]["symbols"][0]["ph_en"]
            word_read = word_read_am + os.linesep + word_read_en
            means_detail_tolang = "[en]" + os.linesep + TransStr.decode("utf-8") + os.linesep + "[zh]" + os.linesep + word_read + os.linesep
            # 释义
            word_mean = ""
            for means in the_json_dict["dict_result"]["simple_means"]["symbols"][0]["parts"]:
                for mean in means["means"]:
                    word_mean = word_mean + mean + ";"
                means_detail_tolang = means_detail_tolang + means["part"] + word_mean + os.linesep

    return means_detail_tolang


def main(TransStr):
    # 检测输入文字的语言
    LangId = check_language(TransStr)
    # 获取语言的对应关系
    ToLangid = to_language(LangId)
    if not ToLangid:
        print "Sorry, please input English or Chiness word !"
        return
    # 向百度请求数据，获得文字的释义
    means_detail_tolang = tanslate(TransStr, ToLangid)
    
    print means_detail_tolang


if __name__ == '__main__':
    # TransStr = "beauty"
    TransStr = "美女"
    main(TransStr)
