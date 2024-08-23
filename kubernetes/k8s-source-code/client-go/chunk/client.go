package main

import (
	"bufio"
	"fmt"
	"io"
	"net/http"
	"os"
)

func main() {
	resp, err := http.Get("http://localhost:8080/chunked")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error fetching URL: %v\n", err)
		os.Exit(1)
	}
	defer resp.Body.Close()

	// 使用bufio.Reader来按行读取数据
	reader := bufio.NewReader(resp.Body)
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				// 达到了文件末尾，正常退出循环
				break
			}
			fmt.Fprintf(os.Stderr, "Error reading from server: %v\n", err)
			os.Exit(1)
		}
		fmt.Print(line) // 打印读取到的行
	}

	// 注意：对于chunked传输，服务器在发送完所有数据后，会发送一个空的chunk（即"\r\n"），
	// 然后关闭连接。上面的循环会在读取到这个空chunk时因为EOF而退出。
	// 在这里不需要额外的处理来识别chunked传输的结束，因为EOF已经足够。
}
