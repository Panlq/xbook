package main

import (
	"encoding/binary"
	"fmt"
	"io"
	"log"
	"net"
)

func sendMessage(conn net.Conn, msg string) error {
	msgBytes := []byte(msg)
	msgLen := uint32(len(msgBytes))
	buf := make([]byte, 4+msgLen)
	binary.BigEndian.PutUint32(buf[:4], msgLen)
	copy(buf[4:], msgBytes)
	_, err := conn.Write(buf)
	return err
}

func readMessage(conn net.Conn) (string, error) {
	header := make([]byte, 4)
	if _, err := io.ReadFull(conn, header); err != nil {
		return "", err
	}

	msgLen := binary.BigEndian.Uint32(header)
	msg := make([]byte, msgLen)
	if _, err := io.ReadFull(conn, msg); err != nil {
		return "", err
	}

	return string(msg), nil
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	for {
		msg, err := readMessage(conn)
		if err != nil {
			if err == io.EOF {
				fmt.Printf("Client %s disconnected", conn.RemoteAddr())
			} else {
				log.Printf("Error reading message: %v", err)
			}
			break
		}
		fmt.Printf("Received message from %s: %s\n", conn.RemoteAddr(), msg)

		reply := fmt.Sprintf("Echo from Go Server: %s", msg)
		sendMessage(conn, reply)
	}
}

func main() {
	// listen on 12345
	listener, err := net.Listen("tcp", ":12345")
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}

	defer listener.Close()
	fmt.Println("Server started on :12345")

	for {
		// accept connection from client
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("Error accepting connection: %v", err)
			continue
		}

		go handleConnection(conn)
	}
}
