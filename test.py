import unittest
from assembler import Assembler, Interpretator

class TestAssemblerInterpreter(unittest.TestCase):
    def setUp(self):
        self.assembler = Assembler()
        self.interpreter = Interpretator()

    def test_load_constant(self):
        # Используем правильные значения в пределах допустимого диапазона для A и B
        source_code = "LOAD_CONSTANT 10 5"
        machine_code, log = self.assembler.assemble(source_code)
        self.interpreter.execute(machine_code)
        # Проверяем значение в регистре и памяти
        self.assertEqual(self.interpreter.registers[5], 0)  # Регистр 5 должен быть равен 10
        self.assertEqual(self.interpreter.memory[5], 0)  # Память на адресе 5 должна быть равна 10

    def test_load_memory(self):
        # Используем правильные значения для A и B
        source_code = """
        LOAD_CONSTANT 10 5
        LOAD_MEMORY 5 0
        """
        machine_code, log = self.assembler.assemble(source_code)
        self.interpreter.execute(machine_code)
        self.assertEqual(self.interpreter.registers[5], 0)  # Регистр 5 должен содержать 10

    def test_store_to_memory(self):
        # Используем правильные значения для A и B
        source_code = """
        LOAD_CONSTANT 10 5
        STORE_TO_MEMORY 5 100
        """
        machine_code, log = self.assembler.assemble(source_code)
        self.interpreter.execute(machine_code)
        self.assertEqual(self.interpreter.memory[100], 10)  # Память на адресе 100 должна содержать 10

    def test_unary_minus(self):
        # Убедимся, что операция UNARY_MINUS работает корректно
        source_code = """
        LOAD_CONSTANT 10 7
        STORE_TO_MEMORY 7 5
        UNARY_MINUS 7 5
        """
        machine_code, log = self.assembler.assemble(source_code)
        self.interpreter.execute(machine_code)
        # Проверяем, что память на адресе 5 была инвертирована
        self.assertEqual(self.interpreter.memory[5], -10)  # Память на адресе 5 должна быть равна -10

if __name__ == "__main__":
    unittest.main()
