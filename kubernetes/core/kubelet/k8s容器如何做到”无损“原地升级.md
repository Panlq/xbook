# 1. 背景

**原地升级**一词中，“升级”不难理解，是将应用实例的版本由旧版替换为新版。那么如何结合 Kubernetes 环境来理解“原地”呢？

![img](https://openkruise.io/zh/assets/images/inplace-update-comparation-fc948df195e332f578d4967c34b0c3d3.png)

**重建升级**时我们要删除旧 Pod、创建新 Pod：

- Pod 名字和 uid 发生变化，因为它们是完全不同的两个 Pod 对象（比如 Deployment 升级）
- Pod 名字可能不变、但 uid 变化，因为它们是不同的 Pod 对象，只是复用了同一个名字（比如 StatefulSet 升级）
- Pod 所在 Node 名字发生变化，因为新 Pod 很大可能性是不会调度到之前所在的 Node 节点的
- Pod IP 发生变化，因为新 Pod 很大可能性是不会被分配到之前的 IP 地址的

但是对于 **原地升级** ，我们仍然复用同一个 Pod 对象，只是修改它里面的字段。因此：

- 可以避免如 _调度_ 、 _分配 IP_ 、_分配、挂载盘_ 等额外的操作和代价
- 更快的镜像拉取，因为开源复用已有旧镜像的大部分 layer 层，只需要拉取新镜像变化的一些 layer
- 当一个容器在原地升级时，Pod 中的其他容器不会受到影响，仍然维持运行

**总结：这种只更新 Pod 中某一个或多个容器版本、而不影响整个 Pod 对象、其余容器的升级方式，被我们称为 Kubernetes 中的原地升级。**

# 2. 收益分析

为什么要在 Kubernetes 中引入这种原地升级的理念和设计呢？

首先，这种原地升级的模式极大地提升了应用发布的效率，根据非完全统计数据，在阿里环境下原地升级至少比完全重建升级提升了 80% 以上的发布速度。这其实很容易理解，原地升级为发布效率带来了以下优化点：

1. 节省了调度的耗时，Pod 的位置、资源都不发生变化；
2. 节省了分配网络的耗时，Pod 还使用原有的 IP；
3. 节省了分配、挂载远程盘的耗时，Pod 还使用原有的 PV（且都是已经在 Node 上挂载好的）；
4. 节省了大部分拉取镜像的耗时，因为 Node 上已经存在了应用的旧镜像，当拉取新版本镜像时只需要下载很少的几层 layer。

其次，当我们升级 Pod 中一些 sidecar 容器（如采集日志、监控等）时，其实并不希望干扰到业务容器的运行。但面对这种场景，Deployment 或 StatefulSet 的升级都会将整个 Pod 重建，势必会对业务造成一定的影响。而容器级别的原地升级变动的范围非常可控，只会将需要升级的容器做重建，其余容器包括网络、挂载盘都不会受到影响。

最后，原地升级也为我们带来了集群的稳定性和确定性。当一个 Kubernetes 集群中大量应用触发重建 Pod 升级时，可能造成大规模的 Pod 飘移，以及对 Node 上一些低优先级的任务 Pod 造成反复的抢占迁移。这些大规模的 Pod 重建，本身会对 apiserver、scheduler、网络/磁盘分配等中心组件造成较大的压力，而这些组件的延迟也会给 Pod 重建带来恶性循环。而采用原地升级后，整个升级过程只会涉及到 controller 对 Pod 对象的更新操作和 kubelet 重建对应的容器。

# 3. 技术背景

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod3
spec:
  containers:
    - name: app
      image: nginx:latest
      resources:
        requests:
          cpu: "0.8" # 请求 0.5 核
          memory: "100Mi" # 请求 100MB
        limits:
          cpu: "1" # 限制 1 核
          memory: "200Mi" # 限制 200MB
```

## 1. kubelet 针对 pod 容器的版本管理规则

源码分析》》[kubelet 源码解析-容器创建和变更原理](./kubelet源码解析-容器创建和变更原理.md)

每个 Node 上的 Kubelet，会针对本机上所有 Pod.spec.containers 中的每个 container 计算一个 hash 值，并记录到实际创建的容器中。

如果我们修改了 Pod 中某个 container 的 image 字段，kubelet 会发现 container 的 hash 发生了变化、与机器上过去创建的容器 hash 不一致，而后 kubelet 就会把旧容器停掉，然后根据最新 Pod spec 中的 container 来创建新的容器。

重建完成后，Pod 中除了该容器的 restartCount 增加以外不会有什么其他变化。 注意，之前临时写到旧容器 **rootfs** 中的文件会丢失，但是 volume mount 挂载卷中的数据都还存在。

```bash
k get pod -w                  ✔ 1|0 ⎈ k3d-panlq-dev-cluster
NAME           READY   STATUS    RESTARTS   AGE
demo-pod3      1/1     Running   0          3m39s
demo-pod3      1/1     Running   0          4m6s
demo-pod3      1/1     Running   1 (5s ago)   4m11s
```

**这个功能，其实就是针对单个 Pod 的原地升级的核心原理。**

## 2. Pod 更新的机制

在原生 kube-apiserver 中，对 Pod 对象的更新请求有严格的 [validation 校验逻辑](https://github.com/kubernetes/kubernetes/blob/master/pkg/apis/core/validation/validation.go#L5281)：

```go
// validate updateable fields:
// 1.  spec.containers[*].image
// 2.  spec.initContainers[*].image
// 3.  spec.activeDeadlineSeconds
```

简单来说，对于 running 中的 pod, 在 Pod Spec 中只允许修改指定的几个字段，如 containers/initContainers .image，修改其他字段会报错。报错内容如下所示

```bash
k apply -f demo3.yaml     18s ⎈ k3d-panlq-dev-cluster
The Pod "demo-pod3" is invalid: spec: Forbidden: pod updates may not change fields other than `spec.containers[*].image`,`spec.initContainers[*].image`,`spec.activeDeadlineSeconds`,`spec.tolerations` (only additions to existing tolerations),`spec.terminationGracePeriodSeconds` (allow it to be set to 1 if it was previously negative)
```

## 3. containerStatuses 上报

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: nginx
      image: nginx:latest
status:
  containerStatuses:
    - name: nginx
      image: nginx:mainline
      imageID: docker-pullable://nginx@sha256:2f68b99bc0d6d25d0c56876b924ec20418544ff28e1fb89a4c27679a40da811b
```

kubelet 会在 pod.status 中上报 containerStatuses，对应 Pod 中所有容器的实际运行状态。

绝大多数情况下，spec.containers[x].image 与 status.containerStatuses[x].image 两个镜像是一致的。

但是也有上述这种情况，kubelet 上报的与 spec 中的 image 不一致（spec 中是 nginx:latest，但 status 中上报的是 nginx:mainline）。

这是因为，kubelet 所上报的 image 其实是从 CRI 接口中拿到的容器对应的镜像名。而如果 Node 机器上存在多个镜像对应了一个 imageID，那么上报的可能是其中任意一个：

```bash
$ docker images | grep nginx
nginx            latest              2622e6cca7eb        2 days ago          132MB
nginx            mainline            2622e6cca7eb        2 days ago
```

## 4. ReadinessGate 控制 Pod 是否 Ready

在 Kubernetes 1.12 版本之前，一个 Pod 是否处于 Ready 状态只是由 kubelet 根据容器状态来判定：如果 Pod 中容器全部 ready，那么 Pod 就处于 Ready 状态。

但事实上，很多时候上层 operator 或用户都需要能控制 Pod 是否 Ready 的能力。因此，Kubernetes 1.12 版本之后提供了一个 readinessGates 功能来满足这个场景。如下：

```yaml
apiVersion: v1
kind: Pod
spec:
  readinessGates:
    - conditionType: MyDemo
status:
  conditions:
    - type: MyDemo
      status: "True"
    - type: ContainersReady
      status: "True"
    - type: Ready
      status: "True"
```

目前 kubelet 判定一个 Pod 是否 Ready 的两个前提条件：

1. Pod 中容器全部 Ready（其实对应了 ContainersReady condition 为 True）；
2. 如果 pod.spec.readinessGates 中定义了一个或多个 conditionType，那么需要这些 conditionType 在 pod.status.conditions 中都有对应的 status: "true" 的状态。

只有满足上述两个前提，kubelet 才会上报 Ready condition 为 True。

# 4. 技术实现

了解上面四个背景，接下来从源码分析一下 OpenKruise 是如何在 k8s 中实现原地升级的

## 1. 单 Pod 如何原地升级？

有背景 1，2 可以知道 Pod 本身就支持原地升级，只是现有提供的高层次的工作负载如 Deployment 等都会先删除在新建 pod。所以只要调整控制器的逻辑，不删除 pod， 而是仅仅修改如 image 字段，然后写入 etcd。kubelet 监听到 pod 变化就会自动对 pod 进行原地升级了。

OpenKruise 就是实现了多种控制器

- [CloneSet](https://openkruise.io/zh/docs/user-manuals/cloneset)
- [Advanced StatefulSet](https://openkruise.io/zh/docs/user-manuals/advancedstatefulset)
- [Advanced DaemonSet](https://openkruise.io/zh/docs/user-manuals/advanceddaemonset)
- [SidecarSet](https://openkruise.io/zh/docs/user-manuals/sidecarset)

## 2. 如何判断 Pod 原地升级成功？

我们再来看下修改前后 pod 的信息有什么变化，

修改前如下

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{},"name":"demo-pod3","namespace":"default"},"spec":{"containers":[{"image":"nginx:latest","name":"app","resources":{"limits":{"cpu":"1","memory":"200Mi"},"requests":{"cpu":"0.5","memory":"100Mi"}}}]}}
  creationTimestamp: "2025-05-28T16:26:56Z"
  name: demo-pod3
  namespace: default
  resourceVersion: "32749"
  uid: 2e675a6b-dca2-4b33-8cf8-3b3dfac64535
spec:
  containers:
    - image: nginx:latest
      imagePullPolicy: Always
      name: app
      resources:
        limits:
          cpu: "1"
          memory: 200Mi
        requests:
          cpu: 500m
          memory: 100Mi

      # ...
status:
  #...
  containerStatuses:
    - containerID: containerd://5cba2af8bf919dfefa5253d64faedf47dd46ee4ff04606d70783518bfe69ec80
      image: docker.io/library/nginx:latest
      imageID: docker.io/library/nginx@sha256:fb39280b7b9eba5727c884a3c7810002e69e8f961cc373b89c92f14961d903a0
      lastState: {}
      name: app
      ready: true
      restartCount: 0
      started: true
      state:
        running:
          startedAt: "2025-05-28T16:27:01Z"
```

当我们修改镜像 image 为 nginx:alpine 后，pod 数据如下

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{},"name":"demo-pod3","namespace":"default"},"spec":{"containers":[{"image":"nginx:latest","name":"app","resources":{"limits":{"cpu":"1","memory":"200Mi"},"requests":{"cpu":"0.5","memory":"100Mi"}}}]}}
  creationTimestamp: "2025-05-28T16:26:56Z"
  name: demo-pod3
  namespace: default
  resourceVersion: "33001"
  uid: 2e675a6b-dca2-4b33-8cf8-3b3dfac64535
spec:
  containers:
    - image: nginx:alpine
      imagePullPolicy: Always
      name: app
      resources:
        limits:
          cpu: "1"
          memory: 200Mi
        requests:
          cpu: 500m
          memory: 100Mi
      # ...
status:
  # ...
  containerStatuses:
    - containerID: containerd://38030ee8c07e1588b8126bdbc2a72052b7d9135e00b505afa3a83d05059d9e47
      image: docker.io/library/nginx:alpine
      imageID: docker.io/library/nginx@sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10
      lastState:
        terminated:
          containerID: containerd://5cba2af8bf919dfefa5253d64faedf47dd46ee4ff04606d70783518bfe69ec80
          exitCode: 0
          finishedAt: "2025-05-28T16:31:02Z"
          reason: Completed
          startedAt: "2025-05-28T16:27:01Z"
      name: app
      ready: true
      restartCount: 1
      started: true
      state:
        running:
          startedAt: "2025-05-28T16:31:06Z"
```

可以看到当我们修改完 image 后，pod 的 contianerStatuses 中对应的镜像的容器 containerID, imageID 都会改变。由“背景 3”可知，比较 spec 和 status 中的 image 字段是不靠谱的，因为很有可能 status 中上报的是 Node 上存在的另一个镜像名（相同 imageID）。

在旧版本的实现中：判断逻辑如下

> **判断 Pod 原地升级是否成功，相对来说比较靠谱的办法，是在原地升级前先将 status.containerStatuses[x].imageID 记录下来。在更新了 spec 镜像之后，如果观察到 Pod 的 status.containerStatuses[x].imageID 变化了，我们就认为原地升级已经重建了容器。**
>
> 但这样一来，我们对原地升级的 image 也有了一个要求：**不能用 image 名字（tag）不同、但实际对应同一个 imageID 的镜像来做原地升级，否则可能一直都被判断为没有升级成功（因为 status 中 imageID 不会变化）。**

在最新版本中，判断原地升级是否成功，是 pod 的数据和 contianer runtime 的实时数据进行对比，如果 pod 元数据和 实际运行在节点上的容器一直，就认为是成功的。

openkruise 提供了一个 daemon pod 会 通过 podInformer 实时监测 pod 的变更事件。然后通过 CRI（Container Runtime Interface）直接从容器运行时（如 Docker、Containerd）获取容器的状态信息。

```go
// pkg/daemon/containermeta/container_meta_controller.go
func (c *Controller) sync(key string) (retErr error) {
	namespace, name, err := cache.SplitMetaNamespaceKey(key)
	if err != nil {
		klog.InfoS("Invalid key", "key", key)
		return nil
	}

	// 从 pod informer indexer 中获取当前的 pod数据
	pod, err := c.podLister.Pods(namespace).Get(name)

	// ...

	// 初始化 cri runtime 和 kube runtime 这两个是用来获取容器实时状态数据的
	criRuntime, kubeRuntime, err := c.getRuntimeForPod(pod)

	// 通过 CRI 获取实际的容器的状态
	kubePodStatus, err := kubeRuntime.GetPodStatus(context.TODO(), pod.UID, name, namespace)
	if err != nil {
		return fmt.Errorf("failed to GetPodStatus: %v", err)
	}

	oldMetaSet, err := appspub.GetRuntimeContainerMetaSet(pod)
	if err != nil {
		klog.ErrorS(err, "Failed to get old runtime meta from Pod", "namespace", namespace, "name", name)
	}
	// 合并新旧状态，生成新的 RuntimeContainerMetaSet(最终用于 原地升级是否成功的判断依据)
	newMetaSet := c.manageContainerMetaSet(pod, kubePodStatus, oldMetaSet, criRuntime)

	return c.reportContainerMetaSet(pod, oldMetaSet, newMetaSet)
}

func (c *Controller) reportContainerMetaSet(pod *v1.Pod, oldMetaSet, newMetaSet *appspub.RuntimeContainerMetaSet) error {
	if reflect.DeepEqual(oldMetaSet, newMetaSet) {
		return nil
	}

	newPod := &v1.Pod{
		ObjectMeta: metav1.ObjectMeta{Namespace: pod.Namespace, Name: pod.Name},
	}
	containerMetaSetStr := util.DumpJSON(newMetaSet)
	klog.InfoS("Reporting container meta changed in Pod", "namespace", pod.Namespace, "name", pod.Name, "containerMetaSetStr", containerMetaSetStr)
	// 使用 StrategicMergePatch 更新 Pod 的 annotations
	mergePatch, _ := json.Marshal(map[string]interface{}{
		"metadata": map[string]interface{}{
			"annotations": map[string]string{
				appspub.RuntimeContainerMetaKey: containerMetaSetStr,
			},
		},
	})
	err := c.runtimeClient.Status().Patch(context.TODO(), newPod, runtimeclient.RawPatch(types.StrategicMergePatchType, mergePatch))
	// ...
	return nil
}
```

kubePodStatus 的获取 源码，通过 pod uid 调用 cri 获取容器实时状态数据

```go
// pkg/daemon/kuberuntime/kuberuntime_container.go
// getPodContainerStatuses gets all containers' statuses for the pod.
func (m *genericRuntimeManager) getPodContainerStatuses(uid types.UID, name, namespace string) ([]*kubeletcontainer.Status, error) {
	// Select all containers of the given pod.
  // 1. 首先通过 CRI 的 ListContainers 接口获取所有属于该 Pod 的容器
	containers, err := m.runtimeService.ListContainers(context.TODO(), &runtimeapi.ContainerFilter{
		LabelSelector: map[string]string{kubelettypes.KubernetesPodUIDLabel: string(uid)},
	})
	if err != nil {
		return nil, fmt.Errorf("run ListContainers error: %v", err)
	}
	statuses := make([]*kubeletcontainer.Status, len(containers))
	for i, c := range containers {
    // 2. 然后对每个容器调用 CRI 的 ContainerStatus 接口获取实时状态
		status, err := m.runtimeService.ContainerStatus(context.TODO(), c.Id, false)
		if err != nil {
			return nil, fmt.Errorf("run ContainerStatus for %s error: %v", c.Id, err)
		}
		cStatus := toKubeContainerStatus(status.Status, m.runtimeName)
		// TODO: Populate the termination message if needed.
		statuses[i] = cStatus
	}

	sort.Sort(containerStatusByCreated(statuses))
	return statuses, nil
}
```

小结，对比源数据获取逻辑如下：

- 当修改镜像并写入 etcd 后， kruise-controller-manager 更新 Pod spec
- kubelet 检测到变化，通过容器运行时重建容器
- kruise-daemon 通过 PodInformer 监听到 Pod 变化（如容器 ID、数量变化）
- kruise-daemon 调用 kubeRuntime.GetPodStatus 从容器运行时获取最新状态
- 计算新容器的哈希值（ PlainHash 、 PlainHashWithoutResources 、 ExtractedEnvFromMetadataHash ）
- 将这些信息更新到 Pod 的 runtime-container-meta annotation

最终对比的位置

```go
type RuntimeContainerHashes struct {
    // PlainHash 是直接从 pod.spec.container[x] 计算出的哈希值
    // 通常由 Kubelet 计算，并保存在每个运行时容器的注解中
    PlainHash uint64

    // PlainHashWithoutResources 是从 pod.spec.container[x] 计算的哈希值
    // 但不包含 Resources 字段
    PlainHashWithoutResources uint64

    // ExtractedEnvFromMetadataHash 是从实际运行的容器中提取的环境变量哈希值
    ExtractedEnvFromMetadataHash uint64
}

// The requirements for hash consistent:
// 1. all containers in spec.containers should also be in status.containerStatuses and runtime-container-meta
// 2. all containers in status.containerStatuses and runtime-container-meta should have the same containerID
// 3. all containers in spec.containers and runtime-container-meta should have the same hashes
func checkAllContainersHashConsistent(pod *v1.Pod, runtimeContainerMetaSet *appspub.RuntimeContainerMetaSet, hashType hashType) bool {
	// 遍历所有容器
	for i := range pod.Spec.Containers {
		containerSpec := &pod.Spec.Containers[i]

		var containerStatus *v1.ContainerStatus
		for j := range pod.Status.ContainerStatuses {
			if pod.Status.ContainerStatuses[j].Name == containerSpec.Name {
				containerStatus = &pod.Status.ContainerStatuses[j]
				break
			}
		}
		if containerStatus == nil {
			klog.InfoS("Find no container in status for Pod", "containerName", containerSpec.Name, "namespace", pod.Namespace, "podName", pod.Name)
			return false
		}
		// 检查 runtime-container-meta
		var containerMeta *appspub.RuntimeContainerMeta
		for i := range runtimeContainerMetaSet.Containers {
			if runtimeContainerMetaSet.Containers[i].Name == containerSpec.Name {
				containerMeta = &runtimeContainerMetaSet.Containers[i]
				continue
			}
		}
		// 如果找不到容器状态或 meta，说明还没准备好
		if containerMeta == nil {
			klog.InfoS("Find no container in runtime-container-meta for Pod", "containerName", containerSpec.Name, "namespace", pod.Namespace, "podName", pod.Name)
			return false
		}
		// 检查容器ID是否一致
		if containerMeta.ContainerID != containerStatus.ContainerID {
			klog.InfoS("Find container in runtime-container-meta for Pod has different containerID with status",
				"containerName", containerSpec.Name, "namespace", pod.Namespace, "podName", pod.Name,
				"metaID", containerMeta.ContainerID, "statusID", containerStatus.ContainerID)
			return false
		}

		// 比较 hash 是否一致
        // 这里的 hash 包含了镜像信息，所以镜像不一致 hash 就不会相同
		switch hashType {
		case plainHash:
			if expectedHash := kubeletcontainer.HashContainer(containerSpec); containerMeta.Hashes.PlainHash != expectedHash {
				klog.InfoS("Find container in runtime-container-meta for Pod has different plain hash with spec",
					"containerName", containerSpec.Name, "namespace", pod.Namespace, "podName", pod.Name,
					"metaHash", containerMeta.Hashes.PlainHash, "expectedHash", expectedHash)
				return false
			}
		case plainHashWithoutResources:
			// 检查不包含资源的纯哈希，kruise 1.8.0 支持 容器的 resize 原地升级
			containerSpecCopy := containerSpec.DeepCopy()
			containerSpecCopy.Resources = v1.ResourceRequirements{}
			if expectedHash := kubeletcontainer.HashContainer(containerSpecCopy); containerMeta.Hashes.PlainHashWithoutResources != expectedHash {
				klog.InfoS("Find container in runtime-container-meta for Pod has different plain hash with spec(except resources)",
					"containerName", containerSpecCopy.Name, "namespace", pod.Namespace, "podName", pod.Name,
					"metaHash", containerMeta.Hashes.PlainHashWithoutResources, "expectedHash", expectedHash)
				return false
			}
		case extractedEnvFromMetadataHash:
			// 检查提取的环境变量元数据哈希， 对比运行时容器的环境变量和 Pod spec 中的 envFrom 元数据
			hasher := utilcontainermeta.NewEnvFromMetadataHasher()
			if expectedHash := hasher.GetExpectHash(containerSpec, pod); containerMeta.Hashes.ExtractedEnvFromMetadataHash != expectedHash {
				klog.InfoS("Find container in runtime-container-meta for Pod has different extractedEnvFromMetadataHash with spec",
					"containerName", containerSpec.Name, "namespace", pod.Namespace, "podName", pod.Name,
					"metaHash", containerMeta.Hashes.ExtractedEnvFromMetadataHash, "expectedHash", expectedHash)
				return false
			}
		}
	}

	return true
}

```

升级成的判断逻辑

- 检查 spec.containers 中的所有容器都存在于 status.containerStatuses 和 runtime-container-meta 中
- 确认 status.containerStatuses 和 runtime-container-meta 中的容器具有相同的 containerID
- 验证 spec.containers 和 runtime-container-meta 中的容器具有相同的哈希值
- 所有检查通过后，Pod 的 InPlaceUpdateReady 条件被设置为 True

## 3. 如何确保原地升级过程中流量无损?

在 Kubernetes 中，一个 Pod 是否 Ready 就代表了它是否可以提供服务。因此，像 Service 这类的流量入口都会通过判断 Pod Ready 来选择是否能将这个 Pod 加入 endpoints 端点中。

由“背景 4”可知，从 Kubernetes 1.12+ 之后，operator/controller 这些组件也可以通过设置 readinessGates 和更新 pod.status.conditions 中的自定义 type 状态，来控制 Pod 是否可用。

因此，得出第三个实现原理：**可以在 pod.spec.readinessGates 中定义一个叫 InPlaceUpdateReady 的 conditionType。**

在原地升级时：

1. **先将 pod.status.conditions 中的 InPlaceUpdateReady condition 设为 "False"，这样就会触发 kubelet 将 Pod 上报为 NotReady，从而使流量组件（如 endpoint controller）将这个 Pod 从服务端点摘除；**
2. **再更新 pod spec 中的 image 触发原地升级。**
3. **原地升级结束后，再将 InPlaceUpdateReady condition 设为 "True"，使 Pod 重新回到 Ready 状态。**

另外在原地升级的两个步骤中，第一步将 Pod 改为 NotReady 后，流量组件异步 watch 到变化并摘除端点可能是需要一定时间的。因此我们也提供优雅原地升级的能力，即通过 gracePeriodSeconds 配置在修改 NotReady 状态和真正更新 image 触发原地升级两个步骤之间的静默期时间。

```go


// pkg/controller/cloneset/cloneset_controller.go
func (r *ReconcileCloneSet) doReconcile(request reconcile.Request) (res reconcile.Result, retErr error) {
	// cloneset 控制器 协调逻辑

	// ...
	// scale and update pods
	syncErr := r.syncCloneSet(instance, &newStatus, currentRevision, updateRevision, revisions, filteredPods, filteredPVCs)

	// ...
}

func (r *ReconcileCloneSet) syncCloneSet(
	instance *appsv1alpha1.CloneSet, newStatus *appsv1alpha1.CloneSetStatus,
	currentRevision, updateRevision *apps.ControllerRevision, revisions []*apps.ControllerRevision,
	filteredPods []*v1.Pod, filteredPVCs []*v1.PersistentVolumeClaim,
) error {
	// ...
	podsUpdateErr = r.syncControl.Update(updateSet, currentRevision, updateRevision, revisions, filteredPods, filteredPVCs)

	// ...
}

// pkg/controller/cloneset/sync/cloneset_update.go
func (c *realControl) Update(cs *appsv1alpha1.CloneSet,
	currentRevision, updateRevision *apps.ControllerRevision, revisions []*apps.ControllerRevision,
	pods []*v1.Pod, pvcs []*v1.PersistentVolumeClaim,
) error {
	// 更新 CloneSet 的状态
	// ...
	for _, pod := range pods {
		patchedState, duration, err := c.refreshPodState(cs, coreControl, pod, updateRevision.Name)
		// ...
	}
	// ...

}

func (c *realControl) refreshPodState(cs *appsv1alpha1.CloneSet, coreControl clonesetcore.Control, pod *v1.Pod, updateRevision string) (bool, time.Duration, error) {
	opts := coreControl.GetUpdateOptions()
	opts = inplaceupdate.SetOptionsDefaults(opts)

	res := c.inplaceControl.Refresh(pod, opts)
	if res.RefreshErr != nil {
		klog.ErrorS(res.RefreshErr, "CloneSet failed to update pod condition for inplace",
			"cloneSet", klog.KObj(cs), "pod", klog.KObj(pod))
		return false, 0, res.RefreshErr
	}
	// ... 省略

	return false, res.DelayDuration, nil
}

func (c *realControl) Refresh(pod *v1.Pod, opts *UpdateOptions) RefreshResult {
	opts = SetOptionsDefaults(opts)

	// check if it is in grace period
	// 优雅退出时间内，不允许更新
	if gracePeriod, _ := appspub.GetInPlaceUpdateGrace(pod); gracePeriod != "" {
		delayDuration, err := c.finishGracePeriod(pod, opts)
		if err != nil {
			return RefreshResult{RefreshErr: err}
		}
		return RefreshResult{DelayDuration: delayDuration}
	}

	// 检查是否已经更新完成
	if stateStr, ok := appspub.GetInPlaceUpdateState(pod); ok {
		state := appspub.InPlaceUpdateState{}
		if err := json.Unmarshal([]byte(stateStr), &state); err != nil {
			return RefreshResult{RefreshErr: err}
		}

		// check in-place updating has not completed yet
		// 这里调用的就是上面第二点讲述的判断升级是否成功
		if checkErr := opts.CheckContainersUpdateCompleted(pod, &state); checkErr != nil {
			klog.V(6).ErrorS(checkErr, "Check Pod in-place update not completed yet", "namespace", pod.Namespace, "name", pod.Name)
			return RefreshResult{}
		}

		// check if there are containers with lower-priority that have to in-place update in next batch
		if len(state.NextContainerImages) > 0 || len(state.NextContainerRefMetadata) > 0 || len(state.NextContainerResources) > 0 {

			// pre-check the previous updated containers
			if checkErr := doPreCheckBeforeNext(pod, state.PreCheckBeforeNext); checkErr != nil {
				klog.V(5).ErrorS(checkErr, "Pod in-place update pre-check not passed", "namespace", pod.Namespace, "name", pod.Name)
				return RefreshResult{}
			}

			// do update the next containers
			// kruise 支持分批更新，这里就是启动下一批更新
			if updated, err := c.updateNextBatch(pod, opts); err != nil {
				return RefreshResult{RefreshErr: err}
			} else if updated {
				return RefreshResult{}
			}
		}
	}

	if !containsReadinessGate(pod) {
		return RefreshResult{}
	}

	// 如果升级完成，则更新 Pod 的 Ready 状态
	newCondition := v1.PodCondition{
		Type:               appspub.InPlaceUpdateReady,
		Status:             v1.ConditionTrue,
		LastTransitionTime: metav1.NewTime(Clock.Now()),
	}
	err := c.updateCondition(pod, newCondition)
	return RefreshResult{RefreshErr: err}
}
```

## 4. 小结

原地升级的本质是利用 pod 本身就有的能力，但是在高层次上的设计要考虑，如何判断是否升级成，如何让流量无损。openkruise 还提供一个镜像预热的功能，让容器镜像的原地升级速度更快 [image preheat](https://openkruise.io/zh/docs/user-manuals/imagepulljob)

# 5. 实践

```yaml
apiVersion: apps.kruise.io/v1alpha1
kind: CloneSet
metadata:
  labels:
    app: sample
  name: sample
spec:
  replicas: 2
  updateStrategy:
    type: InPlaceIfPossible
  selector:
    matchLabels:
      app: sample
  template:
    metadata:
      labels:
        app: sample
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          resources:
            requests:
              cpu: "0.5" # 可修改
              memory: "100Mi" # 可修改
            limits:
              cpu: "0.8" # 可修改
              memory: "300Mi" # 可修改
```

> 使用 k3d 在本地启动 k3s 集群， 注意修改 [kruise daemon.socketLocation 参数](https://openkruise.io/zh/docs/installation#k3s-%E5%AE%89%E8%A3%85%E5%8F%82%E6%95%B0)

```bash
# 1. helm repo add openkruise https://openkruise.github.io/charts/

# 2. install
helm install kruise openkruise/kruise --version 1.8.0 \
  --set featureGates="InPlaceWorkloadVerticalScaling=true" \
  --set daemon.socketLocation="/run/k3s" \
  --set daemon.socketFile="containerd/containerd.sock" \

```

```bash
# 1. 创建 cloneset
k apply -f cloneset-demo.yaml       ⎈ k3d

# 2. 修改镜像地址，可以用 k get pod -w 观察 pod 是否有什么变化
```

# 6. 参考与延伸阅读

1. [揭秘：如何为 Kubernetes 实现原地升级](https://developer.aliyun.com/article/765421)
2. [Kubernetes 容器重启原理-Kubelet Hash 计算](https://mp.weixin.qq.com/s/dcEFXE7VasUAvYG7HbgqgA)
3. [openkruise-原地升级](https://openkruise.io/zh/docs/core-concepts/inplace-update/#%E5%8E%9F%E5%9C%B0%E5%8D%87%E7%BA%A7%E6%94%AF%E6%8C%81%E4%BF%AE%E6%94%B9%E8%B5%84%E6%BA%90)
4. [resize-container-resources ](https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/)
