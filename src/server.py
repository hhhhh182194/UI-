import cv2
import base64
import numpy as np
from deepface import DeepFace
import time
import asyncio
import websockets
import json


def base64_to_image(base64_str):
    img_data = base64.b64decode(base64_str.split(",")[1])
    np_array = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return img


async def analyze(websocket, path):
    async for message in websocket:
        # 接收 base64 编码的视频帧
        img = base64_to_image(message)


        try:
            result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
            dominant_emotion = result[0]['dominant_emotion']
            emotions = result[0]['emotion']


            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            response = {
                "timestamp": timestamp,
                "dominant_emotion": dominant_emotion,
                "emotions": emotions
            }


            await websocket.send(json.dumps(response))
        except Exception as e:
            print(f"Error analyzing frame: {e}")
            await websocket.send(json.dumps({"error": str(e)}))


async def main():
    async with websockets.serve(analyze, "localhost", 5000):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())