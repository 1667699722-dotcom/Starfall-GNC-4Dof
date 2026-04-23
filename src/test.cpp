#include "TEST.hpp"
#include <vector>
static std::vector<float> g_value;
static std::vector<float> data;
#define  len  3
Test::Test() {
    g_value.resize(len);
    data.resize(len);
}

void Test::setvalue(const float* A) {
    for (int i = 0; i < len; ++i) {data[i] = A[i];}
    //printf("A[0] = %f\n", A[0]);
    //printf("A[1] = %f\n", A[1]);
    g_value.assign(data.data(), data.data() + data.size());
    //printf("C++ g_value[0] = %f\n", g_value[0]);
    //printf("C++ g_value[1] = %f\n", g_value[1]);
}

float* Test::getvalue() {
    return g_value.data();
}

