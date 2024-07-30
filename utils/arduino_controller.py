import serial
import time


class ArduinoController:
    def __init__(self):
        self.arduino = None
        
    def connect_arduino(self, port=None) -> bool:
        if self.arduino is not None:
            self.arduino.close()
            print('Connection closed')
        try:
            self.arduino = serial.Serial(port, baudrate=9600, timeout=1)
            print('Connection successful')
            return True
        except:
            print('Connection error')
            return False

    def start_test_ok(self):
        response = ""
        self.arduino.write(b"S")
        response = self.arduino.readline().decode().strip()
        time.sleep(1)
        return response == "OK"

    def read_data(self) -> list:
        test_data = []
        while True:
            self.arduino.timeout = None
            response_data = self.arduino.readline().decode().strip()
            if response_data == "Erro no teste - Reiniciar":
                test_data.clear()
                break
            else:
                test_data.append(response_data)
            if len(test_data) > 19:
                return test_data
        return []

    def close_connection(self):
        print("CLOSING...")
        if self.arduino is not None:
            self.arduino.close()
            self.arduino = None