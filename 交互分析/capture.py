import subprocess
from pathlib import Path
import datetime
import json
import uiautomator2 as u2
import multiprocessing
import time
import os

def record_screen_and_events(duration=30, video_filename="/data/demo.mp4", event_filename="/data/events.txt",time_json="../data/time.json"):
    # 设置文件路径
    remote_video_path = f"/sdcard/demo.mp4"
    # local_video_path = Path("D:\dev\Workspace\Taida\WebSocketEmotionDetection\data\demo.mp4")
    # local_event_path = Path("D:\dev\Workspace\Taida\WebSocketEmotionDetection\data\events.txt")
    local_video_path = ".."+video_filename
    local_event_path = event_filename

    #时间对齐
    # 设备已启动的时间（秒）
    uptime = float(subprocess.check_output(["adb", "shell", "cat /proc/uptime | awk '{print $1}'"], shell=True).strip())

    try:
        # 打开文件用于写入事件日志
        with open(local_event_path, "w") as event_file:
            print("开始记录触摸操作...")
            # 启动 getevent 进程并实时读取输出
            event_process = subprocess.Popen(
                ["adb", "shell", "getevent", "-lt"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 在后台启动线程读取 getevent 输出
            def read_getevent_output(process, output_file):
                for line in process.stdout:
                    # 打印并写入文件
                    print("触摸事件:", line.strip())
                    output_file.write(line)

            # 启动输出读取线程
            import threading
            event_thread = threading.Thread(target=read_getevent_output, args=(event_process, event_file))
            # 记录启动时间
            start_time0 = datetime.datetime.now()
            print(f"ADB shell 触摸数据启动时间: {start_time0}")

            event_thread.start()
            # 开始记录触摸事件

            # 等待 1 秒以确保 getevent 启动完成
            time.sleep(1)
            print("开始录屏...")

            # 记录录屏启动时间
            start_time1 = datetime.datetime.now()
            print(f"ADB shell 录屏数据启动时间: {start_time1}")
            # 运行录屏命令
            start = float(subprocess.check_output(["adb", "shell", "cat /proc/uptime | awk '{print $1}'"], shell=True).strip())

            subprocess.run(["adb", "shell", "screenrecord", f"--time-limit={duration}", remote_video_path], check=True)
            over=float(subprocess.check_output(["adb", "shell", "cat /proc/uptime | awk '{print $1}'"], shell=True).strip())

            # 记录录屏结束时间
            start_time2 = datetime.datetime.now()
            print(f"ADB shell 录屏数据结束时间: {start_time2}")
            print("录屏完成。")
            # 终止 getevent 进程并等待线程完成
            event_process.terminate()
            event_thread.join()

            data = {"start_time": start, "over_time": over}
            with open(time_json, "w") as json_file:
                json.dump(data, json_file)
            # 记录触摸结束时间
            start_time3 = datetime.datetime.now()
            print(f"ADB shell 触摸数据结束时间: {start_time3}")
            print("触摸操作记录完成。")
            print(f"触摸数据启动时间: {start_time0}\n"
                  f"录屏数据启动时间: {start_time1}\n"
                  f"录屏数据结束时间: {start_time2}\n"
                  f"触摸数据结束时间: {start_time3}\n")

        # 将录屏文件拉取到本地
        print(f"正在将录屏文件下载到 {local_video_path}...")
        subprocess.run(["adb", "pull", remote_video_path, str(local_video_path)], check=True)
        print("下载完成。")

        # 清理设备中的录屏文件
        print("正在清理设备中的录屏文件...")
        subprocess.run(["adb", "shell", "rm", remote_video_path], check=True)
        print("清理完成。")

    except subprocess.CalledProcessError as e:
        print(f"出现错误: {e}")

# 采集 XML 数据并保存到文件的函数
def collect_xml_data(device, interval, duration, output_dir):
    """
    每隔 interval 秒采集一次 XML 数据，持续 duration 秒，并保存到指定文件夹。
    :param device: uiautomator2 设备实例。
    :param interval: 采集间隔（秒）。
    :param duration: 总采集时长（秒）。
    :param output_dir: 保存 XML 文件的文件夹路径。
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            # 获取当前时间和采集时间戳
            elapsed_time = time.time() - start_time
            timestamp = f"{elapsed_time:.1f}".replace(".", "_")  # 替换小数点为下划线

            # 获取当前界面的 XML 数据
            xml_data = device.dump_hierarchy()

            # 保存 XML 数据到文件
            file_name = f"{timestamp}.xml"
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as xml_file:
                xml_file.write(xml_data)

            print(f"采集并保存 XML 文件: {file_path}")
        except Exception as e:
            print(f"采集 XML 时出错: {e}")

        # 间隔等待
        time.sleep(interval)

    print("采集任务完成")


# 启动采集的多进程函数
def start_collection_in_process(interval=0.1, duration=10, output_dir="xml"):
    """
    使用多进程启动 XML 采集任务。
    :param interval: 采集间隔（秒）。
    :param duration: 总采集时长（秒）。
    :param output_dir: 保存 XML 文件的文件夹路径。
    """
    device = u2.connect()  # 连接设备

    # 创建多进程
    process = multiprocessing.Process(
        target=collect_xml_data, args=(device, interval, duration, output_dir)
    )
    process.start()  # 启动进程
    process.join()  # 等待进程结束


# if __name__ == "__main__":
#     start_collection_in_process(interval=0.1, duration=5, output_dir="xml")  # 运行 5 秒，每 0.1 秒采集一次

if __name__ == "__main__":
    # 设置录制时间和文件名
    record_screen_and_events(duration=30, video_filename="/data/AAtest.mp4", event_filename="../data/AAtest.txt",time_json="../data/AAtest_time.json")
