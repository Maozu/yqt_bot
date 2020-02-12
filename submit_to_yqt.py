import json
import logging
import re
import time
import requests


logger = logging.getLogger('submit_to_yqt')

URLS = {
    'base_url': 'https://xxcapp.xidian.edu.cn',
    'login_url': '/uc/wap/login/check',
    'yqt_url': '/ncov/wap/default/index',
    'submit_url': '/ncov/wap/default/save'
}


def login(session: requests.Session, username: str, password: str):
    """登录疫情通

    :param session: 请求会话
    :param username: 用户名（学号）
    :param password: 密码
    """
    ret = session.post(f'{URLS["base_url"]}{URLS["login_url"]}', data={'username': username, 'password': password})

    if ret.status_code != 200:
        err_msg = f'登录疫情通时服务端返回异常：[{ret.status_code}] {ret.text}'
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    try:
        ret_data = json.loads(ret.text)
    except json.JSONDecodeError:
        err_msg = f'登录疫情通时服务端返回结构异常：{ret.text}'
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    if ret_data.get('e') != 0:
        err_msg = f'登录疫情通时服务端返回异常：[200] {ret_data.get("e")} - {ret_data.get("m")} - {ret_data.get("d")}'
        logger.error(err_msg)
        raise RuntimeError(err_msg)


def generate_data(session: requests.Session, username: str):
    ret = session.get(f'{URLS["base_url"]}{URLS["yqt_url"]}')

    if ret.status_code != 200:
        err_msg = f'访问疫情通页面错误，状态码 {ret.status_code}'
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    init_data = re.search(r'var def = (.+?)"uid":"([^"]+?)"(.+?)"id":([^"]+?),(.+?);\s*?var vm = new Vue', ret.text)
    if not init_data:
        err_msg = '疫情通页面结构不符合预期'
        logger.error(err_msg)
        raise RuntimeError(err_msg)
    uid = init_data.group(2)
    its_id = init_data.group(4)

    with open(f'conf/geo_api_info/{username}.json', 'rt', encoding='utf-8') as fp:
        geo_api_info_json = fp.read()

    geo_api_info_obj = json.loads(geo_api_info_json)

    data = {
        'uid': uid,
        'date': time.strftime('%Y%m%d'),
        'tw': '1',
        'sfcxtz': '0',
        'sfyyjc': '0',
        'jcjgqr': '0',
        'jcjg': '',
        'sfjcbh': '0',
        'sfcxzysx': '0',
        'qksm': '',
        'remark': '',
        'address': geo_api_info_obj["formattedAddress"],
        'area': (
            f'{geo_api_info_obj["addressComponent"]["province"]} '
            f'{geo_api_info_obj["addressComponent"]["city"]} '
            f'{geo_api_info_obj["addressComponent"]["district"]}'
        ),
        'province': geo_api_info_obj['addressComponent']['province'],
        'city': geo_api_info_obj['addressComponent']['city'],
        'geo_api_info': geo_api_info_json,
        'created': str(int(time.time())),
        'sfzx': '0',
        'sfjcwhry': '0',
        'sfcyglq': '0',
        'gllx': '',
        'glksrq': '',
        'jcbhlx': '',
        'jcbhrq': '',
        'sftjwh': '0',
        'sftjhb': '0',
        'fxyy': '',
        'bztcyy': '',
        'fjsj': '0',
        'created_uid': '0',
        'sfjchbry': '0',
        'sfjcqz': '',
        'jcqzrq': '',
        'jcwhryfs': '',
        'jchbryfs': '',
        'xjzd': '',
        'szgj': '',
        'sfsfbh': '0',
        'id': its_id,
        'gwszdd': '',
        'sfyqjzgc': '',
        'jrsfqzys': '',
        'jrsfqzfy': '',
        'ismoved': '0',
    }

    return data


def submit(session: requests.Session, data: dict):
    ret = session.post(f'{URLS["base_url"]}{URLS["submit_url"]}', data=data)

    if ret.status_code != 200:
        err_msg = f'提交疫情通时服务端返回异常：[{ret.status_code}] {ret.text}'
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    try:
        ret_data = json.loads(ret.text)
    except json.JSONDecodeError:
        err_msg = f'提交疫情通时服务端返回结构异常：{ret.text}'
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    if ret_data.get('e') != 0:
        err_msg = f'提交疫情通时服务端返回异常：[200] {ret_data.get("e")} - {ret_data.get("m")} - {ret_data.get("d")}'
        logger.error(err_msg)
        raise RuntimeError(err_msg)


def submit_to_yqt(username: str, password: str):
    """提交疫情通

    :param username: 用户名（学号）
    :param password: 密码
    :return:
    """

    # 创建会话
    s = requests.Session()

    # 登录
    login(s, username, password)

    # 生成提交表单
    data = generate_data(s, username)

    # 提交
    submit(s, data)

    s.close()
    logger.info(f'{username} 疫情通已提交')
