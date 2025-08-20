package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"

	demo "github/panlq/xbook/grpcproxy/gen/proto"
	"github/panlq/xbook/grpcproxy/server/greeter"
)

type chatServer struct {
	demo.UnimplementedChatServer
}

func (s *chatServer) SayHello(ctx context.Context, in *demo.HelloRequest) (*demo.HelloReply, error) {
	return &demo.HelloReply{
		Message: "Hello from server " + in.Name,
	}, nil
}

func (s *chatServer) Stream(in *demo.HelloRequest, stream demo.Chat_StreamServer) error {
	ctx := stream.Context()
	for i := 1; i <= 5; i++ {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			reply := &demo.HelloReply{
				Message: fmt.Sprintf("Hello %s, this is message #%d from server stream", in.Name, i),
			}
			if err := stream.Send(reply); err != nil {
				return err
			}
			// Sleep to simulate some work
			time.Sleep(1 * time.Second)
		}
	}
	return nil
}

func (s *chatServer) Pipe(stream demo.Chat_PipeServer) error {
	ctx := stream.Context()
	for {
		msg, err := stream.Recv()
		if err != nil {
			return err // client closed or transport error
		}

		// Server can also annotate if desired (for demo visibility).
		if msg.Annotations == nil {
			msg.Annotations = make(map[string]string, 1)
		}
		msg.Annotations["server"] = "echo"

		// Echo back to client unchanged (proxy is only modifying inbound requests).
		if err := stream.Send(msg); err != nil {
			return err
		}

		// Simulate light work to keep the pipeline busy and observable.
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(1 * time.Millisecond):
		}
	}
}

func main() {
	addr := flag.String("addr", ":50055", "listen address")
	flag.Parse()

	lis, err := net.Listen("tcp", *addr)
	if err != nil {
		log.Fatalf("listen: %v", err)
	}

	// Server-side performance/keepalive tuning.
	ka := keepalive.ServerParameters{
		Time:    2 * time.Minute,
		Timeout: 20 * time.Second,
	}
	grpcServer := grpc.NewServer(
		grpc.KeepaliveParams(ka),
		grpc.MaxRecvMsgSize(64<<20), // 64 MiB
		grpc.MaxSendMsgSize(64<<20),
	)

	demo.RegisterChatServer(grpcServer, &chatServer{})
	// 注册Greeter服务，直接使用greeter包中的NewGreeterServer函数
	demo.RegisterGreeterServer(grpcServer, greeter.NewGreeterServer())
	fmt.Println("[server] listening on", *addr)
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("serve: %v", err)
	}
}
