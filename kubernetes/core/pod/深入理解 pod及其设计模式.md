# 1. **为什么需要 pod？**

## 1.1. **容器的本质**

容器的本质：一个视图被隔离、资源受限的进程

- **容器里 PID=1 的进程就是应用本身**
- **管理虚拟机 = 管理基础设施；**
- **管理容器 = 直接管理应用本身**

## 1.2. 什么是**Kubernetes ？**

**kubernetes 类比云时代的操作系统，以此类推，容器镜像可以说是这个操作系统里的软件安装包**

## 1.3. **什么是 pod?**

**在操作系统里跑一个程序，实际上是由一组 linux 线程组成的，这些线程共享主进城的资源，相互写作完成主程序的工作。由以上的类比 pod 就类似进程组，管理多个容器的协调工作。**

![](https://cdn.nlark.com/yuque/0/2023/jpeg/287833/1693321688987-2c0c5d8d-7a91-4711-9d2c-25bdcc81dff5.jpeg)

## 1.4. **进程组（pod）**

![](https://cdn.nlark.com/yuque/0/2023/png/287833/1693577319316-d43def28-50d4-4312-bab1-69b27f8dcbf2.png)

**如何理解 容器是** **"单进程"** **模型？**

一般一个容器就负责一个任务，容器里 PID=1 的进程就是应用本身。如果一个容器里启动了多个进程，但是只有一个 PID=1 的进程，那谁来负责管理剩下的进程？

# 2. **为什么 pod 必须是原子调度单位？**

**举例：假设现在有两个容器密切写作**

- **App：业务容器，写日志文件**
- **LogCollector：转发日志文件到 elasticsearch 中**

**内存要求：**

- **App：1G**
- **LogCollector：0.5G**

**当前可用内存**

- **Node1: 1.25G**
- **Node2: 2G**

**如果 App 先被调度到 Node1 上会怎么样？**

**==> 由于两个容器是需要紧密合作的，App 被调度到 Node1 上，所以 LogCollector 也需要在 Node1 上运行，由于内存不足，LogCollector 就跑不起来了。**

**以上问题就是 Task co-scheduling 问题**

**在业界有一些集中解决方案，而 k8s 的解决方案就是 pod**

- **Mesos：资源囤积 resource hoarding**

  - **所有设置了 Affinity 约束的任务都到达时，才开始统一进行调度**
  - **缺点：调度效率损失，容易造成死锁**

- **Google Omega：乐观调度处理冲突**

  - **先不管这些冲突，而是通过精心设计的机制在出现了冲突之后解决问题**
  - **缺点：实现较为复杂**

**k8s 的解决方案，由于 k8s 中，pod 就是一个容器组，容器组需要多少内存都是可预定义声明的，且 pod 是 k8s 最小的调度单位，所以以上问题就不是问题了。**

![](https://cdn.nlark.com/yuque/0/2023/png/287833/1693579468380-226a3f24-12e8-4e12-9136-dca68577cc09.png)

# 3. **pod 的实现机制**

**由以上描述，我们可以知道 pod 要解决的核心问题在于：如何让一个 pod 里的多个容器之间最高效的共享某些资源和数据？**

**容器之间原本是被 linxu namespace 和 cgroup 隔离开的**

## 3.1. **共享网络**

**通过 infra container 当作父容器，其他业务容器 join 到父容器的网络命名空间中，就可以实现网络的共享。**

**一个 pod 只有一个 ip 地址，也就是这个 pod 的 network namespace 对应的 ip 地址，所有网络资源，都是一个 pod 一份，并且被该 pod 中的所有容器共享**

**且由于这个 infra container 的存在，k8s 就允许你单独更新或者添加容器镜像到 pod 中，且 pod 不需要重启。**

## 3.2. **共享存储**

通过 docker volumn 的特性，宿主机上的某个目录可以同时绑定挂在到每个业务容器中，volumn 是 pod level

```yaml
apiVersion: v1
kind: pod
metadata:
	name: two-cs
spec:
	restartPolicy: Never
	volumes:
  - name: shared-data
    hostPath:
      path: /data
  containers:
  - name: nginx-container
    image: nginx
    volumeMounts:
    - name: shared-data
      mountPath: /usr/share/nginx/index.html

  - name: debian-container
    image: debian
    volumeMounts:
    - name: shared-data
      mountPath: /pod-data
    command: ["/bin/sh"]
    args: ["-c", "echo hello from the debian container > /pod-data/index.html"]
```

# 4. **Pod Sandbox 与 pause 容器**

熟悉 Pod 生命周期的同学应该知道，创建 Pod 时 Kubelet 先调用 CRI 接口 RuntimeService.RunPodSandbox **来创建一个沙箱环境，为 Pod 设置网络（例如：分配 IP）等基础运行环境。当 Pod 沙箱（Pod Sandbox）建立起来后，Kubelet 就可以在里面创建用户容器。当到删除 Pod 时，Kubelet 会先移除 Pod Sandbox 然后再停止里面的所有容器。**

**可能有读者会疑惑，Pod Sandbox 是啥玩意儿啊？其实，这只是同一个事物通过不同角度看得到的不同称谓。从 Kubernetes 的底层容器运行时 CRI 看，Pod 这种在统一隔离环境里资源受限的一组容器，就叫 Sandbox。**

**Tips：一个隔离的应用运行时环境叫容器，一组共同被 Pod 约束的容器就叫 Pod Sandbox。她们同生共死，共享底层资源。**

**了解 KVM 底层的读者应该知道，虚拟机与容器一样底层都使用** cgroups 做资源配额**，而且概念上都抽离出一个**隔离的运行时环境\*\*，只是区别在于资源隔离的实现。因此，从字面是上看，虚拟机和容器还是有机会都用沙箱这个概念来“套“的。事实上，提出 Pod 沙箱概念就是为 Kubernetes 兼容不同运行时环境（甚至包括虚拟机！）预留空间，让运行时根据各自的实现来创建不同的 Pod Sandbox。对于基于 hypervisor 的运行时（KVM，kata 等），Pod Sandbox 就是虚拟机。对于 Linux 容器，Pod Sandbox 就是 Linux Namespace（Network Namespace 等）。

**Pod Sandbox 与我们今天要聊的“主角”pause 容器有着千丝万缕的联系。在 Linux CRI 体系里，Pod Sandbox 其实就是 pause 容器。Kubelet 代码引用的 defaultSandboxImage 其实就是官方提供的 gcr.io/google_containers/pause-amd64 镜像**

**Kubernetes 的 Pod 抽象基于 Linux 的 namespace 和 cgroups，为一组容器共同提供了隔离的运行环境。从网络的角度看，同一个 Pod 中的不同容器犹如在运行在同一个专有主机上，可以通过 localhost 进行通信。**

**原则上，任何人都可以配置 Docker 来控制容器组之间的共享级别——你只需创建一个父容器，并创建与父容器共享资源的新容器，然后管理这些容器的生命周期。在 Kubernetes 中，pause 容器被当作 Pod 中所有容器的“父容器”并为每个业务容器提供以下功能：**

**在 Pod 中它作为共享 Linux Namespace（Network、UTS 等）的基础；**

**启用 PID Namespace 共享，它为每个 Pod 提供 1 号进程，并收集 Pod 内的僵尸进程。**

# 5. **容器设计模式**

### Deployment: 管理部署发布的控制器

![](https://cdn.nlark.com/yuque/0/2021/png/287833/1629904475068-d4ea35d7-83c6-4f7b-9060-7cf83c6a153d.png)

**可以直接管理集群中的 Pod 吗** **？**

1. **如何保证集群内可用 Pod 的数量**
2. **如何为所有 Pod 更新镜像版本**
3. **更新过程中，如何保证服务的可用性**
4. **更新过程中，发现问题如何快速回滚**

**Deployment 的作用** **：**

1. **定义一组 Pod 的期望数量， controller 会维持 Pod 数量与期望值数量一致**
2. **配置 Pod 发布方式，controller 会按照给定策略更新 Pod, 保证更新过程中不可用的 Pod 数量在限定范围内**
3. **如果发布有问题，支持“一键”回滚**

**一个 \***Deployment\* 为 [Pods](https://kubernetes.io/docs/concepts/workloads/pods/pod-overview/) 和 [ReplicaSets](https://kubernetes.io/zh/docs/concepts/workloads/controllers/replicaset/) 提供声明式的更新能力。

### Deployment 语法

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
	name: nginx-deployment
  labels:
  	app: nainx
spec:
	replicas: 3
  selector:
  	matchLabels:
    	app: nginx

  template:
  	metadata:
    	labels:
      	app: nginx

    spec:
    	containers:
      	- name: nginx
        	image: nginx:1.9.1
          prots:
          	- containerPort: 80
```

- **selector 定义 Deployment 如何查找要管理的 Pods。如上，选择在 Pod 模板中定义的标签(**`<span class="ne-text">app:nginx</span>`)
- **template 定义 Pod 的目标状态的模板**

### 管理模式

![](https://cdn.nlark.com/yuque/0/2021/png/287833/1630020204711-7a23bb56-25ab-4fbd-9cff-f4ba3a34223e.png)

**Deployment 只负责管理不同版本的 ReplicaSet，由 ReplicaSet 管理 Pod 副本数**

**每个 ReplicaSet 对应 Deployment template 的一个版本，一个 ReplicaSet 下的 Pod 都是相同的版本**

### 相关命令

**创建 deployment:**

**kubectl create -f nginx-deployment.yaml**

**kubectl get deployment**

```shell
$ kubectl get deployment
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           35h
```

- **DESIRED: 期望的 Pod 数量**
- **CURRENT: 当前实际 Pod 数量**
- **UP-TO-DATE: 到达期望版本的 Pod 数量**
- **AVAILABLE: 运行中并可用的 Pod 数量**
- **AGE: deployment 创建时长**

# 6. **参考**

1. [What are Kubernetes Pods Anyway? - Ian Lewis](https://www.ianlewis.org/en/what-are-kubernetes-pods-anyway)
2. [Kubernetes Pod 网络精髓：pause 容器详解 - 掘金](https://juejin.cn/post/6844904061683138573)
3. [阿里云-k8s-张磊-白话容器进程](https://www.bilibili.com/video/BV1r7411r7h7?p=4)
