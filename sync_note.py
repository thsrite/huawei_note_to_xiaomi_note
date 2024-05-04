# coding=utf8
import urllib.parse

import requests, json

# 华为笔记列表
hw_list_url = "https://cloud.huawei.com/notepad/simplenote/query"
# 华为云服务笔记请求ck
header = {
    'Cookie': 'your huawei cloud ck',
    'Content-Type': 'application/json'
}

# 小米云服务笔记创建接口
xm_note_create_url = "https://i.mi.com/note/note"
# 小米云服务笔记请求ck
xm_header = {
    'Cookie': 'your xiaomi cloud ck',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}
# 小米云服务笔记创建server_token（手动去小米云服务web端新建笔记看请求参数获取）
xm_server_token = urllib.parse.quote("your_server_token")


# 解析所有note目录json数据
def get_hw_notes():
    """
    获取所有华为笔记
    """
    payload = json.dumps({
        "guids": "",
        "traceId": "03131_02_1714742562_16435773"
    })
    response = requests.request("POST", hw_list_url, headers=header, data=payload)
    result = json.loads(response.text)
    result_json = result.get('rspInfo').get('noteList')
    return result_json


def create_xm_note(hw_created, hw_modified):
    """
    创建小米笔记
    获取noteid notetag
    """
    data = f"entry=%7B%22content%22%3A%22%22%2C%22colorId%22%3A0%2C%22folderId%22%3A%220%22%2C%22createDate%22%3A{hw_created}%2C%22modifyDate%22%3A{hw_modified}%7D&serviceToken={xm_server_token}"
    response = requests.request("POST", xm_note_create_url, headers=xm_header, data=data)
    result = json.loads(response.text)
    note_id = result.get('data').get('entry').get('id')
    note_tag = result.get('data').get('entry').get('tag')
    return note_id, note_tag


def post_xm_note(hw_created, hw_modified, note_id, note_tag, title, text):
    """
    发送小米笔记 title、text
    """
    data = f"entry=%7B%22id%22%3A%22{note_id}%22%2C%22tag%22%3A%22{note_tag}%22%2C%22status%22%3A%22normal%22%2C%22createDate%22%3A{hw_created}%2C%22modifyDate%22%3A{hw_modified}%2C%22colorId%22%3A0%2C%22content%22%3A%22%3Ctext%20indent%3D%5C%221%5C%22%3E{text}%3C%2Ftext%3E%22%2C%22folderId%22%3A%220%22%2C%22alertDate%22%3A0%2C%22extraInfo%22%3A%22%7B%5C%22title%5C%22%3A%5C%22{title}%5C%22%7D%22%7D&serviceToken={xm_server_token}"
    url = f"https://i.mi.com/note/note/{note_id}"
    response = requests.request("POST", url, headers=xm_header, data=data)
    result = json.loads(response.text)
    if result.get('code') == 0:
        print(f"{title} 创建成功")
    else:
        print(f"{title} 创建失败")


if __name__ == '__main__':
    # 获取所有的华为笔记
    result_json = get_hw_notes()
    for j in result_json:
        # 获取华为笔记title
        hw_note = json.loads(j.get('data')).get('title')
        # 同步华为笔记的创建时间和修改时间
        hw_created = json.loads(j.get('data')).get('created')
        hw_modified = json.loads(j.get('data')).get('modified')
        try:
            # 分割title和text
            hw_note_title = hw_note.split('\n')[0]
            hw_note_text = hw_note.split('\n')[1]
        except Exception as e:
            hw_note_title = hw_note
            hw_note_text = ""

        # 创建小米笔记
        note_id, note_tag = create_xm_note(hw_created, hw_modified)
        # 发送笔记内容
        post_xm_note(hw_created, hw_modified, note_id, note_tag, urllib.parse.quote(hw_note_title),
                     urllib.parse.quote(hw_note_text))
