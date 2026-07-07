---
outline: deep
---

# Windows 下安全软件误报说明

在 Windows 上下载或运行 Termark 时，部分安全软件可能会提示风险、拦截安装包，或把程序识别为可疑文件。

Termark Windows 版本目前没有购买代码签名证书，因此系统和安全软件可能无法通过证书确认发布者身份。同时，Termark 的后端和部分本地能力使用 Go 编写，Go 编译出的二进制文件在 Windows 上偶尔会被杀毒软件误报。

Go 官方 FAQ 中也提到过类似情况：[Why does my virus-scanning software think my Go distribution or compiled binary is infected?](https://go.dev/doc/faq#virus)

官方说明的核心意思是：这种情况在 Windows 机器上比较常见，并且 “almost always a false positive”；商业杀毒软件有时会被 “the structure of Go binaries” 影响判断。

如果你遇到这类提示，可以先确认以下几点：

- 从 Termark 官方渠道下载安装包，不要使用第三方重新打包的文件。
- 确认下载文件没有被浏览器、代理软件或其他下载工具篡改。
- 如果安全软件支持上报误报，可以把检测结果反馈给安全软件厂商。
- 如果你仍然不确定文件来源或安全性，请先不要继续运行。

未购买代码签名证书和 Go 二进制误报，并不等于程序一定有风险；但安全提示也不应该被无条件忽略。建议优先确认下载来源，再根据安全软件的具体检测结果处理。
