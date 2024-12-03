import os

import cv2
import numpy as np
import matplotlib.pyplot as plt
import json

# 获取平均灰度并画图
def process_video(video_path, output_path):
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    frame_index = 0
    avg_gray_values = []
    #写入输出视频
    # 获取视频帧宽度、高度、帧率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 设置视频输出编解码器和文件路径
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))


    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 转换为灰度图像
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 计算平均灰度值并添加到数组
        avg_gray = np.mean(gray_frame)
        avg_gray_values.append(avg_gray)

        #写入视频中
        avg_gray_d=int(avg_gray)
        text = f"Avg Gray: {avg_gray_d}"
        cv2.putText(frame, text, (width - 200, height - 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 0), 2)

        # 写入帧到输出视频
        out.write(frame)

        frame_index += 1

    # 释放视频资源
    cap.release()
    out.release()
    print("处理完成，输出视频已保存至", output_path)

    # 可视化平均灰度值
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(avg_gray_values)), avg_gray_values, label="Average Gray Value", color="gray")
    plt.xlabel("Frame Number")
    plt.ylabel("Average Gray Value")
    plt.title("Average Gray Value per Frame")
    plt.legend()
    plt.show()

def get_gray(video_path):
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    frame_index = 0
    avg_gray_values = []
    #写入输出视频
    # 获取视频帧宽度、高度、帧率
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 转换为灰度图像
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 计算平均灰度值并添加到数组
        avg_gray = np.mean(gray_frame)
        avg_gray_values.append(avg_gray)
        frame_index += 1

    # 释放视频资源
    cap.release()
    return avg_gray_values



#根据时间寻找交互前后的稳定帧索引
def get_frame_by_index(cap, frame_index):
    # 打开视频文件
    # cap = cv2.VideoCapture(video_path)

    # 设置帧的位置
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

    # 读取帧
    success, frame = cap.read()

    if success:
        return frame
    else:
        print("无法读取指定帧")
        return None

def get_frame_by_timestamp(cap, timestamp_sec):
    # # 打开视频文件
    # cap = cv2.VideoCapture(video_path)

    # 获取视频的帧率 (frames per second)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 计算对应的帧索引
    frame_index = int(fps * timestamp_sec)

    # 使用帧索引读取指定帧
    return get_frame_by_index(cap, frame_index)


def save_frame_as_image(frame, output_path):
    # 将帧保存为图片
    success = cv2.imwrite(output_path, frame)
    if success:
        print(f"图片成功保存到 {output_path}")
    else:
        print("图片保存失败")
#TODO:判断交互后到下一次交互前之间是否存在界面变化
def get_end_frame_index(avg_gray_values,end_time_index,next_end_time_index):
    # 判断下一界面
    check=3
    for i in range(end_time_index,next_end_time_index):
        sum=0
        for j in range(check):
            sum+=avg_gray_values[i+j]
        if avg_gray_values[i]==sum/check:
            return i
    return next_end_time_index

def create_floder(path):
    # 指定要创建的文件夹路径
    folder_path = path

    # 创建文件夹
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"文件夹 '{folder_path}' 创建成功！")
    else:
        print(f"文件夹 '{folder_path}' 已存在。")

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


def find_closest_frame(frame_data, target_time):
    """
    根据输入的时间，找到时间戳最接近的帧索引。

    :param frame_data: 帧时间戳和索引的列表，格式为 [(frame_index, timestamp), ...]
    :param target_time: 目标时间（秒），用于查找最接近的时间戳。
    :return: 最接近的帧索引。
    """
    closest_frame = None
    closest_time_diff = float('inf')

    # 遍历帧数据，计算每一帧与目标时间的时间差
    for frame_index, timestamp in frame_data:
        time_diff = abs(timestamp - target_time)

        # 如果当前帧的时间差更小，更新最接近的帧
        if time_diff < closest_time_diff:
            closest_time_diff = time_diff
            closest_frame = frame_index

    return closest_frame

def get_start_picture_index(frame_index,avg_gray_values,start_index):
    fixed_length_array = [0] * 10

    #偏移量
    for i in range(frame_index-start_index-10):
        max=0
        min=1000
        for j in range(10):
            fixed_length_array[j]=int(avg_gray_values[frame_index-i-j])
            if max<fixed_length_array[j]:
                max=fixed_length_array[j]
            if min>fixed_length_array[j]:
                min=fixed_length_array[j]
        # average = sum(fixed_length_array) / len(fixed_length_array)
        # if average==min and average==max:
        if max-min<=2:
            return frame_index-i-5
    return start_index
def get_end_picture_index(end_index,avg_gray_values,next_start_index):
    fixed_length_array = [0] * 10

    #偏移量
    for i in range(next_start_index-end_index-10):
        max=0
        min=1000
        for j in range(10):
            fixed_length_array[j]=int(avg_gray_values[next_start_index-i-j])
            if max<fixed_length_array[j]:
                max=fixed_length_array[j]
            if min>fixed_length_array[j]:
                min=fixed_length_array[j]
        average = sum(fixed_length_array) / len(fixed_length_array)
        # if average==min and average==max:
        # return next_start_index - i - 5
        if max-min<=2:
            return next_start_index-i-5
    return end_index



def get_picture(video_path,json_path,avg_gray_values,out_path,frame_indices_path):
    # 创建保存文件夹
    create_floder(out_path)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    # 获取视频的帧率 (frames per second)
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # # 计算视频时长（秒）
    # duration = frame_count / fps

    # 打开并读取 JSON 文件
    with open(json_path, 'r') as file:
        datas = json.load(file)  # 使用 json.load() 读取 JSON 文件
    num=0
    with open(frame_indices_path, 'r') as file:
        frame_indices = json.load(file)

    print("开始写入文件")
    for i in range(len(datas)):
        data = datas[i]
        # 最后一帧
        if i==len(datas)-1:
            start_time = data["track_0"][0][0]
            end_time = data["track_0"][0][0]
            folder_name = out_path + "\\" + str(data["id"])
            create_floder(folder_name)
            # 获取帧
            fram = get_frame_by_timestamp(cap, start_time)
            if fram is None:
                continue
            # 保存路径
            out_picture_path = folder_name + "\start.png"
            # 输出开始图片
            save_frame_as_image(fram, out_picture_path)
            # 获取帧
            fram = get_frame_by_timestamp(cap, end_time)
            # 保存路径
            out_picture_path = folder_name + "\end.png"
            # 输出开始图片
            save_frame_as_image(fram, out_picture_path)
            continue
#=======================================================================
        # 下一个交互数据
        if i!=0:
            bef_data=datas[i-1]
        next_data = datas[i+1]
            # num+=1
            # if num!=len(datas):
            #     next_data=datas[num]
            # else:
            #     next_data=data
        # 输出文件
        folder_name = out_path+"\\"+str(data["id"])
        create_floder(folder_name)
        # file_name = "example_file.txt"

        # 遍历字典中的键和值
        if data["operate"]== "Click":
            start_time = data["track_0"][0][0]
            end_time = data["track_0"][0][0]
            if i==0:
                start_index=0
            else:
                bef_end_time=bef_data["track_0"][-1][0]
                start_index=find_closest_frame(frame_indices,bef_end_time)

        #读取写入开始帧
            frame_index=find_closest_frame(frame_indices,start_time)
            #根据索引寻找开始帧
            frame_index=get_start_picture_index(frame_index+5,avg_gray_values,start_index-5)
            frame = get_frame_by_index(cap, frame_index-1)
            # fram = get_frame_by_timestamp(cap, start_time - 0.05)
            # 保存路径
            out_picture_path = folder_name + "\start.png"
            # 输出开始图片
            save_frame_as_image(frame, out_picture_path)

        # 读取写入结束帧
            next_start_time = next_data["track_0"][0][0]
            frame_index = find_closest_frame(frame_indices, start_time)
            end_index = find_closest_frame(frame_indices, next_start_time)
            frame_index=get_end_picture_index(frame_index,avg_gray_values,end_index)
            frame = get_frame_by_index(cap, frame_index+1)
            # fram = get_frame_by_timestamp(cap, start_time + 0.05)
            # 保存路径
            out_picture_path = folder_name + "\end.png"
            # 输出开始图片
            save_frame_as_image(frame, out_picture_path)
            continue

        else:
            start_time = data["track_0"][0][0]
            end_time = data["track_0"][-1][0]
            if i==0:
                start_index=0
            else:
                bef_end_time=bef_data["track_0"][-1][0]
                start_index=find_closest_frame(frame_indices,bef_end_time)
        #根据时间获取视频帧
            # 计算开始时间保存对应的图片
                # frame_index = int(fps * start_time)
            #获取帧
            frame_index = find_closest_frame(frame_indices, start_time)
            frame_index = get_start_picture_index(frame_index+5, avg_gray_values, start_index-5)
            frame = get_frame_by_index(cap, frame_index)
            # fram=get_frame_by_timestamp(cap,start_time-0.05)
            # 保存路径
            out_picture_path=folder_name+"\start.png"
            # 输出开始图片
            save_frame_as_image(frame,out_picture_path)
            # **************************************************
            # 计算结束时间保存对应的图片
                    # if(data["id"]!=next_data["id"]):
                    #     next_end_time=duration
                    # else:
                    #     next_end_time=next_data["timestamps"][0]
        # 获取帧
            next_start_time = next_data["track_0"][0][0]
            end_time_index = find_closest_frame(frame_indices, end_time)
            # end_time_index = int(fps * end_time)
            next_start_time_index= find_closest_frame(frame_indices, next_start_time)
            # next_start_time_index = int(fps * next_start_time)
            frame_index = get_end_picture_index(end_time_index, avg_gray_values, next_start_time_index)
            # frame_index  = get_end_frame_index(avg_gray_values,end_time_index,next_start_time_index)
            frame=get_frame_by_index(cap,frame_index)
            # 保存路径
            out_picture_path = folder_name + "\end.png"
            # 输出结束图片
            save_frame_as_image(frame, out_picture_path)
    #释放资源
    cap.release()


if __name__ == "__main__":
    # avg_gray_values=process_video("D:\dev\Workspace\Taida\WebSocketEmotionDetection\demo.mp4","D:\dev\Workspace\Taida\WebSocketEmotionDetection\demo_out.mp4")  # 替换为你的视频文件路径
    avg_gray_values=get_gray("data/AAtest.mp4")
    print("获取灰度成功")
    lis=[]
    list1=[]
    avg_gray_values=list(map(int, avg_gray_values))
    for i in range(1349):
        lis.append(i)
    list1.append(avg_gray_values)
    list1.append(lis)

    # get_picture("data/niehe2.mp4",
    #             "data/niehe2_output.json",avg_gray_values,
    #             "data/niehe2","data/niehe2_frame_indices.json")

    # get_picture("data/click.mp4",
    #             "data/click_output.json", avg_gray_values,
    #             "data/click", "data/click_frame_indices.json")

    get_picture("data/AAtest.mp4",
                "data/AAtest_output.json", avg_gray_values,
                "data/AAtest", "data/AAtest_frame_indices.json")
