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
from generate_screenshot import generate_screenshot
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
                # 06:00:00 - 08:59:59 中的一个随机数
                shot_time = (random.randint(6, 8), random.randint(0, 59), random.randint(0, 59))

                # 生成截图
                screenshot_name = f'Screenshot_{time.strftime("%Y%m%d")}_{"%02d%02d%02d" % shot_time}_com.tencent.mm.png'
                screenshot = generate_screenshot(item[0], item[2], shot_time=('%02d:%02d' % shot_time[:2]))
                screenshot_fp = io.BytesIO()
                screenshot.save(screenshot_fp, format='png')
                screenshot.close()

                ret = requests.post(
                    UPLOAD_URL,
                    data={'name': item[0], 'dorm': item[1]},
                    files={'photo': (screenshot_name, screenshot_fp.getvalue(), 'image/png')}
                )

                try:
                    ret_data = json.loads(ret.text)
                    if not isinstance(ret_data, dict):
                        ret_data = {}
                except json.JSONDecodeError:
                    ret_data = {}

                if ret.status_code == 200 and ret_data.get('code') == 0:
                    logger.info(f'{item[0]} 上传成功')
                else:
                    logger.warning(f'{item[0]} 上传失败，请手动上传')

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
