import logging
import random
import time
from PIL import Image, ImageDraw, ImageFont


logger = logging.getLogger('generate_screenshot')


def generate_screenshot(name: str, stu_id: str, date: str = None, shot_time: str = None, battery: int = None) -> Image:
    """生成疫情通截图

    :param name: 姓名
    :param stu_id: 学号
    :param date: 日期（%Y-%m-%d），缺省值是今天
    :param shot_time: 截图时间（%H:%M），缺省值是现在
    :param battery: 电量，两位数， 10-99 ，缺省值随机
    """

    # 日期缺省值
    if date is None:
        date = time.strftime('%Y-%m-%d')

    # 时间缺省值
    if shot_time is None:
        shot_time = time.strftime('%H:%M')

    # 电量缺省值是 10-99 的随机整数
    if battery is None:
        battery = random.randint(10, 99)

    logger.info(f'正在生成疫情通截图：{name}， {stu_id} ， {date} ，电量 {battery} ，时间 {shot_time}')

    # 打开模板图片
    template_img = Image.open('./assets/template.png')
    dw = ImageDraw.Draw(template_img)

    # 添加日期、姓名、学号
    form_font = ImageFont.truetype('./assets/msyh.ttc', 56)
    dw.text((112, 1159), date, fill=(20, 20, 20), font=form_font)
    dw.text((112, 1564), name, fill=(20, 20, 20), font=form_font)
    dw.text((112, 1979), stu_id, fill=(20, 20, 20), font=form_font)

    # 添加电池电量、时间
    dw.text((1187, 29), str(battery), fill=(102, 102, 102), font=ImageFont.truetype('./assets/msyh.ttc', 31))
    dw.text((1259, 23), shot_time, fill=(102, 102, 102), font=ImageFont.truetype('./assets/msyh.ttc', 42))

    # 添加提交成功弹窗
    alert_img = Image.open('./assets/alert.png')
    template_img.paste(alert_img, (260, 1369))
    alert_img.close()

    logger.info('截图生成完成.')

    return template_img
