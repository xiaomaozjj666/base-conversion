# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式，并使用符合 PEP 440 的版本号。

## [Unreleased]

## [1.0.1] - 2026-11-06

### Fixed

- 修复 CLI 对负数值参数的解析，负数进制转换按预期工作。
- 补齐 PEP 561 打包，`py.typed` 类型标记随 wheel 分发。

### Added

- 接入 PyPI Trusted Publishing 自动发布流程，附发布指南（`docs/RELEASING.md`）。

### Changed

- CI：Python 3.9 测试固定到 `ubuntu-22.04`（新镜像不再提供 3.9）。

## [1.0.0] - 2026-11-05

### Added

- 支持 2-62 进制的大整数精确转换，以及基于 `Fraction` 的小数精确转换。
- 支持循环小数的括号循环节表示和无损往返解析。
- 提供 `baseconv` 命令行入口、旧 API 兼容别名和 PEP 561 类型标记。
- 提供覆盖转换、命令行和 wheel 打包内容的自动化测试。

[Unreleased]: https://github.com/xiaomaozjj666/base-conversion/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/xiaomaozjj666/base-conversion/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/xiaomaozjj666/base-conversion/releases/tag/v1.0.0
