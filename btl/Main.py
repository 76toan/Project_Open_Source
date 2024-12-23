from tkinter import *
from tkinter import messagebox
import cv2
import time
import os
import webbrowser
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
import mediapipe as mp
import hand as htm
import math
import keyboard
from ctypes import cast , POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities , IAudioEndpointVolume
import numpy as np
from tkinter import Tk, Button, filedialog
import math

#1. Hàm nhận diện số đếm qua bàn tay
def Nhandienso():
    pTime = 0
    cap = cv2.VideoCapture(0)
    folderPath = "D:\\School\\Open Source\\btl\\fingers"
    print(f"Đường dẫn thư mục: {folderPath}")
    lst = os.listdir(folderPath) # Trả về một danh sách các tên tệp tin và thư mục con có trong thư mục được chỉ định
    lst2 =[] # lst2 chứa giá trị các ảnh số ngón taytay
    for i in lst:
        image = cv2.imread(f"{folderPath}/{i}") # Đọc từng đường dẫn các ảnh trong thư mục 
        lst2.append(image) # Chèn vào trong lst2 

    detector = htm.handDetector(detectionCon=0.7) # Khởi tạo 1 đối tượng là handDetector với độ phát hiện bàn tay là 0.7
    finger_id = [4,8,12,16,20] # Khởi tạo 1 list gồm các id của các điểm landmarks đầu ngón taytay
    while(True):
        ret, frame = cap.read() # frame là biến chứa khung hình có mà camera mở lênlên
        frame = detector.findHands(frame) # Xử lí vẽ các đường connect giữa các landmarks
        lmList = detector.findPosition(frame,draw=False) #Trả về 1 list các tọa độ của các landmarks nhưng không tô các điểm landmarks
        print(lmList)

        # THAO TÁC COI NGÓN TAY
        if len(lmList)!= 0: # Kiểm tra xem có nhận diện được bàn tay hay không 
            fingers = [] # Khai báo 1 list chứa các số ngón tay sau mỗi lần xử lí nhận diện bàn tay
            #1.Viết cho ngón cái(điểm 4 nằm trái hay phải điểm 3)

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
            else:  # Góc nhỏ, ngón cái đóng
                fingers.append(0)

            #2.Viết cho trường hợp 4 ngón dài trước vì 4 ngón dài ngập xuống được
            for i in range(1,5): #Kiểm tra tương tự với tọa độ y của các ngón dài còn lại giữa điểm đầu ngón tay và điểm đốt dưới ngón 
                if (lmList[finger_id[i]][2] < lmList[finger_id[i]-2][2]): #[8,569,270] [6,584,329] lấy ra giá trị 270 < 329
                    fingers.append(1) # ngón mở thì append số 1
                else:
                    fingers.append(0) # ngón đóng thì append số 0
            print(fingers)
            soNgonTay = fingers.count(1) # đếm xem có bao nhiêu số 1

            h, w, c = lst2[soNgonTay-1].shape # lấy về kích thước ảnh 
            frame[0:h,0:w] = lst2[soNgonTay-1] #Chèn ảnh số ngón tay vào vùng từ 0 đến h theo trục x và từ 0 đến w theo trục yy

            # vẽ hình hiển thị
            cv2.rectangle(frame,(0,200),(150,400),(0,255,0),-1)
            cv2.putText(frame,str(soNgonTay),(30,390),cv2.FONT_HERSHEY_PLAIN,10,(0,0,0),5) # tọa độ (30, 390) là khoảng cách từ gốc (0,0) đến điểm chọn tính bằng pixel 

        # Tính FPS
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime =  cTime
        print(type(fps))
        cv2.putText(frame,f"FPS:{int(fps)}",(150,70),cv2.FONT_HERSHEY_PLAIN,3,(0,0,0),5) # (khung hình, nội dung, tọa độ, font chữ, kích thước chữ, màu chữ, độ dày của chữchữ)

        cv2.imshow("Khung hinh ^.^ " , frame)

        if (cv2.waitKey(1) == ord('l')):
            break
    cap.release() # giải phóng camera
    cv2.destroyAllWindows()#  thoát tất cả các cửa sổ

#2.hàm điều chỉnh thanh âm lượng bằng tay
def Dieuchinhamluong():
    pTime = 0
    cap = cv2.VideoCapture(0)
    detector = htm.handDetector(detectionCon=0.7)

    devices = AudioUtilities.GetSpeakers() # Lấy danh sách các thiết bị âm thanh đầu ra
    interface = devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None) # Gửi yêu cầu đến hệ thống Windows để kích hoạt giao diện IAudioEndpointVolume. Khi thành công: Trả về một đối tượng giao diện COM (dưới dạng interface) mà bạn có thể sử dụng để gọi các phương thức điều khiển âm thanh.
    volume = cast(interface,POINTER(IAudioEndpointVolume)) # Chuyển đổi 1 đối tượng (cụ thể ở đây là 1 giao diện COM) sang thành 1 con trỏ trỏ đến giao diện IAudioEndpointVolume

    volRange =volume.GetVolumeRange() # Lấy dải âm lượng trả về 1 tuple có 3 giá trị ll là [mức âm lượng nhỏ nhất, mức âm lượng lớn nhất, bước tăng/giảm âm lượng] với đơn vị đo là decibel (dB)
    minVol = volRange[0] # Mức âm lượng nhỏ nhất
    maxVol = volRange[1] # Mức âm lượng lớn nhấtnhất
    print(volRange)
    print(minVol)
    print(maxVol)

    while(True):
        ret, frame = cap.read()
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame,draw=False) # Không vẽ các điểm landmarks

        if (len(lmList) != 0):
            x1 ,y1= lmList[4][1], lmList[4][2] # Lấy tọa độ điểm đầu ngón cái
            x2 ,y2 = lmList[8][1], lmList[8][2] # Lấy tọa độ điểm đầu ngón trỏ

            # vẽ điểm tròn trên ngón cái
            cv2.circle(frame,(x1,y1),15,(155,155,155),-1)
            # vẽ điểm tròn trên ngón trỏ
            cv2.circle(frame,(x2,y2),15,(155,100,155),-1)
            # nối hai điểm
            cv2.line(frame,(x1,y1),(x2,y2),(255,3,255),3)
            # vẽ hình tròn ở giữa
            cx,cy = (x1 + x2)//2,(y1 + y2)//2 # Tọa độ trung điểm giữa 2 điểm landmarks 4 và 8
            cv2.circle(frame,(cx, cy),10,(255,0,255),-1)
            # độ dài đoạn thẳng
            doDaiDoanThang = math.hypot(x2 - x1, y2-y1) 

            # khoảng cách giữa hai điểm vào khoảng 30-230
            # dải âm thanh trên máy chạy từ -74 --> 0
            vol = np.interp(doDaiDoanThang,[30,200],[minVol,maxVol])
            volBar = np.interp(doDaiDoanThang,[30,200],[400,150])
            voltyle = np.interp(doDaiDoanThang,[30,200],[0,100])
            volume.SetMasterVolumeLevel(vol,None)
            if doDaiDoanThang < 30:
                cv2.circle(frame ,(cx, cy),10,(255,0,0),-1)

            cv2.rectangle(frame ,(50,150),(100,400),(0,0,255),3)
            cv2.rectangle(frame ,(50,int(volBar)),(100,400),(0,255,0),-1)
            # show % volume
            cv2.putText(frame,f"FPS:{int(voltyle)} %",(50,450),cv2.FONT_HERSHEY_PLAIN,3,(0,0,0),4)

        # Viết ra FPS
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime =  cTime
        # show fps trên màn hình
        print(type(fps))
        cv2.putText(frame,f"FPS:{int(fps)}",(150,70),cv2.FONT_HERSHEY_PLAIN,3,(0,0,0),5)

        cv2.imshow("Khung hinh ^.^ " , frame)
        if (cv2.waitKey(1) == ord('l')):
            break
    cap.release() # giải phóng camera
    cv2.destroyAllWindows()#  thoát tất cả các cửa sổ

#3. Hàm tạo phím tắt
def PhimTat():
    # tiến hành tạo giá trị
    ns= 0
    n = phimTat.get()
    entry_vars = []
    if(n.isdigit()):
        ns =int(n)
    Label(win, text='Nhập số lượng phím tắt:').place(x=100, y=400)
    Entry(win, width=20, textvariable=phimTat).place(x=250, y=400)
    y = 430
    # Tạo phím tắt
    for i in range(0,ns):
        Label(win, text='Tạo phím tắt {}:'.format(i+1)).place(x=100, y=y)
        Entry(win, width=20, textvariable=ds_bien_phimtat[i]).place(x=250, y=y)
        entry_vars.append(ds_bien_phimtat[i].get())
        y+=30
    print(entry_vars)
    return entry_vars

def phim_Tat():
    entry_var = PhimTat()
    pTime = 0
    cap = cv2.VideoCapture(0)
    folderPath = "D:\\School\\Open Source\\btl\\fingers"
    lst = os.listdir(folderPath)
    lst2 =[]
    for i in lst:
        image = cv2.imread(f"{folderPath}/{i}")
        lst2.append(image)
    detector = htm.handDetector(detectionCon=0.55)
    finger_id = [4,8,12,16,20]
    drive_opened = False
    drive_opened_1 = False
    while(True):
        ret, frame = cap.read()
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame,draw=False)
        # THAO TÁC COI NGÓN TAY
        if len(lmList)!= 0:
            fingers = []
            #1.Viết cho ngón cái(điểm 4 nằm trái hay phải điểm 3)
            if (lmList[finger_id[0]][1] < lmList[finger_id[0]-1][1]):
                fingers.append(1) # ngón mở thì append số 1
            else:
                fingers.append(0) # ngón đóng thì append số 0

            #2.Viết cho trường hợp 4 ngón dài trước vì 4 ngón dài ngập xuống được
            for i in range(1,5):
                if (lmList[finger_id[i]][2] < lmList[finger_id[i]-2][2]):
                    fingers.append(1) # ngón mở thì append số 1
                else:
                    fingers.append(0) # ngón đóng thì append số 0
            print(fingers)
            soNgonTay = fingers.count(1) # đếm xem có bao nhiêu số 1

            h, w,c = lst2[soNgonTay-1].shape
            frame[0:h,0:w] = lst2[soNgonTay-1]

            # vẽ hình hiển thị
            cv2.rectangle(frame,(0,200),(150,400),(0,255,0),-1)
            cv2.putText(frame,str(soNgonTay),(30,390),cv2.FONT_HERSHEY_PLAIN,10,(0,0,0),5)

            # tạo phím tắt 1,2,3
            if (len(entry_var)==1):
                if (soNgonTay == 1 and not drive_opened):
                    drive_url = entry_var[0]
                    webbrowser.open(drive_url)
                    drive_opened = True
            if (len(entry_var) == 2): # 2 phím tắt
                if (soNgonTay == 1 and not drive_opened):
                    drive_url = entry_var[0]
                    webbrowser.open(drive_url)
                    drive_opened = True
                if (soNgonTay == 3):
                    folderPath = entry_var[1]
                    os.startfile(folderPath)
            if (len(entry_var) == 3):
                if (soNgonTay == 1 and not drive_opened):
                    drive_url = entry_var[0] #link web
                    webbrowser.open(drive_url)
                    drive_opened = True
                if (soNgonTay == 2):
                    folderPath1 = entry_var[1] # link máy
                    os.startfile(folderPath1)
                if(soNgonTay == 3):
                    folderPath2 = entry_var[2] # link máy
                    os.startfile(folderPath2)
            if (len(entry_var) == 4):
                if (soNgonTay == 1 and not drive_opened):
                    drive_url = entry_var[0] #link web
                    webbrowser.open(drive_url)
                    drive_opened = True
                if (soNgonTay == 2):
                    folderPath1 = entry_var[1] # link máy
                    os.startfile(folderPath1)
                if(soNgonTay == 3):
                    folderPath2 = entry_var[2] # link máy
                    os.startfile(folderPath2)
                if (soNgonTay == 4 and not drive_opened_1):
                    drive_url1 =entry_var[3] # link web youtube
                    webbrowser.open(drive_url1)
                    drive_opened_1 = True
            if (len(entry_var) == 5):
                if (soNgonTay == 1 and not drive_opened):
                    drive_url = entry_var[0] #link web
                    webbrowser.open(drive_url)
                    drive_opened = True
                if (soNgonTay == 2):
                    folderPath = entry_var[1] # link máy
                    os.startfile(folderPath)
                if(soNgonTay == 3):
                    folderPath1 = entry_var[2] # link máy
                    os.startfile(folderPath1)
                if (soNgonTay == 4 and not drive_opened_1):
                    drive_url =entry_var[3] # link web youtube
                    webbrowser.open(drive_url)
                    drive_opened_1 = True
                if (soNgonTay == 5):
                    folderPath2 = entry_var[4]
                    keyboard.press_and_release(folderPath2)
        # Viết ra FPS
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime =  cTime
        # show fps trên màn hình
        print(type(fps))
        cv2.putText(frame,f"FPS:{int(fps)}",(150,70),cv2.FONT_HERSHEY_PLAIN,3,(0,0,0),5)

        #3. Xử lý thao tác với ngón tay
        cv2.imshow("Khung hinh ^.^ " , frame)

        if (cv2.waitKey(1) == ord('l')):
            break
    cap.release() # giải phóng camera
    cv2.destroyAllWindows()#  thoát tất cả các cửa sổ

#4. Xuất File
def Luu_File():
    ds = PhimTat()
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            for i in range(len(ds)):
                file.write('Phím ' + str(i+1)+ ': ' + ds[i]+'\n')
        messagebox.showinfo("Xuất file","Xuất file thành công")

# 5. TKinter
win = Tk()
phimTat = StringVar()
phimTat1 = StringVar()
phimTat2 = StringVar()
phimTat3 = StringVar()
phimTat4 = StringVar()
phimTat5 = StringVar()
ds_bien_phimtat = [phimTat1,phimTat2, phimTat3, phimTat4, phimTat5]
win.title('Ứng dụng nhận diện,thao tác tăng giảm âm lượng,tạo phím tắt cơ bản với bàn tay')
win.minsize(height=600,width=500)
Label(win,text="Ứng dụng nhận diện,thao tác tăng giảm âm lượng,tạo phím tắt cơ bản với bàn tay",fg='red',font=('cambria',15),width=70).grid(row=0)
listbox = Listbox(win, width=80,height=20)
listbox.grid(row=1,columnspan=2)

# tạo các button
button = Frame(win)
Button(button,text='Nhận diện số',command=Nhandienso).pack(side=LEFT)
Button(button,text='Điều chỉnh thanh âm lượng', command= Dieuchinhamluong).pack(side=LEFT)
Button(button,text='Tạo phím tắt',command=PhimTat).pack(side=LEFT)
Button(button,text='Run',command=phim_Tat).pack(side=LEFT)
Button(button,text='Lưu file',command=Luu_File).pack(side=LEFT)
Button(button,text='Thoát',command=win.quit).pack(side=LEFT)
button.grid(row=5,column=0)

win.mainloop()