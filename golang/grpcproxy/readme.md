# gRPC Proxy (modify protobuf requests) — Go Demo

This demo shows:

- A gRPC **Server** implementing a `Chat.Pipe` bidirectional stream.
- A gRPC **Server** implementing a `Chat.Stream` server-side streaming RPC.
- A gRPC **Proxy** exposing the same services to clients, connecting upstream to the real server.
- The **Proxy modifies incoming request messages** (protobuf payload) before forwarding to the server. Responses are relayed unchanged.
- High-throughput considerations: streaming design, backpressure, connection/window sizing, and avoiding unnecessary copies.

## Requirements

- Go 1.20+
- `protoc` and plugins:
- `protoc-gen-go` (google.golang.org/protobuf/cmd/protoc-gen-go)
- `protoc-gen-go-grpc` (google.golang.org/grpc/cmd/protoc-gen-go-grpc)

Install plugins:

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

## Generate code

```bash
./generate.sh
```

## Run

In separate terminals:

1. Start the **real server** (listens on :50055):

```bash
go run ./server
```

2. Start the **proxy** (listens on :50052, dials server :50055):

```bash
go run ./proxy
```

3. Run the **client** against the proxy (dials :50052):

```bash
go run ./client
```

You should see the server print messages whose `annotations` already include tags injected by the proxy. The client will receive responses echoed by the server.

The client also demonstrates usage of the new server-side streaming RPC `Chat.Stream` which receives a stream of messages from the server.

## Notes on performance

- The proxy uses **two dedicated goroutines** to shuttle messages in each direction; gRPC's HTTP/2 flow control provides backpressure.
- We set **initial window sizes**, **read/write buffer sizes**, and **max message sizes** to better handle large payloads.
- We **modify protobuf in-place** by writing to an `annotations` map (avoids copying large `payload`).
- If you need even higher throughput:
- Tune GOMAXPROCS, CPU pprof, and adjust window sizes further.
- Use **pinned, fixed-size pools** for any scratch buffers you add.
- Avoid per-message allocations in hot paths; prefer reusing slices when possible.
- Keep transformation logic minimal for the streaming path.

## gRPC Proxy Reference

This project demonstrates a transparent gRPC proxy that can modify protobuf requests in-flight. While this implementation is custom-built for demonstration purposes, production systems might consider using established libraries such as:

- [github.com/mwitkow/grpc-proxy](https://github.com/mwitkow/grpc-proxy) - A lightweight gRPC proxy library that proxies requests to backend gRPC servers with support for streaming RPCs

The mwitkow/grpc-proxy library provides a more generic and production-ready approach to building gRPC proxies, supporting all types of gRPC streaming patterns. This demo shows how to implement similar functionality with custom logic for request modification.