## 零钱替换问题 dp 分析

[322. 零钱兑换](https://leetcode.cn/problems/coin-change/)

## 1. 问题定义

给定一个整数数组 `coins` 表示不同面额的硬币，和一个整数 `amount` 表示总金额。要求：

1. 计算凑成总金额所需的最少硬币个数
2. 如果没有任何组合能组成总金额，返回 -1
3. 可以认为每种硬币的数量是无限的（完全背包问题）

示例：
输入：coins = [1, 2, 5], amount = 11
输出：3 （5+5+1）

## 2. DP 定义和初始化

**定义** ：
`dp[i]`：凑出金额 i 所需的最少硬币数（无法凑出时为 ∞）

**初始化** ：

```python
dp = [float('inf')] * (amount + 1)  # 初始化为无穷大
dp[0] = 0  # 金额0需要0个硬币
```

## 3. 递推公式推导

对于每个金额 i（从 1 到 amount）：

1. 遍历所有硬币 coin：
   - 如果 coin ≤ i（当前硬币可用）：
     - 使用该硬币：硬币数 = 1（当前硬币） + dp[i - coin]（剩余金额的最优解）
2. 取所有可能选择中的最小值：

```python
dp[i] = min(dp[i], 1 + dp[i - coin])  # 对所有coin ≤ i
```

**关键点** ：

- `+1` 表示当前选择的硬币
- `dp[i - coin]` 表示剩余金额的最优解

## 4. 遍历顺序

**1. 外层循环** ：遍历所有硬币（顺序无关）

```python
for coin in coins:
```

**2. 内层循环** ：正序遍历金额（完全背包特性）

```python
for i in range(coin, amount + 1):
```

**为什么正序** ：
保证每个硬币可以重复使用（完全背包）。逆序会变成 0-1 背包（每个硬币只能用一次）。

## 5. 完整 DP 表格示例（coins=[1,2,5], amount=5）

| 金额 i | dp[i] | 计算过程（min 取值）                | 对应组合 |
| ------ | ----- | ----------------------------------- | -------- |
| 0      | 0     | 初始化                              | -        |
| 1      | 1     | min(∞, 1+dp[0])=1                   | 1        |
| 2      | 1     | min(∞, 1+dp[1], 1+dp[0])=1          | 2        |
| 3      | 2     | min(∞, 1+dp[2], 1+dp[1])=2          | 2+1      |
| 4      | 2     | min(∞, 1+dp[3], 1+dp[2])=2          | 2+2      |
| 5      | 1     | min(∞, 1+dp[4], 1+dp[3], 1+dp[0])=1 | 5        |

## 6. 代码实现

```python
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1
```

## 7. 复杂度分析

- 时间复杂度：O(n×amount) （n 为硬币种类数）
- 空间复杂度：O(amount)
