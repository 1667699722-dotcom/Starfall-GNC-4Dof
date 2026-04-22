# Starfall-GNC-4Dof — 项目规格书

> 版本：v0.1  |  创建：2026-04-22  |  状态：规划中

---

## 一、项目定位

**目标**：4-DOF 平面火箭 GNC 仿真引擎
**定位**：之前星舰项目的简化平替，聚焦 GNC 核心逻辑
**架构**：C++ 核心 + Python 渲染（ctypes），无外部物理引擎依赖

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

### 5.3 Python 渲染层职责

- 读取 `Telemetry` 结构，实时渲染
- 发送 `sf_send_command()` 控制指令
- 使用 **Pygame** 绘制：火箭姿态、轨迹曲线、高度/速度仪表盘

---

## 六、项目结构

```
Starfall-GNC-4Dof/
├── CMakeLists.txt
├── include/
│   ├── starfall.h          # 公共头文件
│   ├── dynamics.h          # 动力学模型
│   ├── guidance.h          # 导引算法
│   ├── navigation.h        # 导航/滤波
│   ├── control.h           # 控制器
│   └── command.h           # 指令集解析
├── src/
│   ├── starfall.cpp        # 主入口，ctypes 导出
│   ├── dynamics.cpp        # ODE 求解（RK4）
│   ├── guidance.cpp        # 导引逻辑
│   ├── navigation.cpp      # EKF
│   ├── control.cpp         # 串级 PID/LQR
│   └── command.cpp         # 指令解析器
├── python/
│   ├── sim.py              # ctypes 封装，仿真主循环
│   ├── renderer.py         # Pygame 渲染器
│   ├── instruments.py      # 仪表盘 UI
│   └── config.json         # 仿真参数配置
└── SPEC.md
```

---

## 七、关键设计决策（已确认）

- ✅ 可变推力 + 发动机摆角（推力方向可控）
- ✅ 燃料消耗导致质量时变（齐奥尔科夫斯基质量模型）
- ✅ 阻力建模为函数（高度指数密度 + 速度平方阻力）
- ✅ Python Pygame 渲染
- ✅ 自主设计指令集（状态机 + 队列）
- ❌ 我只记录，不写代码

---

*状态：规划中，等待启动*
