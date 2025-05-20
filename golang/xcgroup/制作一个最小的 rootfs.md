## 通过 busybox 制作一个最小的 rootfs

```bash

podman create --name mbusybox docker-prod-registry.cn-hangzhou.cr.aliyuncs.com/global/busybox:latest sh

# podman ps -a 查看 containerid


podman export e02003c2a033 > busybox.tar


mkdir -p my-busybox-rootfs

tar -xf busybox.tar -C my-busybox-rootfs

```

```bash
ls my-busybox-rootfs/
bin  dev  etc  home  lib  lib64  root  tmp  usr  var
ubuntu@node03:~$ sudo chroot my-busybox-rootfs /bin/sh
/ # ls
bin    dev    etc    home   lib    lib64  root   tmp    usr    var
```

## 制作 ubuntu rootfs

安装工具 `debootstrap`

> apt install debootstrap -y

可以指定镜像源

```bash
sudo debootstrap \
  --variant=minbase \
  --arch=amd64 \
  --include=bash,coreutils,apt \
  jammy \
  /home/ubuntu/ubuntufs \
  https://mirrors.tuna.tsinghua.edu.cn/ubuntu/
```

arm64 的只能走原生网络

```
sudo debootstrap \
  --variant=minbase \
  --arch=arm64 \
  --include=bash,coreutils,apt \
  jammy \
  /home/ubuntu/ubuntufs \
  http://ports.ubuntu.com/
```
