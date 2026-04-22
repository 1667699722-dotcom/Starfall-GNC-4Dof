#include "TEST.hpp"
#include <cstring>

extern "C" {
    void link(int n,float* A,float* out) {
    static Test test;
    switch (n)
    {
    case 1:{test.setvalue(A);break;}    
    case 2:{*out=*test.getvalue();break;}    
    default:break;
    }
}
}