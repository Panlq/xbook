package main

import (
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"syscall"
)

// go run main.go run [OPTIONS] <command> [args...]
// 示例:
// sudo go run main.go run /bin/sh -c "echo Hello from container"
// sudo go run main.go run --cpu-period=100000 --cpu-quota=20000 --memory=52428800 /bin/sh -c "echo Hello from container"

var (
	cpuPeriod int64  = -1 // CPU 时间周期 (us)
	cpuQuota  int64  = -1 // CPU 配额 (us)
	memory    int64  = -1 // 内存限制 (bytes)
	rootfs    string      // 根文件系统路径
)

func init() {
	flag.Int64Var(&cpuPeriod, "cpu-period", -1, "CPU period in microseconds")
	flag.Int64Var(&cpuQuota, "cpu-quota", -1, "CPU quota in microseconds")
	flag.Int64Var(&memory, "memory", -1, "Memory limit in bytes")
	flag.StringVar(&rootfs, "rootfs", "", "Root filesystem path")
}

func main() {
	fmt.Println("[Main Process] Starting")

	// 先检查是否有子命令
	if len(os.Args) < 2 {
		panic("Usage: go run main.go run [OPTIONS] COMMAND")
	}

	// 手动分离子命令和flag
	switch os.Args[1] {
	case "run":
		// 创建新的FlagSet避免污染全局flag
		runCmd := flag.NewFlagSet("run", flag.ExitOnError)
		runCmd.Int64Var(&cpuPeriod, "cpu-period", -1, "CPU period")
		runCmd.Int64Var(&cpuQuota, "cpu-quota", -1, "CPU quota")
		runCmd.Int64Var(&memory, "memory", -1, "Memory limit")
		runCmd.StringVar(&rootfs, "rootfs", "", "Root filesystem")

		// 解析run子命令后的参数
		runCmd.Parse(os.Args[2:])
		run(runCmd.Args()) // 传入剩余非flag参数
	case "child":
		child()
	default:
		panic("Unknown command")
	}
}

// run 函数：启动一个新的容器进程
func run(args []string) {
	fmt.Printf("[Main Process] Running %v\n", args)

	// 只保留用户命令部分（过滤掉 flag）
	var userCmd []string
	for _, arg := range args {
		if !isFlagArg(arg) {
			userCmd = append(userCmd, arg)
		}
	}

	if len(userCmd) == 0 {
		panic("no command provided to child process")
	}

	// 创建一个新进程来执行 child 模式
	cmd := exec.Command("/proc/self/exe", append([]string{"child"}, userCmd...)...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// 设置命名空间标志：
	// CLONE_NEWUTS: 主机名隔离
	// CLONE_NEWPID: PID 命名空间隔离
	// CLONE_NEWNS: Mount namespace 隔离
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Cloneflags:   syscall.CLONE_NEWUTS | syscall.CLONE_NEWPID | syscall.CLONE_NEWNS,
		Unshareflags: syscall.CLONE_NEWNS,
	}
	// 设置环境变量传递资源限制
	if cpuPeriod > 0 && cpuQuota > 0 {
		cmd.Env = append(os.Environ(), fmt.Sprintf("CPU_PERIOD=%d", cpuPeriod))
		cmd.Env = append(cmd.Env, fmt.Sprintf("CPU_QUOTA=%d", cpuQuota))
	}
	if memory > 0 {
		cmd.Env = append(cmd.Env, fmt.Sprintf("MEMORY=%d", memory))
	}

	if rootfs != "" {
		cmd.Env = append(cmd.Env, fmt.Sprintf("ROOTFS=%s", rootfs))
	}

	// 执行 child 子进程
	must(cmd.Run())
}

// child 函数：容器进程实际执行的逻辑
func child() {
	// 所有参数都是用户命令（第一个是 child，后面是 /bin/sh -c ...）
	userArgs := os.Args[2:]

	if len(userArgs) == 0 {
		panic("no command provided to child process")
	}

	fmt.Printf("[Child Process] Executing command: %v\n", userArgs)

	// 从环境变量中读取用户设置的资源限制
	cpuPeriodStr := os.Getenv("CPU_PERIOD")
	cpuQuotaStr := os.Getenv("CPU_QUOTA")
	memLimitStr := os.Getenv("MEMORY")
	// 获取环境变量中的 rootfs 路径，默认是 "/home/ubuntu/ubuntufs"
	rootfs := os.Getenv("ROOTFS")
	if rootfs == "" {
		// 获取当然文件所在目录下的 my-busybox-rootfs
		// 获取当前工作目录
		wd, err := os.Getwd()
		if err != nil {
			fmt.Printf("获取当前工作目录失败: %v\n", err)
			return
		}
		// 拼接目标目录路径
		rootfs = filepath.Join(wd, "my-busybox-rootfs")
		if _, err := os.Stat(rootfs); os.IsNotExist(err) {
			panic(fmt.Sprintf("rootfs %s does not exist", rootfs))
		}
	}

	// 设置 cgroup 资源控制（如限制最大进程数、CPU、内存）
	cg(cpuPeriodStr, cpuQuotaStr, memLimitStr)

	// 构建要执行的命令对象
	cmd := exec.Command(userArgs[0], userArgs[1:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// 设置主机名（仅在容器中生效）
	must(syscall.Sethostname([]byte("container")))
	fmt.Printf("[Child Process] Chrooting into %s\n", rootfs)
	// 将当前进程的根目录切换到 ubuntufs（实现文件系统隔离）
	must(syscall.Chroot(rootfs))

	// 切换工作目录到新的根目录下
	fmt.Println("[Child Process] Changing working directory to /")
	must(os.Chdir("/"))

	// 挂载 proc 文件系统（让容器可以访问自己的进程信息）
	fmt.Println("[Child Process] Mounting proc...")
	// 改成判断文件夹是否存在不存在在创建
	if _, err := os.Stat("proc"); os.IsNotExist(err) {
		must(os.Mkdir("proc", 0o755))
		defer os.RemoveAll("proc")
	}
	must(syscall.Mount("proc", "proc", "proc", 0, ""))
	defer func() {
		must(syscall.Unmount("proc", 0))
	}()

	// 挂载 tmpfs（内存中的文件系统，用于模拟 /tmp 等目录）
	fmt.Println("[Child Process] Mounting tmpfs...")
	// 改成判断文件夹是否存在不存在在创建
	if _, err := os.Stat("mytemp"); os.IsNotExist(err) {
		must(os.Mkdir("mytemp", 0o755))
		defer os.RemoveAll("mytemp")
	}
	must(syscall.Mount("tmpfs", "mytemp", "tmpfs", 0, ""))
	defer func() {
		must(syscall.Unmount("mytemp", 0))
	}()

	// 执行用户指定的命令（例如 /bin/sh）
	must(cmd.Run())

	// 卸载挂载点
	// must(syscall.Unmount("proc", 0))
	// must(syscall.Unmount("mytemp", 0))
}

// cg 函数：设置 cgroup（资源控制）
func cg(cpuPeriod, cpuQuota, mem string) {
	cgroupPath := "/sys/fs/cgroup"

	isV2 := isCgroup2Unified()

	if isV2 {
		lizCgroup := filepath.Join(cgroupPath, "liz")
		os.Mkdir(lizCgroup, 0o755)
		defer os.RemoveAll(lizCgroup)

		os.WriteFile(filepath.Join(lizCgroup, "pids.max"), []byte("20"), 0o644)

		if cpuPeriod != "" && cpuQuota != "" {
			os.WriteFile(filepath.Join(lizCgroup, "cpu.max"), []byte(fmt.Sprintf("%s %s", cpuQuota, cpuPeriod)), 0o644)
		}

		if mem != "" {
			os.WriteFile(filepath.Join(lizCgroup, "memory.max"), []byte(mem), 0o644)
		}

		os.WriteFile(filepath.Join(lizCgroup, "cgroup.procs"), []byte(strconv.Itoa(os.Getpid())), 0o644)
	} else {
		pidsPath := filepath.Join(cgroupPath, "pids")
		cpuPath := filepath.Join(cgroupPath, "cpu")
		memoryPath := filepath.Join(cgroupPath, "memory")
		lizCgroup := filepath.Join(pidsPath, "liz")

		os.MkdirAll(lizCgroup, 0o755)
		defer os.RemoveAll(lizCgroup)

		os.WriteFile(filepath.Join(lizCgroup, "pids.max"), []byte("20"), 0o644)
		os.WriteFile(filepath.Join(lizCgroup, "notify_on_release"), []byte("1"), 0o644)

		if cpuPeriod != "" && cpuQuota != "" {
			os.WriteFile(filepath.Join(cpuPath, "liz/cpu.cfs_period_us"), []byte(cpuPeriod), 0o644)
			os.WriteFile(filepath.Join(cpuPath, "liz/cpu.cfs_quota_us"), []byte(cpuQuota), 0o644)
		}

		if mem != "" {
			os.WriteFile(filepath.Join(memoryPath, "liz/memory.limit_in_bytes"), []byte(mem), 0o644)
		}

		os.WriteFile(filepath.Join(lizCgroup, "tasks"), []byte(strconv.Itoa(os.Getpid())), 0o644)
	}
}

// isFlagArg 判断一个参数是否是 flag（即以 "--" 开头）
func isFlagArg(arg string) bool {
	return len(arg) >= 2 && arg[:2] == "--"
}

// isCgroup2Unified 判断是否是 cgroup v2
// cgroup v2 的特点是存在 /sys/fs/cgroup/cgroup.controllers 文件
func isCgroup2Unified() bool {
	_, err := os.Stat("/sys/fs/cgroup/cgroup.controllers")
	return err == nil
}

// must 是一个错误处理函数，如果出错就打印错误并退出程序
func must(err error) {
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
