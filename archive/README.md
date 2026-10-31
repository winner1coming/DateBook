# 历史单文件交付

[DateBook_AllInOne_2026-11-01.py](DateBook_AllInOne_2026-11-01.py) 保留首次交付的57文件快照，原始提交 `8c84778` 也保留在 Git 历史中。

当前开发入口已经是仓库根目录的 Gradle 工程。不要编辑旧快照后覆盖 `app/`、`core/` 或新的文档布局；旧快照里的目录说明和测试报告描述的是当时的单文件交付，不代表当前仓库入口。

仅需要历史对照时运行：

```bash
python3 archive/DateBook_AllInOne_2026-11-01.py --verify
python3 tools/verify_bundle.py archive/DateBook_AllInOne_2026-11-01.py
```
