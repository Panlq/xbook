package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"math/rand"
	"os"
	"strings"
	"time"

	"google.golang.org/grpc"

	demo "github/panlq/xbook/grpcproxy/gen/proto"
)

func main() {
	proxyAddr := flag.String("addr", "127.0.0.1:50052", "proxy address")
	qps := flag.Int("qps", 500, "messages per second to send")
	payloadSize := flag.Int("payload", 1024, "payload size in bytes")
	flag.Parse()

	conn, err := grpc.Dial(*proxyAddr, grpc.WithInsecure(), grpc.WithBlock(), grpc.WithTimeout(5*time.Second))
	if err != nil {
		log.Fatalf("dial: %v", err)
	}
	defer conn.Close()

	cli := demo.NewChatClient(conn)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Unary 调用
	resp, _ := cli.SayHello(context.Background(), &demo.HelloRequest{Name: "Alice"})
	log.Printf("[Client] Response from SayHello: %s", resp.Message)

	// resp2, _ := demo.NewGreeterClient(conn).SayHello(context.Background(), &demo.HelloRequest{Name: "Bob"})
	// log.Printf("[Client] Response from SayHello: %s", resp2.Message)

	// Server-side streaming 调用
	fmt.Println("\n--- Testing Server-side Streaming ---")
	streamClient, err := cli.Stream(context.Background(), &demo.HelloRequest{Name: "StreamingClient"})
	if err != nil {
		log.Fatalf("stream: %v", err)
	}

	for {
		reply, err := streamClient.Recv()
		if err != nil {
			if err == io.EOF {
				break
			}
			log.Fatalf("stream recv error: %v", err)
		}
		log.Printf("[Client] Received from Stream: %s", reply.Message)
	}
	fmt.Println("--- End of Server-side Streaming ---\n")

	time.Sleep(10 * time.Second)

	stream, err := cli.Pipe(ctx)
	if err != nil {
		log.Fatalf("pipe: %v", err)
	}

	// Receiver goroutine (prints occasional responses)
	go func() {
		for {
			msg, err := stream.Recv()
			if err != nil {
				log.Printf("recv done: %v", err)
				return
			}
			// Log every Nth message to avoid console overhead.
			if id := msg.GetId(); len(id) > 0 && id[len(id)-1] == '0' {
				fmt.Printf("[client] got echo id=%s ann=%v\n", msg.GetId(), msg.GetAnnotations())
			}
		}
	}()

	// Prepare a reusable payload buffer (no reallocation per message).
	payload := make([]byte, *payloadSize)
	rand.Read(payload)

	ticker := time.NewTicker(time.Second / time.Duration(*qps))
	defer ticker.Stop()

	fmt.Println("Press ENTER to stop...")
	go func() { _, _ = bufio.NewReader(os.Stdin).ReadString('\n'); cancel() }()

	count := 0
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			count++
			msg := &demo.ChatMessage{
				Id:      fmt.Sprintf("msg-%d", count),
				Payload: payload, // safe: gRPC will copy as needed
				Annotations: map[string]string{
					"client": "demo",
					"note":   strings.Repeat("x", 8),
				},
			}
			if err := stream.Send(msg); err != nil {
				log.Printf("send error: %v", err)
				return
			}
		}
	}
}
