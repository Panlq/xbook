## socket-example 协议约定

> [4 字节大端长度字段][内容]

## how to run

### py socket

> python3 py-example/server.py
>
> python3 py-example/client.py

### go socket

> go run go-example/server/server.go
>
> go run go-example/server/client.go

### py - go socket

> go run go-example/server/server.go
>
> python3 py-example/client.py

> python3 py-example/server.py
>
> go run go-example/client/client.go

## 1. 为什么 tcp 通信右粘包问题？

TCP 协议粘包问题是因为应用层协议开发者的错误设计导致的，他们忽略了 TCP 协议数据传输的核心机制 — 基于字节流，其本身不包含消息、数据包等概念，所有数据的传输都是流式的，需要应用层协议自己设计消息的边界，即消息帧（Message Framing），我们重新回顾一下粘包问题出现的核心原因：

1. TCP 协议是基于字节流的传输层协议，其中不存在消息和数据包的概念；
2. 应用层协议没有使用基于长度或者基于终结符的消息边界，导致多个消息的粘连；

详细》》》[TCP 特性介绍](../tcp三次握手和四次挥手.md)

## 2. 为什么只有长度需要大小端转换？

[脑残式网络编程入门(九)：面试必考，史上最通俗大小端字节序详解](http://www.52im.net/thread-3101-1-1.html)

消息长度字段需要转换大小端（Big-endian），是因为它是整数类型的数据，在不同 CPU 架构下解释方式不同；而内容是字节流（byte stream），不需要转换。

长度字段通常是像 `uint32`、`int` 这样的整型数值。

- 整型数据在内存中存储的方式受 CPU 架构影响（大端 or 小端）。
- 如果发送方和接收方使用不同的字节序，就会导致解析出错误的长度值。
- 所以在网络协议中， **长度字段必须使用统一的字节序格式传输（通常是 Big-endian）** 。

### **为什么“内容”部分不需要考虑大小端？**

因为内容本身是一个 **字节流（byte stream）** ，它不是一个整型数字，而是原始的字节序列。

- 比如字符串 `"hello"` 被编码成 `[h][e][l][l][o]`，每个字符就是一个字节；
- 字节流本身没有“高位低位”的概念，顺序就是从头到尾逐个读取；
- 接收方只要按顺序读取这些字节，再根据约定的编码方式（如 UTF-8）还原成字符串即可。

## 协议设计中的常见做法

| 数据类型                      | 是否需要处理大小端 | 说明                     |
| ----------------------------- | ------------------ | ------------------------ |
| 长度字段（如 uint16, uint32） | ✅ 是              | 必须统一使用 Big-endian  |
| 数值类型字段（如 int, float） | ✅ 是              | 根据协议要求决定是否统一 |
| 字符串（UTF-8 / ASCII）       | ❌ 否              | 字节流无需处理           |
| JSON、Protobuf 等结构化数据   | ❌ 否              | 内部已封装好             |
| 图片、文件等二进制数据        | ❌ 否              | 原始字节流               |
