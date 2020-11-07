from django.test import TestCase
from .logic import WorldGenerator
from .models import Cell
from .constants import MAIN_BIOME, BIOME_MOD
# Create your tests here.


class GenerationTestCase(TestCase):
    def setUp(self):
        WorldGenerator.generate_world()
    def all_biomes_present(self):
        """Passes if the generator creates all types of biomes"""

        self.assertEqual(Cell.objects.filter(main_biome = MAIN_BIOME.WATER).exists(), True)
        self.assertEqual(Cell.objects.filter(main_biome = MAIN_BIOME.PLAIN).exists(), True)
        self.assertEqual(Cell.objects.filter(main_biome = MAIN_BIOME.DESERT).exists(), True)
        self.assertEqual(Cell.objects.filter(biome_mod = BIOME_MOD.NONE).exists(), True)
        self.assertEqual(Cell.objects.filter(biome_mod = BIOME_MOD.FOREST).exists(), True)
        self.assertEqual(Cell.objects.filter(biome_mod = BIOME_MOD.SWAMP).exists(), True)
        self.assertEqual(Cell.objects.filter(biome_mod = BIOME_MOD.HILLS).exists(), True)
        self.assertEqual(Cell.objects.filter(biome_mod = BIOME_MOD.MOUNTAINS).exists(), True)

    def cities_present(self):
        self.assertEqual(Cell.objects.filter(city_tier=1).exists(),True)
