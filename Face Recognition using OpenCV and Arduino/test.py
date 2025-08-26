import serial
import time

# Replace 'COM3' with your Arduino port (e.g., '/dev/ttyACM0' on Linux)
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=.1)

def send_command(cmd):
    arduino.write(cmd.encode())
    time.sleep(0.1)

print("Buzzer Control")
print("Press 1 to turn ON the buzzer, 0 to turn it OFF, or q to quit.")

while True:
    user_input = input("Enter command (1/0/q): ")
    if user_input == '1':
        send_command('1')
    elif user_input == '0':
        send_command('0')
    elif user_input.lower() == 'q':
        print("Exiting...")
        break
    else:
        print("Invalid input. Use 1, 0, or q.")
