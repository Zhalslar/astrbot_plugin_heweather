<div align="center">

![:name](https://count.getloli.com/@astrbot_plugin_heweather?name=astrbot_plugin_heweather&theme=minecraft&padding=6&offset=0&align=top&scale=1&pixelated=1&darkmode=auto)

# astrbot_plugin_heweather

_ 和风天气 _

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.0%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-Zhalslar-blue)](https://github.com/Zhalslar)

</div>

---

# 和风天气（AstrBot）

基于和风天气 API 的 AstrBot 插件，可查询天气、空气质量和预警信息。天气图片使用 Typst 直接编译生成, 轻量又美观

## 调用

| 调用方式 | 格式 | 示例 | 
| --- | --- | --- |
| 指令调用 | `天气 <城市>` | `天气 上海` |
| 自然语言调用 | - | 查查上海的天气 |

## 效果图

## 配置

在 AstrBot 插件配置中填写和风天气控制台提供的 JWT 凭据：

- `jwt_sub`：项目 ID
- `jwt_kid`：Key ID
- `jwt_private_key`：Ed25519 PEM 私钥
- `forecast_days`：预报天数（1-30，依和风天气套餐权限而定）
- `hourlytype`：1 为未来 12 小时，2 为未来 24 小时

和风天气 JWT 认证说明：<https://dev.qweather.com/docs/configuration/authentication/>。

