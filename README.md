<div align="center">

![:name](https://count.getloli.com/@astrbot_plugin_heweather?name=astrbot_plugin_heweather&theme=minecraft&padding=6&offset=0&align=top&scale=1&pixelated=1&darkmode=auto)

# astrbot_plugin_heweather

## 和风天气

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.0%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-Zhalslar-blue)](https://github.com/Zhalslar)

</div>

---
## 🤝 介绍

基于和风天气 API 的 AstrBot 插件，可查询天气、空气质量和预警信息。天气图片使用 Typst 直接编译生成, 轻量又美观

## 📦 安装

- 直接在astrbot的插件市场搜索astrbot_plugin_multimsg，点击安装即可

## ⌨️ 调用

| 调用方式 | 格式 | 示例 | 
| --- | --- | --- |
| 指令调用 | `天气 <城市>` | `天气 上海` |
| 自然语言调用 | - | 查查上海的天气 |

## 效果图

<img width="40%" alt="和风天气卡片" src="https://github.com/user-attachments/assets/0f8b2604-9f46-4070-9c22-6fd872f12ff0" />

## 配置

- 前往 [和风天气控制台](https://console.qweather.com) 注册账号

- 项目管理 -> 创建项目，获得`项目 ID`
- 通过[和风天气JWT认证说明](https://dev.qweather.com/docs/configuration/authentication/)中的步骤（任选一种方式），创建一对密钥：`公钥`和`私钥`
- 刚才创建的项目 -> 创建凭据 -> 选 JSON Web Token -> 填写要上传的`公钥` -> 保存 -> 获得`凭据ID`
- 复制 `项目 ID` `私钥` `凭据ID`

在 AstrBot 插件配置中填写和风天气控制台提供的 JWT 凭据：

- `jwt_sub`：项目 ID
- `jwt_kid`：Key ID
- `jwt_private_key`：Ed25519 PEM 私钥
- `forecast_days`：预报天数（1-30，依和风天气套餐权限而定）
- `hourlytype` 12 小时 或 24 小时



## 👥 贡献指南

- 🌟 Star 这个项目！（点右上角的星星，感谢支持！）
- 🐛 提交 Issue 报告问题
- 💡 提出新功能建议
- 🔧 提交 Pull Request 改进代码

## 📌 注意事项

- 想第一时间得到反馈的可以来作者的插件反馈群（QQ群）：460973561（不点star不给进）

## 🤝 致谢

卡片排版借鉴了[nonebot-plugin-heweather](https://github.com/kexue-z/nonebot-plugin-heweather)
