import cv2
import mediapipe as mp
import time

class handDetector():
    # Hàm khởi tạo đối tượng
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = float(detectionCon) 
        self.trackCon = float(trackCon)  

        self.mpHands = mp.solutions.hands # Tạo thuộc tính mpHands là 1 module mp.solutions.hands 
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode, # static_image_mode=True nếu muốn xử lí ảnh tĩnh, ngược lại là False
            max_num_hands=self.maxHands, # Số lượng bàn tay tối đa cần phát hiện
            min_detection_confidence=self.detectionCon, # Độ tin cậy nhỏ nhất để xác định bàn tay
            min_tracking_confidence=self.trackCon # Độ tin cậy nhỏ nhất để theo dõi bàn tay
        ) # Tạo 1 thuộc tính là 1 đối tượng bàn tay dựa trên module Hands trong thư viện mediapipe

        self.mpDraw = mp.solutions.drawing_utils  # Khởi tạo thuộc tính mpDraw là module hỗ trợ vẽ các landmarks(điểm đặc trưng) và kết nối(connections) của bàn tay hoặc các đối tượng khác lên hình ảnh. 

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # OpenCV sử dụng không gian màu BGR, trong khi đó mediapipe sử dụng kg màu RGB, nên t phải convert không gian màu để mediapipe có thể xử lí dữ liệu chính xác
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks: 
            for handLms in self.results.multi_hand_landmarks: 
                if draw: 
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img 
    
    def findPosition(self, img, handNo=0, draw=True): 
        lmList = []
        if self.results.multi_hand_landmarks and len(self.results.multi_hand_landmarks) > handNo: 
            myHand = self.results.multi_hand_landmarks[handNo] 
            for id, lm in enumerate(myHand.landmark): 
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 255), cv2.FILLED)

        return lmList

def main():
    pTime = 0
    cap = cv2.VideoCapture(0) 
    cap.set(3, 640) 
    cap.set(4, 480) 
    detector = handDetector() 

    while True:
        success, img = cap.read() 
        img = detector.findHands(img, draw= True) 
        lmList = detector.findPosition(img, draw= True) 
        if len(lmList) != 0: 
            print(lmList)


        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img) 

        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

    cap.release() 
    cv2.destroyAllWindows() 

if __name__ == "__main__":
    main()