1. 优雅启动
2. 优雅终止
3. 状态机
4. qos class
5. 集群内容器日志存储

qos 决定怎么死，priority 决定怎么生

# Pod 完整声明周期

![1744621509016](image/pod生命周期/1744621509016.png)

# pod 阶段状态-phase

Pod 的阶段（Phase）是 Pod 在其生命周期中所处位置的简单宏观概述。 该阶段并不是对容器或 Pod 状态的综合汇总，也不是为了成为完整的状态机

| 取值                | 描述                                                                                                                                                        |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Pending`（待调度） | Pod 已被 Kubernetes 系统接受，但有一个或者多个容器尚未创建亦未运行。此阶段包括等待 Pod 被调度的时间和通过网络下载镜像的时间。                               |
| `Running`（运行中） | Pod 已经绑定到了某个节点，Pod 中所有的容器都已被创建。至少有一个容器仍在运行，或者正处于启动或重启状态。                                                    |
| `Succeeded`（成功） | Pod 中的所有容器都已成功结束，并且不会再重启。                                                                                                              |
| `Failed`（失败）    | Pod 中的所有容器都已终止，并且至少有一个容器是因为失败终止。也就是说，容器以非 0 状态退出或者被系统终止，且未被设置为自动重启。                             |
| `Unknown`（未知）   | 因为某些原因无法取得 Pod 的状态。这种情况通常是因为与 Pod 所在主机通信失败<br />或例如当 `csi` 插件被卸载，原先使用这个 `csi` 插件的 Pod 就会出现 `Unknown` |

## 状态机

![1744622624198](image/pod生命周期/1744622624198.png)

## 容器状态

一旦[调度器](https://kubernetes.io/zh-cn/docs/reference/command-line-tools-reference/kube-scheduler/)将 Pod 分派给某个节点，`kubelet` 就通过[容器运行时](https://kubernetes.io/zh-cn/docs/setup/production-environment/container-runtimes)开始为 Pod 创建容器。容器的状态有三种：`Waiting`（等待）、`Running`（运行中）和 `Terminated`（已终止）

# Pod 状态计算细节

| kubectl get pod 返回的状态                                             | Pod Phase | Conditions                                                                                |
| ---------------------------------------------------------------------- | --------- | ----------------------------------------------------------------------------------------- |
| Completed                                                              | Succeeded |                                                                                           |
| ContainerCreating                                                      | Pending   |                                                                                           |
| CrashLoopBackOff                                                       | Running   | Container exits（一般是由于业务异常）                                                     |
| CreateContainerConfigError                                             | Pending   | Configmap “test” not found``secret “my-secret” not found                                  |
| ErrImagePull `ImagePullBackOff`Init:ImagePullBackOff、InvalidImageName | Pending   | Back-off pulling image                                                                    |
| Error                                                                  | Failed    | restartPolicy: Never container exits with Error(not 0)                                    |
| Evicted                                                                | Failed    | Message: Usage of EmptyDir volume “myworkdir” exceeds the limit “40Gi”.’``reason: Evicted |
| Init: 0/1                                                              | Pending   | Init containers don’t exit                                                                |
| Init: CrashLoopBackOff Init: Error                                     | Pending   | Init container crashed (exit with not 1)                                                  |
| OOMKilled                                                              | Running   | Containers are OOMKilled                                                                  |
| StartError                                                             | Running   | Containers cannot be started                                                              |
| Unknown                                                                | Running   | Node NotReady                                                                             |
| OutOfCpu <br />OutOfMemory                                             | Failed    | Scheduled, but it cannot pass kubelet admit                                               |

# Pod 服务质量（**[Quality of Service，QoS](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/pod-qos/)）**

Kubernetes 基于 Pod 中[容器](https://kubernetes.io/zh-cn/docs/concepts/containers/)的[资源请求](https://kubernetes.io/zh-cn/docs/concepts/configuration/manage-resources-containers/)进行分类， 同时确定这些请求如何与资源限制相关

依赖这种分类来决定当 Node 上没有足够可用资源时要驱逐哪些 Pod

![1744623283096](image/pod生命周期/1744623283096.png)

## Guaranteed

`Guaranteed` Pod 具有最严格的资源限制，并且最不可能面临驱逐。 在这些 Pod 超过其自身的限制或者没有可以从 Node 抢占的低优先级 Pod 之前， 这些 Pod 保证不会被杀死。这些 Pod 不可以获得超出其指定 limit 的资源。这些 Pod 也可以使用 [`static`](https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/cpu-management-policies/#static-policy) CPU 管理策略来使用独占的 CPU

> 当 Pod 仅设置了 limits 没有设置 requests 的时候，Kubernetes 会自动为它设置与 limits 相同的 requests 值，所以，这也属于 Guaranteed 情况

判断依据

- **当 Pod 里的每一个 Container cpu&mem 都同时设置了 requests 和 limits，并且 requests 和 limits 值相等的时候，这个 Pod 就属于 Guaranteed 类别**

guaranteed 模式和 cpuset 的能力一致，独占 cpu，不是像 cpushare 那样共享 CPU 的计算能力，操作系统在 CPU 之间进行上下文切换的次数大大减少，容器里应用的性能会得到大幅提升。

在实际的使用中，强烈建议将 DaemonSet 的 Pod 都设置为 Guaranteed 的 QoS 类型。否则，一旦 DaemonSet 的 Pod 被回收，它又会立即在原宿主机上被重建出来，这就使得前面资源回收的动作，完全没有意义了

## Burstable

`Burstable` Pod 有一些基于 request 的资源下限保证，但不需要特定的 limit。 如果未指定 limit，则默认为其 limit 等于 Node 容量，这允许 Pod 在资源可用时灵活地增加其资源。 在由于 Node 资源压力导致 Pod 被驱逐的情况下，只有在所有 `BestEffort` Pod 被驱逐后 这些 Pod 才会被驱逐。因为 `Burstable` Pod 可以包括没有资源 limit 或资源 request 的容器， 所以 `Burstable` Pod 可以尝试使用任意数量的节点资源

判断依据

- 当 Pod 不满足 Guaranteed 的条件，但至少有一个 Container 设置了 requests。那么这个 Pod 就会被划分到 Burstable 类别

## BestEffort

`BestEffort` QoS 类中的 Pod 可以使用未专门分配给其他 QoS 类中的 Pod 的节点资源。 例如若你有一个节点有 16 核 CPU 可供 kubelet 使用，并且你将 4 核 CPU 分配给一个 `Guaranteed` Pod， 那么 `BestEffort` QoS 类中的 Pod 可以尝试任意使用剩余的 12 核 CPU。

判断依据

- **如果一个 Pod 既没有设置 requests，也没有设置 limits，那么它的 QoS 类别就是 BestEffort**

## 作用

如果节点遇到资源压力，kubelet 将优先驱逐 `BestEffort` Pod

**QoS 划分的主要应用场景，是当宿主机资源紧张的时候，kubelet 对 Pod 进行 Eviction（即资源回收）时需要用到的**

具体地说，当 Kubernetes 所管理的宿主机上不可压缩资源短缺时，就有可能触发 Eviction。比如，可用内存（memory.available）、可用的宿主机磁盘空间（nodefs.available），以及容器运行时镜像存储空间（imagefs.available）

目前，Kubernetes 为你设置的 Eviction 的默认阈值如下所示：

```undefined
memory.available<100Mi
nodefs.available<10%
nodefs.inodesFree<5%
imagefs.available<15%
```

当然，上述各个触发条件在 kubelet 里都是可配置的。比如下面这个例子：

```lua
kubelet --eviction-hard=imagefs.available<10%,memory.available<500Mi,nodefs.available<5%,nodefs.inodesFree<5% --eviction-soft=imagefs.available<30%,nodefs.available<10% --eviction-soft-grace-period=imagefs.available=2m,nodefs.available=2m --eviction-max-pod-grace-period=600
```

在这个配置中，你可以看到 **Eviction 在 Kubernetes 里其实分为 Soft 和 Hard 两种模式** 。

其中，Soft Eviction 允许你为 Eviction 过程设置一段“优雅时间”，比如上面例子里的 imagefs.available=2m，就意味着当 imagefs 不足的阈值达到 2 分钟之后，kubelet 才会开始 Eviction 的过程。

而 Hard Eviction 模式下，Eviction 过程就会在阈值达到之后立刻开始。

> Kubernetes 计算 Eviction 阈值的数据来源，主要依赖于从 Cgroups 读取到的值，以及使用 cAdvisor 监控到的数据。

当宿主机的 Eviction 阈值达到后，就会进入 MemoryPressure 或者 DiskPressure 状态，从而避免新的 Pod 被调度到这台宿主机上。

当 eviction 发生的时候，kubelet 就是根据 Qos 类别来执行一下删除顺序

- 首当其冲的，自然是 BestEffort 类别的 Pod。
- 其次，是属于 Burstable 类别、并且发生“饥饿”的资源使用量已经超出了 requests 的 Pod。
- 最后，才是 Guaranteed 类别。并且，Kubernetes 会保证只有当 Guaranteed 类别的 Pod 的资源使用量超过了其 limits 的限制，或者宿主机本身正处于 Memory Pressure 状态时，Guaranteed 的 Pod 才可能被选中进行 Eviction 操作

当 Pod QoS 类别一样，就根据 Pod 的优先级来进行进一步地排序和选择

# pod 的创建过程

1. 用户通过 kubectl 或其他 api 客户端提交需要创建的 pod 信息给 apiserver
2. apiserver 开始生成 pod 对象信息，并将信息存入 etcd，然后返回确认信息至客户端
3. apiserver 开始反应 etcd 中 pod 对象的变化，其他组件使用 watch 机制来跟踪检查 apiserver 上的变动
4. 首先是 kube-schedule，发现有新的 pod 对象要创建，开始为 pod 分配主机并将结果信息更新至 apiserver
   1. 过滤合适的节点
   2. 为节点打分
5. pod.spec.nodename 分配节点后，相关节点的 kubelet watch 到有新的 pod 需要执行，就获取 pod 相关的 secret ，configmap 等依赖配置信息
   1. kubelet 为 pod 初始化 cgroup 资源
   2. 调用 CRI 启动 sandbox 创建 pause 容器，调用 cni，初始化容器网络，分配 ip，然后返回给 apiserver 更新 podStatus
   3. 网络初始化后，拉去业务镜像，按序创建初始化容器
   4. 创建业务主容器，如果有配置 post start hook，则优先调用 post start 如果失败，则根据重启策略重启容器，然后执行探针
      ```bash
      容器启动
      │
      ├── postStart 钩子执行（同步）
      │       └── 如果失败 → 容器重启（取决于重启策略）
      │
      ├── startupProbe 开始探测（如果有配置）
      │       └── 成功后
      │
      ├── readinessProbe 开始探测（容器准备好接收流量）
      │
      └── livenessProbe 开始探测（容器健康检查）
      ```

# [pod 的终止过程](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination-flow)

1. 用户想 apiserver 发送删除 pod 对象的命令/请求
2. apiserver 将 pod 标记为 terminating 状态，且在 metadata 中标记删除时间 `deletionTimestamp`(写 etcd)
3. kube-proxy watch 到 pod 被删事件，将 pod 从 service 的 endpoint 列表移除，新的流量不在转发到 pod
4. kubelet watch 到 pod 状态变更，启动 pod 关闭流程

   1. 如果当前 pod 对象定义了 preStop 钩子处理器，则在其标记为 terminating 后即会以同步的方式启动执行
   2. 发送 `SIGTERM` （kill -1)信号给容器内主进程，通知容器进程开始优雅终止
   3. 等待容器主进程完全终止，如果在 `terminationGracePeriodSecond` 宽限期内（默认 30s)还没退出，如果存在 preStop 钩子在 30s 后还没响应，kubelet 还会给 2s 的延迟，在这之后，就发送立即终止信号 `SIGKILL` (kill -9)，
   4. 容器进程终止，清理 pod 资源
      1. 运行时资源
      2. 如果 pod 使用了卷，kubelet 会释放和卸载卷资源
      3. 删除网络配置
   5. kubelet 通过将宽限期设置为 0（立即删除），触发从 apiserver 强制移除 Pod 对象。从而完成删除操作，此时对于用户不可见

```go
// kubernetes/pkg/kubelet/status/status_manager.go

func (m *manager) deletePod(pod *v1.Pod) {
    delOptions := metav1.DeleteOptions{}
    gracePeriodSeconds := int64(0)
    delOptions.GracePeriodSeconds = &gracePeriodSeconds

    err := m.kubeClient.CoreV1().Pods(pod.Namespace).Delete(context.TODO(), pod.Name, delOptions)
    if err != nil {
        klog.Errorf("Failed to delete pod %q: %v", format.Pod(pod), err)
    }
}
```

# 参考与延伸阅读

1. [Kubernetes 文档](https://kubernetes.io/zh-cn/docs/)/[概念](https://kubernetes.io/zh-cn/docs/concepts/)/[工作负载](https://kubernetes.io/zh-cn/docs/concepts/workloads/)/[Pod](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/)/[Pod 的生命周期](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/pod-lifecycle/)
