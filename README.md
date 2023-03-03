# semgrep

## 链接
工具: [https://github.com/returntocorp/semgrep](https://github.com/returntocorp/semgrep)

工具规则: [https://github.com/returntocorp/semgrep-rules](https://github.com/returntocorp/semgrep-rules)

[工具集成](./工具集成.md)

## 版本
semgrep: v0.100.0

semgrep-rules: Aug 8, 2022

## 规则
目前规则包括两部分：
- semgrep-rules：semgrep标准规则，语言包括c/go/java/js/ts/php/python/ruby/html/yaml，以及通用语言generic和contrib
- njsscan[https://github.com/ajinabraham/njsscan]：js安全规则 [https://semgrep.dev/p/nodejsscan](https://semgrep.dev/p/nodejsscan)

## 自定义规则
[https://semgrep.dev/docs/writing-rules/overview/](https://semgrep.dev/docs/writing-rules/overview/)
参考链接编写规则yaml，并编写测试用例后测试，最后将测试用例和规则上传到rules/custom文件夹下
