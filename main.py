from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Image
from astrbot.api.star import Context, Star
from astrbot.core.message.message_event_result import MessageChain

from .config import PluginConfig
from .weather.client import CityNotFoundError, Weather, WeatherError
from .weather.renderer import render_weather


class HeWeatherPlugin(Star):
    """AstrBot integration for QWeather forecasts."""

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.cfg = PluginConfig(config)

    @filter.llm_tool(name="weather_query") # type: ignore
    @filter.command("天气", alias={"weather"})
    async def weather_query(self, event: AstrMessageEvent, city: str = ""):
        """天气 <城市名>，查询城市天气。
        Args:
            city(string): 要查询的城市名.
        """
        city = city or self.cfg.default_city
        try:
            weather = Weather(city, self.cfg)
            data = await weather.load_data()
            image = await render_weather(data, self.cfg)
        except CityNotFoundError:
            return f"未找到城市 {city}"
        except WeatherError as exc:
            return exc
        except Exception as exc:
            logger.exception("[heweather] Failed to query city %s", city)
            return exc
        await event.send(MessageChain([Image.fromBytes(image)]))
        return data
