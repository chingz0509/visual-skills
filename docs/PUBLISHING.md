# 发布维护

用户只需要照片拼贴的独立安装包。开发源码由 GitHub 提供，不另做混合开发包。

发布前，在仓库目录执行：

```bash
python -m unittest discover -s tests -v
python scripts/check_release.py
python scripts/check_privacy.py --history
python scripts/package.py
```

使用已安装 Pillow、NumPy 的 Python。打包只读取明确允许、已纳入 Git 的技能文件；不遍历整个工作目录。输出为 `dist/photo-paper-collage-0.1.0-experimental.zip` 和 `SHA256SUMS.json`。发布这两项即可，保持版本、提交、Release 文案和校验值一致。

重新下载已发布安装包，核对校验值，并在临时目录解压，确认 `photo-paper-collage/SKILL.md` 以及字体、脚本完整。检查不能代替真实安装、看图和用户验收。

公开目录保留代码、许可、成品、失败案例、必要的计划与验收记录。个人照片、原始 OCR、图层运行清单、宿主路径、依赖缓存、环境变量、宣传草稿和浏览器数据留在仓库外。完整生成包只交付给该任务的用户，不自动公开。

如发现密钥泄露，先撤销密钥，再处理历史和发布包。删除当前文件不会删除 Git 历史；改写共享历史需另行评估与维护者授权。对没有发现敏感信息的旧提交，不为目录精简强推历史。
