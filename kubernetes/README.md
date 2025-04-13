k8s 源码阅读以及其他相关内容的存档记录

# K8s 组件架构

![k8s-arch](https://kubernetes.io/images/docs/kubernetes-cluster-architecture.svg)

![k8s-hl-component-arch](image/README/1744473829790.png)

控制面

- kube-apiserver
- etcd
- kube-scheduler
- kube-controller-manager

节点

- kubelete
- kube-proxy
- container runtime

插件

- dns
- dashboard
- container resource monitoring
- cluster-level-logging

# 参考与延伸阅读

1. 田飞雨-阅读：[https://blog.tianfeiyu.com/source-code-reading-notes/](https://blog.tianfeiyu.com/source-code-reading-notes/)
2. [Kubernetes&#39; Architecture Fundamentals](https://speakerdeck.com/luxas/kubernetes-architecture-fundamentals?slide=10)
