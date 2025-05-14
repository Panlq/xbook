package main

import (
	"encoding/binary"
	"fmt"
	"io"
	"log"
	"net"
	"time"
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

func main() {
	conn, err := net.Dial("tcp", ":12345")
	if err != nil {
		log.Fatalf("Error connecting to server: %v", err)
	}

	defer conn.Close()
	for i := 0; i < 3; i++ {
		msg := fmt.Sprintf("Hello from Go Client #%d", i+1)
		sendMessage(conn, msg)
		// Wait for a reply

		reply, err := readMessage(conn)
		if err != nil {
			log.Printf("Error receiving response: %v", err)
			break
		}
		fmt.Println("Received response from server:", reply)

		time.Sleep(time.Second)
	}
}
