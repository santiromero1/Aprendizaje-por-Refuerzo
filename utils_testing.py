import unittest
from utils import (
    puntaje_y_no_usados,
    separar,
    PUNTAJE_ESCALERA,
    PUNTAJE_3_PARES,
    PUNTAJE_6_IGUALES
)

class TestPuntajeYNoUsados(unittest.TestCase):
    def test_6_iguales(self):
        for i in [1,2,3,4,5,6]:
            self.assertEqual(puntaje_y_no_usados([i]*6), (PUNTAJE_6_IGUALES, []))

    def test_escalera(self):
        self.assertEqual(puntaje_y_no_usados([1,2,3,4,5,6]), (PUNTAJE_ESCALERA, []))

    def test_3_pares(self):
        self.assertEqual(puntaje_y_no_usados([1,1,3,3,6,6]), (PUNTAJE_3_PARES, []))
        self.assertEqual(puntaje_y_no_usados([2,2,4,4,5,5]), (PUNTAJE_3_PARES, []))
        self.assertEqual(puntaje_y_no_usados([1,1,1,1,6,6]), (PUNTAJE_3_PARES, []))
        self.assertEqual(puntaje_y_no_usados([1,1,6,6,6,6]), (PUNTAJE_3_PARES, []))
        self.assertEqual(puntaje_y_no_usados([5,1,5,1,5,1]), (PUNTAJE_3_PARES, []))

    def test_casos_generales_6_dados(self):
        self.assertEqual(puntaje_y_no_usados([2,2,3,3,4,6]), (0, [2,2,3,3,4,6]))
        self.assertEqual(puntaje_y_no_usados([4,2,4,5,6,3]), (50, [2,3,4,4,6]))
        self.assertEqual(puntaje_y_no_usados([6,1,4,2,4,5]), (150, [2,4,4,6]))
        self.assertEqual(puntaje_y_no_usados([2,1,3,1,4,5]), (250, [2,3,4]))
        self.assertEqual(puntaje_y_no_usados([1,1,1,3,4,6]), (1000, [3,4,6]))
        self.assertEqual(puntaje_y_no_usados([1,1,1,1,4,6]), (1100, [4,6]))
        self.assertEqual(puntaje_y_no_usados([4,1,5,1,1,1]), (1150, [4]))
        self.assertEqual(puntaje_y_no_usados([5,1,5,1,4,1]), (1100, [4]))
        self.assertEqual(puntaje_y_no_usados([5,1,5,1,4,1]), (1100, [4]))
        self.assertEqual(puntaje_y_no_usados([5,2,5,2,4,2]), (300, [4]))
        self.assertEqual(puntaje_y_no_usados([5,2,5,2,5,2]), (700, []))

    def test_casos_generales_5_dados(self):
        self.assertEqual(puntaje_y_no_usados([2,2,3,3,4]), (0, [2,2,3,3,4]))
        self.assertEqual(puntaje_y_no_usados([4,2,4,5,6]), (50, [2,4,4,6]))
        self.assertEqual(puntaje_y_no_usados([6,1,4,2,3]), (100, [2,3,4,6]))
        self.assertEqual(puntaje_y_no_usados([1,1,2,3,5]), (250, [2,3]))
        self.assertEqual(puntaje_y_no_usados([1,1,1,4,6]), (1000, [4,6]))
        self.assertEqual(puntaje_y_no_usados([1,1,1,1,4]), (1100, [4]))
        self.assertEqual(puntaje_y_no_usados([1,5,1,1,1]), (1150, []))
        self.assertEqual(puntaje_y_no_usados([5,1,1,4,1]), (1050, [4]))
        self.assertEqual(puntaje_y_no_usados([5,1,5,1,5]), (700, []))
        self.assertEqual(puntaje_y_no_usados([5,1,5,1,4]), (300, [4]))
        self.assertEqual(puntaje_y_no_usados([5,2,5,2,2]), (300, []))
        self.assertEqual(puntaje_y_no_usados([5,2,5,2,5]), (500, [2,2]))

    def test_casos_generales_4_dados(self):
        self.assertEqual(puntaje_y_no_usados([2,2,3,3]), (0, [2,2,3,3]))
        self.assertEqual(puntaje_y_no_usados([4,2,4,5]), (50, [2,4,4]))
        self.assertEqual(puntaje_y_no_usados([6,1,4,2]), (100, [2,4,6]))
        self.assertEqual(puntaje_y_no_usados([1,1,2,3]), (200, [2,3]))
        self.assertEqual(puntaje_y_no_usados([4,1,1,1]), (1000, [4]))
        self.assertEqual(puntaje_y_no_usados([1,1,1,1]), (1100, []))
        self.assertEqual(puntaje_y_no_usados([1,5,1,1]), (1050, []))
        self.assertEqual(puntaje_y_no_usados([5,1,1,4]), (250, [4]))
        self.assertEqual(puntaje_y_no_usados([5,1,5,1]), (300, []))
        self.assertEqual(puntaje_y_no_usados([5,3,1,5]), (200, [3]))
        self.assertEqual(puntaje_y_no_usados([2,4,2,2]), (200, [4]))

    def test_casos_generales_3_dados(self):
        self.assertEqual(puntaje_y_no_usados([1,1,1]), (1000, []))
        for i in [2,3,4,5,6]:
            self.assertEqual(puntaje_y_no_usados([i]*3), (i*100, []))
        self.assertEqual(puntaje_y_no_usados([1,5,1]), (250, []))
        self.assertEqual(puntaje_y_no_usados([5,1,5]), (200, []))
        self.assertEqual(puntaje_y_no_usados([2,5,5]), (100, [2]))
        self.assertEqual(puntaje_y_no_usados([1,1,3]), (200, [3]))
        self.assertEqual(puntaje_y_no_usados([4,1,6]), (100, [4,6]))
        self.assertEqual(puntaje_y_no_usados([5,3,2]), (50, [2,3]))

    def test_casos_generales_2_dados(self):
        self.assertEqual(puntaje_y_no_usados([1,1]), (200, []))
        self.assertEqual(puntaje_y_no_usados([1,2]), (100, [2]))
        self.assertEqual(puntaje_y_no_usados([3,1]), (100, [3]))
        self.assertEqual(puntaje_y_no_usados([4,5]), (50, [4]))
        self.assertEqual(puntaje_y_no_usados([5,5]), (100, []))
        self.assertEqual(puntaje_y_no_usados([6,5]), (50, [6]))

    def test_casos_generales_1_dado(self):
        self.assertEqual(puntaje_y_no_usados([1]), (100, []))
        self.assertEqual(puntaje_y_no_usados([2]), (0, [2]))
        self.assertEqual(puntaje_y_no_usados([3]), (0, [3]))
        self.assertEqual(puntaje_y_no_usados([4]), (0, [4]))
        self.assertEqual(puntaje_y_no_usados([5]), (50, []))
        self.assertEqual(puntaje_y_no_usados([6]), (0, [6]))

class TestSepararDados(unittest.TestCase):
    def test_separar_0_dados(self):
        self.assertEqual(separar([1,2,3,4,5,6], []), [1,2,3,4,5,6])
        self.assertEqual(separar([1,2,3,4,5], []),   [1,2,3,4,5])
        self.assertEqual(separar([1,2,3,4], []),     [1,2,3,4])
        self.assertEqual(separar([1,2,3], []),       [1,2,3])
        self.assertEqual(separar([1,2], []),         [1,2])
        self.assertEqual(separar([1], []),           [1])
        self.assertEqual(separar([], []),            [])

    def test_separar_1_dado(self):
        self.assertEqual(separar([3,2,4,2,1,2], [2]), [3,4,2,1,2])
        self.assertEqual(separar([3,2,4,2,1,2], [1]), [3,2,4,2,2])

    def test_separar_2_dados(self):
        self.assertEqual(separar([3,2,4,2,1,2], [2,2]), [3,4,1,2])
        self.assertEqual(separar([3,2,4,2,1,2], [1,2]), [3,4,2,2])
        self.assertEqual(separar([3,2,4,2,1,2], [4,3]), [2,2,1,2])
        self.assertEqual(separar([2,2], [2,2]), [])
        self.assertEqual(separar([3,2], [2,3]), [])

    def test_separar_3_dados(self):
        self.assertEqual(separar([3,2,4,2,1,2], [2,2,2]), [3,4,1])
        self.assertEqual(separar([3,2,4,2,1,2], [1,2,3]), [4,2,2])
        self.assertEqual(separar([3,2,4,2,1,2], [4,3,1]), [2,2,2])
        self.assertEqual(separar([2,2,2], [2,2,2]), [])
        self.assertEqual(separar([3,2,2], [2,2,3]), [])
        self.assertEqual(separar([3,2,1], [2,1,3]), [])

if __name__ == "__main__":
    unittest.main()
