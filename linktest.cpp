#include "TEST.hpp"
#include <cstring>
#include <vector>
#include <iostream>
int main(){
    static Test test;
    float a[2] = {1.0f, 2.0f};
    test.setvalue(a);
    std::cout<<test.getvalue()<<std::endl;
    return 0;
}
