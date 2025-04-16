# 简介

VXLAN，即Virtual Extensible LAN（虚拟可扩展局域网），是Linux内核本身就支持的一种网络虚似化技术。所以说，VXLAN可以完全在内核态实现上述封装和解封装的工作，从而通过与前面相似的“隧道”机制，构建出覆盖网络（Overlay Network）。

VXLAN的覆盖网络的设计思想是：在现有的三层网络之上，“覆盖”一层虚拟的、由内核VXLAN模块负责维护的二层网络，使得连接在这个VXLAN二层网络上的“主机”（虚拟机或者容器都可以）之间，可以像在同一个局域网（LAN）里那样自由通信。当然，实际上，这些“主机”可能分布在不同的宿主机上，甚至是分布在不同的物理机房里。

而为了能够在二层网络上打通“隧道”，VXLAN会在宿主机上设置一个特殊的网络设备作为“隧道”的两端。这个设备就叫作VTEP，即：VXLAN Tunnel End Point（虚拟隧道端点）。

而VTEP设备的作用是，它进行封装和解封装的对象，是二层数据帧（Ethernet frame）；而且这个工作的执行流程，全部是在内核里完成的（因为VXLAN本身就是Linux内核中的一个模块）

[图解建立VXLAN隧道的步骤（懒人包）](https://henchat.net/vxlan-tunnel-illustration/)

[华为的官方手册-什么是 vxlan](https://support.huawei.com/enterprise/zh/doc/EDOC1100087027?idPath=24030814%7C21782165%7C21782239%7C252837181)

[图解 VXLAN 容器网络通信方案](https://xie.infoq.cn/article/32d73ddc329f8f384f4db2184)

[Overlay 网络互通：VXLAN](https://www.thebyte.com.cn/content/chapter1/vxlan.html)
