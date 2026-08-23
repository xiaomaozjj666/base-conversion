# base-conversion

> 🔀 **本仓库的进制转换功能已合并至 [programming-exercises](https://github.com/xiaomaozjj666/programming-exercises)（2026-08-22）。**
>
> 三语一致的新版转换器（支持负数与小数、任意精度整数）位于：
> - [`python/base_converter.py`](https://github.com/xiaomaozjj666/programming-exercises/blob/main/python/base_converter.py)（`int` + `Fraction` 精确小数）
> - [`js/base_converter.js`](https://github.com/xiaomaozjj666/programming-exercises/blob/main/js/base_converter.js)（`BigInt`，避免 2^53 精度丢失）
> - [`cpp/base_converter.cpp`](https://github.com/xiaomaozjj666/programming-exercises/blob/main/cpp/base_converter.cpp)（`long long` + `double`，教学示例）
>
> 本仓库保留 `src/benchmark.*`（三语算法耗时实测）与 `docs/images/benchmark.svg`（实测图表）作历史归档，不再维护。

## 快速开始（新位置）

```bash
git clone https://github.com/xiaomaozjj666/programming-exercises.git
cd programming-exercises
python3 python/base_converter.py 255 10 16     # -> FF
node    js/base_converter.js -123 10 2          # -> -1111011
./cpp/base_converter 10.5 10 16                 # -> A.8（先编译）

# 内置测试（37 个断言，CI 自动执行）
python3 python/base_converter.py --test
node    js/base_converter.js --test
./cpp/base_converter --test
```

## 归档内容

本仓库保留的 benchmark 源码与实测数据（2026-08-21 本机实测）：

| 算法 | C++（MSVC /O2） | Python 3.14 | Node.js 24 |
|---|---|---|---|
| 线性查找 O(n)，n = 10 000 | ≈0 ms* | 0.2112 ms | 0.0897 ms |
| 二分查找 O(log n)，n = 10 000 | ≈0 ms* | 0.0030 ms | 0.0073 ms |
| 冒泡排序 O(n²)，n = 1 000 | 0.4 ms | 19.30 ms | 5.14 ms |

\* C++ 线性/二分查找耗时低于 0.5 ms 计时精度。

![三语算法耗时实测图表](docs/images/benchmark.svg)

## 许可证

[MIT License](LICENSE)
