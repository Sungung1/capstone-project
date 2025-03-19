import matplotlib.pyplot as plt
import pandas as pd
import os

folder_path = os.path.join(os.getcwd(), "WordData")+"/"
gyro_file_path = folder_path+"좋아하다_accel1"
accel_file_path = folder_path+"좋아하다_gyro1"

gyro_data = pd.read_csv(gyro_file_path)
accel_data = pd.read_csv(accel_file_path)



# 자이로센서 데이터 시각화 (각속도)
plt.figure(figsize=(12, 6))
plt.plot(gyro_data.iloc[:, 0], gyro_data.iloc[:, 1], label='Gyro X')
plt.plot(gyro_data.iloc[:, 0], gyro_data.iloc[:, 2], label='Gyro Y')
plt.plot(gyro_data.iloc[:, 0], gyro_data.iloc[:, 3], label='Gyro Z')
plt.title('Gyroscope Data (Angular Velocity)')
plt.xlabel('Timestamp')
plt.ylabel('Angular Velocity')
plt.legend()
plt.grid(True)
#plt.show()

# 가속도계 데이터 시각화 (각 손가락 X축 값)
plt.figure(figsize=(12, 6))
for i in range(1, 16, 3):  # 손가락마다 X축 값을 플로팅
    plt.plot(accel_data.iloc[:, 0], accel_data.iloc[:, i], label=f'Finger {i//3 + 1} X')
plt.title('Accelerometer Data (X-Axis for Each Finger)')
plt.xlabel('Timestamp')
plt.ylabel('Acceleration (X-axis)')
plt.legend()
plt.grid(True)
plt.show()


# 가속도계 데이터 시각화 (각 손가락 Y축 값)
plt.figure(figsize=(12, 6))
for i in range(2, 17, 3):
    plt.plot(accel_data.iloc[:, 0], accel_data.iloc[:, i], label=f'Finger {i//3 + 1} Y')
plt.title('Accelerometer Data (Y-Axis for Each Finger)')
plt.xlabel('Timestamp')
plt.ylabel('Acceleration (Y-axis)')
plt.legend()
plt.grid(True)
plt.show()

# 가속도계 데이터 시각화 (각 손가락 Z축 값)
plt.figure(figsize=(12, 6))
for i in range(3, 18, 3):
    plt.plot(accel_data.iloc[:, 0], accel_data.iloc[:, i], label=f'Finger {i//3 + 1} Z')
plt.title('Accelerometer Data (Z-Axis for Each Finger)')
plt.xlabel('Timestamp')
plt.ylabel('Acceleration (Z-axis)')
plt.legend()
plt.grid(True)
plt.show()