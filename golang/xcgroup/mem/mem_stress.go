package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("Memory stress test with physical memory allocation")

	// 每块10MB，强制写入数据
	const blockSize = 10 * 1024 * 1024
	var blocks [][]byte

	for i := 0; i < 20; i++ {
		// 分配并立即使用内存
		block := make([]byte, blockSize)
		for j := 0; j < len(block); j += 4096 {
			block[j] = 1 // 每页写入1字节
		}
		blocks = append(blocks, block)

		// 读取cgroup内存统计
		// data, err := os.ReadFile("/sys/fs/cgroup/liz/memory.current")
		// if err != nil {
		// 	fmt.Printf("Error reading cgroup memory: %v\n", err)
		// 	continue
		// }

		// fmt.Printf("Allocated: %d MB, Cgroup Memory: %s bytes\n",
		// 	(i+1)*10,
		// 	string(data))

		fmt.Printf("Allocated: %d MB\n", (i+1)*10)

		time.Sleep(1 * time.Second)
	}
}
