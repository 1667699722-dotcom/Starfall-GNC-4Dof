clang++ -shared -fPIC -std=c++17 src/test.cpp link.cpp  -I include -o link.dylib -framework Metal -framework Foundation
source venv/bin/activate