# 1. 概述

kube-shceudle 的调度策略有两种

- predicate: 过滤不符合条件的节点
- priority: 优先级排序, 选择优先级最高的节点

这篇文章会专注介绍这两个调度策略的工作原理，发生作用的阶段及源码解析。

# 2. predicates 策略

predicates 算法主要是对集群中的 node 进行过滤，选出符合当前 pod 运行的 nodes。

## 策略介绍

一个一个插件运行，任何一个插件过滤掉，这个节点就被过滤。

- `PodFitHostPorts`：检查是否有 `Host Ports` 冲突（当 Pod 直接使用主机的 `Port`）
- `PodFitsPorts`：同 `PodFitsHostPorts`
- `PodFitsResources`：检查 `Node` 的资源是否充足，包括允许的 `Pod` 数量、`CPU`、内存、`GPU` 个数以及其他的 `OpaqueIntResources`。
- `HostName`：检查 `pod.Spec.NodeName` 是否与候选节点一致（当指定 Pod 的运行节点）
- `MatchNodeSelector`：检查候选节点的 `pod.Spec.NodeSelector` 是否匹配
- `NoVolumeZoneConflict`：检查 `volume zone` 是否冲突
- `MatchInterPodAffinity`：检查是否匹配 Pod 的亲和性要求
- `NoDiskConflict`：检查是否存在 `Volume` 冲突，仅限于 GCE PD、AWS EBS、Ceph RBD 以及 iSCSI
- `PodToleratesNodeTaints`：检查 `Pod` 是否容忍 `Node Taints`
- `CheckNodeMemoryPressure`：检查 `Pod` 是否可以调度到 `MemoryPressure` 的节点上
- `NoVolumeNodeConflict`：检查节点是否满足 `Pod` 所引用的 `Volume` 的条件

还有很多其他策略，也可以编写自己的策略，用来过滤节点。

## predicates plugin 工作原理

![1744383950526](image/predicates调度策略与源码分析/1744383950526.png)

在经过插件的层层过滤，剩下符合条件的 Node list

# 3. Priorities 策略

priorities 调度算法是在 pridicates 算法后执行的，主要功能是对已经过滤出的 nodes 进行打分并选出最佳的一个 node。

## 策略介绍

不同的 `plugin` 都会有打分，最终会结合 `plugin` 的权重选择 node

- `SelectorSpreadPriority`：优先减少节点上属于同一个 `Service` 或 `Replication Controller` 的 `Pod` 数量
- `InterPodAffinityPriority`：优先将 `Pod` 调度到相同的拓扑上（如同一个节点、Rack、Zone 等）（亲和性）
- `LeastRequestedPriority`：优先调度到请求资源少的节点上
- `BalanceResourceAllocation`：优先平衡各节点的资源使用
- `NodePreferAvoidPodsPriority`：`alpha.kubernetes.io/preferAvoidPods` 字段判断，权重为 10000，避免其他优先级策略的影响
- `NodeAffinityPriority`：优先调度到匹配 `NodeAffinity` 的节点上
- `TaintTolerationPriority`：优先调度到匹配 `TaintToleration` 的节点上
- `ServiceSpreadPriority`：尽量将同一个 `service` 的 `Pod` 分布到不同节点上，已经被 `SelectorSpreadPriority` 替代（默认未使用）
- `EqualPriority`：将所有节点的优先级设置为 1 （默认未使用）
- `ImageLocalityPriority`：尽量将使用大镜像的容器调度到已经下拉了该镜像的节点上（默认未使用）
- `MostRequestPriority`：尽量调度到已经使用过的 `Node` 上，特别适用于 `cluster-autoscaler` （默认未使用）

# 参考与延伸阅读

1. [kube_scheduler_algorithm--田飞雨](https://blog.tianfeiyu.com/source-code-reading-notes/kubernetes/kube_scheduler_algorithm.html)
