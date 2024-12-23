import cv2
import mediapipe as mp
import time

class handDetector():
    # Hàm khởi tạo đối tượng
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = float(detectionCon)  # Chuyển thành float
        self.trackCon = float(trackCon)  # Chuyển thành float

        self.mpHands = mp.solutions.hands # Tạo thuộc tính mpHands là 1 module mp.solutions.handshands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        ) # Tạo 1 thuộc tính là 1 đối tượngtượng bàn tay dựa trên module Hands trong thư viện mediapipe

        self.mpDraw = mp.solutions.drawing_utils    # Khởi tạo thuộc tính mpDraw là module hỗ trợ vẽ các landmarks(điểm đặc trưng) và kết nối(connections) của bàn tay hoặc các đối tượng khác lên hình ảnh. 

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # OpenCV sử dụng không gian màu BGR, trong khi đó mediapipe sử dụng kg màu RGB, nên t phải convert không gian màu để mediapipe có thể xử lí dữ liệu chính xác
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks: # self.results là biến chứa thông tin về các landmarks của bàn tay nếu cócó
            for handLms in self.results.multi_hand_landmarks: # self.results.multi_hand_landmarks chứa thông tin về tọa độ 21 landmarks của bàn tay
                if draw: #Theo như tham số gốc nhập vào (draw=True) thì sẽ vẽ các đường nối giữa các landmarks, nếu tham số mình nhập vào là False, bước này sẽ không thực hiện
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img # hàm trả về 1 đối tượng là img được truyền vào sau khi đã được xử lí vẽ các đường nối giữa các landmarks 

    def findPosition(self, img, handNo=0, draw=True): # tham số truyền vào trong hàm: img(ảnh, video), handNo= số thứ tự bàn tay, biến draw cho phép vẽ điểm landmarks hay không
        lmList = []
        if self.results.multi_hand_landmarks and len(self.results.multi_hand_landmarks) > handNo: # Kiểm tra xem có phát hiện được bàn tay hay không
            myHand = self.results.multi_hand_landmarks[handNo] # Khai báo biến myHand và lựa chọn bàn tay đầu tiên phát hiện được là bàn tay để xử lí với biến handNo = 0
            for id, lm in enumerate(myHand.landmark): #lm chứa các tọa độ của từng landmark trong bàn tay với tung độ hoành độ từ 0 đến 1
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
# Sử dụng cv2 để vẽ 1 vòng tròn với các tham số: img(cửa sổ vẽ), (cx, cy)(tọa độ vẽ), 10(bán kính vòng tròn, (0,255,0)(màu vẽ, lựa chọn theo không gian màu BGR, ở đây chọn màu xanh lá cây), cv2.FILLED(vẽ kín vòng tròn))
# nếu draw = False, hàm vẫn trả về 1 lmList chứa các thông số về id và tọa độ của các landmarks nhưng không vẽ các vòng tròn màu xanh tại các landmarks
        return lmList

def main():
    pTime = 0
    cap = cv2.VideoCapture(0) # Khởi tạo webcam để ghi hình, tham số 0 là lựa chọn camera của thiết bị
    cap.set(3, 640) # Thiết lập chiều rộng cho khung hình
    cap.set(4, 480) # Thiết lập chiều dài cho khung hình
    detector = handDetector() #Khởi tạo 1 đối tượng detector được định nghĩa là 1 handDetetor đã khởi tạo ở class trên

    while True:
        success, img = cap.read() # phương thức read trong thư viện opencv dùng để đọc từng frame trong khung hình, success là biến kiểm tra(=True nếu đọc thành công và ngược lại), img là kết quả đọc được từ khung hình
        img = detector.findHands(img, draw= True) #Sử dụng phương thức findHands trong class handDetector để xử lí img vừa đọc đượcđược
        lmList = detector.findPosition(img, draw= True) 
        if len(lmList) != 0: #Kiểm tra lmList có trống hay không
            print(lmList)

#Công thức tính fps là 1/(thời gian trôi qua giữa khung hình hiện tại và khung hình trước đó)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
# Hàm để hiển thị nội dung lên cửa sổ: cửa sổ được chọn, nội dung, tọa độ, font chữ, kích thước chữ, màu sắc, độ đậm của chữ
        cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img) #Hiển thị khung hình với cửa sổ tên là "ImageImage"

        if cv2.waitKey(1) & 0xFF == ord('q'): # waiKey là hàm chờ phím bấm trong 1 khoảng thời gian tính bằng miliseconds và kết quả trả về là 1 giá trị 32 bits, & 0xFF để giới hạn kết quả trả về trong phạm vi 8 bits(đảm bảo phù hợp so với bảng mã ASCII), hàm ord trả về mã ASCII của kí tự được truyền vào 
            break

    cap.release() # Đóng camera
    cv2.destroyAllWindows() #Giải phóng hình ảnh

if __name__ == "__main__":
    main()