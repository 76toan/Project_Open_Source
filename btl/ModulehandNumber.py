import cv2
import time
import os
import hand as htm
import math

pTime = 0
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

folderPath = "D:\\School\\Open Source\\btl\\fingers"
lst = [cv2.imread(f"{folderPath}/{img}") for img in os.listdir(folderPath)]
detector = htm.handDetector(detectionCon=0.55)
finger_id = [4, 8, 12, 16, 20]

while True:
    ret, frame = cap.read()
    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False)

    if len(lmList) != 0:
        fingers = []
        

        # Lấy các tọa độ landmarks
        x1, y1 = lmList[1][1], lmList[1][2]
        x2, y2 = lmList[2][1], lmList[2][2]
        x4, y4 = lmList[4][1], lmList[4][2]

        # Tạo vector
        v1 = (x2 - x1, y2 - y1)
        v2 = (x2 - x4, y2 - y4)

        # Tính tích vô hướng và độ dài vector
        dot_product = v1[0]*v2[0] + v1[1]*v2[1]
        magnitude_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        magnitude_v2 = math.sqrt(v2[0]**2 + v2[1]**2)

        #Tính góc giữa hai vector
        angle = math.acos(dot_product / (magnitude_v1 * magnitude_v2))
        angle = math.degrees(angle)  # Chuyển sang độ
        print(angle)

        # Xét ngón cái mở hoặc đóng
        if angle > 120:  # Góc lớn, ngón cái mở
            fingers.append(1)
            print("Ngón cái mở")
        else:  # Góc nhỏ, ngón cái đóng
            fingers.append(0)
            print("Ngón cái đóng")

        for i in range(1, 5):
            fingers.append(1 if lmList[finger_id[i]][2] < lmList[finger_id[i] - 2][2] else 0)

        soNgonTay = fingers.count(1)
        h, w, c = lst[soNgonTay - 1].shape
        frame[0:h, 0:w] = lst[soNgonTay - 1]

        cv2.rectangle(frame, (0, 200), (150, 400), (0, 255, 0), -1)
        cv2.putText(frame, str(soNgonTay), (30, 390), cv2.FONT_HERSHEY_PLAIN, 10, (0, 0, 0), 5)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(frame, f"FPS: {int(fps)}", (150, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 5)

    cv2.imshow("Finger Counting", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()