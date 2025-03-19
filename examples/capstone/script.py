import time, threading, pygame, os, sys
import tkinter as tk
from tkinter import ttk

from pycparser.c_ast import Continue

from tapsdk import TapSDK, TapInputMode

# 전역 변수
tap_instances = {} # 여러 Tap 장치를 저장하는 딕셔너리 (오른손, 왼손 구분)
tap_instance_left = None
tap_instance_right = None

tap_identifiers = {"left": None, "right": None}  # 기기 ID를 오른손, 왼손으로 구분하여 저장

# 손별 데이터 파일 관리
tempFilesGyro = {"left": None, "right": None}
tempFilesAccel = {"left": None, "right": None}

isCollecting = False
isConnecting = False
row = ""
insertedWord = ""
insertedCount = 0
folderPath = ""
stop_event = threading.Event()

# pygame 초기화
pygame.mixer.init()

def play_short_beep_sound():
    # 현재 스크립트 위치를 기준으로 파일 경로 설정
    base_path = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트 위치
    sound_path = os.path.join(base_path, "effectSounds", "beep3.wav")

    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()

def play_long_beep_sound():
     # 현재 스크립트 위치를 기준으로 파일 경로 설정
    base_path = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트 위치
    sound_path = os.path.join(base_path, "effectSounds", "beep_last.wav")
    pygame.mixer.music.load(sound_path)
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
        
        update_label_text(i)
        if i>1 :
            play_short_beep_sound()
        else :
            play_long_beep_sound()
        time.sleep(1)


def collecting_data():
    #데이터 수집을 시작하는 함수입니다.
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
    for hand in ["left", "right"]:
        if tap_identifiers[hand] is not None:
            save_data_for_hand(hand)

    for hand in tap_instances:
        tap_instances[hand].loop = False  # 각 손의 Tap 인스턴스 루프를 중지
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
    #반복적으로 데이터 수집을 제어하는 함수입니다.
    global insertedCount, insertedWord, stop_event, isCollecting, folderPath
    while insertedCount < 5 and not stop_event.is_set():
        print("insertedCount : "+str(insertedCount))
        update_label_text(f"{insertedWord} 단어 수집을 시작합니다\n준비 자세를 취해 주세요.\n화면에 \"(수집 중)\"이라고 뜨면 움직이세요.")
        counting3()
        if stop_event.is_set():
            break

        # 저장 경로 지정
        folderName = "WordData"
        folderPath = os.path.join(__file__, "..", folderName)
        folderPath = os.path.abspath(folderPath)  # 절대 경로로 변환 C:\Users\sehwa\WordData
        print(f"✅ 저장 경로 : {folderPath}")

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        # 임시 파일을 직접 초기화
        global tempFileGyro, tempFileAccel
        tempFilesGyro["left"] = open(os.path.join(folderPath, "TempGyro_left"), 'w+')
        tempFilesGyro["right"] = open(os.path.join(folderPath, "TempGyro_right"), 'w+')
        tempFilesAccel["left"] = open(os.path.join(folderPath, "TempAccel_left"), 'w+')
        tempFilesAccel["right"] = open(os.path.join(folderPath, "TempAccel_right"), 'w+')

        isCollecting = True  # 수집 시작
        collecting_data()  # 데이터를 수집하는 함수 호출
        if stop_event.is_set():
            break
        else:
            saving()  # 수집된 데이터 저장

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
    
    #Tap 기기가 연결되었을 때 호출되는 함수입니다.
    
    print(f"Device connected: {name} (ID: {identifier})")

    if identifier == "BluetoothLE#BluetoothLEb4:8c:9d:31:e8:2c-d2:6d:e8:4d:1a:8e" :
        tap_identifiers["left"] = identifier
        hand = "left"
    else :
        tap_identifiers["right"] = identifier
        hand = "right"
    
    # raw 모드로 입력 설정
    try :
        tap_instances[hand].set_input_mode(TapInputMode("raw", sensitivity=[2, 1, 4]), identifier)
        print(f"{hand.capitalize()} hand device is now in raw input mode.")
    except Exception as e:
        print(f"An error occurred while setting input mode: {str(e)}")
        
    if  tap_identifiers["left"] is not None and tap_identifiers["right"] is not None:
        global isConnecting
        isConnecting = True
        print("오른 손 : "+str(tap_identifiers["right"]))
        print("왼 손 : "+str(tap_identifiers["left"]))
        
        print("양손 기기 모두 연결 완료되었습니다. 데이터 수집 프로그램을 시작합니다.")
def on_disconnect(identifier):
    hand = "left" if identifier == tap_identifiers["left"] else "right"
    if hand:
        print(f"{hand.capitalize()} hand device disconnected.")
        tap_identifiers[hand] = None
        del tap_instances[hand]  # 연결이 끊긴 기기를 tap_instances에서 제거

    global isConnecting
    isConnecting = False
    sys.exit()

def on_raw_sensor_data(identifier, raw_sensor_data):
    """Tap 기기의 원시 센서 데이터를 처리하여 오른손, 왼손으로 분류합니다."""
    global row
    
    hand = "left" if identifier == tap_identifiers["left"] else "right" if identifier == tap_identifiers["right"] else None
    if hand and isCollecting and isConnecting:
        # print("identifier : "+identifier)
        global tempFilesGyro, tempFilesAccel
        # 디버그: 현재 데이터를 받고 있는 손과 데이터 타입 출력
        # Type에 따른 raw_sensor_data 출력
        if str(raw_sensor_data.type) == "None":
            pass
        elif str(raw_sensor_data.type) == "Device":
            row = f"{raw_sensor_data.timestamp}"
            for point in raw_sensor_data.points:
                row += f",{point.x},{point.y},{point.z}"
            tempFilesAccel[hand].write(row + "\n")
        elif str(raw_sensor_data.type) == "IMU":
            row = f"{raw_sensor_data.timestamp},{raw_sensor_data.points[0].x},{raw_sensor_data.points[0].y},{raw_sensor_data.points[0].z}"
            tempFilesGyro[hand].write(row + "\n")

        row = ""

def is_temp_file_empty(hand) :
    tempFilesGyro[hand].seek(0)  # 파일 포인터를 맨 앞으로 이동
    gyro_content = tempFilesGyro[hand].read().strip()  # 파일 내용 읽고 앞뒤 공백 제거

    tempFilesAccel[hand].seek(0)  # 파일 포인터를 맨 앞으로 이동
    accel_content = tempFilesAccel[hand].read().strip()  # 파일 내용 읽고 앞뒤 공백 제거

    return not bool(gyro_content) and not bool(accel_content) #내용이 없으면 True, 있으면 False
        

def save_data_for_hand(hand):

    #기기 연결 등 문제로 tempFilesGyro[hand], tempFilesAccel[hand]가 비었으면 저장하지 않고 프로그램을 종료합니다. 
    if is_temp_file_empty(hand):
        print("⚠️ temp 파일이 비어서 프로그램을 종료합니다. 기기 연결을 확인해주세요.")
        back_or_end()

    # 현재 수집한 단어의 저장될 파일 이름을 지정합니다. 
    # 1부터 차례로 저장됩니다. 
    global folderPath, insertedWord
    file_path = folderPath + "/" + insertedWord
    i = 1
    while True:
        temp_file_path_gyro = f"{file_path}_{hand}_gyro{i}"
        temp_file_path_accel = f"{file_path}_{hand}_accel{i}"
        if not os.path.exists(temp_file_path_gyro) and not os.path.exists(temp_file_path_accel):
            break
        i += 1
    
    #양 손의 자이로 센서 데이터를 저장합니다
    tempFilesGyro[hand].seek(0)
    with open(temp_file_path_gyro, 'w') as file_gyro:
        file_gyro.write(tempFilesGyro[hand].read())
    tempFilesGyro[hand].close()

    #가속도계 저장
    tempFilesAccel[hand].seek(0)
    with open(temp_file_path_accel, 'w') as file_accel:
        file_accel.write(tempFilesAccel[hand].read())
    tempFilesAccel[hand].close()

def main():
    global tap_instance_left, tap_instance_right
    #기기 연결 대기
    #왼손
    tap_instance_left = TapSDK()
    tap_instances["left"] = tap_instance_left
    tap_instance_left.register_connection_events(on_connect)
    tap_instance_left.register_disconnection_events(on_disconnect)
    tap_instance_left.register_raw_data_events(on_raw_sensor_data)

    tap_instance_left.run()
    tap_instance_left.loop = False
    
    #오른 손
    tap_instance_right = TapSDK()
    tap_instances["right"] = tap_instance_right
    tap_instance_right.register_connection_events(on_connect)
    tap_instance_right.register_disconnection_events(on_disconnect)
    tap_instance_right.register_raw_data_events(on_raw_sensor_data)

    tap_instance_right.run()
    tap_instance_right.loop = False
    

    global isCollecting
    isCollecting = False

    global isConnecting
    # print("while 들어감")
    while not isConnecting:  # 변수가 True가 아닐 때까지 반복
        time.sleep(0.1)  # CPU 사용을 줄이기 위해 잠시 대기
        

    #기기 연결 완료 후 GUI 출력
    # print("while 탈출")
    # print("while 탈출cncf")
    root.mainloop()


if __name__ == "__main__":
    main()