import time, threading, pygame
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass, field
from typing import Final
from tapsdk import TapSDK, TapInputMode
import time, os, sys, threading


def main():
    
    audio_manager = AudioManager() # 효과음 초기화
    audio_manager.play_music(AudioManager.COUNTING)
    
    guiManager = GUIManager(audio_manager)
    #GUI에 들어갈 애들 초기화
   

    #연결 확인까지 GUI에서 프로그래스 링 돌며 대기 시키기
    #connected 변수 체크하며 대기
    #커넥트 끊기면 바로 종료하는 로직도 달기
    
    
    
    #시작 화면
    
    #버튼 시작 버튼 클릭 기다림
    #입력값 평가 입력값이 정상이면 밑으로 넘어감
    
    
    #데이터 수집 영역 
    #카운트 3 2 1
    #시작 3초동안 데이터 수집함 중간에 종료버튼 받아들이는 함수 만들어주기
    #->수집중 
    #수집완료
    #<-저장
    #종료 
    
    #시작화면으로 넘어감
    guiManager.show()
    
@dataclass
class AudioManager:
    """Class for beep sounds"""
    #정적 상수
    COUNTING: Final[bool] = field(default=True, init=False) # 변하지 않는 값
    START: Final[bool] = field(default=False, init=False) # 변하지 않는 값

    def __init__(self, counting_beep_path: str= "effectSounds/beep3.wav", start_beep_path: str="effectSounds/beep_last.wav"):
        pygame.mixer.init()  # pygame.mixer 초기화
        self.counting_beep_path = counting_beep_path
        self.start_beep_path = start_beep_path

    def play_music(self, is_counting_sound: bool) -> None: 
        if is_counting_sound:
            pygame.mixer.music.load(self.counting_beep_path)
        else:
            pygame.mixer.music.load(self.start_beep_path)
        pygame.mixer.music.play()

@dataclass
class GUIManager:
    """Class for GUI"""
    root = tk.Tk()

    def __init__(self, audio_manager: AudioManager):
        self.audio_manager = audio_manager

        # 버튼 생성 및 콜백으로 메서드 연결 (self.insert_word)
        #self.btnStart = tk.Button(self.root, text="가보자고", width=15, padx=10, pady=5, command=self.insert_word)
        #self.btnStart.pack()

    #def beep(self):
        #audio_manager.play_music(AudioManager.COUNTING)

    #def insert_word(self):
    #    # insert_word 호출 시 beep 실행
    #    self.beep()

    def show(self) -> None :
        # Tkinter 메인 루프 시작
        self.root.mainloop()

    
if __name__ == "__main__":
    main()