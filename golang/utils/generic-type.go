package utils

import (
	"fmt"
)

// 类型约束：定义一个接口，限制 K 必须是 comparable（可比较），V 可以是任何类型
type Cacheable interface {
	comparable // 类型约束：K 必须支持 == 和 !=
}

// 泛型类型：定义一个泛型结构体 Cache，K 和 V 是类型形参
type Cache[K Cacheable, V any] struct {
	data map[K]V
}

// 泛型接收器：方法 Set 的接收器是泛型类型 Cache[K, V]
func (c *Cache[K, V]) Set(key K, value V) {
	c.data[key] = value
}

// 泛型接收器：方法 Get 的接收器是泛型类型 Cache[K, V]
func (c *Cache[K, V]) Get(key K) (V, bool) {
	val, ok := c.data[key]
	return val, ok
}

// 泛型函数：NewCache 是一个泛型函数，返回泛型类型 Cache[K, V]
func NewCache[K Cacheable, V any]() *Cache[K, V] {
	return &Cache[K, V]{
		data: make(map[K]V),
	}
}

type Number interface {
	~int | ~float64 // 底层是 int 或 float64 的所有类型
}

func Add[T Number](a, b T) T {
	return a + b
}

type MyInt int

func main() {
	// 实例化：Cache[string, int]，string 和 int 是类型实参
	stringIntCache := NewCache[string, int]()
	stringIntCache.Set("age", 30)
	age, ok := stringIntCache.Get("age")
	fmt.Println(age, ok) // 输出：30 true

	// 实例化：Cache[int, string]，int 和 string 是类型实参
	intStringCache := NewCache[int, string]()
	intStringCache.Set(1, "one")
	one, ok := intStringCache.Get(1)
	fmt.Println(one, ok) // 输出：one true

	// 联合元素
	Add(1, 2)               // OK: int 满足 ~int
	Add(1.5, 2.5)           // OK: float64 满足 ~float64
	Add(MyInt(1), MyInt(2)) // OK: MyInt 的底层是 int
}
