# 将捕获的数据进行格式化处理
# 触摸数据处理为json
#
import re
import json
import copy
import math

import cv2

# 正则表达式解析模式
pattern = r'\[\s*(\d+\.\d+)\] (/dev/input/\w+): (\w+)\s+(\w+)\s+(\w+)'
pattern1 = r'\[\s*(\d+\.\d+)\]'  # 匹配时间戳的格式

# 计算两点间距离
def calculate_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


# 解析数据的函数
def parse_event_data(file_path,time_json="data/time2.json"):
    events = []
    id=1

    # 获取记录的起始时间
    try:
        with open(time_json, 'r', encoding='utf-8') as file:
            time_data = json.load(file)
    except FileNotFoundError:
        print("文件未找到！")
    except json.JSONDecodeError:
        print("JSON 格式错误！")
    first_timestamp=float(time_data['start_time'])
    # hang=1
    with open(file_path, 'r') as file:
        for line in file:
            # print(hang)
            # hang =hang+1
            # if hang==931:
            #     print(1)
            match = re.search(pattern, line)
            if not match:
                continue
            timestamp, event_type, event_code, key, value = match.groups()
            if key == "BTN_TOOL_FINGER" and value == "DOWN":
                track = [[]]
                solt_flag = []
                flag = "00000000"
                solt_flag.append(flag)
                data = {}
                data[flag] = []
                data_bef = copy.deepcopy(data)
                data_bef[flag].append(0)
                data_bef[flag].append(0)
                data_bef[flag].append(0)
                continue
            if key == "ABS_MT_POSITION_X":
                if not data:
                    data[flag] = []
                data_bef[flag][0] = float(timestamp)-first_timestamp
                data_bef[flag][1] = int(value, 16)
                data[flag].append(float(timestamp)-first_timestamp)
                data[flag].append(int(value, 16))
                continue
            if key == "ABS_MT_POSITION_Y":
                if not data:
                    data[flag] = []
                data_bef[flag][0] = float(timestamp)-first_timestamp
                data_bef[flag][2] = int(value, 16)
                data[flag].append(int(value, 16))
                continue
            if key == "SYN_REPORT":
                # 判断需要有预存数据
                if flag not in data:
                    continue
                if not data[flag]:
                    continue
                for key, value in data.items():
                    index = solt_flag.index(key)
                    if value == data_bef[key]:
                        track[index].append(value)
                    else:
                        track[index].append(copy.deepcopy(data_bef[key]))
                data = {}
                continue
            if key == "ABS_MT_SLOT":
                flag = value
                # 向track里面添加track
                if flag not in solt_flag:
                    solt_flag.append(flag)
                    track.append([])
                if flag not in data_bef:
                    data_bef[flag] = []
                    data_bef[flag].append(0)
                    data_bef[flag].append(0)
                    data_bef[flag].append(0)
                data[flag] = []

            if key == "BTN_TOOL_FINGER" and value == "UP":
                # print(track)
                event = {"id": id}
                start_pos = []
                end_pos = []
                start_time = []
                end_time = []
                for i in range(len(track)):
                    start_pos.append(track[i][0][1:3])
                    end_pos.append(track[i][-1][1:3])
                    start_time.append(track[i][0][0])
                    end_time.append(track[i][-1][0])
                    event["track_" + str(i)] = track[i]
                event["start_pos"] = start_pos
                event["end_pos"] = end_pos
                event["start_time"] = start_time
                event["end_time"] = end_time
                # 识别交互
                # 多指
                if len(track) > 1:
                    start_distance = calculate_distance(start_pos[0], start_pos[1])
                    end_distance = calculate_distance(end_pos[0], end_pos[1])
                    # 放大
                    if end_distance > start_distance:
                        event["operate"] = "Zoom In"
                    # 缩小
                    elif end_distance < start_distance:
                        event["operate"] = "Zoom Out"
                    else:
                        event["operate"] = "Unknown"
                # 单指
                else:
                    if start_pos[0] == end_pos[0]:
                        event["operate"] = "Click"
                    else:
                        x_diff = end_pos[0][0] - start_pos[0][0]
                        y_diff = end_pos[0][1] - start_pos[0][1]
                        if abs(x_diff) > abs(y_diff):  # 水平方向滑动
                            event["operate"] = "Swipe Right" if x_diff > 0 else "Swipe Left"
                        else:  # 垂直方向滑动
                            event["operate"] = "Swipe Down" if y_diff > 0 else "Swipe Up"
                events.append(event)
                id += 1
    print(events)
    return events


# data数组转json
def data_to_json(data,output_path):
    with open(output_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print("Data has been written to output.json")


# txt转json
def txt_to_json(input_file, output_file):
    # 存储转换后的数据
    events = []

    with open(input_file, 'r') as file:
        # 逐行读取文件
        for line in file:
            # 去掉每行的空白字符并处理格式（这里假设是单引号，可以调整为双引号）
            line = line.strip().replace("'", "\"")

            # 解析为字典
            try:
                event = json.loads(line)
                events.append(event)
            except json.JSONDecodeError:
                print(f"无法解析这行数据: {line}")
                continue

    # 将字典写入输出的JSON文件
    with open(output_file, 'w') as json_file:
        json.dump(events, json_file, indent=4)

def extract_frame_indices(video_path):
    """
    根据时间戳解析视频帧索引。
    :param video_path: 视频文件路径。
    :return: 帧时间戳和对应的帧索引列表。
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("无法打开视频文件")
        return []

    frame_indices = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 获取当前帧的时间戳（毫秒）
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # 转为秒
        frame_indices.append((frame_count, timestamp))
        frame_count += 1

    cap.release()
    print(f"解析完成，共 {frame_count} 帧")
    return frame_indices


if __name__ == "__main__":
    # 文件路径，请根据你的实际文件路径进行修改
    file_path = 'data/AAtest.txt'
    output_file="data/AAtest_output.json"
    video_path="data/AAtest.mp4"
    frame_indices_json="data/AAtest_frame_indices.json"
    time_json="data/AAtest_time.json"
    # 解析事件数据并打印结果
    events = parse_event_data(file_path,time_json)
    data_to_json(events,output_file)
    for event in events:
        print(event)
    frame_indices=extract_frame_indices(video_path)
    data_to_json(frame_indices,frame_indices_json)

