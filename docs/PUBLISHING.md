# 首次发布指南

目标：以 `visual-skills` 为仓库名，发布 `v0.1.0-experimental` 预发布版本。使用者能看到效果、安装一个风格，并了解当前验证边界。

## 发布前本地检查

用 skill 的 bootstrap 返回的 Python 执行：

```bash
python -m unittest discover -s tests -v
python scripts/check_release.py
python scripts/package.py
git status --short
```

检查脚本核对冻结清单、案例数量和版本材料；不会代替看图或用户验收。打包后的 ZIP 在 `dist/`。完整运行素材保留在本地，不随仓库发布。`.github/workflows/checks.yml` 仅验证程序和打包，不把 CI 通过等同审美通过。

## 登录并创建仓库

以下命令在仓库目录执行。首次需要维护者在浏览器完成 GitHub 登录：

```bash
gh auth login --hostname github.com --git-protocol https --web
gh api user --jq .login
```

确认输出是预期的个人账号。组织仓库应显式使用 `组织名/visual-skills`，不要猜测目标。

```bash
gh repo create visual-skills --public --source=. --remote=origin --push --description '给 Agent 一张照片，做成拼贴海报。Photo-to-poster skills for agents.'
gh repo view --web
```

如果远端已有同名项目，先检查内容与归属，不覆盖或强推。确认首页图片和文档可访问，查看 Actions 的检查结果。首次发布日期在成功后再写入 CHANGELOG。

## 发布预发布版

先确认本地工作区干净、提交已推送且远端检查通过，再对同一提交打包和标记版本：

```bash
python scripts/package.py
git tag -a v0.1.0-experimental -m 'First experimental photo paper collage skill'
git push origin v0.1.0-experimental
gh release create v0.1.0-experimental dist/photo-paper-collage-0.1.0-experimental.zip dist/visual-style-skills-0.1.0-experimental.zip dist/SHA256SUMS.json --verify-tag --prerelease --title '0.1.0-experimental · 摄影剪贴拼贴' --notes-file docs/RELEASE-0.1.0.md
```

发布后从 Release 下载独立 skill 包到新目录，验证校验值和安装步骤。把真实仓库链接提供给试用者，请他们记录系统、Agent、首次安装是否成功、主体保真与版式是否可用。优先改善安装和失败处理，再引入第二种风格。

命令依据：[GitHub 创建仓库](https://cli.github.com/manual/gh_repo_create)、[发布 Release](https://cli.github.com/manual/gh_release_create)、[Python 自动检查](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)。
