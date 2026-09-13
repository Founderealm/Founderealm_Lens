using System;
using System.Collections.Generic;
namespace Demo {
    public interface IRunner { int Run(); }
    public class Lambda : IRunner { public int Run() { return 1; } }
    public static class Helper { public static void Go() { Console.WriteLine(new Lambda().Run()); } }
}
