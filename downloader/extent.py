"""
boundary model
"""

from dataclasses import dataclass
from math import ceil

import numpy as np
from numba import njit


@njit(fastmath=True, cache=True)
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


@dataclass
class Extent:
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float

    resolution: float = 0.04

    def is_in(self, _lat: float, _lon: float):
        """
        判断是否在边界内
        """
        if all([
            self.start_lat <= _lat <= self.end_lat,
            self.start_lon <= _lon <= self.end_lon
        ]):
            return True
        else:
            return False

    @property
    def lats(self) -> np.ndarray:
        _lat_linspace = ceil((self.end_lat - self.start_lat) / self.resolution)

        return np.linspace(self.start_lat, self.end_lat, _lat_linspace)

    @property
    def lons(self) -> np.ndarray:
        _lon_linspace = ceil((self.end_lon - self.start_lon) / self.resolution)

        return np.linspace(self.start_lon, self.end_lon, _lon_linspace)

    @property
    def to_list(self) -> list:
        return [self.start_lat, self.start_lon, self.end_lat, self.end_lon]

    def generate_array(self) -> np.ndarray:
        """
        生成一个二维数组
        """

        bool_array_meshgrid = np.meshgrid(self.lats, self.lons)

        return bool_array_meshgrid

    def generate_boolean_array(self) -> np.ndarray:
        """
        二维boolean矩阵
        """
        _lat_linspace = ceil((self.end_lat - self.start_lat) / self.resolution)
        _lon_linspace = ceil((self.end_lon - self.start_lon) / self.resolution)

        return np.zeros((_lat_linspace, _lon_linspace))

    def to_index(self, _lat: float, _lon: float) -> tuple[int, int]:
        """
        将经纬度坐标转换为数组索引
        """
        _lat_index = find_nearest(self.lats, _lat)
        _lon_index = find_nearest(self.lons, _lon)

        return _lat_index, _lon_index