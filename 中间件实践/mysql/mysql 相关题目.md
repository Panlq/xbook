### 1. 求一个商品表中价格最高的第 10 和第 14 个产品，输出 SQL 语句

关键字 limit ，所以可以排序后取第 10 个和 14 个

- `LIMIT offset, count`：跳过 `offset` 条记录后取 `count` 条。

```sql
(
    SELECT *
    FROM products
    ORDER BY price DESC
    LIMIT 9, 1   -- 第10个（偏移9）
)
UNION ALL
(
    SELECT *
    FROM products
    ORDER BY price DESC
    LIMIT 13, 1  -- 第14个（偏移13）
);
```

# 2. 怎么理解乐观锁和悲观锁？

乐观锁对应于生活中乐观的人总是想着事情往好的方向发展，悲观锁对应于生活中悲观的人总是想着事情往坏的方向发展。

## 一、MySQL 中的乐观锁与悲观锁

### 1. 悲观锁示例：`SELECT ... FOR UPDATE`

在 MySQL 的 InnoDB 引擎中，可以使用 `SELECT ... FOR UPDATE` 对查询的数据加排他锁，防止其他事务修改，这是典型的悲观锁行为。

```sql
START TRANSACTION;
SELECT * FROM orders WHERE id = 1001 FOR UPDATE;
UPDATE orders SET status = 'paid' WHERE id = 1001;
COMMIT;
```

在这个例子中：

- 在事务中对数据行加锁；
- 其他事务必须等待当前事务提交后才能修改该行；
- 这种方式适用于写冲突频繁的场景

### 2. 乐观锁示例：版本号机制（Version）

MySQL 中常通过“版本号”字段实现乐观锁。例如：

```sql
UPDATE products
SET stock = stock - 1, version = version + 1
WHERE id = 1001 AND version = 5;
```

在这个例子中：

- 只有当 `version = 5` 时才会执行更新；
- 如果其他事务已经修改了 `version`，则当前更新不会生效；
- 客户端需要判断影响行数是否为 0 来决定是否重试

## 二、Go 语言中的乐观锁与悲观锁

### 1. 悲观锁示例：`sync.Mutex`

Go 的 `sync.Mutex` 提供了互斥锁，是一种悲观锁的实现方式。使用 `mu.Lock()` 加锁保证同一时间只有一个 goroutine 能修改 `count`；

```go
package main

import (
    "fmt"
    "sync"
)

var (
    count int
    mu    sync.Mutex
)

func increment() {
    mu.Lock()
    defer mu.Unlock()
    count++
}

func main() {
    var wg sync.WaitGroup
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            increment()
        }()
    }
    wg.Wait()
    fmt.Println("Final count:", count) // 输出: Final count: 1000
}
```

### 2. 乐观锁示例：`sync/atomic` 包（CAS）

Go 的 `sync/atomic` 包提供了原子操作，底层基于 CAS（Compare and Swap）实现乐观锁。

```go
package main

import (
    "fmt"
    "sync/atomic"
)

var count int32

func increment() {
    for {
        old := atomic.LoadInt32(&count)
        if atomic.CompareAndSwapInt32(&count, old, old+1) {
            break
        }
    }
}

func main() {
    var wg sync.WaitGroup
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            increment()
        }()
    }
    wg.Wait()
    fmt.Println("Final count:", count) // 输出: Final count: 1000
}
```

在这个例子中：

- 使用 `CompareAndSwapInt32` 实现无锁并发；
- 多个 goroutine 同时尝试更新，失败则重试；
- 这是典型的乐观锁实现
