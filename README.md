# semgrep

## 链接
工具: [https://github.com/returntocorp/semgrep](https://github.com/returntocorp/semgrep)

[工具集成](./工具集成.md)

## 版本
semgrep: v0.100.0

## 自定义规则
规则只支持自定义：
[https://semgrep.dev/docs/writing-rules/overview/](https://semgrep.dev/docs/writing-rules/overview/)
参考链接编写规则yaml，并编写测试用例后测试，最后将测试用例和规则上传到rules/custom文件夹下

## 2025.2.17更新
鉴于[semgrep-rules](https://github.com/returntocorp/semgrep-rules)的License变更为[Semgrep Rules License v1.0](https://github.com/returntocorp/semgrep-rules/blob/develop/LICENSE)，该协议不允许分发这些规则，或将其作为服务提供给其他人，只能用户用于内部业务目的。TCA下架semgrep的所有官方规则，只保留自定义规则。