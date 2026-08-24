"""Safe mathematical calculation tool for the Gemini Chatbot."""

import math
import ast
import operator
from typing import Dict, Any, Union

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
}

_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def _safe_eval(node: ast.AST) -> Union[int, float]:
    """Recursively evaluate an AST expression safely."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.Name):
        if node.id in _CONSTANTS:
            return _CONSTANTS[node.id]
        raise ValueError(f"Unknown variable or constant: {node.id}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in _OPERATORS:
            left = _safe_eval(node.left)
            right = _safe_eval(node.right)
            return _OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in _OPERATORS:
            operand = _safe_eval(node.operand)
            return _OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in _FUNCTIONS:
            func = _FUNCTIONS[node.func.id]
            args = [_safe_eval(arg) for arg in node.args]
            return func(*args)
        raise ValueError(f"Unsupported function call in expression: {ast.dump(node.func)}")
    else:
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def calculate_expression(expression: str) -> Dict[str, Any]:
    """Safely calculate the numerical result of a mathematical expression.

    Args:
        expression: The mathematical expression to evaluate (e.g. '24 * 7', 'sqrt(144) + 10', '1500 * (1 + 0.05)**3').

    Returns:
        A dictionary containing the input expression and the calculated result or error message.
    """
    cleaned_expr = expression.strip().replace("^", "**")
    try:
        parsed = ast.parse(cleaned_expr, mode="eval")
        result = _safe_eval(parsed)
        return {
            "status": "success",
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "expression": expression,
            "error": f"Evaluation error: {str(e)}"
        }
