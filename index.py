"""SCF 函数的入口
"""
import base64
import io
import json
import logging
import random
import time

import requests

from conf.settings import WORKPIECES
from screenshot import generate_screenshot, upload_yqt_screenshot
from submit_to_yqt import submit_to_yqt


logger = logging.getLogger('upload_yqt_screenshot')

UPLOAD_URL = 'http://yqt.zhengsj.top/photo/'


def main_handler(event, _):

    # 定时触发
    if event.get('Type') == 'Timer':
        for item in WORKPIECES:

            # 提交疫情通
            if event.get('TriggerName') == 'submit' and 'submit' in item[4]:
                submit_to_yqt(item[2], item[3])

            # 上传图片
            elif event.get('TriggerName') == 'upload' and 'upload' in item[4]:
                try:
                    upload_yqt_screenshot(name=item[0], stu_id=item[2], dorm=item[1])
                except RuntimeError as e:
                    logger.warning(f'截图上传失败，已忽略，请手动上传，错误信息：{e}')

        return None

    # API 网关触发，生成图片或发送定位页
    elif 'queryString' in event:

        if 'gps' in event['queryString']:
            with open('get_geo_api_info.html', 'rt', encoding='utf-8') as fp:
                gps_page = fp.read()
            return {
                'body': gps_page,
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'isBase64Encoded': False
            }

        name = event['queryString'].get('name')
        stu_id = event['queryString'].get('stu_id')
        if not name or not stu_id:
            return {
                'body': '"请求参数 `name` 和 `stu_id` 必须提供"',
                'statusCode': 400,
                'headers': {},
                'isBase64Encoded': False
            }

        date = event['queryString'].get('date')
        shot_time = event['queryString'].get('time')
        battery = event['queryString'].get('battery')

        name = name[:6]
        stu_id = stu_id[:11]
        date = date[:10] if date else None
        shot_time = shot_time[:5] if shot_time else None
        try:
            battery = int(battery) if 10 <= int(battery) <= 99 else None
        except (TypeError, ValueError):
            battery = None

        img = generate_screenshot(name, stu_id, date, shot_time, battery)
        fp = io.BytesIO()
        img.save(fp, format='PNG')
        img.show()

        return {
            'body': base64.standard_b64encode(fp.getvalue()).decode(),
            'statusCode': 200,
            'headers': {'Content-Type': 'image/png'},
            'isBase64Encoded': True
        }

    else:
        raise RuntimeError('不能理解的触发方式')
