# Starfall-GNC-4Dof — 项目规格书

> 版本：v0.2  |  创建：2026-04-22  |  更新：2026-04-23  |  状态：**Phase 1 进行中**

---

## 一、项目定位

**目标**：4-DOF 平面火箭 GNC 仿真引擎
**定位**：之前星舰项目的简化平替，聚焦 GNC 核心逻辑
**架构**：C++ 核心 + Python 渲染（ctypes）+ Mathematica 重算层

### 各层职责

| 层级 | 组件 | 职责 |
|------|------|------|
| **总控（Python）** | main.py / Pygame | ctypes 通信、Pygame 动画、指令调度、GUI |
| **核心引擎（C++）** | link.cpp / test.cpp | 动力学积分、控制算法、空气阻力、指令解析 |
| **重算引擎（Mathematica）** | .nb /.m | ODE 解析求解、复杂轨迹优化、凸优化规划 |

> Python 作为总控协调各方；Mathematica 处理复杂解析/优化任务（而非实时仿真）

---

## 二、物理模型规格

### 2.1 自由度定义

| 自由度 | 物理量 | 符号 |
|--------|--------|------|
| 水平位移 | x | m |
| 垂向位移 | z（高度） | m |
| 速度 | vx, vz | m/s |
| 俯仰角 | θ | rad |
| 俯仰角速率 | ω | rad/s |

**约束**：无偏航、无滚转，火箭始终在 x-z 平面内运动。

### 2.2 动力学模型

**状态向量**：
```
x = [x, z, vx, vz, θ, ω, m]ᵀ
```

**常微分方程**：
```
ẋ   = vx
ż   = vz
v̇x  = (T·cos(θ+δ) - D·vx/v) / m
v̇z  = (T·sin(θ+δ) - D·vz/v - m·g) / m
θ̇   = ω
ω̇   = M / I_y
ṁ   = -ṁ_fuel
```

其中：
- `T`：发动机推力（N），可变推力 [T_min, T_max]
- `δ`：发动机摆角（rad），相对于箭体纵轴
- `D = ½·ρ(z)·v²·C_D·A`：气动阻力（N）
- `ρ(z)`：大气密度，高度指数函数（简化：ρ = ρ₀·e^(-z/H)）
- `v = √(vx²+vz²)`：总速度
- `M`：俯仰力矩（N·m），控制输入
- `I_y`：俯仰惯量（kg·m²），时变（燃料消耗影响）
- `ṁ_fuel`：燃料质量流率（kg/s）

### 2.3 大气模型

```
ρ(z) = ρ₀ · exp(-z / H)
ρ₀   = 1.225 kg/m³  （海平面密度）
H    = 8500 m        （标高）
```

### 2.4 质量模型

```
m(t) = m_dry + m_fuel(t)
m_fuel(t) = m_fuel0 - ∫ṁ_fuel dt
ṁ_fuel = T / (I_sp · g₀)   （齐奥尔科夫斯基公式）
```

- `m_dry`：干质量（不含燃料）
- `m_fuel0`：初始燃料质量
- `I_sp`：比冲（s）
- `g₀ = 9.80665 m/s²`

---

## 三、GNC 系统设计

### 3.1 Guidance（导引）— 飞行轨迹规划

**飞行阶段**：
1. **助推段**：垂直上升，保持 θ=0
2. **拐弯段**：程序角控制，按预设俯仰程序转弯
3. **自由飞行段**：发动机关机，弹道飞行
4. **着陆段**：发动机重新点火，自主软着陆

**着陆导引算法**（待定）：
- 方案A：恒定升力/阻力系数剖面（Constant-β）
- 方案B：显式制导（Explicit Guidance）
- 方案C：在线 QP 轨迹优化

### 3.2 Navigation（导航）— 状态估计

**传感器模型**（含噪声）：
- 高度计：z += N(0, σ_alt)
- GPS（水平）：x += N(0, σ_gps)
- IMU：加速度/角速度带偏差和噪声

**滤波器**：扩展卡尔曼滤波（EKF），7状态/6测量

### 3.3 Control（控制）— 串级控制

```
轨迹误差 → 期望俯仰角 θ_d    （外环）
θ_d → 期望角速率 ω_d         （中环）
ω_d → 俯仰力矩 M             （内环：PD 控制）
```

---

## 四、指令集设计（自定义 Command Set）

核心思路：**状态机 + 指令队列**

```
Command Format: [CMD_ID] [ARG1] [ARG2] ... [CHECKSUM]
```

**指令类型**：

| CMD_ID | 名称 | 参数 | 说明 |
|--------|------|------|------|
| `NOP` | 空指令 | — | 无操作 |
| `THR` | 设置推力 | T (N) | 推力值 |
| `GIM` | 发动机摆角 | delta (rad) | 相对箭体纵轴 |
| `ATG` | 设置姿态目标 | theta_d (rad) | 期望俯仰角 |
| `ANG` | 设置角速率目标 | omega_d (rad/s) | 期望俯仰角速率 |
| `MOM` | 直接力矩 | M (N·m) | 俯仰力矩 |
| `PHASE` | 切换飞行阶段 | phase_id | 0-3 |
| `IGN` | 点火 | — | 发动机启动 |
| `Cut` | 关机 | — | 发动机关机 |
| `LAND` | 进入着陆模式 | — | 启动着陆导引 |
| `ABORT` | 中止 | code | 紧急中止 |
| `SYNC` | 同步帧 | frame_id | 时间同步 |

**校验**：异或校验（XOR checksum），防止通信错误。

---

## 五、C++ / Python 接口（ctypes）

### 5.1 共享数据结构

```cpp
// starfall.h — 暴露给 Python 的核心类型
struct State {
    double x, z;        // 位置 m
    double vx, vz;      // 速度 m/s
    double theta;      // 俯仰角 rad
    double omega;      // 角速率 rad/s
    double mass;       // 质量 kg
    double T;         // 当前推力 N
    double delta;      // 当前摆角 rad
    double D;          // 当前阻力 N
};

struct Telemetry {
    uint64_t timestamp_us;
    State state;
    uint8_t phase;
    uint8_t flags;
};
```

### 5.2 核心 API

```cpp
// 仿真控制
void sf_init(const char* config_json);
void sf_reset();
void sf_step(double dt);          // 推进 dt 秒
void sf_send_command(uint8_t cmd, double arg);

// 状态读取
State sf_get_state();
Telemetry sf_get_telemetry();
double sf_get_time();

// 参数设置
void sf_set_thrust_range(double T_min, double T_max);
void sf_set_mass(double m_dry, double m_fuel0, double I_sp);
```

### 5.3 Python 总控层职责

- Pygame 渲染：火箭姿态、轨迹曲线、仪表盘
- 指令调度：向 C++ 内核发送 THR/GIM/ATG 等指令
- 协调 Mathematica：复杂轨迹优化结果回传至 C++ 内核
- 仿真主循环：帧节奏控制（60fps）

### 5.4 Mathematica 重算层职责

- ODE 解析求解（解析积分 vs 数值积分的对比验证）
- 复杂轨迹优化（凸优化/QP，在线规划前离线验证）
- 气动系数查表生成（风洞数据拟合）
- 控制参数整定（LQR/PID 参数搜索）

> **设计原则**：Mathematica 不参与实时仿真循环，仅在设计阶段或关键决策点被调用，结果以查表或指令形式注入 C++ 内核。

---

## 六、项目结构（Phase 1 进行中）

```
Starfall-GNC-4Dof/
├── link.cpp              ← C++ ctypes 导出入口（已实现）
├── link.py               ← Python ctypes 封装（已实现）
├── main.py               ← Pygame 主循环 + 动画（已实现）
├── run.sh                ← 编译脚本（clang++ + Metal）
├── include/
│   ├── TEST.hpp          ← 临时测试类（Phase 1 演示用）
│   ├── starfall.h        # 规划中
│   ├── dynamics.h        # 规划中
│   ├── guidance.h        # 规划中
│   ├── navigation.h      # 规划中
│   ├── control.h         # 规划中
│   └── command.h          # 规划中
├── src/
│   ├── test.cpp          ← 动力学积分演示（Phase 1 演示用）
│   ├── starfall.cpp      # 规划中（替换 link.cpp）
│   ├── dynamics.cpp      # 规划中
│   ├── guidance.cpp      # 规划中
│   ├── navigation.cpp    # 规划中
│   ├── control.cpp       # 规划中
│   └── command.cpp       # 规划中
├── python/
│   ├── renderer.py       # 规划中
│   ├── instruments.py    # 规划中
│   └── config.json       # 规划中
├── bin/                  ← 编译输出
└── SPEC.md
```

> 注：Phase 1 演示用 link.cpp/test.cpp 为快速验证版本；正式架构将整合为 starfall.cpp + 各模块头文件。

---

## 七、关键设计决策（已确认）

- ✅ 可变推力 + 发动机摆角（推力方向可控）
- ✅ 燃料消耗导致质量时变（齐奥尔科夫斯基质量模型）
- ✅ 阻力建模为函数（高度指数密度 + 速度平方阻力）
- ✅ Python Pygame 渲染（总控层）
- ✅ 自主设计指令集（状态机 + 队列）
- ✅ C++ 内核与 Python ctypes 通信（Phase 1 完成）
- ✅ Pygame 动画效果（main.py，60fps）
- ✅ 初步指令集（case 0/1/2 演示：初始化/设置/积分）
- ⏳ 动力学模型（ODE 求解、C++ 实现）
- ⏳ 串级控制（姿态环 + 轨迹环）
- ⏳ 空气动力学模型（ρ(z)、阻力函数）
- ⏳ Mathematica 重算层（ODE 解析求解、凸优化轨迹规划）

---

*状态：Phase 1 进行中（已完成 C++/Python 通信 + 动画）*