# 🐳 简易容器实现（基于 Linux Namespace 和 Cgroup）

> Linux 环境

本项目通过使用 Go 语言结合 Linux 内核特性（Namespace 和 Cgroup），实现了 **一个简易的容器运行时** 。它支持：

- 进程隔离（PID Namespace）
- 主机名隔离（UTS Namespace）
- 文件系统隔离（Mount Namespace + chroot）
- CPU 时间配额控制（Cgroup v1/v2）
- 内存使用限制（Cgroup v1/v2）

项目可帮助理解 Docker 等容器技术背后的底层机制。

---

## 🧰 功能说明

| 功能         | 实现方式                                                     |
| ------------ | ------------------------------------------------------------ |
| 容器启动     | 使用 `exec.Command("/proc/self/exe", ...)`启动子进程模拟容器 |
| 进程隔离     | PID Namespace (`CLONE_NEWPID`)                               |
| 主机名隔离   | UTS Namespace (`CLONE_NEWUTS`)                               |
| 文件系统隔离 | Mount Namespace +`chroot()`切换根目录                        |
| CPU 配额     | Cgroup `cpu.cfs_quota_us`/`cpu.max`                          |
| 内存限制     | Cgroup `memory.limit_in_bytes`/`memory.max`                  |
| proc         | 挂载让容器能查看自己的进程信息                               |
| tmpfs        | 挂载提供基于内存的临时文件系统                               |

---

## 🚀 如何运行

### 前提条件

- **Linux 系统**
- root 权限（需要操作 cgroup）
- 已安装 Go 环境
- 准备好一个根文件系统（如 busybox 或 Ubuntu 的根目录）

当前目录已默认集成了一个 busybox rootfs。其他的可参考》》》》 [制作一个最小的 rootfs](制作一个最小的 rootfs.md)

### 步骤

**1. 编译并运行容器**

```go
sudo go run main.go run \
  --rootfs=/home/ubuntu/xcgroup/my-busybox-rootfs \
  --cpu-period=100000 \
  --cpu-quota=20000 \
  --memory=52428800 \
  /bin/sh -c "echo Hello from container"
```

**2. 测试内存压力程序**

> CGO_ENABLED=0 go build -ldflags '-extldflags "-static"' -o mem_stress mem/mem_stress.go
>
> cp mem/mem_stress ./my-busybox-rootfs/

```go
sudo go run main.go run --memory=52428800 /mem_stress
```

如果设置的内存限制为 50MB，则在尝试分配超过该值时会触发 OOM Kill。

> --memory=52428800 # 即 50 _ 1024 _ 1024 = 52,428,800 字节 = 50 MB

```bash
sudo go run main.go run --cpu-period=100000   --cpu-quota=20000   --memory=52428800   /mem_stress
[Main Process] Starting
[Main Process] Running [/mem_stress]
[Main Process] Starting
[Child Process] Executing command: [/mem_stress]
[Child Process] Chrooting into /home/ubuntu/xcgroup/my-busybox-rootfs
[Child Process] Changing working directory to /
[Child Process] Mounting proc...
[Child Process] Mounting tmpfs...
Memory stress test with physical memory allocation
Allocated: 10 MB
Allocated: 20 MB
Allocated: 30 MB
Allocated: 40 MB
Error: signal: killed
Error: exit status 1
exit status 1
```

查看 linux 内核日志可以看到详细的退出原因和进程信息

> sudo journalctl -f

```bash
May 20 16:38:46 node03 kernel: thp_swpout_fallback 0
May 20 16:38:46 node03 kernel: Tasks state (memory values in pages):
May 20 16:38:46 node03 kernel: [  pid  ]   uid  tgid total_vm      rss rss_anon rss_file rss_shmem pgtables_bytes swapents oom_score_adj name
May 20 16:38:46 node03 kernel: [  10228]     0 10228   306444      544      160      384         0    73728        0             0 exe
May 20 16:38:46 node03 kernel: [  10233]     0 10233   306448    12608    12608        0         0   184320        0             0 mem_stress
May 20 16:38:46 node03 kernel: oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=liz,mems_allowed=0,oom_memcg=/liz,task_memcg=/liz,task=mem_stress,pid=10233,uid=0
May 20 16:38:46 node03 kernel: Memory cgroup out of memory: Killed process 10233 (mem_stress) total-vm:1225792kB, anon-rss:50432kB, file-rss:0kB, shmem-rss:0kB, UID:0 pgtables:180kB oom_score_adj:0
May 20 16:38:46 node03 sudo[10166]: pam_unix(sudo:session): session closed for user root
```

#### 🔍 关键日志分析

#### 1. 进程信息（关键）

```bash
May 20 16:38:46 node03 kernel: [  10233]     0 10233   306448    12608    12608        0         0   184320        0             0 mem_stress
```

这行是关键，表示进程 `mem_stress` 的内存使用情况：

| 列        | 含义                         | 数值         |
| --------- | ---------------------------- | ------------ |
| total_vm  | 虚拟内存大小（页数）         | 306448 pages |
| rss       | 实际使用的物理内存页数       | 12608 pages  |
| rss_anon  | 匿名页数量（堆、栈等）       | 12608 pages  |
| rss_file  | 文件映射页数（如 mmap 文件） | 0            |
| rss_shmem | 共享内存页数                 | 0            |

> ⚠️ Linux 中每页通常是 **4KB** ，所以我们可以换算一下：

```bash
rss_anon = 12608 pages × 4 KB = 50,432 KB = 50.4 MB
```

✅ **这就是超过 50MB 的证据！**

#### 2. OOM 触发原因

```bash
May 20 16:38:46 node03 kernel: Memory cgroup out of memory: Killed process 10233 (mem_stress) total-vm:1225792kB, anon-rss:50432kB, ...
```

- `anon-rss:50432kB`：匿名 RSS 内存为 50.432MB，已经**略微超过你的 50MB 限制**
- `oom_score_adj:0`：默认 OOM 分数（越低越不容易被杀）
- `task_memcg=/liz`：这个进程属于 `/liz` 这个 cgroup
- `Memory cgroup out of memory`：说明是因为 cgroup 的内存限制达到了上限

```bash
May 20 16:38:46 node03 kernel: oom-kill:constraint=CONSTRAINT_MEMCG,...
```

- `constraint=CONSTRAINT_MEMCG`：表示 OOM 是由 **cgroup 内存限制**触发的。
- `memcg=/liz`：再次确认是 `/liz` 这个 cgroup 触发的 OOM。
- `task=mem_stress`：被杀的是 `mem_stress` 进程。

---

## 🔍 容器的本质：进程隔离与资源限制

Docker 等容器本质上并不是虚拟机，而是：

> **一种特殊的进程管理机制 —— 在命名空间中运行的普通进程，并受到资源限制。**

### 1️⃣ 进程隔离（Namespaces）

Linux 提供多种命名空间用于隔离资源：

| Namespace 类型 | 隔离内容                                 |
| -------------- | ---------------------------------------- |
| `UTS`          | 主机名和域名                             |
| `PID`          | 进程 ID 空间（每个容器有独立的 PID 1）   |
| `MNT`          | 文件系统挂载点（容器看到的文件结构不同） |
| `NET`          | 网络接口、IP 地址等（未在本项目中实现）  |

本项目使用了 `CLONE_NEWUTS`, `CLONE_NEWPID`, `CLONE_NEWNS` 实现基础隔离。

### 2️⃣ 资源限制（Control Groups）

Cgroups（Control Groups）是 Linux 提供的一套机制，用来：

- 控制一组进程使用的资源总量（CPU、内存、IO 等）
- 限制、优先级划分、快照、迁移

#### 示例：

- 设置 CPU 占用时间：
  ```bash
  echo 20000 > /sys/fs/cgroup/cpu/liz/cpu.cfs_quota_us
  echo 100000 > /sys/fs/cgroup/cpu/liz/cpu.cfs_period_us
  ```
- 设置内存上限：
  ```bash
  echo 52428800 > /sys/fs/cgroup/memory/liz/memory.limit_in_bytes
  ```

本项目根据用户输入自动选择使用 Cgroup v1 或 v2 接口进行配置。

---

## 📌 注意事项

- 必须以 `root` 身份运行
- 不支持网络隔离
- 只适用于学习用途，不适用于生产环境
- 确保 `/sys/fs/cgroup` 已挂载且有写权限

---

## 📚 参考与延伸阅读

1. 如何实现一个简单的 runc [&#34;Building a container from scratch in Go&#34;](https://www.youtube.com/watch?v=Utf-A4rODH8)
2. [Understanding Linux Namespaces](https://lwn.net/Articles/531388/?spm=a2ty_o01.29997173.0.0.5700c921o8sjAS)
3. [Cgroups v2 Documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html?spm=a2ty_o01.29997173.0.0.5700c921o8sjAS)
4. Docker 源码：[https://github.com/moby/moby](https://github.com/moby/moby)
