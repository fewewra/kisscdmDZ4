import sys
import json

class Assembler:
    def __init__(self):
        self.instructions = {
            "LOAD_CONSTANT": 13,  # 0b1101
            "LOAD_MEMORY": 11,    # 0b1011
            "STORE_TO_MEMORY": 21, # 0b10101
            "UNARY_MINUS": 31     # 0b11111
        }

    def assemble(self, source_code):
        machine_code = []
        log = []

        for line_no, line in enumerate(source_code.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith(";"):  # Пропуск пустых строк и комментариев
                continue

            parts = line.split()
            command = parts[0]

            if command not in self.instructions:
                raise ValueError(f"Unknown instruction '{command}' on line {line_no}")

            opcode = self.instructions[command]

            if command == "LOAD_CONSTANT":
                if len(parts) != 3:
                    raise ValueError(f"Invalid number of arguments for command: {line}")
                _, value, address = parts
                value = int(value)
                address = int(address)

                if not (0 <= value < (1 << 16)):
                    raise ValueError(f"Invalid constant value: {value}")
                if not (0 <= address < 32):  # Регистр-аккумулятор
                    raise ValueError(f"Invalid register address: {address}")

                encoded = (opcode << 24) | (address << 20) | value
                machine_code.append(encoded)
                log.append({"line": line_no, "instruction": line, "binary": f"{encoded:08X}"})

            elif command in ["LOAD_MEMORY", "STORE_TO_MEMORY", "UNARY_MINUS"]:
                if len(parts) != 3:
                    raise ValueError(f"Invalid number of arguments for command: {line}")
                _, reg, address = parts
                reg = int(reg)
                address = int(address)

                if not (0 <= reg < 32):
                    raise ValueError(f"Invalid register number: {reg}")
                if not (0 <= address < (1 << 25)):
                    raise ValueError(f"Invalid memory address: {address}")

                encoded = (opcode << 24) | (reg << 20) | address
                machine_code.append(encoded)
                log.append({"line": line_no, "instruction": line, "binary": f"{encoded:08X}"})

        return machine_code, log


class Interpretator:
    def __init__(self):
        self.registers = [0] * 32  # Регистры
        self.memory = [0] * 128   # Память
        self.log = []  # Лог выполнения команд

    def execute(self, machine_code):
        for index, instruction in enumerate(machine_code):
            opcode = (instruction >> 24) & 0xFF
            reg = (instruction >> 20) & 0x1F
            address = instruction & 0xFFFFF

            if opcode == 13:  # LOAD_CONSTANT
                self.registers[reg] = address
                self.log.append(f"[{index}] LOAD_CONSTANT: Loaded {address} into register[{reg}].")

            elif opcode == 11:  # LOAD_MEMORY
                if address >= len(self.memory):
                    raise RuntimeError(f"LOAD_MEMORY failed: Invalid address {address}.")
                self.registers[reg] = self.memory[address]
                self.log.append(f"[{index}] LOAD_MEMORY: Loaded memory[{address}] = {self.memory[address]} into register[{reg}].")

            elif opcode == 21:  # STORE_TO_MEMORY
                if address >= len(self.memory):
                    raise RuntimeError(f"STORE_TO_MEMORY failed: Invalid address {address}.")
                self.memory[address] = self.registers[reg]
                self.log.append(f"[{index}] STORE_TO_MEMORY: Stored register[{reg}] = {self.registers[reg]} into memory[{address}].")

            elif opcode == 31:  # UNARY_MINUS
                if address >= len(self.memory):
                    raise RuntimeError(f"UNARY_MINUS failed: Invalid address {address}.")
                original_value = self.memory[address]
                value = -original_value
                self.memory[address] = value
                self.log.append(
                    f"[{index}] UNARY_MINUS: Negated memory[{address}] (original value: {original_value}) -> {value}."
                )

            else:
                raise RuntimeError(f"Unknown opcode {opcode} at index {index}.")

    def get_memory_dump(self):
        return {f"address_{i}": value for i, value in enumerate(self.memory)}


def main():
    if len(sys.argv) != 5:
        print("Usage: python script.py <input_file> <output_bin> <log_file> <result_json>")
        sys.exit(1)

    input_file, binary_file, log_file, result_file = sys.argv[1:]

    with open(input_file, "r") as f:
        source_code = f.read()

    assembler = Assembler()
    machine_code, log = assembler.assemble(source_code)

    with open(binary_file, "wb") as f:
        for instruction in machine_code:
            f.write(instruction.to_bytes(4, byteorder='big'))
    print(f"Binary file saved to {binary_file}")

    with open(log_file, "w") as f:
        json.dump(log, f, indent=4)
    print(f"Log file saved to {log_file}")

    vm = Interpretator()
    try:
        vm.execute(machine_code)
        memory_dump = vm.get_memory_dump()
        with open(result_file, "w") as f:
            json.dump(memory_dump, f, indent=4)
        print(f"Memory dump saved to {result_file}")
    except RuntimeError as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
