package main

import (
	"fmt"
	"io"
	"net/http"
	"time"
)

/*
chunked 类型的 response 由一个个 chunk 组成，每个 chunk 都是格式都是 Chunk size + Chunk data + Chunk boundary，也就是块大小+数据+边界标识。chunk 的结尾是一个大小为0的 chunk，也就是"0\r\n"。串在一起整体格式类似这样：

[Chunk size][Chunk data][Chunk boundary][Chunk size][Chunk data][Chunk boundary][Chunk size=0][Chunk boundary]

*/

func chunkedHandler(w http.ResponseWriter, r *http.Request) {
	// 设置响应头以支持chunked传输
	w.Header().Set("Content-Type", "text/plain")
	w.Header().Set("Transfer-Encoding", "chunked")

	// 模拟发送chunked数据
	for i := 0; i < 5; i++ {
		// 发送数据块
		fmt.Fprintf(w, "Chunk %d\n", i)
		// 刷新输出缓冲区，发送当前数据块
		if f, ok := w.(http.Flusher); ok {
			f.Flush()
		}
		// 等待一段时间再发送下一个数据块
		time.Sleep(1 * time.Second)
	}

	// 关闭响应体，结束chunked传输
	// net http 内已经针对 chunked 通信机制实现了[Chunk size] xx [Chunk boundary] 所以只需要写入 data即可
	io.WriteString(w, "\n") // 注意：最后发送一个空行作为chunked传输的结束标志
}

func main() {
	http.HandleFunc("/chunked", chunkedHandler)
	fmt.Println("Server listening on :8080...")
	http.ListenAndServe(":8080", nil)
}
