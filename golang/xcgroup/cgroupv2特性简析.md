```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
spec:
  containers:
    - name: app
      image: nginx
      resources:
        requests:
          cpu: "0.5" # 请求 0.5 核
          memory: "100Mi" # 请求 100MB
        limits:
          cpu: "1" # 限制 1 核
          memory: "200Mi" # 限制 200MB
```

## **1. CPU 资源映射关系**

### **(1) `limits.cpu` → `cpu.max`**

- **Kubernetes** ：`limits.cpu: "1"`
- **Cgroup v2** ：

```bash
  # 格式: $MAX $PERIOD (单位: 微秒)
  echo "100000 100000" > /sys/fs/cgroup/kubepods.slice/cpu.max
```

- `100000/100000 = 1核`（即每 100ms 周期内最多使用 100ms CPU 时间）
- **作用** ：硬性限制容器最多使用 1 核 CPU

### **(2) `requests.cpu` → `cpu.weight`**

- **Kubernetes** ：`requests.cpu: "0.5"`
- **Cgroup v2** ：

```bash
  # 权重范围 1-10000，默认 100
  echo 50 > /sys/fs/cgroup/kubepods.slice/cpu.weight
```

- `0.5核 / 1核 = 50%` → 权重值 `50`（相对于默认值 100）
- **作用** ：当节点 CPU 竞争时，此容器至少获得 50% 的 CPU 时间份额

## **2. 内存资源映射关系**

### **(1) `limits.memory` → `memory.max`**

- **Kubernetes** ：`limits.memory: "200Mi"`
- **Cgroup v2** ：

```bash
  echo "209715200" > /sys/fs/cgroup/kubepods.slice/memory.max
```

- `200MiB = 200 * 1024 * 1024 = 209715200 字节`
- **作用** ：容器内存使用超过 200MB 时触发 OOM Kill

### **(2) `requests.memory` → `memory.low`**

- **Kubernetes** ：`requests.memory: "100Mi"`
- **Cgroup v2** ：

```bash
  echo "104857600" > /sys/fs/cgroup/kubepods.slice/memory.low
```

- `100MiB = 104857600 字节`
- **作用** ：
  - 当节点内存紧张时，系统会尽量保护这 100MB 内存不被回收
  - 类似于"内存最低保障"，但允许临时超用（不超过 `memory.max`）

## **3. 完整 cgroup v2 文件树示例**

假设 Pod 的 UID 为 `1234abcd`，在 systemd 管理的节点上：

```bash
/sys/fs/cgroup/
└── kubepods.slice/
    └── kubepods-pod1234abcd.slice/
        ├── cpu.max          # "100000 100000" (limits.cpu: 1)
        ├── cpu.weight       # "50" (requests.cpu: 0.5)
        ├── memory.max       # "209715200" (limits.memory: 200Mi)
        ├── memory.low       # "104857600" (requests.memory: 100Mi)
        └── cgroup.procs     # 包含容器内所有进程的 PID
```

## **4. 实际场景行为分析**

### **场景 1：CPU 资源竞争**

- **节点有 2 个核** ，运行了 2 个 Pod：
  - PodA：`requests.cpu: 0.5` → `cpu.weight=50`
  - PodB：`requests.cpu: 1.5` → `cpu.weight=150`
- **资源分配** ：
  - 总权重 `50 + 150 = 200`
  - PodA 获得 `50/200 = 25%` 的 CPU 时间（即 0.5 核）
  - PodB 获得 `150/200 = 75%` 的 CPU 时间（即 1.5 核）
- **关键点** ：
  - `cpu.weight` 仅在竞争时生效，无竞争时 Pod 可超用（不超过 `cpu.max`）

### **场景 2：内存超用**

- 容器内存使用增长：
  1. `<100MB`：正常使用，受 `memory.low` 保护
  2. `100MB~200MB`：允许使用，但可能被回收（内核优先回收其他无保护的内存）
  3. `>200MB`：触发 OOM Kill
- **关键点** ：
  - `memory.low` 不是硬限制，而是"尽量保障"的语义
  - 实际分配可能超过 `requests`，但不会超过 `limits`

## **5. 与 Kubernetes 调度器的关系**

1. **调度阶段** ：

- 仅检查 `requests`（`cpu.weight`/`memory.low` 的配置值）

* 确保节点有足够资源满足所有 Pod 的 `requests` 总和

1. **运行时阶段** ：

- `limits` 通过 `cpu.max`/`memory.max` 强制限制
- `requests` 通过 `cpu.weight`/`memory.low` 提供服务质量保障

### **总结：映射关系表**

| Kubernetes 字段   | Cgroup v2 文件 | 示例值                 |
| ----------------- | -------------- | ---------------------- |
| `limits.cpu`      | `cpu.max`      | `100000 100000` (1 核) |
| `requests.cpu`    | `cpu.weight`   | `50` (0.5 核权重)      |
| `limits.memory`   | `memory.max`   | `209715200` (200Mi)    |
| `requests.memory` | `memory.low`   | `104857600` (100Mi)    |

## **6. 总结：关键知识点**

| 参数/文件      | Cgroup v1                           | Cgroup v2                           | Kubernetes 关联                                                            | 作用说明                                                |
| -------------- | ----------------------------------- | ----------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------- |
| **CPU 权重**   | `cpu.shares` (基准 1024)            | `cpu.weight` (基准 100)             | `spec.containers[].resources.requests.cpu`                                 | **权重分配** ：竞争时按比例分配 CPU 时间                |
| **CPU 硬限制** | `cpu.cfs_quota_us`cpu.cfs_period_us | `cpu.max`                           | `spec.containers[].resources.limits.cpu`                                   | **硬性限制** ：限制最大 CPU 使用量                      |
| **内存保护**   | `memory.soft_limit_in_bytes`        | `memory.low`                        | `requests.memory`                                                          | **保护性分配** ：内存紧张时尽量保障的用量（不严格强制） |
| **内存硬限制** | `memory.limit_in_bytes`             | `memory.max`                        | `limits.memory`                                                            | **硬性限制** ：超过此值触发 OOM Kill                    |
| **进程数限制** | `pids.max` (v1/v2 相同)             | `pids.max`                          | [pidlimit](https://kubernetes.io/zh-cn/docs/concepts/policy/pid-limiting/) | 限制容器内进程数（需通过 kubelet 全局配置）             |
| **内存监控**   | `memory.usage_in_bytes`             | `memory.current`                    | `kubectl top pod`                                                          | 查看当前内存使用情况                                    |
| **压力监控**   | 无原生支持                          | `cpu.pressure`<br />memory.pressure |                                                                            | 提供资源竞争导致的延迟统计（PSI 机制）                  |

## 7. cgroupv1 和 cgroupv2 目录结构对比

### **假设条件**

- Pod 名称：`demo-pod`
- Pod UID：`1234abcd`
- 容器 ID：`5678efgh`
- Kubernetes 使用的 cgroup 驱动：`cgroupfs`（默认）

### **Cgroup v1 目录结构（含 Pod 和容器层级）**

```bash
/sys/fs/cgroup/
├── cpu,cpuacct/                 # CPU 控制器
│   └── kubepods/                # 所有 Pod 的父目录
│       ├── pod1234abcd/         # 具体 Pod 的目录（含 UID）
│       │   ├── cpu.shares       # 对应 requests.cpu=0.5 → 512
│       │   ├── cpu.cfs_quota_us # 对应 limits.cpu=1 → 100000
│       │   └── cpu.cfs_period_us# → 100000
│       │       └── 5678efgh/    # 容器目录（容器 ID）
│       │           └── ...      # 容器级配置继承 Pod
├── memory/                      # 内存控制器
│   └── kubepods/
│       └── pod1234abcd/
│           ├── memory.soft_limit_in_bytes # requests.memory=100Mi → 104857600
│           ├── memory.limit_in_bytes      # limits.memory=200Mi → 209715200
│           └── 5678efgh/
└── pids/                        # PID 控制器
    └── kubepods/
        └── pod1234abcd/
            ├── pids.max         # 全局 PID 限制
            └── 5678efgh/
```

### **Cgroup v2 目录结构（含 Pod 和容器层级）**

```bash
/sys/fs/cgroup/
└── kubepods.slice/                          # 所有 Pod 的父 slice
    ├── kubepods-pod1234abcd.slice/          # 具体 Pod 的 slice（含 UID）
    │   ├── cpu.max                          # limits.cpu=1 → "100000 100000"
    │   ├── cpu.weight                       # requests.cpu=0.5 → 50
    │   ├── memory.max                       # limits.memory=200Mi → 209715200
    │   ├── memory.low                       # requests.memory=100Mi → 104857600
    │   └── cri-containerd-5678efgh.scope/   # 容器目录（容器 ID）
    │       └── ...                          # 容器级配置继承 Pod
    └── kubepods-burstable.slice/            # 其他 QoS 类别的 Pod
```
