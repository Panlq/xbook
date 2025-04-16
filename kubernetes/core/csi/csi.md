# 概述

进入 K8s 的世界，会发现有很多方便扩展的 Interface，包括 CSI, CNI, CRI 等，将这些接口抽象出来，是为了更好的提供开放、扩展、规范等能力。

K8s 持久化存储经历了从 in-tree Volume 到 CSI Plugin(out-of-tree) 的迁移，一方面是为了将 K8s 核心主干代码与 Volume 相关代码解耦，便于更好的维护；另一方面则是为了方便各大云厂商实现统一的接口，提供个性化的云存储能力，以期达到云存储生态圈的开放共赢。

# 参考与延伸阅读

1. [如何接入 K8s 持久化存储？K8s CSI 实现机制浅析](https://www.cnblogs.com/tencent-cloud-native/p/15468049.html "发布于 2021-10-26 21:48")
2. [基于 CSI Kubernetes 存储插件的开发实践](https://kubesphere.io/zh/conferences/csi/)
3. [Kubernetes &amp; Storage: in-tree storage deprecation, CSI drivers and more](https://www.linkedin.com/pulse/kubernetes-storage-in-tree-deprecation-csi-drivers-more-arrieta/)
4. [Unix domain socket 简介 ](https://www.cnblogs.com/sparkdev/p/8359028.html "发布于 2018-01-27 17:40")
