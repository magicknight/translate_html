import json
from .tools import merge_conflict, TokenAcquirer


def youdao(self, src_data, proxies, src_template):
    """
    有道翻译的实现(废弃)
    :param src_data: 原生数据
    :param proxies: 代理
    :param src_template: 原生数据模板
    :return: 结果
    """
    url = "http://fanyi.youdao.com/translate"
    resp = self.session.post(url=url, data={
        'keyfrom': 'fanyi.web',
        'i': src_data,
        'doctype': 'json',
        'action': 'FY_BY_CLICKBUTTON',
        'ue': 'UTF-8',
        'xmlVersion': '1.8',
        'type': 'AUTO',
        'typoResult': 'true'}, headers=self.headers,
                         timeout=self.translate_timeout, proxies=proxies)
    return src_template % tuple(map(lambda y: "".join(
        map(lambda x: x["tgt"], y)), json.loads(resp.text)["translateResult"]))


def baidu(self, src_data, proxies, src_template):
    """
    百度翻译的实现, 百度翻译最长只能翻译5000个字符
    :param src_data: 原生数据
    :param proxies: 代理
    :param src_template: 原生数据模板
    :return: 结果
    """
    url = "http://fanyi.baidu.com/v2transapi"
    resp = self.session.post(url=url, data={
        'from': 'en',
        'to': 'zh',
        'transtype': 'realtime',
        'query': src_data,
        'simple_means_flag': 3}, headers=self.headers,
                         timeout=self.translate_timeout, proxies=proxies)
    return src_template % tuple(
        "".join(map(lambda x: x["src_str"], json.loads(resp.text)["trans_result"]['phonetic'])).split("\n"))


def qq(self, src_data, proxies, src_template):
    """
    腾讯翻译的实现, 腾讯翻译最长只能翻译2000个字符
    :param src_data: 原生数据
    :param proxies: 代理
    :param src_template: 原生数据模板
    :return: 结果
    """
    url = 'http://fanyi.qq.com/api/translate'
    resp = self.session.post(
        url, data={'source': 'auto', 'target': 'en', 'sourceText': src_data},
        headers=self.headers, timeout=self.translate_timeout, proxies=proxies)
    return merge_conflict(
        src_template,
        [record["targetText"] for record in json.loads(resp.text)["translate"]["records"] if record.get("sourceText") != "\n"])


def google(self, src_data, proxies, src_template):
    url = 'https://translate.google.cn/translate_a/single'
    data = {
        'client': 't',
        'sl': "auto",
        'tl': "zh",
        'hl': "zh",
        'dt': ['at', 'bd', 'ex', 'ld', 'md', 'qca', 'rw', 'rm', 'ss', 't'],
        'ie': 'UTF-8',
        'oe': 'UTF-8',
        'otf': 1,
        'ssel': 0,
        'tsel': 0,
        'tk': TokenAcquirer(session=self.session).do(src_data),
        'q': src_data,
    }
    resp = self.session.get(url, params=data, headers=self.headers,
                            timeout=self.translate_timeout, proxies=proxies)
    return merge_conflict(src_template, [line[0] for line in json.loads(resp.text)[0] if line[0]])