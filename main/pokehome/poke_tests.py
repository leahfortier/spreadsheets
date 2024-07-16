import unittest

from commands import get_family_pokes


class EvolutionTestCase(unittest.TestCase):
    def test_get_family_pokes(self):
        self.assertSetEqual(
            get_family_pokes("Lapras"),
            {"Lapras"}
        )
        self.assertSetEqual(
            get_family_pokes("Tauros, Paldean Tauros"),
            {"Tauros", "Paldean Tauros"}
        )
        self.assertSetEqual(
            get_family_pokes("Bulbasaur -> Ivysaur -> Venusaur"),
            {"Bulbasaur", "Ivysaur", "Venusaur"}
        )
        self.assertSetEqual(
            get_family_pokes("Wurmple -> Silcoon, Cascoon | Silcoon -> Beautifly | Cascoon -> Dustox"),
            {"Wurmple", "Silcoon", "Cascoon", "Beautifly", "Dustox"}
        )


if __name__ == '__main__':
    unittest.main()
