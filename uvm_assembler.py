import sys
import struct
from pathlib import Path
from typing import List, Tuple, Optional


class Instruction:

    OPCODE_LOAD = 102  # 0x66
    OPCODE_READ = 155  # 0x9B
    OPCODE_WRITE = 49  # 0x31
    OPCODE_XOR = 136  # 0x88

    def __init__(self, opcode: int, operand: int):
        self.opcode = opcode
        self.operand = operand

    def encode(self) -> bytes:
        # Байт 0: опкод
        byte0 = self.opcode & 0xFF
        # Байты 1-3: операнд в little-endian
        byte1 = (self.operand >> 0) & 0xFF
        byte2 = (self.operand >> 8) & 0xFF
        byte3 = (self.operand >> 16) & 0xFF

        return bytes([byte0, byte1, byte2, byte3])

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"Instruction(opcode={self.opcode}, operand={self.operand})"


class AssemblyException(Exception):
    pass


class UVMAssembler:
    MNEMONICS = {
        'LOAD': Instruction.OPCODE_LOAD,
        'READ': Instruction.OPCODE_READ,
        'WRITE': Instruction.OPCODE_WRITE,
        'XOR': Instruction.OPCODE_XOR,
    }

    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.instructions: List[Instruction] = []

    def assemble(self, input_file: str, output_file: str) -> None:
        # Этап 1: Чтение исходного файла
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {input_file}")

        # Этап 2: Парсинг и трансляция
        self._parse_assembly(lines)

        # Этап 3: Вывод внутреннего представления (если режим тестирования)
        if self.test_mode:
            self._print_internal_representation()

        # Этап 4: Генерация бинарного файла
        self._write_binary_file(output_file)

    def _parse_assembly(self, lines: List[str]) -> None:
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()

            if not line:
                continue

            tokens = line.split()
            if not tokens:
                continue

            mnemonic = tokens[0].upper()

            try:
                instr = self._parse_instruction(mnemonic, tokens, line_num)
                self.instructions.append(instr)
            except AssemblyException as e:
                raise AssemblyException(f"Line {line_num}: {str(e)}")

    def _parse_instruction(self, mnemonic: str, tokens: List[str],
                           line_num: int) -> Instruction:
        # Проверка количества аргументов
        if len(tokens) < 2:
            raise AssemblyException(f"Команда '{mnemonic}' требует операнда")

        # Парсим операнд
        try:
            operand = self._parse_operand(tokens[1])
        except ValueError as e:
            raise AssemblyException(f"Неверный формат операнда: {tokens[1]}")

        # Валидируем диапазон (биты 8-30, т.е. макс. 2^23 - 1 = 8388607)
        if not (0 <= operand <= 0x7FFFFF):
            raise AssemblyException(f"Операнд вне диапазона: {operand}")

        # Получаем опкод
        if mnemonic not in self.MNEMONICS:
            raise AssemblyException(f"Неизвестная команда: {mnemonic}")

        opcode = self.MNEMONICS[mnemonic]
        return Instruction(opcode, operand)

    def _parse_operand(self, operand_str: str) -> int:
        operand_str = operand_str.strip()

        # Удаляем запятую если она есть (для совместимости)
        if operand_str.endswith(','):
            operand_str = operand_str[:-1]

        # Поддерживаем шестнадцатеричные числа (0x...)
        if operand_str.lower().startswith('0x'):
            return int(operand_str, 16)

        # Десятичное число
        return int(operand_str, 10)

    def _print_internal_representation(self) -> None:
        print("\n=== ВНУТРЕННЕЕ ПРЕДСТАВЛЕНИЕ ===\n")

        for i, instr in enumerate(self.instructions, start=1):
            encoded = instr.encode()

            print(f"Instruction {i}:")
            print(f"  Opcode (A): {instr.opcode}")
            print(f"  Operand (B): {instr.operand}")
            print(f"  Binary: {', '.join(f'0x{b:02X}' for b in encoded)}")
            print()

    def _write_binary_file(self, output_file: str) -> None:
        with open(output_file, 'wb') as f:
            for instr in self.instructions:
                f.write(instr.encode())


def print_usage():
    """Выводит справку по использованию."""
    print("Использование: python3 uvm_assembler.py <input.asm> <output.bin> [--test]")
    print()
    print("Примеры:")
    print("  python uvm_assembler.py program.asm program.bin")
    print("  python uvm_assembler.py program.asm program.bin --test")


def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = len(sys.argv) > 3 and sys.argv[3] == '--test'

    try:
        assembler = UVMAssembler(test_mode)
        assembler.assemble(input_file, output_file)
        print(f"✓ Успешно скомпилировано в {output_file}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except AssemblyException as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()