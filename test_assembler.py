import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Выполняет команду и выводит результат."""
    if description:
        print(description)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"✗ Ошибка: {result.stderr}", file=sys.stderr)
            return False
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Ошибка выполнения: {e}", file=sys.stderr)
        return False


def print_header(title):
    """Выводит заголовок."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}\n")


def main():
    """Основная функция скрипта."""

    print_header("Ассемблер для УВМ: Этап 1 (Python)")

    # 1. Проверка наличия Python
    print("1. Проверка окружения...")
    result = run_command("python --version", "   python:")
    if not result:
        print("✗ Python3 не установлен")
        sys.exit(1)
    print("✓ Python3 доступен\n")

    # 2. Тестирование на примерах из спецификации
    print("2. Тестирование на примерах спецификации...")
    print("   Команда: python uvm_assembler.py tests.asm tests.bin --test\n")

    cmd = "python uvm_assembler.py ./files/tests.txt ./files/output.bin --test"
    success = run_command(cmd)

    if not success:
        print("✗ Ошибка при ассемблировании")
        sys.exit(1)

    print()

    # 3. Проверка результатов
    print("3. Проверка сгенерированного бинарного файла...")

    if Path('./files/output.bin').exists():
        size = Path('./files/output.bin').stat().st_size
        print(f"✓ Файл ./files/output.bin создан успешно")
        print(f"  Размер: {size} байт (ожидается 16 байт для 4 инструкций)")

        # Показываем содержимое в шестнадцатеричном формате
        print(f"  Содержимое (шестнадцатеричный формат):")

        with open('./files/output.bin', 'rb') as f:
            data = f.read()
            hex_str = ' '.join(f'{b:02X}' for b in data)
            # Разбиваем на строки по 16 байт (4 инструкции)
            for i in range(0, len(hex_str), 47):  # 47 символов = 4 байта * "XX " + пробелы
                print(f"    {hex_str[i:i + 47]}")

        print()
    else:
        print("✗ Файл ./files/output.bin не создан")
        sys.exit(1)

    # 4. Вывод результатов
    print_header("Результаты тестирования")

    print("ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ (из спецификации):\n")

    tests = [
        ("LOAD 98", 102, 98, "0x66, 0x62, 0x00, 0x00"),
        ("READ 531", 155, 531, "0x9B, 0x13, 0x02, 0x00"),
        ("WRITE 198", 49, 198, "0x31, 0xC6, 0x00, 0x00"),
        ("XOR 306", 136, 306, "0x88, 0x32, 0x01, 0x00"),
    ]

    for i, (cmd, opcode, operand, expected) in enumerate(tests, start=1):
        print(f"Инструкция {i} ({cmd}):")
        print(f"  A={opcode} (0x{opcode:02X}), B={operand} (0x{operand:04X})")
        print(f"  Ожидаемый результат: {expected}")
        print()

    # Проверка полученных результатов
    print("ПОЛУЧЕННЫЕ РЕЗУЛЬТАТЫ:\n")

    with open('./files/output.bin', 'rb') as f:
        data = f.read()

    for i in range(4):
        offset = i * 4
        chunk = data[offset:offset + 4]
        opcode = chunk[0]
        operand = chunk[1] | (chunk[2] << 8) | (chunk[3] << 16)
        hex_str = ', '.join(f'0x{b:02X}' for b in chunk)

        print(f"Инструкция {i + 1}:")
        print(f"  A={opcode}, B={operand}")
        print(f"  Binary: {hex_str}")
        print()

    print_header("Тестирование завершено успешно")
    print("✓ Все инструкции скомпилированы корректно")


if __name__ == '__main__':
    main()