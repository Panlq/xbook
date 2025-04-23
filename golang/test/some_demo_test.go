package main

import (
	"fmt"
	"io"
	"reflect"
	"runtime"
	"sync"
	"testing"
	"time"

	"github/panlq/xbook/go/utils"
)

type A struct {
	name string
}

// 语法糖，实际等效于 func HiName(a) string {}
// 修改的就是拷贝后的值对象，值接收者
func (a A) HiName() string {
	a.name = "Hi! " + a.name
	return a.name
}

// 等效于 func HiName2(a *A) string {
// 	a.name = "Hi! " + a.name
// 	return a.name
// }

func (a *A) HiName2() string {
	a.name = "Hi! " + a.name
	return a.name
}

func NameOfA(a A) string {
	a.name = "Hi! " + a.name
	return a.name
}

func Test_NameOfA(t *testing.T) {
	t1 := reflect.TypeOf(A.HiName)
	t2 := reflect.TypeOf(NameOfA)
	fmt.Println(t1 == t2)
}

func Test_Call(t *testing.T) {
	a := A{name: "golang"}

	// 值接收者，对象拷贝
	fmt.Println(a.HiName())
	fmt.Println(a.name)
	// Call the method again to see if the name has changed
	fmt.Println(A.HiName(a))
	fmt.Println(a.name)

	// 指针接收者，
	// Call the method again to see if the name has changed
	fmt.Println(a.HiName2())
	fmt.Println(a.name)

	// Call the method again to see if the name has changed
	fmt.Println((&a).HiName2())
	fmt.Println(a.name)
}

func Test_defer_multi_call(t *testing.T) {

	// call last
	defer func() {
		fmt.Println("last")
	}()

	// call second
	defer func() {
		fmt.Println("second")
	}()

	// call first
	defer func() {
		fmt.Println("first")
	}()

	fmt.Println("main")
}

func dB(a int) int {
	return a * 2
}

func dA(a int) {
	fmt.Println(a)
}

func Test_defer_func_params(t *testing.T) {
	a := 1

	defer dA(dB(a))

	fmt.Println(a)
}

func Test_empty_interface(t *testing.T) {
	var empty interface{}
	if empty == nil {
		fmt.Println("empty is nil")

	} else {
		fmt.Println("empty is not nil")
	}

	var w io.Writer
	if w == nil {
		fmt.Println("w is nil")

	} else {
		fmt.Println("w is not nil")
	}
}

func Test_go_schedule_queue(t *testing.T) {
	runtime.GOMAXPROCS(1)

	var wg sync.WaitGroup
	wg.Add(3)
	go func(n int) {
		fmt.Println(n)
		wg.Done()
	}(1)

	go func(n int) {
		fmt.Println(n)
		wg.Done()
	}(2)

	go func(n int) {
		fmt.Println(n)
		wg.Done()
	}(3)

	wg.Wait()
}

func Test_go_schedule_queue2(t *testing.T) {
	runtime.GOMAXPROCS(1)

	var wg sync.WaitGroup
	wg.Add(3)
	go func(n int) {
		fmt.Println(n)
		wg.Done()
	}(1)
	runtime.Gosched() // 让出 CPU，触发调度

	go func(n int) {
		fmt.Println(n)
		wg.Done()
	}(2)
	runtime.Gosched() // 再次让出 CPU

	go func(n int) {
		fmt.Println(n)
		wg.Done()
	}(3)

	wg.Wait()
}

type PI interface {
	SetX(int)
}

type Point struct {
	x int
}

func (p Point) X() int {
	return p.x
}

func (p Point) SetX(x int) {
	// 值对象赋值只在当前 函数内生效
	// 当前 SetX 函数相当于 (*Point).SetX()
	p.x = x
}

func (p *Point) SetX2(x int) {
	p.x = x
}

func Test_point_method(t *testing.T) {
	p := Point{x: 1}
	fmt.Println(p.X())
	p.SetX(2)
	fmt.Println(p.X())
	p.SetX2(3)
	fmt.Println(p.X())

	Point.SetX(p, 4)
	fmt.Println(p.X())

	(*Point).SetX2(&p, 5)
	fmt.Println(p.X())

	var pi PI
	pi = p
	pi.SetX(6)
	fmt.Println(p.X())
}

func main() {
	go func(n int) {
		for {
			n++
			fmt.Println(n)
		}
	}(0)

	for {

	}
}

func Test_generic_type(t *testing.T) {

	// 实例化：Cache[string, int]，string 和 int 是类型实参
	stringIntCache := utils.NewCache[string, int]()
	stringIntCache.Set("age", 30)
	age, ok := stringIntCache.Get("age")
	fmt.Println(age, ok) // 输出：30 true

	// 实例化：Cache[int, string]，int 和 string 是类型实参
	intStringCache := utils.NewCache[int, string]()
	intStringCache.Set(1, "one")
	one, ok := intStringCache.Get(1)
	fmt.Println(one, ok) // 输出：one true

}

func Test_HappensBefore_case1(t *testing.T) {
	var ch = make(chan struct{}, 1)
	var s string

	f := func() {
		s = "hello world"
		ch <- struct{}{}
	}

	go f()
	<-ch
	fmt.Println(s)
}

func Test_HappensBefore_case2(t *testing.T) {
	var ch = make(chan struct{}, 1)
	var s string

	f := func() {
		s = "hello world"
		close(ch)
	}

	go f()
	<-ch
	fmt.Println(s)
}

func Test_HappensBefore_case3(t *testing.T) {
	var ch = make(chan struct{})
	var s string

	f := func() {
		s = "hello world"
		<-ch
	}

	go f()
	ch <- struct{}{}
	fmt.Println(s)
}

func Test_HappensBefore_case4(t *testing.T) {
	var mu sync.Mutex
	var s string

	f := func() {
		s = "hello world"
		mu.Unlock()
	}

	mu.Lock()
	go f()
	mu.Lock()
	fmt.Println(s)
}

func Test_HappensBefore_case5(t *testing.T) {
	var s string
	var once sync.Once

	f := func() {
		s = "hello world"
	}
	once.Do(f)
	fmt.Println(s)
}

func Test_channel_fifo(t *testing.T) {

	ch := make(chan int, 3) // 创建缓冲大小为3的channel

	// 启动发送者
	go func() {
		for i := 0; i < 5; i++ {
			ch <- i
			fmt.Printf("Sent: %d\n", i)
		}
		close(ch)
	}()

	// 主goroutine作为接收者
	for v := range ch {
		fmt.Printf("Received: %d\n", v)
		time.Sleep(500 * time.Millisecond) // 模拟处理延迟
	}

}

func Test_memory_reorder(t *testing.T) {
	var a, b int

	f := func() {
		a = 1 // w之前的写操作
		b = 2 // 写操作w
	}

	g := func() {
		fmt.Println(b) // 读操作r
		fmt.Println(a) // ???
	}

	go f() //g1
	g()    //g2
}

func Test_memory_reorder2(t *testing.T) {
	go func(n int) {
		for {
			n++
			fmt.Println(n)
		}
	}(0)

	for {

	}
}
