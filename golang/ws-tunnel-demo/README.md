# WebSocket 隧道转发 Demo

这个 demo 展示了如何使用 WebSocket 实现一个简单的隧道转发服务。

## 架构

该 demo 包含三个组件：

1. 本地服务 (端口 8080)
   - 提供一个简单的 HTTP 接口 `/hello`
   - 模拟实际场景中的目标服务

2. 隧道服务端 (端口 3000)
   - 接收 WebSocket 连接
   - 将请求转发到本地服务
   - 将响应通过 WebSocket 返回

3. 隧道客户端 (端口 4000)
   - 与隧道服务端建立 WebSocket 连接
   - 提供 HTTP 接口接收外部请求
   - 通过 WebSocket 转发请求和响应

## 运行方式

1. 启动服务：
   ```bash
   go run main.go
   ```

2. 测试转发：
   ```bash
   curl http://localhost:4000/proxy/hello
   ```
   应该会收到来自本地服务的响应："Hello from local server!"

## 数据流

1. 外部请求打到隧道客户端的 4000 端口
2. 隧道客户端通过 WebSocket 将请求转发给隧道服务端
3. 隧道服务端将请求转发到本地 8080 端口的服务
4. 响应按照相反的路径返回给请求方

## 注意事项

- 这是一个简化的 demo，实际使用时需要添加错误处理、重连机制等
- WebSocket 连接断开时需要优雅处理
- 生产环境中需要添加安全认证机制