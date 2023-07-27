import cdsapi

from pathlib import Path
from datetime import datetime, timedelta
from typing import List

from .extent import Extent
from .reply import Reply


class Client:
    # DI for cdsapi client
    __cds_client: cdsapi.Client

    # output dir for downloaded files
    output_dir: Path

    # download time
    download_time: datetime

    # boundary
    # [90, 0, -90, 359.75]
    extent: Extent
    __default_extent = Extent(
        start_lat=90,
        start_lon=0,
        end_lat=-90,
        end_lon=359.75,
    )

    # The variables required
    surface_variables: list
    upper_variables: list
    pressure_levels: list

    # download time interval
    interval: int

    # forecast duration
    span: int

    # surface default variables
    __default_surface_variables = [
        'mean_sea_level_pressure',
        '10m_u_component_of_wind',
        '10m_v_component_of_wind',
        '2m_temperature'
    ]

    # upper air default variables
    __default_upper_variables = [
        'geopotential',
        'specific_humidity',
        'temperature',
        'u_component_of_wind',
        'v_component_of_wind'
    ]

    # Pressure levels required
    __default_pressure_levels = ['1000', '925', '850', '700', '600', '500', '400', '300', '250', '200', '150', '100', '50']

    def __init__(self, output_dir: str, download_time: datetime, **kwargs):
        """
        Initialize the client
        :param output_dir: output directory
        :param download_time: data initial time
        :param kwargs: other parameters for downloading
        """
        # download area extent, pressure_levels, surface_variables, upper_variables,
        # span, interval, etc. are optional parameters, which can be injected be into **kwargs

        if not Path(output_dir).is_dir():
            raise NotADirectoryError(f"{output_dir} is not a directory")
        self.output_dir = Path(output_dir)

        if download_time > datetime.now():
            raise ValueError("Download time cannot be in the future")

        self.download_time = download_time

        # parse other download parameters
        for k, v in kwargs.items():
            setattr(self, k, v)

        # parse extent if exist
        self.extent = self.__parse_extent(**kwargs)

        self.__cds_client = cdsapi.Client()

    def __parse_extent(self, **kwargs) -> Extent:
        """
        Parse extent to string
        """
        # check if area is defined by users
        if "extent" in kwargs:
            extent = Extent(
                start_lat=kwargs["extent"][0],
                start_lon=kwargs["extent"][1],
                end_lat=kwargs["extent"][2],
                end_lon=kwargs["extent"][3]
            )
        else:
            extent = self.__default_extent

        return extent

    def __generate_download_timestamp(self) -> tuple[List[str], List[str]]:
        """
        Generate multiple timestamps for downloading
        """
        if not hasattr(self, "span") or not hasattr(self, "interval"):
            return [self.download_time.date().strftime("%Y-%m-%d")], [self.download_time.time().strftime("%H:%M")]

        download_times = []

        dates = []

        # avoid duplicate times
        times = set()

        # generate multiple timestamps
        i = 0
        while self.interval * i <= self.span:
            download_times.append(self.download_time + timedelta(hours=self.interval * i))
            i += 1

        for t in download_times:
            dates.append(t.date().strftime("%Y-%m-%d"))
            times.add(t.time().strftime("%H:%M"))

        return dates, [t for t in sorted(times)]

    def retrieve(self):
        # retrieve surface and upper air data
        # check whether upper and surface variables changed
        if not hasattr(self, "surface_variables"):
            self.surface_variables = self.__default_surface_variables

        if not hasattr(self, "upper_variables"):
            self.upper_variables = self.__default_upper_variables

        if not hasattr(self, "pressure_levels"):
            self.pressure_levels = self.__default_pressure_levels

        # gets multiple timestamps
        dates, times = self.__generate_download_timestamp()

        # download surface data
        r = self.__cds_client.retrieve("reanalysis-era5-single-levels", {
            "product_type": "reanalysis",
            "format": "netcdf",
            "variable": self.surface_variables,
            "pressure_level": self.pressure_levels,
            "date": dates,
            "time": times,
            "area": self.extent.to_list,
        })

        # download asynchronously
        Reply(r).download(str(self.output_dir.joinpath("surface.nc")))

        # download upper air data
        # follow the same order with surface data
        self.__cds_client.retrieve("reanalysis-era5-pressure-levels", {
            "product_type": "reanalysis",
            "format": "netcdf",
            "variable": self.upper_variables,
            "pressure_level": self.pressure_levels,
            "date": dates,
            "time": times,
            "area": self.extent.to_list,
        })

        # download asynchronously
        Reply(r).download(str(self.output_dir.joinpath("upper.nc")))