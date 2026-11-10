from __future__ import annotations

import ast
import math
import operator
from typing import Any

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {
    "sqrt": math.sqrt, "abs": abs, "round": round,
    "min": min, "max": max, "sum": lambda *a: sum(a),
    "avg": lambda *a: sum(a) / len(a),
    "log": math.log, "log10": math.log10,
}
_CONSTS = {"pi": math.pi, "e": math.e}
_MAX_POW = 10_000


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POW:
            raise ValueError("exponent too large")
        return _BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS and not node.keywords:
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError("unsupported expression")


def calculate(expression: str = "", precision: int = 6) -> dict[str, Any]:
    """Safely evaluate a math expression. Never raises; returns a dict."""
    if not isinstance(expression, str) or not expression.strip():
        return {"tool": "calculator", "error": "expression must be a non-empty string"}
    if isinstance(precision, bool) or not isinstance(precision, int) or not 0 <= precision <= 15:
        return {"tool": "calculator", "error": "precision must be an integer between 0 and 15"}
    if len(expression) > 500:
        return {"tool": "calculator", "error": "expression too long"}
    try:
        tree = ast.parse(expression.strip().replace("^", "**").replace(",", ",") , mode="eval")
        value = _eval(tree)
    except ZeroDivisionError:
        return {"tool": "calculator", "error": "division by zero", "expression": expression}
    except (ValueError, TypeError, SyntaxError, OverflowError, RecursionError) as exc:
        return {"tool": "calculator", "error": f"cannot evaluate: {exc}", "expression": expression}
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return {"tool": "calculator", "error": "result is not a finite number", "expression": expression}
    result = round(value, precision) if isinstance(value, float) else value
    return {"tool": "calculator", "expression": expression, "result": result}
