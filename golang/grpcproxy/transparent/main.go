package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"net"

	proxy "github.com/mwitkow/grpc-proxy/proxy"
	"google.golang.org/grpc"

	pb "github/panlq/xbook/grpcproxy/gen/proto"
)

const backendAddr = "localhost:50055"

// 特殊实现：只拦截 SayHello，修改请求体后再调用 backend
type chatProxy struct {
	conn grpc.ClientConnInterface
	pb.UnimplementedChatServer
}

var director = func(ctx context.Context, fullMethodName string) (context.Context, grpc.ClientConnInterface, error) {
	// 这里你可以针对不同的 fullMethodName 做路由/请求头修改的逻辑
	// md, ok := metadata.FromIncomingContext(ctx)

	// if ok {
	//     // Decide on which backend to dial
	//     if val, exists := md[":authority"]; exists && val[0] == "staging.api.example.com" {
	//         // Make sure we use DialContext so the dialing can be cancelled/time out together with the context.
	//         conn, err := grpc.DialContext(ctx, "api-service.staging.svc.local", grpc.WithCodec(proxy.Codec()))
	//         return ctx, conn, err
	//     } else if val, exists := md[":authority"]; exists && val[0] == "api.example.com" {
	//         conn, err := grpc.DialContext(ctx, "api-service.prod.svc.local", grpc.WithCodec(proxy.Codec()))
	//         return ctx, conn, err
	//     }
	// }

	fmt.Println("fullMethodName:", fullMethodName)
	conn, err := grpc.DialContext(ctx, backendAddr, grpc.WithInsecure())
	if err != nil {
		return nil, nil, err
	}
	return ctx, conn, nil
}

func (p *chatProxy) Pipe(stream pb.Chat_PipeServer) error {
	// 直接透传
	return proxy.TransparentHandler(director)(stream.Context(), stream)
}

func (p *chatProxy) Stream(req *pb.HelloRequest, stream pb.Chat_StreamServer) error {
	// 透传 Server-side Streaming 需要透传 请求参数
	// return proxy.TransparentHandler(director)(stream.Context(), stream)
	// 1. 建立到后端的 stream
	backend, err := pb.NewChatClient(p.conn).Stream(stream.Context(), req)
	if err != nil {
		return err
	}

	// 2. 透传后端响应
	for {
		resp, err := backend.Recv()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return err
		}

		// 这里你可以修改 resp 再转发
		resp.Message = "[proxy modified] " + resp.Message

		if err := stream.Send(resp); err != nil {
			return err
		}
	}
}

func (p *chatProxy) SayHello(ctx context.Context, req *pb.HelloRequest) (*pb.HelloReply, error) {
	log.Printf("[Proxy] Intercept SayHello: original=%s", req.Name)

	// 修改请求体
	req.Name = "Modified-by-proxy-" + req.Name

	// 调用 backend
	return pb.NewChatClient(p.conn).SayHello(ctx, req)
}

func main() {
	lis, err := net.Listen("tcp", ":50052")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	// Director 用于透明透传：不在代理中实现的方法，会自动转到 backend
	grpcServer := grpc.NewServer(
		grpc.CustomCodec(proxy.Codec()),
		grpc.UnknownServiceHandler(proxy.TransparentHandler(director)),
	)

	cc, err := grpc.Dial(backendAddr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("Proxy serve error: %v", err)
	}
	defer cc.Close()

	// 只注册我们要改的部分接口，这里是直接注册的 chatServe 所以需要实现他下面的所有接口
	// TODO：看看有没有什么其他方式可以只注册拦截 需要 重写的 server. 的接口
	pb.RegisterChatServer(grpcServer, &chatProxy{conn: cc})

	log.Println("[Proxy] listening on :50052")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Proxy serve error: %v", err)
	}
}
