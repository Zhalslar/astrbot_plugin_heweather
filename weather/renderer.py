import asyncio
import json
from uuid import uuid4

import typst

from ..config import PluginConfig


async def render_weather(data: dict, config: PluginConfig) -> bytes:
    """Compile a weather card to PNG using Typst.

    Args:
        data: JSON-compatible weather information from the QWeather client.
        config: Plugin configuration containing template and output paths.

    Returns:
        Rendered PNG image bytes.

    Raises:
        RuntimeError: If Typst cannot compile the template or output image.
    """
    config.temp_dir.mkdir(parents=True, exist_ok=True)
    render_id = uuid4().hex
    output_path = config.temp_dir / f"weather_{render_id}.png"
    data_path = config.temp_dir / f"weather_{render_id}.json"
    data_path_value = f"/{data_path.resolve().relative_to(config.root_dir.resolve()).as_posix()}"
    try:
        await asyncio.to_thread(
            data_path.write_text,
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )
        await asyncio.to_thread(
            typst.compile,
            str(config.template_path.resolve()),
            output=str(output_path),
            root=str(config.root_dir.resolve()),
            font_paths=[str(config.font_path.parent)],
            format="png",
            ppi=96,
            sys_inputs={"data_path": data_path_value},
        )
        return await asyncio.to_thread(output_path.read_bytes)
    finally:
        output_path.unlink(missing_ok=True)
        data_path.unlink(missing_ok=True)
