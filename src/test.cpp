#include "TEST.hpp"

static float* g_value;
static float data;
Test::Test() {
    g_value = nullptr; // 初始化
}

void Test::setvalue(float* A) {
    data=*A;
    g_value = &data;
}

float* Test::getvalue() {
    return g_value;
}

