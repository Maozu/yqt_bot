# 工件，定时任务需要处理的人
WORKPIECES = [
    {
        'name': '姓名',    # 仅 actions 含 'upload_screenshot' 时必填
        'stu_id': '学号',  # 必填
        'dorm': '宿舍号',  # 仅 actions 含 'upload_screenshot' 时必填
        'passwd': '密码',  # 仅 actions 含 'submit_to_yqt' 时必填

        # 'submit_to_yqt' 表示填报疫情通， 'upload_screenshot' 表示上传截图（仅 1613012 班需要）
        'actions': ('submit_to_yqt', 'upload_screenshot')
    },
    # 多人可继续追加，格式同上
]


YQT_SCREENSHOT_UPLOAD_URL = 'http://yqt.zhengsj.top/photo/'

from .secrets import WORKPIECES
