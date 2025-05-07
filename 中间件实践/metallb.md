# 什么是 MetalLB

MetalLB 是一个用于裸机 Kubernetes 集群的负载均衡器实现，使用标准路由协议。

k8s 并没有为裸机集群实现负载均衡器，因此我们只有在以下 IaaS 平台（GCP, AWS, Azure）上才能使用 LoadBalancer 类型的 service。

因此裸机集群只能使用 NodePort 或者 externalIPs service 来对面暴露服务，然而这两种方式和 LoadBalancer service 相比都有很大的缺点。

而 MetalLB 的出现就是为了解决这个问题。

# 参考与延伸阅读

1. [裸机 Kubernetes 集群负载均衡器: MetalLB 简明教程](https://www.lixueduan.com/posts/cloudnative/01-metallb/#2-%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%A8%8B)
