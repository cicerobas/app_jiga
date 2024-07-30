import flet as ft

from app import App
from utils.serial_ports import *
from utils.constants import *
from utils.arduino_controller import *


def main(page: ft.Page):
    page.window.height = 400
    page.window.width = 400
    page.window.max_height = 450
    page.window.max_width = 450
    page.window.min_height = 350
    page.window.min_width = 350

    page.add(App(page=page, ports=get_ports()))


ft.app(main)
