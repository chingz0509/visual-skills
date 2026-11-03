# Visual Skills · 视觉技能库

**给 Agent 一张照片，做成拼贴海报。**

自动安排标题、配色和布局，保留原照片主体。当前提供「照片拼贴」，后续逐步增加风格。

![照片拼贴：十张实际成品](examples/contact-sheet.jpg)

[安装使用](#安装使用) · [全部案例](benchmark/REPORT.md) · [English](README.en.md)

## 安装使用

把下面这句话发给 Codex：

> 请安装 https://github.com/chingz0509/visual-skills 中的 `skills/photo-paper-collage`，并准备运行环境。

安装后，上传照片并说：

> 用照片拼贴，把这张照片做成海报。

也可以附上你想用的标题。不提供文案时，Agent 会自动设计。

## 你会得到

- **一张海报**：默认 3:4 竖版 PNG，1200 × 1600。
- **原片主体保真**：照片可以抠图、变黑白、加印刷质感，主体不交给生图模型重绘。
- **可再次合成的素材包**：保存原图、图层、字体和布局。

基础流程使用你现有的 Agent 和本地工具，无需额外生图密钥。

## 可用风格

| 风格 | 适用照片 | 状态 |
|---|---|---|
| [照片拼贴](skills/photo-paper-collage/SKILL.md) | 单人、合照、产品、宠物、风景 | 实验版 |

每个风格可单独安装。合照保留所有人和原有关系，风景保留完整照片。

## 当前进展

首个验证环境是 **Codex 桌面端 + Apple Silicon Mac**；其他环境尚未完整验证。

固定十张测试中，8 张初次通过 Agent 检查，2 张修复后通过，**用户最终验收待完成**。当前版式较少，复杂毛发抠图仍有限制。[查看全部结果，包括失败尝试 →](benchmark/REPORT.md)

## 更多

[下载 ZIP](https://github.com/chingz0509/visual-skills/releases/tag/v0.1.0-experimental) · [使用与运行说明](docs/USAGE.md) · [贡献风格](CONTRIBUTING.md) · [设计约定](docs/DESIGN.md) · [版本记录](CHANGELOG.md) · [发布指南](docs/PUBLISHING.md)

代码采用 MIT 许可；照片和字体遵循各自许可。[素材来源](THIRD_PARTY.md)
