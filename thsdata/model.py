import json
from .util import convert_data_keys


class Reply:
    def __init__(self, json_str: str):
        # 将输入的JSON字符串转换为Python字典
        data_dict = json.loads(json_str)

        # 提取各个字段
        self.data = data_dict.get('data', [])
        self.dicExt = data_dict.get('dicExt', {})
        self.ext = data_dict.get('ext', None)
        self.head = data_dict.get('head', {})

    def __repr__(self):
        return f"Reply(data={self.data}, dicExt={self.dicExt}, ext={self.ext}, head={self.head})"

    def convert_data(self):
        if self.data is None:
            self.data = []

        self.data = convert_data_keys(self.data)
