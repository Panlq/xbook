# 概述

> 译：https://learncloudnative.com/blog/2023-05-31-kubeproxy-iptables

整个k8s 集群中，网络连通性要考虑的有四个层面

1. container to container
2. pod to pod
3. pod to service
4. ingress and egress


# 1. Container-to-Container

在 Kubernetes 中，Pod 通过网络命名空间解决容器间的通信问题。每个 Pod 都有自己的网络命名空间、IP 地址和端口空间。

Pod（网络命名空间）内的容器可以通过本地主机进行通信(localhost / socket)，并共享相同的 IP 地址和端口。Linux 中的 “网络命名空间” 使我们能够拥有与系统其余部分分离的网络接口和路由表。

# 2. Pod-to-Pod 



# 参考与延伸阅读

1. [Kubernetes Network Policy](1. https://learncloudnative.com/blog/2020-10-07-network-policies)
