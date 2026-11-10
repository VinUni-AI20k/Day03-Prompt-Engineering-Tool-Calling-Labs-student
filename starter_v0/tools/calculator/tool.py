from __future__ import annotations

import ast
import operator
from typing import Any

from tools._shared import err


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def _evaluate(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value

    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        return OPERATORS[type(node.op)](left, right)

    raise ValueError("Expression contains an unsupported operation")


def calculator(expression: str = "") -> dict[str, Any]:
    try:
        if not expression.strip():
            raise ValueError("Expression must not be empty")

        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)

        return {
            "tool": "calculator",
            "expression": expression,
            "result": result,
        }
    except Exception as exc:
        return err("calculator", exc)