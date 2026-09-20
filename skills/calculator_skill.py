import re
import math
from .base import BaseSkill
from nlp.entity_extractor import extract_calculation

class CalculatorSkill(BaseSkill):
    name = "calculator"
    description = "Evaluates mathematical expressions safely"
    intents = ["calculator"]

    SAFE_CHARS = set("0123456789+-*/().%^ ")

    def safe_eval(self, expr: str):
        # replace ^ with **, handle %
        expr = expr.replace("^", "**")
        # validate chars
        if any(c not in self.SAFE_CHARS for c in expr):
            # allow ** already handled
            if "**" not in expr:
                raise ValueError("Invalid characters in expression")
        # check for dangerous patterns
        if re.search(r"__|import|exec|eval", expr):
            raise ValueError("Blocked")
        # evaluate with restricted globals
        allowed = {"__builtins__": {}}
        # add math functions
        for k in ["sqrt", "sin", "cos", "tan", "log", "exp", "ceil", "floor", "factorial"]:
            allowed[k] = getattr(math, k)
        allowed["pi"] = math.pi
        allowed["e"] = math.e
        return eval(expr, allowed, {})

    def handle(self, text, intent, entities):
        expr = extract_calculation(text)
        if not expr:
            # fallback: try to find any numbers and operator words
            return "🔢 I couldn't parse that. Try something like 'calculate 12 * 8 + 5' or 'what is 100 / 4?'"
        try:
            result = self.safe_eval(expr)
            # format result
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"🧮 {expr} = **{result}**"
        except ZeroDivisionError:
            return "❌ Division by zero is not allowed."
        except Exception as e:
            return f"❌ Could not calculate '{expr}': {e}"
