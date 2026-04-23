
#ifndef TESTHPP
#define TESTHPP
#include <vector>

class Test{
public:
   Test();
   void setvalue(const float*);
   float* getvalue();
private:
   std::vector<float> value;
   std::vector<float> data;
};

#endif