# 页面原型与设计资源

[UI_PROTOTYPE_v1.1.html](UI_PROTOTYPE_v1.1.html) 是设计阶段的16页交互原型，可下载后在浏览器打开；GitHub 的普通文件页不会直接运行其中的脚本。原型不是 Android App，也不执行真实保存、通知或权限操作。

`assets/` 保存 TD 原件中提取的10个 UI 插图，技术设计阅读版直接引用它们。真实 Compose 页面位于 [app/ui](../../app/src/main/kotlin/cn/datebook/app/ui/)，以代码和设备运行结果为准。

必须保持的交互：一级详情只列二级；进入二级才列三级；三级不可继续新增。搜索列表允许显示跨层级结果，但不能改变详情页的直属约束。
