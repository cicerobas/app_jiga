import serial
import time


class ArduinoController:
    def __init__(self, port):
        self.arduino = None
        self.port = port
        self.is_testing = False
        
    def check_arduino_connection(self) -> bool:
        print("Conectando...")
        time.sleep(1)
        try:
            self.arduino = serial.Serial(self.port, baudrate=9600, timeout=1)
            print(f"Conectado em {self.port}")
            return True
        except:
            return False

    def start_test(self):
        response = ""
        self.arduino.write(b"S")
        response = self.arduino.readline().decode().strip()
        time.sleep(1)
        return response == "OK"

    def read_data(self) -> list:
        test_data = []
        while self.is_testing:
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
