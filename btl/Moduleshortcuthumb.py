import cv2
import time
import os
import hand as htm
import webbrowser

pTime = 0
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

folderPath = "D:\\School\\Open Source\\btl\\fingers"
lst = [cv2.imread(f"{folderPath}/{img}") for img in os.listdir(folderPath)]
detector = htm.handDetector(detectionCon=0.77)
finger_id = [4, 8, 12, 16, 20]

drive_opened = False
youtube_opened = False

while True:
    ret, frame = cap.read()
    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False)

    if len(lmList) != 0:
        fingers = []
        fingers.append(1 if lmList[finger_id[0]][1] < lmList[finger_id[0] - 1][1] else 0)
        for i in range(1, 5):
            fingers.append(1 if lmList[finger_id[i]][2] < lmList[finger_id[i] - 2][2] else 0)

        soNgonTay = fingers.count(1)
        h, w, c = lst[soNgonTay - 1].shape
        frame[0:h, 0:w] = lst[soNgonTay - 1]

        if soNgonTay == 1 and not drive_opened:
            webbrowser.open('https://drive.google.com')
            drive_opened = True
        elif soNgonTay == 3:
            os.startfile("F:\\Downloads")
        elif soNgonTay == 5 and not youtube_opened:
            webbrowser.open('https://www.youtube.com')
            youtube_opened = True

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(frame, f"FPS:{int(fps)}", (150, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 5)

    cv2.imshow("Gesture-Controlled Web/File", frame)
    if cv2.waitKey(1) == ord('l'):
        break

cap.release()
cv2.destroyAllWindows()