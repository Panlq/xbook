#!/usr/bin/env bash
set -euo pipefail

mkdir -p gen
auto_out=gen

protoc \
  --go_out="${auto_out}" --go_opt=paths=source_relative \
  --go-grpc_out="${auto_out}" --go-grpc_opt=paths=source_relative \
  proto/chat.proto proto/greeter.proto

echo "Generated code into ${auto_out}/"