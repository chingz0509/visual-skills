# 第三方素材与许可

## 测试照片

固定照片来自 Pexels。2026-11-03 已读取 [Pexels 官方许可](https://www.pexels.com/license/)，其允许下载、修改及展示照片。照片不属于本项目 MIT 许可，也不应把照片中人物或品牌写成项目代言者。演示中的短句为创作文案，不是人物引语或品牌广告。

测试源照片只保存在本地 `benchmark/inputs/` 和运行包，排除在仓库与 skill 分发包之外。仓库公开的是转换后的实验海报、来源链接与清单；本项目不是原片素材库。下载脚本对固定输入做 SHA-256 核验，远端改变时停止，不静默替换。

冻结清单早期的部分作者/页面路径存在误填；后续查证在 `benchmark/provenance-addendum.json` 留存更正，原始冻结清单与照片哈希不改。以下使用更正后的信息。

| ID | 摄影者 | 来源 |
|---|---|---|
| person-easy | Pixabay | [Pexels 415829](https://www.pexels.com/photo/woman-wearing-black-spaghetti-strap-top-415829/) |
| person-hard | Andrea Piacquadio | [Pexels 774909](https://www.pexels.com/photo/woman-in-collared-shirt-774909/) |
| group-easy | fauxels | [Pexels 3184398](https://www.pexels.com/photo/people-taking-group-picture-3184398/) |
| group-hard | fauxels | [Pexels 3184338](https://www.pexels.com/photo/photo-of-three-people-smiling-while-having-a-meeting-3184338/) |
| product-easy | Maddy Jaya | [Pexels 90946](https://www.pexels.com/photo/black-fujifilm-dslr-camera-90946/) |
| product-hard | Fernando Arcos（署名来自已发布照片信用记录，单页未抓取成功） | [Pexels 190819](https://www.pexels.com/photo/190819/) |
| pet-easy | Pixabay（CDN 图可访问，单页未抓取成功） | [Pexels 45201](https://www.pexels.com/photo/45201/) |
| pet-hard | Chevanon Photography | [Pexels 1108099](https://www.pexels.com/photo/two-yellow-labrador-retriever-puppies-1108099/) |
| landscape-easy | James Wheeler | [Pexels 417074](https://www.pexels.com/photo/lake-and-mountain-417074/) |
| landscape-hard | Francesco Ungaro | [Pexels 1671325](https://www.pexels.com/photo/trees-on-a-dark-forest-1671325/) |

变更包括排版、纸层、旋转缩放、轻微印刷颗粒，部分照片黑白化或抠图。全部最终和中间失败海报见 `benchmark/REPORT.md`。

## 字体

- [Noto Sans SC](https://github.com/google/fonts/tree/main/ofl/notosanssc)，Google/Adobe，SIL Open Font License 1.1。
- [Bebas Neue](https://github.com/google/fonts/tree/main/ofl/bebasneue)，The Bebas Neue Project Authors / Ryoichi Tsunekawa，SIL Open Font License 1.1。

原字体未修改，随 skill 提供各自 OFL 许可。下载文件 SHA-256 和来源见 `skills/photo-paper-collage/assets/fonts/manifest.json`。

## 程序与系统能力

Python、Pillow、NumPy 作为运行时依赖使用，不把其许可证替换为 MIT。Apple Vision 为宿主系统能力，本项目只分发调用代码，不分发 Apple 模型。纸纹、撕纸边、星形、胶带、植物线条均为本项目程序绘制，不提取用户参考海报里的设计素材。
