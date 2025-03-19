import threading
import sys
import time

# 트레이스 콜백 함수 정의
def trace_callback(frame, event, arg):
    if event == "line":
        lineno = frame.f_lineno
        print(f"Thread {threading.current_thread().name} is executing line {lineno}")
    return trace_callback

def worker():
    print("Worker 시작")
    time.sleep(1)
    print("Worker 종료")

# 각 스레드에서 트레이스를 설정하는 함수
def threaded_trace(func):
    sys.settrace(trace_callback)  # 각 스레드에 트레이스를 설정
    func()

# 스레드 생성
t1 = threading.Thread(target=threaded_trace, args=(worker,), name='Thread-1')
t2 = threading.Thread(target=threaded_trace, args=(worker,), name='Thread-2')

# 스레드 시작
t1.start()
t2.start()

# 스레드가 끝날 때까지 대기
t1.join()
t2.join()

print("모든 스레드가 종료되었습니다.")