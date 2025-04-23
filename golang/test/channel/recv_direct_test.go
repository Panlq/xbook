package channel

import (
	"fmt"
	"runtime"
	"testing"
	"time"
)

func goroutineA(a <-chan int) {
	fmt.Println("goroutine A started")
	val := <-a
	fmt.Println("goroutine A received data: ", val)
	return
}

func goroutineB(b <-chan int) {
	fmt.Println("goroutine B started")
	val := <-b
	fmt.Println("goroutine B received data: ", val)
	return
}

func Test_channel_recv_direct_from_send(t *testing.T) {
	ch := make(chan int)
	go goroutineA(ch)
	go goroutineB(ch)
	fmt.Println("send chan start")
	ch <- 3
	fmt.Println("send chan end")
	time.Sleep(time.Second)
	fmt.Println("main end")
}

func Test_foloop(t *testing.T) {

	var x int
	threads := runtime.GOMAXPROCS(0)
	for i := 0; i < threads; i++ {
		go func() {
			for {
				x++
			}
		}()
	}
	time.Sleep(time.Second)
	fmt.Println("x =", x)

}
