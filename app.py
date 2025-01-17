import flet as ft
from utils.constants import *
from utils.result_file import *
from utils.serial_ports import *
from utils.arduino_controller import *
from time import sleep


class App(ft.Container):
    def __init__(self, page: ft.Page, ports: list):
        super().__init__()
        self.page = page
        self.page.window.prevent_close = True
        self.page.window.on_event = self.on_window_close
        self.arduino = ArduinoController(self.update_pr)
        self.ports = ports

        self.file_picker = ft.FilePicker(on_result=self.on_path_result)
        self.page.overlay.append(self.file_picker)

        self.selected_path = self.page.client_storage.get(PATH_KEY)
        self.selected_port = None
        if len(self.ports) > 0:
            self.selected_port = self.ports[0]

        self.header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    on_click=self.open_config_dialog,
                ),
                ft.IconButton(
                    icon=ft.icons.HELP,
                    on_click=lambda e: self.page.open(self.helper_dialog),
                ),
            ],
        )
        self.name_tf = ft.TextField(
            width=300,
            label="Nome",
            prefix_icon=ft.icons.ASSIGNMENT_IND,
        )

        self.serial_number_tf = ft.TextField(
            width=300,
            label="Nº de Série",
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=8,
            prefix_icon=ft.icons.NUMBERS,
            error_text="",
        )
        self.run_test_btn = ft.ElevatedButton(
            disabled=True,
            icon=ft.icons.ARROW_RIGHT,
            height=30,
            text="Iniciar Teste",
            on_click=self.run_test,
        )
        self.helper_dialog = ft.AlertDialog(
            title=ft.Text("Ajuda", text_align=ft.TextAlign.CENTER),
            content=ft.Text(
                "Antes de iniciar o teste, certifique-se que a jiga esta ligada e selecionado o menu do respectivo grupo com a mensagem ”Aguardando Comando” no display LCD.",
            ),
        )
        self.default_path_tb = ft.TextButton(
            text=self.selected_path,
            width=300,
            on_click=self.file_picker.get_directory_path,
        )
        self.port_options = ft.RadioGroup(
            content=ft.Column(controls=[]),
            value=self.selected_port,
            on_change=lambda e: self.set_port,
        )

        self.configs_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Configurações", text_align=ft.TextAlign.CENTER),
            content=ft.Column(
                [
                    ft.Text("Diretório Padrão:"),
                    self.default_path_tb,
                    ft.Text("Porta Serial:"),
                    self.port_options,
                ]
            ),
            actions=[
                ft.TextButton(
                    text="Cancelar",
                    on_click=lambda e: self.page.close(self.configs_dialog),
                ),
                ft.TextButton(
                    text="Salvar", on_click=lambda _: self.save_default_path_config()
                ),
            ],
        )
        self.snack_bar = ft.SnackBar(content=ft.Text(value="SELECIONE O TESTE"))
        self.test_pr = ft.ProgressRing(value=0)
        # LAYOUT
        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.header,
                self.name_tf,
                self.serial_number_tf,
                self.run_test_btn,
                self.test_pr,
            ],
        )

    def did_mount(self):
        self.page.window.center()
        if self.selected_port is not None:
            self.run_test_btn.disabled = not self.arduino.connect_arduino(
                self.selected_port
            )
            self.run_test_btn.update()
        self.update_serial_number()

    def run_test(self, e):
        if self.name_tf.value == "":
            self.name_tf.error_text = "Campo Obrigatório"
            self.name_tf.update()
            return
        else:
            self.name_tf.error_text = ""
            self.name_tf.update()

        serial_number = self.serial_number_tf.value.zfill(8)
        self.serial_number_tf.value = serial_number
        self.serial_number_tf.update()

        if self.arduino.start_test_ok():
            self.arduino.test_running = True
            self.run_test_btn.disabled = self.arduino.test_running
            self.run_test_btn.update()

            test_data = self.arduino.read_data()
            if len(test_data) > 19:
                generate_test_file(
                    self.selected_path,
                    self.serial_number_tf.value,
                    self.name_tf.value,
                    test_data,
                )
                self.update_serial_number()
                self.page.update()

            self.run_test_btn.disabled = self.arduino.test_running
            self.run_test_btn.update()

        else:
            self.page.snack_bar = self.snack_bar
            self.page.snack_bar.open = True
            self.page.update()

    def update_serial_number(self):
        self.serial_number_tf.value = str(
            check_latest_test_file(self.selected_path) + 1
        ).zfill(8)
        self.serial_number_tf.update()

    def on_path_result(self, e: ft.FilePickerResultEvent):
        if e.path is not None:
            self.default_path_tb.text = e.path
            self.default_path_tb.update()
            self.selected_path = e.path

    def set_port(self, e):
        self.selected_port = e.control.value
        self.arduino.connect_arduino(port=self.selected_port)
        self.port_options.update()

    def save_default_path_config(self):
        self.page.client_storage.set(PATH_KEY, self.selected_path)
        self.page.close(self.configs_dialog)

    def open_config_dialog(self, e):
        self.page.open(self.configs_dialog)
        self.check_ports()

    def check_ports(self):
        self.ports.clear()
        self.port_options.content.controls.clear()
        self.ports = get_ports()
        for port in self.ports:
            self.port_options.content.controls.append(ft.Radio(value=port, label=port))
        self.port_options.update()

    def update_pr(self, value):
        self.test_pr.value = (5 * value) * 0.01
        self.test_pr.update()

    def on_window_close(self, e):
        if e.data == "close":
            self.arduino.test_running = False
            self.arduino.close_connection()
            self.page.window.destroy()
