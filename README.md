# base-conversion

> 🔀 **本仓库的进制转换功能已合并至 [programming-exercises](https://github.com/xiaomaozjj666/programming-exercises)（2026-08-22）。**
>
> 三语一致的新版转换器（支持负数与小数、任意精度整数）位于：
> - [`python/base_converter.py`](https://github.com/xiaomaozjj666/programming-exercises/blob/main/python/base_converter.py)（`int` + `Fraction` 精确小数）
> - [`js/base_converter.js`](https://github.com/xiaomaozjj666/programming-exercises/blob/main/js/base_converter.js)（`BigInt`，避免 2^53 精度丢失）
> - [`cpp/base_converter.cpp`](https://github.com/xiaomaozjj666/programming-exercises/blob/main/cpp/base_converter.cpp)（`long long` + `double`，教学示例）
>
> 本仓库内容已全部并入 [programming-exercises](https://github.com/xiaomaozjj666/programming-exercises)：进制转换 → `python|js|cpp/base_converter.*`，benchmark 源码与图表 → [`benchmark/`](https://github.com/xiaomaozjj666/programming-exercises/tree/main/benchmark)（2026-08-29 迁移）。本仓库纯作历史归档，不再维护。

## 快速开始（新位置）

```bash
git clone https://github.com/xiaomaozjj666/programming-exercises.git
cd programming-exercises
python3 python/base_converter.py 255 10 16     # -> FF
node    js/base_converter.js -123 10 2          # -> -1111011
./cpp/base_converter 10.5 10 16                 # -> A.8（先编译）

# 内置测试（39 个断言，CI 自动执行）
python3 python/base_converter.py --test
node    js/base_converter.js --test
./cpp/base_converter --test
```

## 归档内容

本仓库的历史 benchmark 实测数据（2026-08-21 本机实测；源码已并入 programming-exercises 的 [`benchmark/`](https://github.com/xiaomaozjj666/programming-exercises/tree/main/benchmark) 目录）：

| 算法 | C++（MSVC /O2） | Python 3.14 | Node.js 24 |
|---|---|---|---|
| 线性查找 O(n)，n = 10 000 | ≈0 ms* | 0.2112 ms | 0.0897 ms |
| 二分查找 O(log n)，n = 10 000 | ≈0 ms* | 0.0030 ms | 0.0073 ms |
| 冒泡排序 O(n²)，n = 1 000 | 0.4 ms | 19.30 ms | 5.14 ms |

\* C++ 线性/二分查找耗时低于 0.5 ms 计时精度。

![三语算法耗时实测图表](docs/images/benchmark.svg)

> 🛠 2026-08-29 归档后做过一次健壮性修复：三语转换器负数/小数解析与错误处理加固，CI 回归用例 6 → 10（详见 `git log`），此后继续封存不再维护。

## 本地运行（归档版）

```bash
# 三语内置测试（进制转换断言 + 查找/排序验证 + 耗时实测）
python3 src/benchmark.py --test
node    src/benchmark.js              # 不带参数即运行测试
g++ -O2 -std=c++11 -Wall -Wextra src/benchmark.cpp -o benchmark && ./benchmark

# C++ JSON 批量用例（格式见 .github/workflows/ci.yml）
./benchmark cases.json

# 进制转换（负数、小数解析三语一致；py/js 的转出仅支持整数）
python3 src/benchmark.py --convert --number=-5  --from-base=10 --to-base=2    # -> -101
python3 src/benchmark.py --convert --number=0.1 --from-base=2  --to-base=10   # -> 0.5
node    src/benchmark.js --convert -101 2 10                                  # -> -5
node    src/benchmark.js --convert 0.1 2 10                                   # -> 0.5
```

> 以 `-` 开头的参数值请用 `--number=-5` 等号写法，argparse 会把裸的 `-5` 当作选项。

## 许可证

[MIT License](LICENSE)
