#include "TEST.hpp"
#include <vector>
//static std::vector<float> g_value;
//static std::vector<float> data;
#define  len  3
Test::Test() {
    //g_value.resize(len);
    value.resize(len);
    data.resize(len);
}

void Test::setvalue(const float* A) {
    for (int i = 0; i < len; ++i) {data[i] = A[i];}
    //printf("A[0] = %f\n", A[0]);
    //printf("A[1] = %f\n", A[1]);
    value.assign(data.data(), data.data() + data.size());
    //printf("C++ g_value[0] = %f\n", g_value[0]);
    //printf("C++ g_value[1] = %f\n", g_value[1]);
}

float* Test::getvalue() {
    int n=value[0];
    int g=10;
    switch (n)
    {
    case 0:{value[2]-=g*value[1];break;}
    case 1:{value[1]+=1;break;}
    default:break;
    }
    
    return value.data();
}

