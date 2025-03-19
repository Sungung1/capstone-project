import time, threading, pygame, os, sys
import tkinter as tk
from tkinter import ttk

from tapsdk import TapSDK, TapInputMode

# 전역 변수
tap_instance = []
tap_identifiers = []

isCollecting = False
isConnecting = False
row=""
insertedWord = ""
insertedCount = 0
folderPath = ""
tempFileGyro = None
tempFileAccel = None


stop_event = threading.Event()

# pygame 초기화
pygame.mixer.init()

def play_short_beep_sound():
    pygame.mixer.music.load("effectSounds/beep3.wav")
    pygame.mixer.music.play()

def play_long_beep_sound():
    pygame.mixer.music.load("effectSounds/beep_last.wav")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def counting3():
    global stop_event
    if stop_event.is_set():
        return
    time.sleep(2)
    for i in range(3, 0, -1):
        if stop_event.is_set():
            return
        play_short_beep_sound()
        update_label_text(i)
        time.sleep(1)

    if not stop_event.is_set():
        update_label_text("")
        play_long_beep_sound()

def collecting_data():
    global stop_event, isCollecting
    if stop_event.is_set():
        return
    update_label_text("(수집 중)")
    isCollecting = True
    for _ in range(30):  # 3초 동안 0.1초 간격으로 체크
        if stop_event.is_set():
            isCollecting = False
            return
        time.sleep(0.1)
    isCollecting = False

def saving():
    global stop_event, insertedCount, isCollecting, insertedWord
    if stop_event.is_set():
        return
    
    print("saving")
    i = 1
    file_path = folderPath + "/" + insertedWord
    while True :
        temp_file_path_gyro = file_path+"_gyro" + str(i)
        temp_file_path_accel = file_path+"_accel" + str(i)
        if not os.path.exists(temp_file_path_gyro) and not os.path.exists(temp_file_path_accel):
            break
        i+=1

    #자이로 저장 
    tempFileGyro.seek(0) #내용을 옮기기 위해 읽는 지점을 파일의 처음으로
    file_gyro = open(file_path+"_gyro"+str(i), 'w') #insertedWord 파일 추가모드로 열기
    
    file_gyro.write(tempFileGyro.read())  #insertedWord+Temp 파일 내용을 insertedWord 파일에 붙이기
    
    file_gyro.close()   #insertedWord 파일 닫기
    tempFileGyro.close()  #insertedWord+Temp 파일 닫기
    
    
    #5손가락 가속도계 저장
    tempFileAccel.seek(0) #내용을 옮기기 위해 읽는 지점을 파일의 처음으로
    file_accel = open(file_path+"_accel"+str(i), 'w') #insertedWord 파일 추가모드로 열기
    file_accel.write(tempFileAccel.read())  #insertedWord+Temp 파일 내용을 insertedWord 파일에 붙이기
        
    file_accel.close()   #insertedWord 파일 닫기
    tempFileAccel.close()  #insertedWord+Temp 파일 닫기
        
    tap_instance.loop = False
    isCollecting = False
    insertedCount += 1
    doubleVar.set(insertedCount)
    progressbar.update()

def refresh():
    global insertedWord, insertedCount
    btnStart.config(text=beginText)
    btnStart.config(state=tk.NORMAL)
    btnEnd.config(text=endText)
    label.config(text= "")
    insertedWord = ""
    insertedCount = 0
    doubleVar.set(0)
    word.config(state=tk.NORMAL)
    word.delete(0, tk.END)

def start_counting():
    global insertedCount, insertedWord, stop_event, isCollecting, folderPath
    while insertedCount < 5 and not stop_event.is_set():
        print("insertedCount : "+str(insertedCount))
        update_label_text(f"{insertedWord} 단어 수집을 시작합니다\n3초 후 삐- 소리가 끝나면 동작을 해주세요.")
        counting3()
        if stop_event.is_set():
            break
        
        #저장 경로 지정
        folderName = "WordData"
        folderPath = os.path.join(os.getcwd(), folderName)
        
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        global tempFileGyro, tempFileAccel
        tempFileGyro = open(folderPath + "/TempGyro", 'w+')#Temp 파일 만들기(있으면 내용 비우고 새로)
        tempFileAccel = open(folderPath + "/TempAccel", 'w+')#Temp 파일 만들기(있으면 내용 비우고 새로)

        isCollecting = True
        tap_instance.loop = True
        collecting_data()
        if stop_event.is_set():
            break
        else : 
            saving()

    if stop_event.is_set():
        stop_event.clear()
    else:
        update_label_text("5번 수집 완료")
        time.sleep(2)

    refresh()

def start_collecting():
    btnStart.config(state=tk.DISABLED)
    btnEnd.config(text="취소")
    thread = threading.Thread(target=start_counting)
    thread.start()

def ask_word_inserted_right():
    btnStart.config(text="네")
    btnEnd.config(text="아니오")
    label.config(text= f"수집할 단어가 {len(insertedWord)} 길이의 {insertedWord}가 맞나요?")

def insert_word():
    global insertedWord
    insertedWord = word.get()

    if len(insertedWord) == 0:
        return
    word.config(state=tk.DISABLED)

    if btnStart.cget('text') == beginText:
        ask_word_inserted_right()
    else:
        start_collecting()

beginText = "수집 시작"
endText = "프로그램 종료"

def back_or_end():
    global endText, stop_event
    if btnEnd.cget('text') == endText:
        root.destroy()
    else:
        stop_event.set()
        refresh()

def update_label_text(text):
    global label, root
    label.config(text=text)
    root.update()

# GUI 설정
root = tk.Tk()
root.title("TapStrap Data Collecting Program")
root.geometry("400x240+600+300")
root.resizable(False, False)

word = tk.Entry(root, font=("스물셋유진체!", 15))
word.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

btn_width = 15

btnStart = tk.Button(root, text=beginText, width=btn_width, padx=10, pady=5, command=insert_word)
btnEnd = tk.Button(root, text=endText, width=btn_width, padx=10, pady=5, command=back_or_end)

btnStart.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
btnEnd.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

label = tk.Label(root, text="수집할 단어를 입력하세요.", font=("스물셋유진체!", 15))
label.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")

doubleVar = tk.DoubleVar()
progressbar = ttk.Progressbar(root, maximum=5, variable=doubleVar)
progressbar.grid(row=10, column=0, columnspan=2, padx=10, sticky="nsew")

for i in range(2):
    root.columnconfigure(i, weight=1)
root.rowconfigure(2, minsize=100)


def on_connect(identifier, name, fw):
    if identifier not in tap_identifiers:
        tap_identifiers.append(identifier)
    tap_instance.set_input_mode(TapInputMode("raw", sensitivity=[2,1,4]), identifier)
    global isConnecting
    isConnecting = True



def on_disconnect(identifier):
    if identifier in tap_identifiers:
        tap_identifiers.remove(identifier)
    global isConnecting
    isConnecting = False
    sys.exit()

def on_raw_sensor_data(identifier, raw_sensor_data):
    global row
    if isCollecting and isConnecting:
        global tempFileGyro, tempFileAccel

        # Type에 따른 raw_sensor_data 출력

        if str(raw_sensor_data.type) =="None":
            pass
        elif str(raw_sensor_data.type) == "Device":
            row+= str(raw_sensor_data.timestamp)
            for point in raw_sensor_data.points:
                row += ","+str(point.x)
                row += ","+str(point.y)
                row += ","+str(point.z)
            tempFileAccel.write(row+"\n")
        elif str(raw_sensor_data.type) ==  "IMU":
            row += str(raw_sensor_data.timestamp)
            row += ","+str(raw_sensor_data.points[0].x)
            row += ","+str(raw_sensor_data.points[0].y)
            row += ","+str(raw_sensor_data.points[0].z)
            tempFileGyro.write(row+"\n")

        row=""
        return
    else:
        return
def wait_for_enter():
    input()  # 사용자가 엔터를 누를 때까지 기다림
def main():
    #기기 연결 대기
    global tap_instance
    tap_instance = TapSDK()
    tap_instance.register_connection_events(on_connect)
    tap_instance.register_disconnection_events(on_disconnect)
    tap_instance.register_raw_data_events(on_raw_sensor_data)

    tap_instance.run()
    tap_instance.loop = False

    global isCollecting
    isCollecting = False

    global isConnecting
    while not isConnecting:  # 변수가 True가 아닐 때까지 반복
        time.sleep(0.1)  # CPU 사용을 줄이기 위해 잠시 대기
    
    #기기 연결 완료 후 GUI 출력
    root.mainloop()
        

if __name__ == "__main__":
    main()