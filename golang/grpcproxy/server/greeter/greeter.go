package greeter

import (
	"context"

	demo "github/panlq/xbook/grpcproxy/gen/proto"
)

func NewGreeterServer() demo.GreeterServer {
	return &greeterServer{}
}

type greeterServer struct {
	demo.UnimplementedGreeterServer
}

func (g *greeterServer) SayHello(ctx context.Context, req *demo.HelloRequest) (*demo.HelloReply, error) {
	return &demo.HelloReply{Message: "Hello From Greeter " + req.Name}, nil
}
