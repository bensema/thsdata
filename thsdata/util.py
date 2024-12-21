from .constants import FieldNameMap
import random
from datetime import datetime


def ths_int2time(scr: int) -> datetime:
    # 提取分钟、小时、日期、月份和年份
    m = scr & 63  # 111111 (分钟)
    h = (scr & 1984) >> 6  # 11111 000000 (小时)
    dd = (scr & 63488) >> 11  # 11111 00000 000000 (日期)
    mm = (scr & 983040) >> 16  # 1111 00000 00000 000000 (月份)
    yyyy = (scr & 133169152) >> 20  # 1111111 0000 00000 00000 000000 (年份)

    # 将年份从2000年开始
    yyyy = 2000 + yyyy % 100

    # 构造时间字符串
    time_str = f"{yyyy}-{mm:02d}-{dd:02d} {h:02d}:{m:02d}:00"

    # 转换为datetime对象
    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")


def rand_instance(n: int) -> str:
    digits = "0123456789"
    d2 = "123456789"  # d2 used for the first digit to avoid 0 at the start

    if n <= 1:
        return str(random.randint(0, 9))  # Return a single random digit

    # Generate the string with n characters
    result = [random.choice(digits) for _ in range(n)]

    # Ensure the first digit is from d2 (i.e., 1-9)
    result[0] = random.choice(d2)

    return ''.join(result)


def convert_data_keys(data):
    # Loop through each entry in the data
    converted_data = []

    for entry in data:
        # Convert each entry by renaming keys
        converted_entry = {}
        for key, value in entry.items():
            # Check if the key exists in the FieldNameMap
            if int(key) in FieldNameMap:
                # Map the key to the corresponding name
                converted_entry[FieldNameMap[int(key)]] = value
            else:
                # If no mapping exists, keep the original key
                converted_entry[int(key)] = value
        converted_data.append(converted_entry)

    return converted_data
