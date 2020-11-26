import os

from pynames.from_tables_generator import FromCSVTablesGenerator

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'namegen_fixtures')

class TestNameGen(FromCSVTablesGenerator):
    SOURCE = [
        os.path.join(FIXTURES_DIR, 'test_settings.csv'),
        os.path.join(FIXTURES_DIR, 'test_names_templates.csv'),
        os.path.join(FIXTURES_DIR, 'test_names_tables.csv'),
    ]


class HungarianNamesSimple(FromCSVTablesGenerator):
    SOURCE = [
        os.path.join(FIXTURES_DIR, 'test_settings.csv'),
        os.path.join(FIXTURES_DIR, 'test_names_templates.csv'),
        os.path.join(FIXTURES_DIR, 'hungarian_names_tables.csv'),
    ]

hungarian = HungarianNamesSimple()