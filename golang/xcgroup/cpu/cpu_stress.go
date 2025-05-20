package main

import (
	"fmt"
	"runtime"
	"time"
)

func main() {
	// 使用所有可用CPU
	cores := runtime.NumCPU()
	runtime.GOMAXPROCS(cores)

	fmt.Printf("Starting CPU(%d) stress test...\n", cores)

	// 创建多个goroutine来消耗CPU
	for i := 0; i < cores; i++ {
		go func() {
			for {
				// 无限循环消耗CPU
			}
		}()
	}

	// 主goroutine打印状态
	ticker := time.NewTicker(5 * time.Second)
	for range ticker.C {
		fmt.Println("Still running...")
	}
}
