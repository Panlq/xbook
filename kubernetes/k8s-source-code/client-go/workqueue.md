# 1. kubernetes workqueue 实现

1. 标准队列
2. 延时队列
3. 限速队列

```shell
client-go: master
latest-commit-id: 86d49e7265f07676cb39f34
```

具备如下特性

```go
// Package workqueue provides a simple queue that supports the following
// features:
//   - Fair: items processed in the order in which they are added.
//   - Stingy: a single item will not be processed multiple times concurrently,
//     and if an item is added multiple times before it can be processed, it
//     will only be processed once.
//   - Multiple consumers and producers. In particular, it is allowed for an
//     item to be reenqueued while it is being processed.
//   - Shutdown notifications.
package workqueue // import "k8s.io/client-go/util/workqueue"
```

# 2. Queue

Queue 对应的接口定义如下：
定义了 queue 对应的几个接口函数，重点关注的生产和消费，即 Add(), Get(), Done()

```go
// util/workqueue/queue.go: 26

type Interface interface {
	Add(item interface{})
	Len() int
	Get() (item interface{}, shutdown bool)
	Done(item interface{})
	ShutDown()
	ShutDownWithDrain()
	ShuttingDown() bool
}

```

Queue 的实现结构体定义如下：

```go
// Type is a work queue (see the package comment).
type Type struct {
	// queue defines the order in which we will work on items. Every
	// element of queue should be in the dirty set and not in the
	// processing set.
	queue []t

	// dirty defines all of the items that need to be processed.
	dirty set

	// Things that are currently being processed are in the processing set.
	// These things may be simultaneously in the dirty set. When we finish
	// processing something and remove it from this set, we'll check if
	// it's in the dirty set, and if so, add it to the queue.
	processing set

	cond *sync.Cond

	shuttingDown bool
	drain        bool

	metrics queueMetrics

	unfinishedWorkUpdatePeriod time.Duration
	clock                      clock.WithTicker
}

type empty struct{}
type t interface{}
type set map[t]empty
```

- queue: 定义了这个队列中 items 的顺序，是一个 `[]interface{}` 类型的切片，可以保存任意类型的元素
- dirty: set 类型，底层是一个 `map[interface{}]struct{}` ，queue 中的元素会存到这个 dirty set 中，即待处理的 items, 并起到过滤重复元素的作用
- processing: set 类型，存储正在执行的 items
- cond：条件变量，是一个不常用的并发原语，主要是为等待/通知场景下的并发问题提供支持，后面看具体源码在具体分析其使用方式和注意事项
- metrics：用来做链路追踪的 metrics 采集器
- shuttingDown：队列关闭的标识
- drain：是否跑完队列内的元素在退出

从源码注释可以了解到，当一个 item 从 queue 中被取出后，这个 item 会被加入到 processing set 中，同时会从 dirty set 中移除，即 processing set 中保存了目前正在被处理，但是没有处理完的 items，即会存在某个动作来标记一个 item 是否已经被处理完成。
下面看 Add, Get, Done 的具体实现

## 2.1 Queue.Add(item interface{})

```go
// util/workqueue/queue.go: 162
// Add marks item as needing processing.
func (q *Type) Add(item interface{}) {
	q.cond.L.Lock()
	defer q.cond.L.Unlock()
    // 如果已经关闭，立即返回
	if q.shuttingDown {
		return
	}

    // 过滤已存在的元素
	if q.dirty.has(item) {
		return
	}

	q.metrics.add(item)

    // 加入到 set 中
	q.dirty.insert(item)
    // 如果已经在执行了，则不放入到待执行队列
	if q.processing.has(item) {
		return
	}

    // 追加到待执行队列中
	q.queue = append(q.queue, item)
    // 唤醒等待中的消费者可开始消费队列中的元素
	q.cond.Signal()
}
```

Add 方法主要实现两个逻辑

1. 如果 item 在 dirty set 中不存在，就插入到 dirty set 中，达到过滤重复 item 的问题。这个特性在 `workquque` 包的 `doc.go` 中被描述为 `Stingy`，即不允许同一个 item 被并发处理。
2. 如果 item 在 processing set 中，正在被处理，则不会被重复加入到 queue 里去排队。显然这也是为了 `Stingy` 。但这个 item 会被放入到 dirty set 中，当这个 item 在处理完成后(即调用 Done 方法), 由于有相同元素正在被处理被加入到 dirty set 中的新的 item，会被重新加入到 queue 中。

总结一句话：Add 的过程会保证一个 Queue 中同一时刻不存在重复的 item

## 2.2 Queue.Get() 方法

```go
// util/workqueue/queue.go: 196
func (q *Type) Get() (item interface{}, shutdown bool) {
	q.cond.L.Lock()
	defer q.cond.L.Unlock()
    // 当队列中无元素且未关闭，阻塞等待
	for len(q.queue) == 0 && !q.shuttingDown {
		q.cond.Wait()
	}
	if len(q.queue) == 0 {
		// We must be shutting down.
		return nil, true
	}

	item = q.queue[0]
	// The underlying array still exists and reference this object, so the object will not be garbage collected.
	q.queue[0] = nil
	q.queue = q.queue[1:]

	q.metrics.get(item)

	q.processing.insert(item)
	q.dirty.delete(item)

	return item, false
}
```

Get 方法尝试从队列中获取第一个 item，同时将其加入到 processing set 中，并从 dirty set 删除。
需要注意的是，当调用 Get 处理完成后，必须调用 Done 来结束 item

## 2.3 Queue.Done(item interface{})

```go
// util/workqueue/queue.go: 223
func (q *Type) Done(item interface{}) {
	q.cond.L.Lock()
	defer q.cond.L.Unlock()

	q.metrics.done(item)

	q.processing.delete(item)
	if q.dirty.has(item) {
		q.queue = append(q.queue, item)
		q.cond.Signal()
	} else if q.processing.len() == 0 {
		q.cond.Signal()
	}
}
```

Done 方法用来标记一个 item 被处理完成，即从 processing set 中移除。另外在 Add 中提到的，当 Add 时如果发现 item 正在被处理，那么这个 item 会被暂存在 dirty set 中。此时会将其取出重新加入到 queue 中排队。这个行为同样是有意义的，在 `Stingy`的同时允许一个 item 在处理过程中被重新入队，等待下一次重新处理。

# 3. DelayingQueue

DelayingQueue 接口实现如下：

```go
// DelayingInterface is an Interface that can Add an item at a later time. This makes it easier to
// requeue items after failures without ending up in a hot-loop.
type DelayingInterface interface {
	Interface
	// AddAfter adds an item to the workqueue after the indicated duration has passed
	AddAfter(item interface{}, duration time.Duration)
}

```

这里的 `Interface` 即前文提到的 标准 Queue 的接口定义，DelayingQueue 在 Queue 的基础上加了一个 AddAfter 的接口函数，实现“延时多久后在将元素加入到队列排队”的功能。这样也就使得一个 item 处理失败之后，能够在指定延时之后再重入入队。

DelayingQueue 的结构体类型定义如下，具体的属性含义用法，在后续源码分析中在描述，先跟踪下 AddAfter 的实现

```go
// delayingType wraps an Interface and provides delayed re-enquing
type delayingType struct {
	Interface

	// clock tracks time for delayed firing
	clock clock.Clock

	// stopCh lets us signal a shutdown to the waiting loop
	stopCh chan struct{}
	// stopOnce guarantees we only signal shutdown a single time
	stopOnce sync.Once

	// heartbeat ensures we wait no more than maxWait before firing
	heartbeat clock.Ticker

	// waitingForAddCh is a buffered channel that feeds waitingForAdd
	waitingForAddCh chan *waitFor

	// metrics counts the number of retries
	metrics retryMetrics
}
```

## 3.1 DelayingQueue.AddAfter(item interface{}, duration time.Duration)

```go
// util/workqueue/delaying_queue.go: 207
// AddAfter adds the given item to the work queue after the given delay
func (q *delayingType) AddAfter(item interface{}, duration time.Duration) {
	// don't add if we're already shutting down
	if q.ShuttingDown() {
		return
	}

	q.metrics.retry()

	// immediately add things with no delay
	if duration <= 0 {
		q.Add(item)
		return
	}

	select {
	case <-q.stopCh:
		// unblock if ShutDown() is called
	case q.waitingForAddCh <- &waitFor{data: item, readyAt: q.clock.Now().Add(duration)}:
	}
}
```

当延时 duration > 0 时，AddAfter 只是简单的构造了一个 waitFor 对象，然后丢到 `chan *waitFor` 类型的 waitForAddCh 中。所以核心逻辑在如何消费这个 channel

跟一下 waitFroAddCh 的实现，可以找到在初始化延时队列时，会初始化 channel 的容量，并启动一个异步任务在消费其中的元素

```go
// util/workqueue/delaying_queue.go: 103
func newDelayingQueue(clock clock.WithTicker, q Interface, name string, provider MetricsProvider) *delayingType {
	ret := &delayingType{
		Interface:       q,
		clock:           clock,
		heartbeat:       clock.NewTicker(maxWait),
		stopCh:          make(chan struct{}),
		waitingForAddCh: make(chan *waitFor, 1000),
		metrics:         newRetryMetrics(name, provider),
	}

	go ret.waitingLoop()
	return ret
}
```

其中 waitFor 的定义如下

```go
// waitFor holds the data to add and the time it should be added
type waitFor struct {
	data    t
	readyAt time.Time
	// index in the priority queue (heap)
	index int
}
```

## 3.2 waitingLoop 消费延时队列

```go
// util/workqueue/delaying_queue.go: 228
// maxWait keeps a max bound on the wait time. It's just insurance against weird things happening.
// Checking the queue every 10 seconds isn't expensive and we know that we'll never end up with an
// expired item sitting for more than 10 seconds.
const maxWait = 10 * time.Second

// waitingLoop runs until the workqueue is shutdown and keeps a check on the list of items to be added.
func (q *delayingType) waitingLoop() {
	defer utilruntime.HandleCrash()

	// Make a placeholder channel to use when there are no items in our list
	never := make(<-chan time.Time)

	// Make a timer that expires when the item at the head of the waiting queue is ready
	var nextReadyAtTimer clock.Timer

    // 初始化了一个优先级队列，用一个最小堆保存了 所有的 waitFor 元素
	waitingForQueue := &waitForPriorityQueue{}
	heap.Init(waitingForQueue)

    // 标记元素是否已经在处理
	waitingEntryByData := map[t]*waitFor{}

    // 长轮训消费延时任务
	for {
		if q.Interface.ShuttingDown() {
			return
		}

		now := q.clock.Now()

		// Add ready entries
        // 处理已就绪的任务直到消费完
		for waitingForQueue.Len() > 0 {
            // 拿出堆顶的元素，如果还没到时间，则继续轮询，由于是最小堆，所以堆顶都不满足，其他元素肯定也还没到期
			entry := waitingForQueue.Peek().(*waitFor)
			if entry.readyAt.After(now) {
				break
			}

            // 取出到期的元素对象，添加到待处理队列，并从优先级队列过滤器中移除
			entry = heap.Pop(waitingForQueue).(*waitFor)
			q.Add(entry.data)
			delete(waitingEntryByData, entry.data)
		}

        // 拿到堆顶元素，标记下一跳的时钟长度，并在长轮训中做监听
		// Set up a wait for the first item's readyAt (if one exists)
		nextReadyAt := never
		if waitingForQueue.Len() > 0 {
			if nextReadyAtTimer != nil {
				nextReadyAtTimer.Stop()
			}
			entry := waitingForQueue.Peek().(*waitFor)
			nextReadyAtTimer = q.clock.NewTimer(entry.readyAt.Sub(now))
			nextReadyAt = nextReadyAtTimer.C()
		}

		select {
		case <-q.stopCh:
			return

		case <-q.heartbeat.C():
            // 默认10s的心跳
			// continue the loop, which will add ready items

		case <-nextReadyAt:
			// continue the loop, which will add ready items

		case waitEntry := <-q.waitingForAddCh:
            // 如果需要延时处理，则插入到延时优先级队列中，否则直接插入到待处理的队列
			if waitEntry.readyAt.After(q.clock.Now()) {
				insert(waitingForQueue, waitingEntryByData, waitEntry)
			} else {
				q.Add(waitEntry.data)
			}

			drained := false
            // select 执行到此节点时，将waitingForAddCh中所有元素都一并拿出来插入到响应队列中
			for !drained {
				select {
				case waitEntry := <-q.waitingForAddCh:
					if waitEntry.readyAt.After(q.clock.Now()) {
						insert(waitingForQueue, waitingEntryByData, waitEntry)
					} else {
						q.Add(waitEntry.data)
					}
				default:
					drained = true
				}
			}
		}
	}
}

```

可以看到 waitingLoop 就是一个 for 长轮训消费 channel 中的 waitFor 对象。其中[waitForPriorityQueue](https://github.com/kubernetes/client-go/blob/master/util/workqueue/delaying_queue.go)是一个用最小堆实现的优先级队列。
从上到下，我们先看从`waitingForAddCh`取出来的逻辑，当对象被取出来之后, 如果还没 ready, 则插入到延时优先级队列中，否则直接加入到待消费队列。并通过一个循环，将`waitingForAddCh`中的所有元素都取出来并插入响应队列中

其中 insert 主要有如下 2 个逻辑：

1. 如果 item 不存在则，将其插入堆中，
2. 如果 item 已存在且延时时间有提前则修改延时时间，并重塑最小堆，否则不处理

```go
// insert adds the entry to the priority queue, or updates the readyAt if it already exists in the queue
func insert(q *waitForPriorityQueue, knownEntries map[t]*waitFor, entry *waitFor) {
	// if the entry already exists, update the time only if it would cause the item to be queued sooner
	existing, exists := knownEntries[entry.data]
	if exists {
		if existing.readyAt.After(entry.readyAt) {
			existing.readyAt = entry.readyAt
			heap.Fix(q, existing.index)
		}

		return
	}

	heap.Push(q, entry)
	knownEntries[entry.data] = entry
}
```

这个 waitingLoop() 写的还是很漂亮，滴水不漏，逻辑严谨，相当优雅。waitingLoop 通过优先级队列实现元素按照时间顺序从近到远排序，这样就能最高效地获取到最快 ready 的元素。然后又根据优先级队列中最快能 ready 的元素的 ready 剩余时间来构造等待计时器，等待的过程中又监测着 waitingForAddCh 这个 channel 中是否有新元素…… 这个过程很完美地体现了 Golang 特色的 Channel 机制的优雅与强大。

# 4. RateLimitingQueue

```go
// util/workqueue/rate_limiting_queue.go: 21
// RateLimitingInterface is an interface that rate limits items being added to the queue.
type RateLimitingInterface interface {
	DelayingInterface

	// AddRateLimited adds an item to the workqueue after the rate limiter says it's ok
	AddRateLimited(item interface{})

	// Forget indicates that an item is finished being retried.  Doesn't matter whether it's for perm failing
	// or for success, we'll stop the rate limiter from tracking it.  This only clears the `rateLimiter`, you
	// still have to call `Done` on the queue.
	Forget(item interface{})

	// NumRequeues returns back how many times the item was requeued
	NumRequeues(item interface{}) int   // item 在队列中执行的次数，即失败重试次数
}
```

限速队列建立在延时队列之上，RateLimitingInterface 接口继承了 DelayingInterface 的所有方法，增加了与限速相关的(AddRateLimited，Forget，Numrequeues)三个接口函数
限速队列的结构体类型定义也很简单

```go
// rateLimitingType wraps an Interface and provides rateLimited re-enquing
type rateLimitingType struct {
	DelayingInterface

	rateLimiter RateLimiter
}

```

## 4.1 RateLimitingQueue.AddRateLimited

```go

// AddRateLimited AddAfter's the item based on the time when the rate limiter says it's ok
func (q *rateLimitingType) AddRateLimited(item interface{}) {
	q.DelayingInterface.AddAfter(item, q.rateLimiter.When(item))
}

```

通过一个 rateLimiter 确定一个 item 的 ready 时间，然后通过延时队列完成延时入队的逻辑。这里就只剩下 rateLimiter 这个限速器的实现需要研究了。相关的两个其他方法也是调用的 rateLimiter 的实现，所以重点就在限速器的实现了。

# 5. rateLimiter 限速器的实现

rateLimiter 的接口定义如下：

```go
type RateLimiter interface {
	// When gets an item and gets to decide how long that item should wait
	When(item interface{}) time.Duration // 返回一个 item 需要等待的时常
	// Forget indicates that an item is finished being retried.  Doesn't matter whether it's for failing
	// or for success, we'll stop tracking it
	Forget(item interface{})           // 标识一个元素结束重试
	// NumRequeues returns back how many failures the item has had
	NumRequeues(item interface{}) int  // 标识这个元素被处理里多少次了
}
```

对应的实现有六种算法，不同限速思路，体现算法之美

1. BucketRateLimiter
2. ItemExponentialFailureRateLimiter
3. ItemFastSlowRateLimiter
4. MaxOfRateLimiter
5. WithMaxWaitRateLimiter

## 5.1 BucketRateLimiter

用 golang 标准库的 golang.org/x/time/rate.Limiter 实现。BucketRateLimiter 实例化的时候，需要传入一个 Limiter, 如：
`rate.NewLimiter(rate.Limit(10), 100)`，表示令牌桶里最多有 100 个令牌，每秒发放 10 个令牌。

```golang
// BucketRateLimiter adapts a standard bucket to the workqueue ratelimiter API
type BucketRateLimiter struct {
	*rate.Limiter
}

var _ RateLimiter = &BucketRateLimiter{}

func (r *BucketRateLimiter) When(item interface{}) time.Duration {
    // 过多久后给当前 item发放一个令牌
	return r.Limiter.Reserve().Delay()
}

func (r *BucketRateLimiter) NumRequeues(item interface{}) int {
	return 0
}

func (r *BucketRateLimiter) Forget(item interface{}) {
}
```

## 5.2 ItemExponentialFailureRateLimiter

Exponent 是指数的意思，从这个限速器的名字大概能猜到是失败次数越多，限速越大而且是指数级增长的一种限速器。
初始化时需要指定指数增加基数，以及最大的限速时长
结构体定义如下

```golang
// ItemExponentialFailureRateLimiter does a simple baseDelay*2^<num-failures> limit
// dealing with max failures and expiration are up to the caller
type ItemExponentialFailureRateLimiter struct {
	failuresLock sync.Mutex
	failures     map[interface{}]int

	baseDelay time.Duration
	maxDelay  time.Duration
}

var _ RateLimiter = &ItemExponentialFailureRateLimiter{}

func NewItemExponentialFailureRateLimiter(baseDelay time.Duration, maxDelay time.Duration) RateLimiter {
	return &ItemExponentialFailureRateLimiter{
		failures:  map[interface{}]int{},
		baseDelay: baseDelay,
		maxDelay:  maxDelay,
	}
}


func (r *ItemExponentialFailureRateLimiter) When(item interface{}) time.Duration {
	r.failuresLock.Lock()
	defer r.failuresLock.Unlock()

	exp := r.failures[item]
	r.failures[item] = r.failures[item] + 1 // 失败次数+1

    // 每调用一次，exp 也就加了 1， 对应的就是指数操作 2^n
	// The backoff is capped such that 'calculated' value never overflows.
	backoff := float64(r.baseDelay.Nanoseconds()) * math.Pow(2, float64(exp))
	if backoff > math.MaxInt64 {
        // 如果超过了最大整型，就使用最大延时，避免溢出
		return r.maxDelay
	}

	calculated := time.Duration(backoff)
	if calculated > r.maxDelay {
        // 如果超过最大延时，则返回最大延时
		return r.maxDelay
	}

	return calculated
}

func (r *ItemExponentialFailureRateLimiter) NumRequeues(item interface{}) int {
	r.failuresLock.Lock()
	defer r.failuresLock.Unlock()

	return r.failures[item]
}

func (r *ItemExponentialFailureRateLimiter) Forget(item interface{}) {
	r.failuresLock.Lock()
	defer r.failuresLock.Unlock()

	delete(r.failures, item)
}
```

## 5.3 ItemFastSlowRateLimiter

快慢限速器，也就是先快后慢，定义一个阈值，超过了就慢慢重试。看看类型定义和实现：

```golang
// ItemFastSlowRateLimiter does a quick retry for a certain number of attempts, then a slow retry after that
type ItemFastSlowRateLimiter struct {
	failuresLock sync.Mutex
	failures     map[interface{}]int

	maxFastAttempts int                // 快速重试的次数
	fastDelay       time.Duration      // 快重试间隔
	slowDelay       time.Duration      // 慢充实间隔
}

var _ RateLimiter = &ItemFastSlowRateLimiter{}


func (r *ItemFastSlowRateLimiter) When(item interface{}) time.Duration {
	r.failuresLock.Lock()
	defer r.failuresLock.Unlock()

	r.failures[item] = r.failures[item] + 1 // 标识重试次数+1

    // 如果重试次数未达到最大快重试限制，则返回快重试间隔，否则就是慢重试
	if r.failures[item] <= r.maxFastAttempts {
		return r.fastDelay
	}

	return r.slowDelay
}

func (r *ItemFastSlowRateLimiter) NumRequeues(item interface{}) int {
	r.failuresLock.Lock()
	defer r.failuresLock.Unlock()

	return r.failures[item]
}

func (r *ItemFastSlowRateLimiter) Forget(item interface{}) {
	r.failuresLock.Lock()
	defer r.failuresLock.Unlock()

	delete(r.failures, item)
}
```

## 5.4 MaxOfRateLimiter

内部支持嵌入多个限速器，然后返回限速最狠的一个延时

```go
// MaxOfRateLimiter calls every RateLimiter and returns the worst case response
// When used with a token bucket limiter, the burst could be apparently exceeded in cases where particular items
// were separately delayed a longer time.
type MaxOfRateLimiter struct {
	limiters []RateLimiter
}

func (r *MaxOfRateLimiter) When(item interface{}) time.Duration {
	ret := time.Duration(0)
	for _, limiter := range r.limiters {
		curr := limiter.When(item)
		if curr > ret {
			ret = curr
		}
	}

	return ret
}

func NewMaxOfRateLimiter(limiters ...RateLimiter) RateLimiter {
	return &MaxOfRateLimiter{limiters: limiters}
}

func (r *MaxOfRateLimiter) NumRequeues(item interface{}) int {
	ret := 0
	for _, limiter := range r.limiters {
		curr := limiter.NumRequeues(item)
		if curr > ret {
			ret = curr
		}
	}

	return ret
}

func (r *MaxOfRateLimiter) Forget(item interface{}) {
	for _, limiter := range r.limiters {
		limiter.Forget(item)
	}
}
```

## 5.5 WithMaxWaitRateLimiter

在其他限速器上，在包一层最大延迟的属性，如果限速器 When 获取到的时长达到了最大延迟则直接返回最大延迟时长

```go
// WithMaxWaitRateLimiter have maxDelay which avoids waiting too long
type WithMaxWaitRateLimiter struct {
	limiter  RateLimiter
	maxDelay time.Duration
}

func NewWithMaxWaitRateLimiter(limiter RateLimiter, maxDelay time.Duration) RateLimiter {
	return &WithMaxWaitRateLimiter{limiter: limiter, maxDelay: maxDelay}
}

func (w WithMaxWaitRateLimiter) When(item interface{}) time.Duration {
	delay := w.limiter.When(item)
	if delay > w.maxDelay {
		return w.maxDelay
	}

	return delay
}

func (w WithMaxWaitRateLimiter) Forget(item interface{}) {
	w.limiter.Forget(item)
}

func (w WithMaxWaitRateLimiter) NumRequeues(item interface{}) int {
	return w.limiter.NumRequeues(item)
}
```

# 6. 使用场景

在写自定义控制器时，会用到这样一段代码

```go
queue := workqueue.NewRateLimitingQueue(workqueue.DefaultControllerRateLimiter())
```

这个其实就是 kubernetes workqueue 里是一个默认的控制器限速队列，调用的`NewMaxOfRateLimiter`，指定了令牌桶和指数增长限速器

```golang

// DefaultControllerRateLimiter is a no-arg constructor for a default rate limiter for a workqueue.  It has
// both overall and per-item rate limiting.  The overall is a token bucket and the per-item is exponential
func DefaultControllerRateLimiter() RateLimiter {
	return NewMaxOfRateLimiter(
		NewItemExponentialFailureRateLimiter(5*time.Millisecond, 1000*time.Second),
		// 10 qps, 100 bucket size.  This is only for retry speed and its only the overall factor (not per item)
		&BucketRateLimiter{Limiter: rate.NewLimiter(rate.Limit(10), 100)},
	)
}
```

- ItemExponentialFailureRateLimiter 限速器会指数级增加限速时长，也就是先延迟 5 毫秒，如果失败就变成 10 毫秒、20 毫秒、40 毫秒…… 最大不超过 1000 秒。

- BucketRateLimiter 是一个比较基础的令牌桶实现，在这里的 2 个参数 10 和 100 的含义是令牌桶里最多有 100 个令牌，每秒发放 10 个。
