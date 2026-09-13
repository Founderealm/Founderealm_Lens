#include <vector>
#include <string>
namespace iota {
class Kappa { public: int run() { return 1; } };
int helper() { std::vector<int> v; return Kappa().run(); }
}
