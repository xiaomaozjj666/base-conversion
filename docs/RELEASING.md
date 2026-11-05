# 发布指南

本项目通过 `.github/workflows/pypi.yml` 自动构建并发布 `base-conversion`。正式发布只接受 **`v<pyproject.toml 中的 project.version>`** 形式的 tag，例如版本 `1.0.0` 对应且仅对应 tag `v1.0.0`。发布使用 PyPI Trusted Publishing（GitHub OIDC），仓库中不需要、也不应保存 PyPI 密码或 API token。

## 一次性前置条件（需要用户在网页端操作）

以下配置不能由仓库文件代替，也不能由本地脚本自动完成。请使用有仓库管理权限和 PyPI 项目权限的账号操作。

### 1. GitHub：启用工作流与 TestPyPI 环境

1. 打开 GitHub 仓库 `xiaomaozjj666/base-conversion`，在 **Settings → Actions → General** 确认允许 GitHub Actions 和所需 actions。
2. 正式发布不绑定 GitHub environment，无需创建正式环境，也无需添加 `PYPI_API_TOKEN` secret。
3. 仅当需要 TestPyPI 时，在 **Settings → Environments → New environment** 创建名称严格为 `testpypi` 的环境。可按团队要求配置审查人或只允许 `main` 分支部署；环境名必须与工作流完全一致。
4. 不要把 PyPI 密码或长期 token 写入仓库、environment secrets 或 Actions secrets。OIDC 权限已由工作流的 `id-token: write` 声明。

### 2. PyPI：登记正式 Trusted Publisher

打开 [PyPI Trusted Publishing 管理页](https://pypi.org/manage/account/publishing/)：

- 若 `base-conversion` 项目尚不存在，在 **Pending publishers** 中新增；首次匹配的工作流发布成功后，PyPI 会创建项目。
- 若项目已存在，进入该项目的 **Manage → Publishing** 新增 publisher。

按下表填写，大小写和文件名必须完全一致：

| 字段 | 值 |
| --- | --- |
| PyPI Project Name（仅 pending publisher） | `base-conversion` |
| Owner | `xiaomaozjj666` |
| Repository | `base-conversion` |
| Workflow name | `pypi.yml` |
| Environment name | **留空**（正式 publish 未绑定 environment） |

如果 PyPI 中填写了 environment，而 GitHub 工作流没有同名 environment，OIDC 身份将不匹配，发布会失败。项目名是否可用及 pending publisher 是否已生效，也需要在该网页确认。

### 3. TestPyPI：单独登记 Trusted Publisher（可选）

[TestPyPI](https://test.pypi.org/) 与 PyPI 的账号、项目和 Trusted Publisher 配置相互独立。需要预发布时，打开 [TestPyPI Trusted Publishing 管理页](https://test.pypi.org/manage/account/publishing/)，按上一节方式新增 publisher：

| 字段 | 值 |
| --- | --- |
| PyPI Project Name（仅 pending publisher） | `base-conversion` |
| Owner | `xiaomaozjj666` |
| Repository | `base-conversion` |
| Workflow name | `pypi.yml` |
| Environment name | `testpypi` |

完成前，请先在 GitHub 网页创建同名 `testpypi` environment。正式 tag 不会触发 TestPyPI，手动运行也不会触发正式 PyPI。

## 每次正式发布

### 1. 准备发布提交

从最新 `main` 开始，确保工作区干净且待发布提交已经合并：

```bash
git switch main
git pull --ff-only origin main
git status --short
```

### 2. bump 版本号

编辑 `pyproject.toml` 的 `[project].version`，使用符合 PEP 440 的新版本号。PyPI 不允许覆盖或重复上传同一个版本，因此每次发布都必须递增版本；不要复用旧 tag。

可用以下命令读取将要发布的版本：

```bash
version="$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")"
printf '准备发布：%s\n' "$version"
```

### 3. 更新 CHANGELOG

编辑 `CHANGELOG.md`：把本次 `[Unreleased]` 中的变更整理到 `[<新版本>] - YYYY-MM-DD` 小节，并保留新的空 `[Unreleased]` 小节。说明新增、变更、修复和破坏性变更；同步更新文档和项目链接（如适用）。

版本号和 CHANGELOG 更新应在创建 tag 前进入同一个发布提交：

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): 准备 v${version} 发布"
```

### 4. 本地完整验证

在创建、推送 tag 前执行：

```bash
python -m pytest
python -m build
python scripts/verify_wheel.py dist
python -m twine check dist/*
```

如需在干净环境安装检查工具，可运行 `python -m pip install build twine`。上述检查全部通过后再继续；不要为通过检查删除测试或排除应打包文件。

### 5. 创建并核对 tag

tag 必须严格为 `v` 加上包版本，不能带空格、构建说明或其他后缀：

```bash
git tag -a "v${version}" -m "Release v${version}"
test "$(git describe --tags --exact-match)" = "v${version}"
git show --stat --oneline "v${version}"
```

### 6. 推送提交和 tag，触发自动发布

确认提交和 tag 均无误后，由维护者执行：

```bash
git push origin main
git push origin "v${version}"
```

tag push 会启动 **Actions → PyPI**：`build` 重新构建 sdist/wheel、执行 wheel 清单验证和 `twine check`，随后 `publish` 仅在 `github.ref_name == "v${version}"` 时通过 OIDC 发布。若 tag 与版本不一致，`publish` 会跳过，不会上传；应检查版本与 tag 后重新走发布流程，不要将不匹配视为已发布。

### 7. 发布后检查

1. 在 Actions 运行详情确认 `build` 和 `publish` 均成功，并核对构建哈希。
2. 打开 `https://pypi.org/project/base-conversion/<版本号>/` 核对版本、元数据和文件。
3. 在隔离环境安装验证：`python -m pip install "base-conversion==<版本号>"`。
4. 如使用 GitHub Releases，可基于同一 tag 创建 Release，并粘贴 CHANGELOG 对应小节。

上传成功后不能替换同版本文件。若发布物有问题，应修复并发布新版本；PyPI 的 yank 只用于按项目策略撤回有缺陷的发行版，不等同于删除或复用版本。

## 可选：手动发布 TestPyPI

1. 确保待测提交包含新的、TestPyPI 尚未使用的 `project.version`，并已完成上述一次性配置。
2. 打开 GitHub **Actions → PyPI → Run workflow**，选择待测 ref（通常为 `main`）并手动运行。
3. `build` 成功后，`testpypi` 任务使用 `testpypi` environment 的 OIDC 身份上传。该任务只接受 `workflow_dispatch`，任何正式 tag push 都不会触发它；反之，手动运行时正式 `publish` 必定跳过。
4. 在 `https://test.pypi.org/project/base-conversion/` 核对结果，可用 `python -m pip install --index-url https://test.pypi.org/simple/ "base-conversion==<版本号>"` 做隔离安装验证。

TestPyPI 同样不允许重复上传相同文件名/版本。若返回 “File already exists”，应递增版本后重试，不要删除正式 PyPI 文件或绕过版本检查。
