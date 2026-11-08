# visual-skills

**给 Agent 一张照片，做成拼贴海报。**

自动安排标题、配色和构图。可选**保留原片**，或用你自己的图像工具做 **AI 创意改造**。当前提供「照片拼贴」。

| 创意人像 | 创意宠物 |
|---|---|
| ![创意人像拼贴](examples/v0.2.0-preview/portrait.jpg) | ![创意宠物拼贴](examples/v0.2.0-preview/kitten.jpg) |

新版实际生成案例：同一批测试照片，经 AI 创意处理。原十张案例保留在[旧版报告](benchmark/REPORT.md)。

[安装使用](#安装使用) · [全部案例](benchmark/REPORT.md) · [English](README.en.md)

## 安装使用

项目、skill 和安装包统一叫 **`visual-skills`**，当前支持照片拼贴。所需脚本和字体已包含，只需安装这一个 skill。

把下面这句话发给 Codex：

> 请安装 https://github.com/chingz0509/visual-skills 中的 `skills/visual-skills`，只安装这个 skill，首次使用时按说明自动准备运行依赖。

安装后，上传照片并说：

> 用 visual-skills，把这张照片做成拼贴海报。

也可以附上你想用的标题。不提供文案时，Agent 会自动设计。

想让主体也更有风格，可以说：

> 用 visual-skills 做创意拼贴，允许改造主体质感和背景，人物要能认出来。

只想摆放原照片，可以说“保留原片”。没选过时 Agent 会问一次。

## 你会得到

- **一张海报**：默认 3:4 竖版 PNG，1200 × 1600。
- **两种主体模式**：原片模式不重绘；创意模式允许约定范围内的改造，检查辨识度、肢体和关键物品。
- **可复现的记录**：原片模式保存照片、纸层、字体和布局；AI 整图保存原片、实际成品、提示词和参数，其内部不是独立可编辑图层。

基础流程使用你现有的 Agent，无需额外生图密钥或其他 skill。首次使用可能需要下载 Python 图像处理依赖，由 Agent 自动处理；需要本地执行权限。

创意模式还需要宿主可用的图像工具，或你自己配置的图像服务；不使用作者的密钥。有无生图能力取决于宿主，不是安装 skill 就自带免费模型。

## 可用风格

| 风格 | 适用照片 | 状态 |
|---|---|---|
| [visual-skills · 照片拼贴](skills/visual-skills/SKILL.md) | 单人、合照、产品、宠物、风景 | 实验版 |

每个风格可单独安装。合照保留所有人和原有关系，风景保留完整照片。

## 当前进展

首个验证环境是 **Codex 桌面端 + Apple Silicon Mac**；其他环境尚未完整验证。

`0.2.0-preview` 增加自由创意改造、三种本地构图和更严格的视觉检查。上方两张通过 Agent 初检，本轮用户认可展示效果；这不等于完整十张验收或通用成功率。

本轮相机创意测试仍因细节重绘错误失败，已保留原因。[新版验证与限制](docs/VALIDATION-0.2.md) · [旧版全部结果](benchmark/REPORT.md)

## 更多

[下载 visual-skills 安装包](https://github.com/chingz0509/visual-skills/releases/tag/v0.2.0-preview) · [使用与运行说明](docs/USAGE.md) · [贡献风格](CONTRIBUTING.md) · [设计约定](docs/DESIGN.md) · [版本记录](CHANGELOG.md) · [发布指南](docs/PUBLISHING.md)

代码采用 MIT 许可；照片和字体遵循各自许可。[素材来源](THIRD_PARTY.md)
