import unittest

from gamelang.compiler import compile_source
from gamelang.interpreter import run


SOURCE = """entity bot {
    health = 40;
    x = 0;
    y = 0;
}
damage bot by 2 * (3 + 1);
heal bot by 0;
move bot by (0, 0);
repeat 1 { move bot by (5 + 0, 2 * 1); }
print bot.health;
"""


class OptimizerTests(unittest.TestCase):
    def test_optimizations_are_reported(self):
        compilation = compile_source(SOURCE, optimize_ir=True)
        counts = compilation.optimization_report.counts
        self.assertGreater(counts["constant_folding"], 0)
        self.assertGreater(counts["algebraic_simplification"], 0)
        self.assertGreater(counts["dead_code_elimination"], 0)

    def test_observable_behavior_is_preserved(self):
        plain = compile_source(SOURCE).ir
        optimized = compile_source(SOURCE, optimize_ir=True).ir
        self.assertEqual(run(plain).snapshot(), run(optimized).snapshot())

    def test_noop_instructions_are_removed(self):
        optimized = compile_source(SOURCE, optimize_ir=True).ir
        operations = [item.op for item in optimized.instructions]
        self.assertNotIn("heal", operations)
        self.assertNotIn("repeat", operations)


if __name__ == "__main__":
    unittest.main()

