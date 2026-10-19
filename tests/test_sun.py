"""Tests for SunData."""

from __future__ import annotations

from datetime import date
import logging
from unittest.mock import MagicMock

from astral import LocationInfo
from astral.location import Location
import pytest

from custom_components.adaptive_cover.sun import SunData

TIMEZONE = "Europe/Berlin"


def _hass(elevation: int) -> MagicMock:
    hass = MagicMock()
    hass.config.latitude = 50.0
    hass.config.longitude = 10.0
    hass.config.elevation = elevation
    hass.config.time_zone = TIMEZONE
    return hass


def _reference(hass: MagicMock) -> Location:
    return Location(
        LocationInfo("", "", TIMEZONE, hass.config.latitude, hass.config.longitude)
    )


def test_no_deprecated_helper(caplog: pytest.LogCaptureFixture) -> None:
    """SunData must not use the deprecated get_astral_location helper."""
    with caplog.at_level(logging.WARNING):
        SunData(TIMEZONE, _hass(0))
    assert "get_astral_location" not in caplog.text


@pytest.mark.parametrize("elevation", [0, 500])
def test_solar_position_unchanged(elevation: int) -> None:
    """Azimuth and elevation match the previous astral Location results."""
    hass = _hass(elevation)
    sun_data = SunData(TIMEZONE, hass)
    location = _reference(hass)

    assert sun_data.solar_azimuth == [
        location.solar_azimuth(t, elevation) for t in sun_data.times
    ]
    assert sun_data.solar_elevation == [
        location.solar_elevation(t, elevation) for t in sun_data.times
    ]


@pytest.mark.parametrize("elevation", [0, 500])
def test_sunrise_sunset_unchanged(elevation: int) -> None:
    """Sunrise and sunset match the previous astral Location results."""
    hass = _hass(elevation)
    sun_data = SunData(TIMEZONE, hass)
    location = _reference(hass)

    assert sun_data.sunrise() == location.sunrise(date.today(), local=False)
    assert sun_data.sunset() == location.sunset(date.today(), local=False)
