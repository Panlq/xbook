Burstable

BestEffort

Guaranteed

# 调度流程

## 磁盘资源需求

容器临时存储（ephemeral storage ）包含日志和可写层数据，可以通过定义 Pod Spec 中的 limits.ephemeral-storage 和 requests.ephemeral-storage 来申请。

Pod 调度完成后，计算节点对临时存储的限制不是基于 CGroup 的，而是由 kubelet 定时获取容器的日志和容器可写层的磁盘使用情况，如果超过限制，则会对 Pod 进行驱逐。

## Init Container 的资源需求

- 当 kube-scheduler 调度带有多个 init 容器的 Pod 时，只计算 cpu.request 最多的 init 容器，而不是计算所有的 init 容器总和。
- 由于多个 init 容器按顺序执行，并且执行完成立即退出，所以申请最多的资源 init 容器中的所需资源，即可满足所有 init 容器需求。
- kube-scheduler 在计算该节点被占用的资源时，init 容器的资源依然会被纳入计算。因为 init 容器在特定情况下可能会被再次执行，比如由于更换镜像而引起 Sandbox 重建时。

# 问题

## 1. 计算密集型的长作业如何锁死申请的 cpu,memory?

如果时间片隔离的(cpuset)，可以使用 guaranteed 类型的 resources 定义，

绝对隔离的需要使用 kernal 级别的内核隔离
