# archive/ — 历史快照，勿参照

**本目录是 2026-09 归档整理时冻结的历史快照，不属于本库实现，也不再维护。请勿引用、复制或据此修改 `src/`。**

- 这里的脚本实现的是早期的 **2-36 进制**转换（数字表仅 `0-9A-Z`，大小写不敏感），与主库当前的 **2-62 进制**（`0-9A-Za-z`，37 起大小写敏感）、`Fraction` 精确小数和括号循环节语义**已经分叉**。相同输入在两边可能得到不同结果，不能互相参照或当作回归基准。
- 文件只为保留当时的算法对比与计时记录，依赖旧环境，可能无法在当前环境中直接运行。
- 现行实现见 [`src/base_conversion/`](../src/base_conversion/)，现行文档见仓库根 [`README.md`](../README.md)，历史基准实测数据见 [`docs/images/benchmark.svg`](../docs/images/benchmark.svg)。
- 本目录不接受任何功能变更或修复；进制转换的后续演进已迁入 [programming-exercises](https://github.com/xiaomaozjj666/programming-exercises)。
