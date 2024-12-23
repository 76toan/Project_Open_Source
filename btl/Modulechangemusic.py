import numpy as np
import cv2
import time
import hand as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

pTime = 0
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height
detector = htm.handDetector(detectionCon=0.7)


# Thiết lập âm thanh
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]  # Ngón cái
        x2, y2 = lmList[8][1], lmList[8][2]  # Ngón trỏ

        cv2.circle(frame, (x1, y1), 10, (255, 0, 0), -1)
        cv2.circle(frame, (x2, y2), 10, (255, 0, 0), -1)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        length = math.hypot(x2 - x1, y2 - y1)

        # Chỉ định giá trị âm lượng dựa trên chiều dài
        if length < 30:
            vol = minVol
        elif length > 200:
            vol = maxVol
        else:
            vol = np.interp(length, [30, 200], [minVol, maxVol])

        volume.SetMasterVolumeLevel(vol, None)

        # Hiển thị thanh âm lượng
        volBar = np.interp(length, [30, 200], [400, 150])
        cv2.rectangle(frame, (50, 150), (85, 400), (0, 0, 255), 3)
        cv2.rectangle(frame, (50, int(volBar)), (85, 400), (0, 255, 0), -1)

    # Tính FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(frame, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

    cv2.imshow("Volume Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
