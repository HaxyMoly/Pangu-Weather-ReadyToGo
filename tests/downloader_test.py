import unittest
from downloader.client import Client
from datetime import datetime
from pathlib import Path

from netCDF4 import Dataset


class TestClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output = "outputs"
        cls.c = Client(
            output_dir="outputs",
            download_time=datetime(2023, 7, 20, 0, 0),
        )

    def test_download(self):
        self.c.retrieve()

        surface_file = Path(self.output).joinpath("surface.nc")
        upper_file = Path(self.output).joinpath("upper.nc")

        self.assertTrue(surface_file.exists())
        self.assertTrue(upper_file.exists())

    def test_download_multi_time(self):
        c = Client(
            output_dir="outputs",
            download_time=datetime(2023, 7, 10, 0, 0),
            span=72,
            interval=6,
            extent=[0, 100, 40, 140],
        )

        c.retrieve()

        surface_file = Path(self.output).joinpath("surface.nc")
        upper_file = Path(self.output).joinpath("upper.nc")

        self.assertTrue(surface_file.exists())
        self.assertTrue(upper_file.exists())

        with Dataset(surface_file, "r") as f:
            self.assertEqual(f.variables["u10"].shape[0], 72 // 6 + 1)

    def test_download_full_scale(self):
        c = Client(
            output_dir="outputs",
            download_time=datetime(2023, 7, 10, 0, 0),
        )

        c.retrieve()

        surface_file = Path(self.output).joinpath("surface.nc")
        upper_file = Path(self.output).joinpath("upper.nc")

        self.assertTrue(surface_file.exists())
        self.assertTrue(upper_file.exists())

        with Dataset(surface_file, "r") as f:
            self.assertEqual(f.variables["u10"].shape[1:], (721, 1440))

    def test_download_defined_area(self):
        c = Client(
            output_dir="outputs",
            download_time=datetime(2023, 7, 10, 0, 0),
            extent=[0, 100, 40, 140],
        )

        surface_file = Path(self.output).joinpath("surface.nc")
        upper_file = Path(self.output).joinpath("upper.nc")

        c.retrieve()

        self.assertTrue(surface_file.exists())
        self.assertTrue(upper_file.exists())

        with Dataset(surface_file, "r") as f:
            self.assertEqual(f.variables["u10"].shape[1:], (161, 161))
