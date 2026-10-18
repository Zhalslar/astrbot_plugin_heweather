import asyncio
from datetime import datetime
from typing import Any

import aiohttp
import jwt

from ..config import PluginConfig

_ICON_CODES = (
    "100",
    "101",
    "102",
    "103",
    "104",
    "150",
    "151",
    "152",
    "153",
    "300",
    "301",
    "302",
    "303",
    "304",
    "305",
    "306",
    "307",
    "308",
    "309",
    "310",
    "311",
    "312",
    "313",
    "314",
    "315",
    "316",
    "317",
    "318",
    "350",
    "351",
    "399",
    "400",
    "401",
    "402",
    "403",
    "404",
    "405",
    "406",
    "407",
    "408",
    "409",
    "410",
    "456",
    "457",
    "499",
    "500",
    "501",
    "502",
    "503",
    "504",
    "507",
    "508",
    "509",
    "510",
    "511",
    "512",
    "513",
    "514",
    "515",
    "800",
    "801",
    "802",
    "803",
    "804",
    "805",
    "806",
    "807",
    "900",
    "901",
    "999",
)
_ICON_CHARS = {code: chr(0xF101 + index) for index, code in enumerate(_ICON_CODES)}


def _icon_char(code: object) -> str:
    """Converts a QWeather icon code to its bundled icon-font character.

    Args:
        code: Numeric QWeather weather icon code.

    Returns:
        A private-use Unicode character understood by the QWeather icon font.
    """
    return _ICON_CHARS.get(str(code), _ICON_CHARS["999"])


class WeatherError(Exception):
    """Base exception for weather API failures."""


class CityNotFoundError(WeatherError):
    """Raised when QWeather cannot find the requested city."""


class Weather:
    """Fetches current, forecast, air-quality, and warning data from QWeather."""

    API_HOST = "https://api.qweather.com"

    def __init__(self, city_name: str, config: PluginConfig):
        self.city_name = city_name.strip()
        self.cfg = config

    def _make_token(self) -> str:
        """Creates the short-lived EdDSA token required by QWeather."""
        subject = self.cfg.jwt_sub
        key_id = self.cfg.jwt_kid
        private_key = self.cfg.jwt_private_key
        if not subject or not key_id or not private_key:
            raise WeatherError(
                "请在插件配置中填写 QWeather JWT 项目 ID、Key ID 和私钥"
            )

        now = int(datetime.now().timestamp())
        return jwt.encode(
            {"iat": now - 30, "exp": now + 900, "sub": subject},
            str(private_key).replace("\\n", "\n"),
            algorithm="EdDSA",
            headers={"kid": key_id},
        )

    async def _get(
        self,
        session: aiohttp.ClientSession,
        path: str,
        params: dict[str, str | int] | None = None,
    ) -> dict[str, Any]:
        """Requests one QWeather endpoint and validates its API status code."""
        async with session.get(
            f"{self.API_HOST}{path}",
            params=params,
            headers={"Authorization": f"Bearer {self._token}"},
        ) as response:
            response.raise_for_status()
            payload = await response.json(content_type=None)
        code = str(payload.get("code", ""))
        if code == "404" and path == "/geo/v2/city/lookup":
            raise CityNotFoundError(self.city_name)
        if code and code not in {"200", "204"}:
            raise WeatherError(
                f"QWeather 返回错误代码 {code}。请检查 JWT 配置和套餐权限。"
            )
        return payload

    async def load_data(self) -> dict[str, Any]:
        """Loads and normalizes one city's weather data for the renderer.

        Returns:
            A JSON-compatible dictionary containing current conditions, hourly
            and daily forecasts, air quality, and active warnings.

        Raises:
            CityNotFoundError: If the requested city is not recognized.
            WeatherError: If authentication or QWeather API validation fails.
            aiohttp.ClientError: If a network request fails.
        """
        self._token = self._make_token()
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as client:
            city_data = await self._get(
                client,
                "/geo/v2/city/lookup",
                {"location": self.city_name, "number": 1},
            )
            locations = city_data.get("location") or []
            if not locations:
                raise CityNotFoundError(self.city_name)
            location = locations[0]
            self.city_name = location.get("name", self.city_name)
            location_id = str(location["id"])
            latitude = float(location["lat"])
            longitude = float(location["lon"])

            now_data, daily_data, hourly_data = await asyncio.gather(
                self._get(client, "/v7/weather/now", {"location": location_id}),
                self._get(
                    client,
                    f"/v7/weather/{self.cfg.forecast_days}d",
                    {"location": location_id},
                ),
                self._get(client, "/v7/weather/24h", {"location": location_id}),
            )
            optional_data = await asyncio.gather(
                self._get(
                    client,
                    f"/airquality/v1/current/{latitude:.2f}/{longitude:.2f}",
                ),
                self._get(client, "/v7/warning/now", {"location": location_id}),
                return_exceptions=True,
            )

        air_result, warning_result = optional_data
        air_data = air_result if isinstance(air_result, dict) else {}
        warning_data = warning_result if isinstance(warning_result, dict) else {}

        current = now_data.get("now") or {}
        forecast = daily_data.get("daily") or []
        hourly_forecast = hourly_data.get("hourly") or []
        if self.cfg.show_full_day:
            hourly_forecast = hourly_forecast[::2][:12]
        else:
            hourly_forecast = hourly_forecast[:12]

        weekday_names = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
        normalized_days = []
        for item in forecast[:self.cfg.forecast_days]:
            fx_date = str(item.get("fxDate", ""))
            date_display = fx_date
            try:
                date_value = datetime.strptime(fx_date, "%Y-%m-%d")
                date_display = f"{date_value.month}月{date_value.day}日"
                weekday = weekday_names[date_value.weekday()]
            except ValueError:
                weekday = ""
            normalized_days.append(
                {
                    "date": date_display,
                    "weekday": weekday,
                    "text_day": item.get("textDay", ""),
                    "text_night": item.get("textNight", ""),
                    "temp_max": item.get("tempMax", "-"),
                    "temp_min": item.get("tempMin", "-"),
                    "icon_day": _icon_char(item.get("iconDay", "999")),
                    "icon_night": _icon_char(item.get("iconNight", "999")),
                }
            )

        air_indexes = air_data.get("indexes") or []
        selected_index = next(
            (item for item in air_indexes if item.get("code") == "qaqi"),
            None,
        ) or next(
            (item for item in air_indexes if item.get("code") == "us-epa"),
            air_indexes[0] if air_indexes else None,
        )
        pollutants = {item.get("code"): item for item in air_data.get("pollutants", [])}
        normalized_air = None
        if selected_index:
            air_color = "#a5c84e"
            raw_color = selected_index.get("color")
            if isinstance(raw_color, dict):
                try:
                    air_color = "#{:02x}{:02x}{:02x}".format(
                        int(raw_color["red"]),
                        int(raw_color["green"]),
                        int(raw_color["blue"]),
                    )
                except (KeyError, TypeError, ValueError):
                    pass

            pollutant_values = {}
            normalized_pollutants = []
            pollutant_labels = {
                "pm2p5": "PM2.5",
                "pm10": "PM10",
                "o3": "O₃",
                "co": "CO",
                "no2": "NO₂",
                "so2": "SO₂",
            }
            for pollutant_code in ("pm2p5", "pm10", "o3", "co", "no2", "so2"):
                pollutant = pollutants.get(pollutant_code) or {}
                concentration = pollutant.get("concentration") or {}
                value = concentration.get("value", "-")
                pollutant_values[pollutant_code] = value
                try:
                    percent = max(0, min(int(float(value) / 200 * 100), 100))
                except (TypeError, ValueError):
                    percent = 0
                normalized_pollutants.append(
                    {
                        "label": pollutant_labels[pollutant_code],
                        "value": value,
                        "percent": percent,
                    }
                )

            normalized_air = {
                "aqi": selected_index.get("aqiDisplay", selected_index.get("aqi", "-")),
                "category": selected_index.get("category") or "",
                "primary": (selected_index.get("primaryPollutant") or {}).get(
                    "name", ""
                ),
                "effect": (selected_index.get("health") or {}).get("effect", ""),
                "color": air_color,
                "pm25": pollutant_values["pm2p5"],
                "pm10": pollutant_values["pm10"],
                "o3": pollutant_values["o3"],
                "co": pollutant_values["co"],
                "no2": pollutant_values["no2"],
                "so2": pollutant_values["so2"],
                "pollutants": normalized_pollutants,
            }

        numeric_temperatures = []
        for item in hourly_forecast:
            try:
                numeric_temperatures.append(int(float(item.get("temp", 0))))
            except (TypeError, ValueError):
                pass
        if numeric_temperatures:
            minimum = min(numeric_temperatures)
            maximum = max(numeric_temperatures)
            chart_low = minimum - (maximum - minimum)
            chart_span = max(maximum - chart_low, 1)
        else:
            chart_low = 0
            chart_span = 1

        normalized_hours = []
        for item in hourly_forecast:
            try:
                date_value = datetime.fromisoformat(
                    str(item.get("fxTime", "")).replace("Z", "+00:00")
                )
                hour_label = date_value.strftime("%I%p").lstrip("0")
            except (TypeError, ValueError):
                hour_label = ""
            try:
                temperature = int(float(item.get("temp", 0)))
                temp_percent = int((temperature - chart_low) / chart_span * 100)
            except (TypeError, ValueError):
                temp_percent = 0
            normalized_hours.append(
                {
                    "time": hour_label,
                    "temp": item.get("temp", "-"),
                    "text": item.get("text", ""),
                    "icon": _icon_char(item.get("icon", "999")),
                    "temp_percent": max(0, min(temp_percent, 100)),
                }
            )

        return {
            "city": self.city_name,
            "updated_at": current.get("obsTime", ""),
            "now": {
                "temp": current.get("temp", "-"),
                "text": current.get("text", ""),
                "feels_like": current.get("feelsLike", "-"),
                "wind_dir": current.get("windDir", ""),
                "wind_scale": f"{current.get('windScale', '')}级",
                "wind": f"{current.get('windDir', '')} {current.get('windScale', '')}级".strip(),
                "humidity": current.get("humidity", "-"),
                "precip": current.get("precip", "-"),
                "visibility": current.get("vis", "-"),
                "icon": _icon_char(current.get("icon", "999")),
            },
            "daily": normalized_days,
            "hourly": normalized_hours,
            "air": normalized_air,
            "warnings": [
                {
                    "title": item.get("title", "天气预警"),
                    "text": item.get("text", ""),
                }
                for item in (warning_data.get("warning") or [])
            ],
        }
