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
from tkinter import Tk, Button, filedialog , PhotoImage
import math

#1. Hàm nhận diện số đếm qua bàn tay
def Nhandienso():
    pTime = 0
    cap = cv2.VideoCapture(0)
    folderPath = "D:\\School\\Open Source\\btl\\fingers"
    print(f"Đường dẫn thư mục: {folderPath}")
    lst = os.listdir(folderPath) 
    lst2 =[] 
    for i in lst:
        image = cv2.imread(f"{folderPath}/{i}") 
        lst2.append(image) 

    detector = htm.handDetector(detectionCon=0.7) 
    finger_id = [4,8,12,16,20] 
    while(True):
        ret, frame = cap.read() 
        frame = detector.findHands(frame) 
        lmList = detector.findPosition(frame,draw=False) 
        print(lmList)

        # THAO TÁC COI NGÓN TAY
        if len(lmList)!= 0: 
            fingers = [] 
            #1.Viết cho ngón cái

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
            if angle > 140:  # Góc lớn, ngón cái mở
                fingers.append(1)
            else:  # Góc nhỏ, ngón cái đóng
                fingers.append(0)

            #2.Viết cho trường hợp 4 ngón dài trước vì 4 ngón dài ngập xuống được
            for i in range(1,5): 
                if (lmList[finger_id[i]][2] < lmList[finger_id[i]-2][2]): 
                    fingers.append(1) # ngón mở thì append số 1
                else:
                    fingers.append(0) # ngón đóng thì append số 0
            print(fingers)
            soNgonTay = fingers.count(1) # đếm xem có bao nhiêu số 1

            h, w, c = lst2[soNgonTay-1].shape # lấy về kích thước ảnh 
            frame[0:h,0:w] = lst2[soNgonTay-1] 

            # vẽ hình hiển thị
            cv2.rectangle(frame,(0,200),(150,400),(0,255,0),-1)
            cv2.putText(frame,str(soNgonTay),(30,390),cv2.FONT_HERSHEY_PLAIN,10,(0,0,0),5) # tọa độ (30, 390) là khoảng cách từ gốc (0,0) đến điểm chọn tính bằng pixel 

        # Tính FPS
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime =  cTime
        print(type(fps))
        cv2.putText(frame,f"FPS:{int(fps)}",(150,70),cv2.FONT_HERSHEY_PLAIN,3,(255, 0, 255),5) # (khung hình, nội dung, tọa độ, font chữ, kích thước chữ, màu chữ, độ dày của chữchữ)

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
    interface = devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None) 
    volume = cast(interface,POINTER(IAudioEndpointVolume)) 

    volRange =volume.GetVolumeRange() 
    minVol = volRange[0] 
    maxVol = volRange[1] 
    print(volRange)
    print(minVol)
    print(maxVol)

    while(True):
        ret, frame = cap.read()
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame,draw=False) 

        if (len(lmList) != 0):
            x1 ,y1= lmList[4][1], lmList[4][2] 
            x2 ,y2 = lmList[8][1], lmList[8][2] 

            # vẽ điểm tròn trên ngón cái
            cv2.circle(frame,(x1,y1),15,(155,155,155),-1)
            # vẽ điểm tròn trên ngón trỏ
            cv2.circle(frame,(x2,y2),15,(155,100,155),-1)
            # nối hai điểm
            cv2.line(frame,(x1,y1),(x2,y2),(255,3,255),3)
            # vẽ hình tròn ở giữa
            cx,cy = (x1 + x2)//2,(y1 + y2)//2 
            cv2.circle(frame,(cx, cy),10,(255,0,255),-1)
            # độ dài đoạn thẳng
            doDaiDoanThang = math.hypot(x2 - x1, y2-y1) 

            # np.interp giúp chuyển đổi giá trị từ dải này sang dải khác (công thức nội suy) 
            vol = np.interp(doDaiDoanThang,[30,200],[minVol,maxVol]) 
            volBar = np.interp(doDaiDoanThang,[30,200],[400,150]) 
            voltyle = np.interp(doDaiDoanThang,[30,200],[0,100]) 
            volume.SetMasterVolumeLevel(vol,None) 
            if doDaiDoanThang < 30:
                cv2.circle(frame ,(cx, cy),10,(255,0,0),-1) 

            cv2.rectangle(frame ,(50,150),(100,400),(0,0,255),3) 
            cv2.rectangle(frame ,(50,int(volBar)),(100,400),(0,255,0),-1) 
            # show % volume
            cv2.putText(frame,f"FPS:{int(voltyle)} %",(50,450),cv2.FONT_HERSHEY_PLAIN,3,(255, 0, 255),4) 

        # Viết ra FPS
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime =  cTime
        # show fps trên màn hình
        print(type(fps))
        cv2.putText(frame,f"FPS:{int(fps)}",(150,70),cv2.FONT_HERSHEY_PLAIN,3,(255, 0, 255),5)

        cv2.imshow("Khung hinh ^.^ " , frame)
        if (cv2.waitKey(1) == ord('l')):
            break
    cap.release() # giải phóng camera
    cv2.destroyAllWindows()#  thoát tất cả các cửa sổ

#3. Hàm tạo phím tắt
def PhimTat():
    # Tiến hành tạo giá trị
    ns= 0
    n = phimTat.get() # Lấy giá trị từ ô nhập 
    entry_vars = []
    if(n.isdigit()): # Kiểm tra xem giá trị nhập vào có phải là số không
        ns = int(n)
        if ns < 1 or ns > 5:
            messagebox.showerror("Lỗi","Số lượng phím tắt không hợp lệ. Vui lòng nhập lại")
            return
    
    # Xóa các widget cũ
    for label in label_widgets:
        label.destroy()
    for entry in entry_widgets:
        entry.destroy()
    
    # Xóa các entry label cũ được lưu trữ trong list
    label_widgets.clear()
    entry_widgets.clear()
    
    # Tạo label entry nhập giá trị số lượng phím tắt
    Label(win, text='Nhập số lượng phím tắt:').place(x=100, y=400)
    Entry(win, width=20, textvariable=phimTat).place(x=250, y=400)

    # Tạo phím tắt
    y = 430

    for i in range(0,ns):
        if y == 430:
            label = Label(win, text='{}. Nhập đường dẫn link web 1:'.format(i+1))
            label.place(x=100, y=y)
            entry = Entry(win, width=60, textvariable=ds_bien_phimtat[i])
            entry.place(x=350, y=y)
            entry_vars.append(ds_bien_phimtat[i].get())
        elif y == 460:
            label = Label(win, text='{}. Nhập đường dẫn link web 2:'.format(i+1))
            label.place(x=100, y=y)
            entry = Entry(win, width=60, textvariable=ds_bien_phimtat[i])
            entry.place(x=350, y=y)
            entry_vars.append(ds_bien_phimtat[i].get())
        elif y == 490:
            label = Label(win, text='{}. Nhập đường dẫn folder/file:'.format(i+1))
            label.place(x=100, y=y)
            entry = Entry(win, width=60, textvariable=ds_bien_phimtat[i])
            entry.place(x=350, y=y)
            entry_vars.append(ds_bien_phimtat[i].get())
        elif y == 520:
            label = Label(win, text='{}. Mở ứng dụng máy tính (Calculator):'.format(i+1))
            label.place(x=100, y=y)
            entry = Entry(win, width=60, textvariable=ds_bien_phimtat[i])
            entry.place(x=350, y=y)
            entry_vars.append(ds_bien_phimtat[i].get())
        elif y == 550:
            label = Label(win, text='{}. Nhập tổ hợp hoặc đơn lẻ các phím:'.format(i+1))
            label.place(x=100, y=y)
            entry = Entry(win, width=60, textvariable=ds_bien_phimtat[i])
            entry.place(x=350, y=y)
            entry_vars.append(ds_bien_phimtat[i].get())
        label_widgets.append(label)
        entry_widgets.append(entry)
        y+=30
    print(entry_vars)
    return entry_vars

#4. Hàm nhận diện và thao tác với bàn tay
def phim_Tat():
    entry_var = PhimTat() # Hàm trả về 1 list giá trị entry của các phím tắt được tạo từ button "Tạo phím tắt"
    if len(entry_var) == 0:
        messagebox.showerror("Lỗi","Vui lòng nhập số lượng phím tắt")
        return
    for i in range(len(entry_var)):
        if entry_var[i] == '':
            messagebox.showerror("Lỗi","Vui lòng nhập đầy đủ thông tin")
            return
        if len(entry_var) > 3:
            if entry_var[3] != 'no' and entry_var[3] != 'yes':
                messagebox.showerror("Lỗi","Vui lòng nhập yes hoặc no ở mục 4.")
                return
    pTime = 0
    cap = cv2.VideoCapture(0)

    # Lưu các ảnh trong folder fingers vào trong list lst2 
    folderPath = "D:\\School\\Open Source\\btl\\fingers"
    lst = os.listdir(folderPath)
    lst2 =[]
    for i in lst:
        image = cv2.imread(f"{folderPath}/{i}")
        lst2.append(image)
    
    # Khởi tạo 1 đối tượng handDetector
    detector = htm.handDetector(detectionCon=0.7)
    finger_id = [4,8,12,16,20]
    opened1 = False
    opened2 = False
    opened3 = False
    opened4 = False

    while(True):
        ret, frame = cap.read()
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame,draw=False)

        # THAO TÁC COI NGÓN TAY
        if len(lmList)!= 0:
            fingers = []
            # Viết cho ngón cái
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
            if angle > 140:  # Góc lớn, ngón cái mở
                fingers.append(1)
            else:  # Góc nhỏ, ngón cái đóng
                fingers.append(0)

            # Viết cho trường hợp 4 ngón dài trước vì 4 ngón dài ngập xuống được
            for i in range(1,5):
                if (lmList[finger_id[i]][2] < lmList[finger_id[i]-2][2]):
                    fingers.append(1) # ngón mở thì append số 1
                else:
                    fingers.append(0) # ngón đóng thì append số 0
            print(fingers)
            soNgonTay = fingers.count(1) # đếm xem có bao nhiêu số 1

            h, w,c = lst2[soNgonTay-1].shape
            frame[0:h,0:w] = lst2[soNgonTay-1]

            # Vẽ hình hiển thị số ngón tay nhận diện được
            cv2.rectangle(frame,(0,200),(150,400),(0,255,0),-1)
            cv2.putText(frame,str(soNgonTay),(30,390),cv2.FONT_HERSHEY_PLAIN,10,(0,0,0),5)

            # Xử lý thao tác với ngón tay
            # 1 phím tắt
            if (len(entry_var)==1):
                if (soNgonTay == 1 and not opened1):
                    url1 = entry_var[0]
                    webbrowser.open(url1)
                    opened1 = True
                elif (soNgonTay == 0):
                    opened1 = False

            # 2 phím tắt
            if (len(entry_var) == 2): # 2 phím tắt
                if (soNgonTay == 1 and not opened1):
                    url1 = entry_var[0]
                    webbrowser.open(url1)
                    opened1 = True
                elif (soNgonTay == 2 and not opened2):
                    url2 = entry_var[1]
                    webbrowser.open(url2)
                    opened2 = True
                elif (soNgonTay == 0):
                    opened1 = False
                    opened2 = False

            # 3 phím tắt
            if (len(entry_var) == 3):
                if (soNgonTay == 1 and not opened1):
                    drive_url1 = entry_var[0]
                    webbrowser.open(drive_url1)
                    opened1 = True
                elif (soNgonTay == 2 and not opened2):
                    drive_url2 = entry_var[1]
                    webbrowser.open(drive_url2)
                    opened2 = True
                elif (soNgonTay == 3 and not opened3):
                    folderPath = entry_var[2]
                    if os.path.exists(folderPath):
                        os.startfile(folderPath)
                        opened3 = True
                    else:
                        messagebox.showerror("Lỗi","Đường dẫn không tồn tại")
                elif (soNgonTay == 0):
                    opened1 = False
                    opened2 = False
                    opened3 = False

            # 4 phím tắt
            if (len(entry_var) == 4):
                if (soNgonTay == 1 and not opened1):
                    drive_url1 = entry_var[0]
                    webbrowser.open(drive_url1)
                    opened1 = True
                elif (soNgonTay == 2 and not opened2):
                    drive_url2 = entry_var[1]
                    webbrowser.open(drive_url2)
                    opened2 = True
                elif (soNgonTay == 3 and not opened3):
                    folderPath = entry_var[2]
                    if os.path.exists(folderPath):
                        os.startfile(folderPath)
                        opened3 = True
                    else:
                        messagebox.showerror("Lỗi","Đường dẫn không tồn tại")
                elif (soNgonTay == 4 and not opened4):
                    open_cal = entry_var[3]
                    if open_cal == 'yes':
                        os.system('calc')
                        opened4 = True
                elif (soNgonTay == 0):
                    opened1 = False
                    opened2 = False
                    opened3 = False
                    opened4 = False
            
            # 5 phím tắt
            if (len(entry_var) == 5):
                if (soNgonTay == 1 and not opened1):
                    drive_url1 = entry_var[0]
                    webbrowser.open(drive_url1)
                    opened1 = True
                elif (soNgonTay == 2 and not opened2):
                    drive_url2 = entry_var[1]
                    webbrowser.open(drive_url2)
                    opened2 = True
                elif (soNgonTay == 3 and not opened3):
                    folderPath = entry_var[2]
                    if os.path.exists(folderPath):
                        os.startfile(folderPath)
                        opened3 = True
                    else:
                        messagebox.showerror("Lỗi","Đường dẫn không tồn tại")
                elif (soNgonTay == 4 and not opened4):
                    open_cal = entry_var[3]
                    if open_cal == 'yes':
                        os.system('calc')
                        opened4 = True
                elif (soNgonTay == 5):
                    key = entry_var[4]
                    keyboard.press_and_release(key)
                elif (soNgonTay == 0):
                    opened1 = False
                    opened2 = False
                    opened3 = False
                    opened4 = False
        # Viết ra FPS
        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime =  cTime
        # show fps trên màn hình
        print(type(fps))
        cv2.putText(frame,f"FPS:{int(fps)}",(150,70),cv2.FONT_HERSHEY_PLAIN,3,(255, 0, 255),5)

        #3. Xử lý thao tác với ngón tay
        cv2.imshow("Khung hinh ^.^ " , frame)

        if (cv2.waitKey(1) == ord('l')):
            break
    cap.release() # giải phóng camera
    cv2.destroyAllWindows()#  thoát tất cả các cửa sổ

#5. Xuất File
def Luu_File():
    ds = PhimTat()
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            for i in range(len(ds)):
                file.write('Phím ' + str(i+1)+ ': ' + ds[i]+'\n')
        messagebox.showinfo("Xuất file","Xuất file thành công")

#6. TKinter
label_widgets = []
entry_widgets = []
win = Tk()
phimTat = StringVar()
phimTat1 = StringVar()
phimTat2 = StringVar()
phimTat3 = StringVar()
phimTat4 = StringVar()
phimTat5 = StringVar()
ds_bien_phimtat = [phimTat1,phimTat2, phimTat3, phimTat4, phimTat5]
win.title('Hand Recognition Application')
win.minsize(height=600,width=500)
Label(win,text="Ứng dụng nhận diện, đếm số ngón tay, thao tác tăng giảm âm lượng, tạo phím tắt cơ bản với bàn tay",fg='red',font=('cambria',15)).grid(row=0)
image = PhotoImage(file="d:\School\Open Source\Documents\Hand.png")
label = Label(win, image=image)
label.grid(row=2, column=0)

# tạo các button
button = Frame(win)
Button(button,text='Nhận diện số',command=Nhandienso).pack(side=LEFT)
Button(button,text='Điều chỉnh âm lượng', command= Dieuchinhamluong).pack(side=LEFT)
Button(button,text='Tạo phím tắt',command=PhimTat).pack(side=LEFT)
Button(button,text='Run',command=phim_Tat).pack(side=LEFT)
Button(button,text='Lưu thông tin phím tắt',command=Luu_File).pack(side=LEFT)
Button(button,text='Thoát',command=win.quit).pack(side=LEFT)
button.grid(row=3,column=0)

win.mainloop()