# base-conversion

<p align="center">
  <a href="https://github.com/xiaomaozjj666/base-conversion/actions/workflows/ci.yml"><img src="https://github.com/xiaomaozjj666/base-conversion/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/ruff-linted-261230" alt="Ruff" />
  <img src="https://img.shields.io/badge/tests-70%20passed-brightgreen" alt="Tests" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" />
</p>

**任意进制（2-62）精确转换库** — 大整数无精度损失、小数用分数精确算术、循环小数用括号循环节表示并可无损往返。

## 为什么用它

| 能力 | 内置 `int(s, base)` | 本库 |
|------|---------------------|------|
| 进制范围 | 2-36 | **2-62**（`0-9A-Za-z`，37 起大小写敏感） |
| 小数 | ✗ | ✓ **Fraction 精确**（二进制 `"0.1"` ≡ 1/2） |
| 循环小数 | ✗ | ✓ `1/3` ↔ `"0.(3)"` 无损往返 |
| 大整数 | ✓ | ✓（同一量级性能，见下） |
| CLI | ✗ | ✓ `baseconv` 一条命令 |

浮点实现的转换在 `0.1` 这类值上必然引入二进制近似误差；本库全程使用 `int` 与 `fractions.Fraction`，**任何输入的转换结果都是数学上精确的**。

## 安装

```bash
git clone https://github.com/xiaomaozjj666/base-conversion.git
cd base-conversion
python -m pip install .
```

> 尚未发布到 PyPI；从源码安装（零运行时依赖，仅标准库）。

## 快速开始

```python
>>> from base_conversion import to_base, to_decimal
>>> to_base(255, 16)
'FF'
>>> to_decimal("ff", 16)          # 2-36 进制大小写不敏感
255
>>> to_decimal("0.1", 2)          # 精确：不是 0.5 的浮点近似
Fraction(1, 2)
>>> to_base(Fraction(1, 3), 10)   # 循环小数 → 括号循环节
'0.(3)'
>>> to_decimal("0.(3)", 10)       # 且可无损解析回来
Fraction(1, 3)
>>> to_base(10**100 + 7, 62)      # 大整数无损
'4Wm5fNnOOhv5...'
```

命令行：

```bash
baseconv 255 10 16           # → FF
baseconv -- -123 10 2        # → -1111011（负数用 -- 分隔）
baseconv -n 0.1 -f 2 -t 10   # → 0.5（选项式，负数推荐）
```

## API

| 函数 | 签名 | 说明 |
|------|------|------|
| `to_decimal` | `(s: str, base: int) → int \| Fraction` | 解析 `base` 进制字符串；支持 `±`、小数点、括号循环节 |
| `to_base` | `(value: int \| Fraction \| float, base: int) → str` | 渲染为目标进制；非整数 float 拒绝（精度陷阱） |
| `decimal_to_base` / `base_to_decimal` | 同上 | 旧 API 兼容别名 |
| `decimal_to_binary` / `binary_to_decimal` | — | 二进制快捷方式 |
| `decimal_to_hex` / `hex_to_decimal` | — | 十六进制快捷方式（输出大写） |

常量：`BASE_MIN=2`、`BASE_MAX=62`、`DIGITS`（62 字符表）。

### 文法（`to_decimal` 接受的输入）

```
[sign] digits [ "." digits ] [ "(" digits ")" ]
```

- 2-36 进制大小写不敏感；37-62 大小写敏感（`'A'`=10、`'a'`=36）；
- `".5"`、`"5."` 合法，单独的 `"."` 非法；
- 循环节括号必须收尾、非空、不嵌套：`"0.(3)"`、`"0.1(6)"` 合法，`"0.()"`、`"0.(3"` 非法。

### 错误处理

- 非法字符 / 文法错误 → `ValueError`（信息含具体字符与进制）；
- 进制越界（非 2-62）→ `ValueError`；非 int 进制或 `bool` → `TypeError`；
- `to_base` 收到非整数 `float` → `ValueError`（提示改用 `str` 或 `Fraction`——浮点表示本身有精度损失，转换它没有意义）。

## 与内置的性能关系

核心整数路径就是「除基取余 / 乘基累加」，与内置 `int(s, base)`、`format(n, 'x')` 同一数量级——测试含 500 例随机大整数交叉验证（对照内置 `int(s, base)`）与 300 例随机 Fraction 往返性质测试，10^60 量级毫秒级完成。本库的定位差异在**能力**（62 进制、精确小数、循环节）而非速度；极限吞吐场景请直接用内置函数。

## 历史与归档

本仓库早期是三语言（C++ / Python / JS）进制转换 + 查找排序基准的对比实现，2026-09 归档整理后：

- Python 部分重写为本库（2-62 进制、Fraction 精确小数、CLI、70 个测试）；
- 三语言基准脚本保留在 [`archive/`](archive/)（历史快照，不再维护）；
- 查找/排序算法练习与多语言题解迁移至 [programming-exercises](https://github.com/xiaomaozjj666/programming-exercises)。

历史 benchmark 实测数据（2026-08-21 本机，三语言算法对比）见 [`docs/images/benchmark.svg`](docs/images/benchmark.svg)。

## 开发

```bash
python -m pip install -e ".[dev]"
pytest                 # 70 个测试（含随机交叉验证与往返性质测试）
ruff check src tests   # 代码检查
mypy src               # 类型检查
python -m build        # 构建分发包
```

CI 在 Python 3.9-3.13 矩阵上运行测试，并执行 lint、类型检查与构建验证。

## License

[MIT](LICENSE)
