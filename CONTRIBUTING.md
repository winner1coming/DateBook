# 开发与协作约定

先读 [构建指南](docs/development/BUILD_GUIDE.md)、[当前架构](docs/technical/ARCHITECTURE.md) 和 [实现状态](docs/development/IMPLEMENTATION_STATUS.md)。当前工作不需要后端、邮箱、云库或HTTP服务。

1. 业务源码以 `app/` 和 `core/` 为准；`archive/` 是不可变历史快照，不从它覆盖新工程。
2. 每次变更写清需求、文件、数据/权限影响与测试结果。产品规则变动先确认并更新PRD/需求与ADR。
3. 保持core不依赖Android/app；不得在UI跨代缓存Room连接、绕过服务层校验或静默重建坏库。
4. schema变更必须提供Migration和测试；文件协议变更必须考虑版本及兼容，不静默接受未知关键字段。
5. 保护三级树、同本、唯一寄语、epoch/revision、版本冲突、幂等与副作用票据。
6. 不加入网络、账号、广告、遥测或远程崩溃SDK；额外权限/外部数据流须单独评审。
7. 不提交本机路径、用户数据、备份、照片、密钥、令牌、构建缓存或签名文件。
8. PR应附实际执行的测试，未执行项明确记录；禁止用删除断言/修改预期来掩盖故障。

```bash
python3 tools/verify_delivery.py
python3 tools/verify_repository.py
./gradlew :core:test :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
./gradlew :app:connectedDebugAndroidTest
```

仅本次目录迁移使用 `python3 tools/verify_repository.py --check-baseline` 核对源码与首次快照一致。默认检查及CI不启用历史字节一致性限制，后续可以正常实现和修改业务代码；每次修改仍需评审和回归。发布前完成 [发布清单](docs/testing/RELEASE_CHECKLIST.md)。
