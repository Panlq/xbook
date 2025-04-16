# 1. 简介

NetworkPolicy 描述针对一组 Pod 所允许的网络流量，即白名单。

**Kubernetes里的Pod默认都是“允许所有”（Accept All）的** ，即：Pod可以接收来自任何发送方的请求；或者，向任何接收方发送请求。而如果你要对这个情况作出限制，就必须通过NetworkPolicy对象来指定。



# 2. 案例解析

```yaml
apiVersion: extensions/v1beta1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
   - Ingress
   - Egress
  ingress:
   - from:
     - namespaceSelector:
         matchLabels:
           project: myproject
     - podSelector:
         matchLabels:
           role: frontend
     ports:
       - protocol: tcp
         port: 6379
```

## 字段说明

- podSelector: 定义这个NetworkPolicy的限制范围，比如：当前Namespace里携带了role=db标签的Pod
- policyTypes: 定义了这个NetworkPolicy的类型是ingress和egress，即：它既会影响流入（ingress）请求，也会影响流出（egress）请求

ingress.from 含义：指定的ingress“白名单”，是任何Namespace里，携带project=myproject标签的Namespace里的Pod；以及default Namespace里，携带了role=frontend标签的Pod。允许被访问的端口是：6379

被隔离的对象，是所有携带了role=db标签的Pod

需要注意的是，定义一个NetworkPolicy对象的过程，容易犯错的是“白名单”部分（from和to字段）

```yaml
  ...
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          user: alice
    - podSelector:
        matchLabels:
          role: client
  ...
```

上面↑是或(OR)关系，下面👇是与(and)关系

```yaml
...
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          user: alice
      podSelector:
        matchLabels:
          role: client
  ...
```


## 依赖

如果要使上面定义的NetworkPolicy在Kubernetes集群里真正产生作用，你的CNI网络插件就必须是支持Kubernetes的NetworkPolicy的。

在具体实现上，凡是支持NetworkPolicy的CNI网络插件，都维护着一个NetworkPolicy Controller，通过控制循环的方式对NetworkPolicy对象的增删改查做出响应，然后在宿主机上完成iptables规则的配置工作。

在Kubernetes生态里，目前已经实现了NetworkPolicy的网络插件包括Calico、Weave和kube-router等多个项目，但是并不包括Flannel项目。

所以说，如果想要在使用Flannel的同时还使用NetworkPolicy的话，你就需要再额外安装一个网络插件，比如Calico项目，来负责执行NetworkPolicy。


# 3. 原理解析

根据上面案例，CNI插件会使用这个 NetWorkpolicy 的定义，在宿主机生成对应的 iptables规则。大概如下

```go
for dstIP := range 所有被networkpolicy.spec.podSelector选中的Pod的IP地址
  for srcIP := range 所有被ingress.from.podSelector选中的Pod的IP地址
    for port, protocol := range ingress.ports {
      iptables -A KUBE-NWPLCY-CHAIN -s $srcIP -d $dstIP -p $protocol -m $protocol --dport $port -j ACCEPT 
    }
  }
} 
```

这条规则的名字是KUBE-NWPLCY-CHAIN，含义是：当IP包的源地址是srcIP、目的地址是dstIP、协议是protocol、目的端口是port的时候，就允许它通过（ACCEPT）

**可以看到，Kubernetes网络插件对Pod进行隔离，其实是靠在宿主机上生成NetworkPolicy对应的iptable规则来实现的。**

在设置好隔离规则之后，网络插件还要相办法将所有对被隔离Pod的访问请求，都转发到上述KUBE-NWPLCY-CHAIN规则上去进行匹配。并且，如果匹配不通过，这个请求应该被“拒绝”。

在CNI网络插件中，上述需求可以通过设置两组iptables规则来实现

## 第一组

```go
for pod := range 该Node上的所有Pod {
    if pod是networkpolicy.spec.podSelector选中的 {
        iptables -A FORWARD -d $podIP -m physdev --physdev-is-bridged -j KUBE-POD-SPECIFIC-FW-CHAIN
        iptables -A FORWARD -d $podIP -j KUBE-POD-SPECIFIC-FW-CHAIN
        ...
    }
}
```


其中， **第一条FORWARD链“拦截”的是一种特殊情况** ：它对应的是同一台宿主机上容器之间经过CNI网桥进行通信的流入数据包。其中，–physdev-is-bridged的意思就是，这个FORWARD链匹配的是，通过本机上的网桥设备，发往目的地址是podIP的IP包。

当然，如果是像Calico这样的非网桥模式的CNI插件，就不存在这个情况了。

> kube-router其实是一个简化版的Calico，它也使用BGP来维护路由信息，但是使用CNI bridge插件负责跟Kubernetes进行交互。

而 **第二条FORWARD链“拦截”的则是最普遍的情况，即：容器跨主通信** 。这时候，流入容器的数据包都是经过路由转发（FORWARD检查点）来的

## 第二组

第一组这些规则最后都跳转（即：-j）到了名叫KUBE-POD-SPECIFIC-FW-CHAIN的规则上。它正是网络插件为NetworkPolicy设置的第二组规则

```bash
iptables -A KUBE-POD-SPECIFIC-FW-CHAIN -j KUBE-NWPLCY-CHAIN
iptables -A KUBE-POD-SPECIFIC-FW-CHAIN -j REJECT --reject-with icmp-port-unreachable
```


可以看到，首先在第一条规则里，我们会把IP包转交给前面定义的KUBE-NWPLCY-CHAIN规则去进行匹配。按照我们之前的讲述，如果匹配成功，那么IP包就会被“允许通过”。

而如果匹配失败，IP包就会来到第二条规则上。可以看到，它是一条REJECT规则。通过这条规则，不满足NetworkPolicy定义的请求就会被拒绝掉，从而实现了对该容器的“隔离”


# 4. 参考与延伸阅读

1. [深入剖析 kubernetes-为什么说Kubernetes只有soft multi-tenancy？- 张磊](https://learn.lianglianglee.com/%e4%b8%93%e6%a0%8f/%e6%b7%b1%e5%85%a5%e5%89%96%e6%9e%90Kubernetes/36%20%e4%b8%ba%e4%bb%80%e4%b9%88%e8%af%b4Kubernetes%e5%8f%aa%e6%9c%89soft%20multi-tenancy%ef%bc%9f.md)
2. [Kubernetes 文](https://kubernetes.io/zh-cn/docs/)/[参考](https://kubernetes.io/zh-cn/docs/reference/)/[Kubernetes API](https://kubernetes.io/zh-cn/docs/reference/kubernetes-api/)/[策略资源](https://kubernetes.io/zh-cn/docs/reference/kubernetes-api/policy-resources/)/[NetworkPolicy](https://kubernetes.io/zh-cn/docs/reference/kubernetes-api/policy-resources/network-policy-v1/)
