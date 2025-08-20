package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"time"

	"golang.org/x/sync/errgroup"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/keepalive"

	demo "github/panlq/xbook/grpcproxy/gen/proto"
)

// generateID creates a compact random hex id for tagging.
func generateID() string {
	var b [8]byte
	_, _ = rand.Read(b[:])
	return hex.EncodeToString(b[:])
}

type proxyServer struct {
	demo.UnimplementedChatServer
	up demo.ChatClient
}

func (p *proxyServer) SayHello(ctx context.Context, req *demo.HelloRequest) (*demo.HelloReply, error) {
	// Forward the request to upstream
	return p.up.SayHello(ctx, req)
}

// Stream implements the server-side streaming method, acting as a proxy endpoint for clients.
func (p *proxyServer) Stream(in *demo.HelloRequest, down demo.Chat_StreamServer) error {
	// Forward the request to upstream and get the stream
	upstream, err := p.up.Stream(context.Background(), in)
	if err != nil {
		return err
	}
	defer func() {
		if closeable, ok := upstream.(interface{ Close() error }); ok {
			_ = closeable.Close()
		}
	}()

	// Relay all messages from upstream to downstream
	for {
		msg, err := upstream.Recv()
		if err != nil {
			if err == io.EOF {
				return nil
			}
			return err
		}

		// Send message to client
		if err := down.Send(msg); err != nil {
			return err
		}
	}
}

// Pipe implements the same method as the real server, acting as a proxy endpoint for clients.
// It modifies ONLY inbound requests before forwarding upstream; responses pass through unchanged.
func (p *proxyServer) Pipe(down demo.Chat_PipeServer) error {
	ctx := down.Context()

	// Dial an upstream stream for this session.
	upstream, err := p.up.Pipe(ctx)
	if err != nil {
		return err
	}

	g, ctx := errgroup.WithContext(ctx)

	// Downstream(client)->Proxy->Upstream(server): Recv then modify then Send.
	g.Go(func() error {
		defer func() { _ = upstream.CloseSend() }()
		for {
			msg, err := down.Recv()
			if err != nil {
				if err == io.EOF {
					return nil
				}
				return err
			}

			// *** Modify protobuf request in-place (no payload copy) ***
			if msg.Annotations == nil {
				msg.Annotations = make(map[string]string, 4)
			}
			// Inject fast-to-generate tags.
			msg.Annotations["proxy.tag"] = "ingress"
			msg.Annotations["proxy.req.id"] = generateID()
			msg.Annotations["proxy.ts"] = fmt.Sprintf("%d", time.Now().UnixNano())

			if err := upstream.Send(msg); err != nil {
				return err
			}
		}
	})

	// Upstream(server)->Proxy->Downstream(client): pure relay, no mutation.
	g.Go(func() error {
		for {
			msg, err := upstream.Recv()
			if err != nil {
				if err == io.EOF {
					return nil
				}
				return err
			}
			if err := down.Send(msg); err != nil {
				return err
			}
		}
	})

	return g.Wait()
}

func main() {
	listenAddr := flag.String("listen", ":50052", "proxy listen address")
	upstreamAddr := flag.String("upstream", "127.0.0.1:50055", "upstream server address")
	flag.Parse()

	// Listener for downstream clients.
	lis, err := net.Listen("tcp", *listenAddr)
	if err != nil {
		log.Fatalf("listen: %v", err)
	}

	// Upstream client dial options with throughput tuning.
	dialOpts := []grpc.DialOption{
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithInitialWindowSize(1 << 22),     // ~4 MiB stream window
		grpc.WithInitialConnWindowSize(1 << 24), // ~16 MiB conn window
		grpc.WithWriteBufferSize(1 << 20),
		grpc.WithReadBufferSize(1 << 20),
	}

	conn, err := grpc.Dial(*upstreamAddr, dialOpts...)
	if err != nil {
		log.Fatalf("dial upstream: %v", err)
	}
	defer conn.Close()

	srv := grpc.NewServer(
		grpc.MaxRecvMsgSize(64<<20),
		grpc.MaxSendMsgSize(64<<20),
		grpc.KeepaliveParams(keepalive.ServerParameters{Time: 2 * time.Minute, Timeout: 20 * time.Second}),
	)
	demo.RegisterChatServer(srv, &proxyServer{up: demo.NewChatClient(conn)})
	fmt.Println("[proxy] listening on", *listenAddr, "-> upstream", *upstreamAddr)
	if err := srv.Serve(lis); err != nil {
		log.Fatalf("serve: %v", err)
	}
}
