from wolframclient.evaluation import WolframLanguageSession
# 你的路径
KERNEL_PATH = "/Applications/Wolfram.app/Contents/MacOS/WolframKernel"

# ======================
# 全局只启动一次会话
# ======================
print("正在启动 Wolfram 内核（仅第一次需要等待）...")
session = WolframLanguageSession(KERNEL_PATH)

# ======================
# 计算函数（随时调用，秒算）
# ======================
def wolfram_calc(expr):
    return session.evaluate(f"{expr}")
# ======================
# 🔥 关键：转成 SymPy 可渲染的公式
# ======================



# 转换

# ======================
# 你想算什么就写什么
# ======================
print(wolfram_calc("Sqrt[10]"))   # 算平方根
print(wolfram_calc("2^10"))       # 算次方
print(wolfram_calc("Sin[Pi/2]"))   # 算三角函数
print(wolfram_calc("1+2+3+4"))     # 随便算
sol=wolfram_calc("DSolveValue[y''[x] + y[x] == 0, y[x], x]")
print(sol)
# 最后不想用了，再关闭
session.terminate()
