"""Fetch sun data."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from astral import Observer
from astral.sun import azimuth, elevation, sunrise, sunset
import pandas as pd
from homeassistant.core import HomeAssistant


class SunData:
    """Access local sun data."""

    def __init__(self, timezone: str, hass: HomeAssistant) -> None:
        """Initialise location, elevation and timezone from HA config."""
        self.hass = hass
        latitude = hass.config.latitude
        longitude = hass.config.longitude
        self.observer = Observer(latitude, longitude, hass.config.elevation)
        self.sea_level_observer = Observer(latitude, longitude)
        self.timezone = timezone

    @property
    def times(self) -> pd.DatetimeIndex:
        """Define 5-minute time interval for today."""
        start_date = date.today()
        return pd.date_range(
            start=start_date,
            end=start_date + timedelta(days=1),
            freq="5min",
            tz=self.timezone,
            name="time",
        )

    @property
    def solar_azimuth(self) -> list[float]:
        """Return solar azimuth for each 5-minute slot today."""
        # OPTIM: list comprehension — eliminates manual index for-loop
        return [azimuth(self.observer, t.astimezone(UTC)) for t in self.times]

    @property
    def solar_elevation(self) -> list[float]:
        """Return solar elevation for each 5-minute slot today."""
        # OPTIM: list comprehension — eliminates manual index for-loop
        return [elevation(self.observer, t.astimezone(UTC)) for t in self.times]

    def sunset(self) -> datetime:
        """Return today's sunset time (UTC)."""
        return sunset(self.sea_level_observer, date.today())

    def sunrise(self) -> datetime:
        """Return today's sunrise time (UTC)."""
        return sunrise(self.sea_level_observer, date.today())
