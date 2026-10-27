import json
import tempfile
import unittest
from pathlib import Path

from gamelang.compiler import compile_source
from gamelang.interpreter import run
from gamelang.ir import IRProgram


SOURCE = """entity player {
    health = 100;
    x = 0;
    y = 0;
}
entity enemy {
    health = 25;
    x = 0;
    y = 0;
}
repeat 2 { move player by (3, 1); }
when player touches enemy {
    damage player by 7;
    print player.health;
}
"""


class PipelineTests(unittest.TestCase):
    def test_interpreter_state(self):
        result = run(compile_source(SOURCE).ir, [("player", "enemy")])
        self.assertEqual(result.state.entities["player"].properties["health"], 93)
        self.assertEqual(result.state.entities["player"].properties["x"], 6)
        self.assertEqual(result.output, ["93"])

    def test_collision_is_symmetric(self):
        result = run(compile_source(SOURCE).ir, [("enemy", "player")])
        self.assertEqual(result.output, ["93"])

    def test_ir_json_roundtrip(self):
        original = compile_source(SOURCE).ir
        restored = IRProgram.from_dict(json.loads(original.to_json()))
        self.assertEqual(run(original, [("player", "enemy")]).snapshot(), run(restored, [("player", "enemy")]).snapshot())

    def test_generated_python_equivalence(self):
        compilation = compile_source(SOURCE, optimize_ir=True)
        namespace = {"__name__": "generated_test"}
        exec(compile(compilation.python, "generated.py", "exec"), namespace)
        interpreted = run(compilation.ir, [("player", "enemy")]).snapshot()
        generated = namespace["run"]([("player", "enemy")]).snapshot()
        self.assertEqual(interpreted, generated)

    def test_generated_file_is_valid_python(self):
        code = compile_source(SOURCE).python
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "game.py"
            path.write_text(code, encoding="utf-8")
            compile(path.read_text(encoding="utf-8"), str(path), "exec")


if __name__ == "__main__":
    unittest.main()

