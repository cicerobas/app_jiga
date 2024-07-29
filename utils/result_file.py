import os
import datetime


def check_latest_test_file(path) -> int:
    number = 0
    for file in os.listdir(path):
        if file.endswith(".txt"):
            if int(file.split(".")[0]) > number:
                number = int(file.split(".")[0])

    return number


def generate_test_file(path, serial_number, name, test_data):
    filename = os.path.join(f"{path}/{serial_number}.txt")
    with open(filename, "w") as file:
        file.write(f"|" + "=" * 88 + "|\n")
        file.write(
            f"| Fornecedor: CEBRA - Conversores Estáticos Brasileiros Ltda.                            |\n"
        )
        file.write(
            f"| Cliente: Intelbras                                                                     |\n"
        )
        file.write(
            f"| Grupo: G01158 - SCA2201J                                                               |\n"
        )
        file.write(f"| Operador: {name+ " " * (77 - len(name))}|\n")
        file.write(f"| Número de série: {serial_number}" + " " * 62 + "|\n")
        file.write(
            f"| Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            + " " * 62
            + "|\n"
        )
        file.write(
            f"|________________________________________________________________________________________|\n"
        )
        file.write(
            f"|     Entrada      |             Etapa             | Limites |    Medido     | Resultado |\n"
        )
        file.write(
            f"|__________________|_______________________________|_________|_______________|___________|\n"
        )
        for data in test_data:
            file.write(f"{data}\n")
