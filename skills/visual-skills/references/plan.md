# 计划格式

先看照片再填写；下例仅演示格式，不是每次复用的文案。当前输出固定 1200×1600。用户明确要求别的尺寸时，说明当前限制，不能默默输出另一种比例。

```json
{
  "schema_version": 2,
  "subject_policy": "preserve",
  "category": "person",
  "title": ["把今天", "贴成喜欢的样子"],
  "subtitle": "把平常的瞬间认真收藏",
  "palette": "cobalt",
  "layout": "cover",
  "photo_mode": "cutout",
  "tone": "mono",
  "seed": 103,
  "design_reason": "干净背景的人像适合保留原面容的剪贴，紫底与橙色纸层形成对比。",
  "motif": "A LITTLE / DAYDREAM",
  "eyebrow": "PAPER / MOMENTS",
  "edition": "A MOMENT, KEPT",
  "formal_copy": []
}
```

`category` 为 `person/group/product/pet/landscape`；`photo_mode` 为 `cutout/whole`；`tone` 为 `color/mono`。`seed` 为整数，控制本地程序纸边和颗粒，不控制生成模型的随机性。原图文件不是计划中的远程 URL，由命令行提供本地文件。

`title` 是 1–3 行原文，用户正式标题允许换行但不改字。当前布局只适合短海报文案，标题以每行约 2–10 个中文字符为宜。过长时程序拒绝压到不可读字号；保留原文并报告限制，不截断、不省略。

`formal_copy` 列出用户提供且必须出现在标题或副标题中的完整字符串。没有正式文案时留空；创意短句不填入。修复时此列表不能改变。程序只做字符串核对，Agent 仍要读成品确认字形、标点、可读性和遮挡。

`motif/eyebrow/edition` 为少量英文装饰，可自行拟定而不捏造事实。`motif` 在 cutout 中可能被照片遮挡，正式信息不能放这里。

所有路径用绝对路径并正确引用空格。用文件写入工具或结构化 JSON 写计划；不要把用户文字拼到 shell 命令里。

## 新版模式和构图

省略 `subject_policy` 时按旧计划解释为 `preserve`。新版原片计划优先用 `cover`、`split`、`window`；前两个支持 whole/cutout，window 保留 whole。新增 `cobalt` 和 `tomato` 配色。旧四种布局和旧四种配色保持可读。

创意计划举例（实际图必须由宿主图像工具生成，并通过 `--artwork` 导入）：

```json
{
  "schema_version": 2,
  "subject_policy": "creative",
  "allowed_changes": ["黑白印刷质感", "背景与纸层构图"],
  "keep_features": ["人物可辨识的脸和发型", "耳饰和项链", "只有一人"],
  "category": "person",
  "title": ["不必", "乖乖入框"],
  "subtitle": "把今天，剪成自己的样子。",
  "palette": "cobalt",
  "layout": "freeform",
  "photo_mode": "whole",
  "tone": "mono",
  "seed": 109,
  "formal_copy": [],
  "design_reason": "偏置的人像与短大字形成封面关系，蓝色纸场连接标题与主体。"
}
```

`whole` 在 freeform 中表示导入完整海报，不表示生成模型没有处理主体。实际处理与不保真声明保存在 `generation.json`。具体能力和保存流程见 [创意改造](enhancement.md)。
