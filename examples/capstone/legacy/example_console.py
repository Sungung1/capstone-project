from tapsdk import TapSDK, TapInputMode
from tapsdk.models import AirGestures
import time, os, sys, threading

tap_instance = []
tap_identifiers = []
isCollecting = False
isConnecting = False
isWordInserted = False
tempFileGyro = None
tempFileAccel = None

def on_connect(identifier, name, fw):
    #print(identifier + " Tap: " + str(name), " FW Version: ", fw)
    if identifier not in tap_identifiers:
        tap_identifiers.append(identifier)
    #print("Connected taps:")
    #for identifier in tap_identifiers:
    #    print(identifier)
    tap_instance.set_input_mode(TapInputMode("raw", sensitivity=[2,1,4]), identifier)
    global isConnecting
    isConnecting = True



def on_disconnect(identifier):
    #print("Tap has disconnected")
    if identifier in tap_identifiers:
        tap_identifiers.remove(identifier)
    #for identifier in tap_identifiers:
    #    print(identifier)
    global isConnecting
    isConnecting = False
    #print("장치의 연결이 끊겼습니다.")
    sys.exit()


def on_mouse_event(identifier, dx, dy, isMouse):
    if isMouse:
        print(str(dx), str(dy))
    else:
        pass
        # print("Air: ", str(dx), str(dy))


def on_tap_event(identifier, tapcode):
    #print(identifier, str(tapcode))
    if int(tapcode) == 17:
        sequence = [500, 200, 500, 500, 500, 200]
        tap_instance.send_vibration_sequence(sequence, identifier)


def on_air_gesture_event(identifier, air_gesture):
    #print(" Air gesture: ", AirGestures(int(air_gesture)).name)
    if air_gesture == AirGestures.UP_ONE_FINGER.value:
        tap_instance.set_input_mode(TapInputMode("raw"), identifier)
    if air_gesture == AirGestures.DOWN_ONE_FINGER.value:
        tap_instance.set_input_mode(TapInputMode("text"), identifier)
    if air_gesture == AirGestures.LEFT_ONE_FINGER.value:
        tap_instance.set_input_mode(TapInputMode("controller"), identifier)


def on_air_gesture_state_event(identifier: str, air_gesture_state: bool):
    if air_gesture_state:
        print("Entered air mouse mode")
    else:
        print("Left air mouse mode")

row = "" # timestamp, gyro (총 4개) || timestamp, 엄지 x y z ~ 새끼 x y z (총 16개)

#
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

stopCollecting = False
def wait_for_enter():
    global isWordInserted, stopCollecting
    input()  # 사용자가 엔터를 누를 때까지 기다림
    isWordInserted = False
    stopCollecting = True
def main():
    global tap_instance
    global isWordInserted
    tap_instance = TapSDK()
    tap_instance.register_connection_events(on_connect)
    tap_instance.register_disconnection_events(on_disconnect)
    tap_instance.register_raw_data_events(on_raw_sensor_data)

    tap_instance.run()
    tap_instance.loop = False

    isWordInserted = False
    insertedWord = None
    insertedCount = 5
    global isCollecting, stopCollecting #stopCollecting = enter 입력 들어오는 거 감지
    isCollecting = False

    global isConnecting
    while not isConnecting:  # 변수가 True가 아닐 때까지 반복
        time.sleep(0.1)  # CPU 사용을 줄이기 위해 잠시 대기

    # 데이터 수신을 위한 루프 실행
    while True:
        if isWordInserted:
            if (insertedCount > 0):
                print("5초 후 다시 수집합니다. 수집을 멈추려면 enter를 눌러주세요.")
                #이 이후의 5초 안에 입력이 들어오면 continue 

                # 사용자 입력을 기다리는 스레드를 생성
                input_thread = threading.Thread(target=wait_for_enter)
                input_thread.start()

                # 5초 대기 (사용자가 입력을 기다리는 동안)
                for i in range(5):
                    if stopCollecting:
                        break  # 입력이 들어오면 루프를 종료하고 continue로 넘어감
                    print(f"남은 시간: {5 - i}초")
                    time.sleep(1)

                if stopCollecting:
                    print("끝났습니다")
                    stopCollecting = False
                    insertedCount = 5
                    continue
            else :
                isWordInserted = False
                continue


                #insertedWord = input(insertedWord + "의 데이터를 수집하려면 y를, 아니면 n을 입력해주세요.")
            #if insertedWord == "y":
            #    isWordInserted = True
            #elif insertedWord == "n":
            #    isWordInserted = False
            #    continue
            #else:
            #    print("잘못 입력하셨습니다.")
            #    continue
        else:
            insertedWord = input("데이터를 수집할 단어를 입력하세요. 종료를 원하시면 q를 입력해주세요.")
            if insertedWord == "q":
                sys.exit()
            insertedWord = insertedWord
            insertedWord = input(f"데이터를 수집할 단어가 {len(insertedWord)} 길이의 {insertedWord}가 맞으면 y를 아니면 n을 입력해주세요.")
            if insertedWord == "y":
                isWordInserted = True
            elif insertedWord == "n":
                isWordInserted = False
                continue
            else:
                print("잘못 입력하셨습니다.")
                continue

        #카운트 다운
        count = 3
        print(f"{insertedWord}의 데이터를 {count}초 후 수집합니다.")

        for i in range(count, 0, -1):
            print(f"남은 시간: {i}초")
            time.sleep(1)  # 1초 대기

        print("데이터 수집 시작")

        folderName = "WordData"
        folderPath = os.path.join(os.getcwd(), folderName)
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        global tempFileGyro, tempFileAccel
        tempFileGyro = open(folderPath + "/TempGyro", 'w+')#Temp 파일 만들기(있으면 내용 비우고 새로)
        tempFileAccel = open(folderPath + "/TempAccel", 'w+')#Temp 파일 만들기(있으면 내용 비우고 새로)

        isCollecting = True
        tap_instance.loop = True
        print("삐 --------------------------------------------") #데이터 수집 시작 알림음
        #        input("데이터 수집을 종료하려면 엔터키를 눌러주세요.")
        time.sleep(3) #3초간 데이터 수집
        print("삐 --------------------------------------------") #데이터 수집 끝 알림음
        #이번이 몇 번째 데이터인지 - i 찾기
        i = 1
        file_path = folderPath + "/" + insertedWord
        while (True) :
            temp_file_path_gyro = file_path+"_gyro" + str(i)
            temp_file_path_accel = file_path+"_accel" + str(i)
            if not os.path.exists(temp_file_path_gyro) and not os.path.exists(temp_file_path_accel):
                break
            i+=1

        #자이로
        tempFileGyro.seek(0) #내용을 옮기기 위해 읽는 지점을 파일의 처음으로
        file_gyro = open(file_path+"_gyro"+str(i), 'w') #insertedWord 파일 추가모드로 열기

        file_gyro.write(tempFileGyro.read())  #insertedWord+Temp 파일 내용을 insertedWord 파일에 붙이기

        file_gyro.close()   #insertedWord 파일 닫기
        tempFileGyro.close()  #insertedWord+Temp 파일 닫기


        #5손가락 가속도계
        tempFileAccel.seek(0) #내용을 옮기기 위해 읽는 지점을 파일의 처음으로
        file_accel = open(file_path+"_accel"+str(i), 'w') #insertedWord 파일 추가모드로 열기
        file_accel.write(tempFileAccel.read())  #insertedWord+Temp 파일 내용을 insertedWord 파일에 붙이기

        file_accel.close()   #insertedWord 파일 닫기
        tempFileAccel.close()  #insertedWord+Temp 파일 닫기

        tap_instance.loop = False
        isCollecting = False
        insertedCount-=1

if __name__ == "__main__":
    main()

#tap_instance.register_mouse_events(on_mouse_event)
#tap_instance.register_tap_events(on_tap_event)
#tap_instance.register_air_gesture_events(on_air_gesture_event)
#tap_instance.register_air_gesture_state_events(on_air_gesture_state_event)
#tap_instance.set_input_mode(TapInputMode("raw"))

#tap_instance.
# whenever new raw data sample is being made <-> whenever a tap event has occured
# register_raw_data_events -> Resgister callback to raw sensors data packet received event.
# continuously sends raw data from the following sensors