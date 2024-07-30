import serial
import time


class ArduinoController:
    def __init__(self, update_pr):
        self.arduino = None
        self.test_running = False
        self.update_pr = update_pr

    def connect_arduino(self, port=None) -> bool:
        if self.arduino is not None:
            self.arduino.close()
        try:
            self.arduino = serial.Serial(port, baudrate=9600, timeout=1)
            return True
        except:
            return False

    def start_test_ok(self):
        response = ""
        self.arduino.write(b"S")
        response = self.arduino.readline().decode().strip()
        time.sleep(1)
        return response == "OK"

    def read_data(self) -> list:
        self.update_pr(0)
        test_data = []
        while self.test_running:
            self.arduino.timeout = None
            try:
                response_data = self.arduino.readline().decode().strip()
            except:
                break
            if response_data == "Erro no teste - Reiniciar":
                self.test_running = False
                test_data.clear()
                break
            else:
                test_data.append(response_data)
                self.update_pr(len(test_data))
            if len(test_data) > 19:
                self.test_running = False
                return test_data
        return []

    def close_connection(self):
        if self.arduino is not None:
            self.arduino.cancel_read()
            self.arduino.close()
            self.arduino = None
