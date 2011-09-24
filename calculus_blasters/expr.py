import re
import ast
import sys
import random


try:
	from bigfloat import *
except:
	from math import *
	from operator import *
	BigFloat = float
	const_pi = lambda: pi
	div, sum = truediv, fsum
	csc = lambda x: 1 / sin(x)
	sec = lambda x: 1 / cos(x)
	cot = lambda x: 1 / tan(x)

N = 10 ** 3
h = 10 ** -10
idhash = lambda s: hash(s) % (10 ** 3)
static = lambda k: lambda x: BigFloat(k)

unary = {
	"ln": log,
	"exp": exp,
	"abs": abs,
	"sqrt": sqrt,
	"sin": sin,
	"cos": cos,
	"tan": tan,
	"arcsin": asin,
	"arccos": acos,
	"arctan": atan,
	"csc": csc,
	"sec": sec,
	"cot": cot,
}

binary = {
	ast.Add: ('+', add),
	ast.Sub: ('-', sub),
	ast.Mult: ('*', mul),
	ast.Div: ('/', div),
	ast.Pow: ('^', pow),
}

special = {
	"e": exp(1),
	"pi": const_pi(),
	ast.USub: lambda x: -x,
}

for name in ["u", "n", "a", "b", "du"]:
	special[name] = idhash(name)

special_funcs = set(["f", "g", "f_prime", "g_prime"])
for name in special_funcs:
	special[name] = lambda x: x + idhash(name)

def VarFunc_resolver(match):
	vf = match.group(1)
	if vf in unary or vf in special_funcs:
		return vf + '('
	return vf + '*('

def Funcall_resolver(match):
	fn, arg = match.groups()
	if fn in unary:
		return fn + '(' + arg + ')'
	return fn + ' ' + arg

rewrite = (
	[r'\[', r'('],
	[r'\]', r')'],
	[r'\^', r'**'],
	[r'\'', r'_prime'],
	# "Var(" but not "Func("
	[re.compile(r'([a-z_]+)\s*\('), VarFunc_resolver],
	# "NumVar|Func" or "Num(" or ")(" or ")Var|Func"
	[re.compile(r'\)\s*(\d+|[a-z_\(])'), r')*\g<1>'],
	[re.compile(r'(\d+)\s*([a-z_\(])'), r'\g<1>*\g<2>'],
	# Unary function-call group prediction: Func u => Func(u)
	[re.compile(r'([a-z_]+)\s+([a-z_]+|\d+)'), Funcall_resolver],
)

def rewrite_terms(s):
	new = s
	for rule, pattern in rewrite:
		new = re.sub(rule, pattern, new)
	return new if new == s else rewrite_terms(new)

def parse(s):
	'Create a nested-lambda expression from a string.'
	s = rewrite_terms(s)
	try:
		print("[Parser] " + s)
		return build_expr(ast.parse(s))
	except:
		return static(float('inf'))

ast_hints = ast.Name, ast.Num, ast.BinOp, ast.Call, ast.UnaryOp

def build_expr(node):
	'Search for a lambdify-able AST node.'
	child = ast.iter_child_nodes(node)
	for sub in child:
		if type(sub) in ast_hints:
			return lambdify(sub)
		return build_expr(sub)
	raise Exception("Error: couldn't parse the AST.")

def lambdify(node):
	'Convert AST nodes to their lambda equivalents.'
	if isinstance(node, ast.Name):
		return lambda x: special.get(node.id, x)
	elif isinstance(node, ast.Num):
		return static(node.n)
	elif isinstance(node, ast.BinOp):
		_, fn = binary[type(node.op)]
		lfx, rfx = map(lambdify, (node.left, node.right))
		return lambda x: fn(lfx(x), rfx(x))
	elif isinstance(node, ast.Call):
		name = node.func.id
		func = unary.get(name, special.get(name))
		fx = lambdify(node.args[0])
	elif isinstance(node, ast.UnaryOp):
		func = special[type(node.op)]
		fx = lambdify(node.operand)
	return lambda x: func(fx(x))

pick_op = lambda table: random.choice(list(table.keys()))

def make_unary(child):
	op = pick_op(unary)
	fx = lambda x: unary[op](child[1](x))
	return (op, child[0]), fx

def make_binary(lhs, rhs):
	op = pick_op(binary)
	name, fn = binary[op]
	fx = lambda x: fn(lhs[1](x), rhs[1](x))
	return (name, lhs[0], rhs[0]), fx

def make_var():
	k, expt = random.randint(2, 10), random.randint(1, 10)
	fmt = "{0}x{1}".format(k, "^{0}".format(expt) if expt > 1 else "")
	return fmt, lambda x: k * (x ** expt)

def func_gen(size):
	'Generate a function and its string representation given a size.'
	prob = random.random()
	if size == 0 or prob < 0.25:
		return make_var()
	elif prob < 0.65:
		return make_unary(func_gen(size - 1))
	else:
		return make_binary(func_gen(size // 2), func_gen(size // 2))

def func_infix(elt):
	if isinstance(elt, tuple):
		if elt[0] in unary:
			return elt[0] + '(' + func_infix(elt[1]) + ')'
		else:
			return ' '.join([
				func_infix(elt[1]), elt[0], func_infix(elt[2])
			])
	return elt

def equal(lhs, rhs):
	'Compare floats for equality.'
	return abs(lhs - rhs) < 0.001

domain = [0, .5, 1, 2, 9, special['e'], special['pi']]
domain.extend([-n for n in domain[1:]])
domain = [BigFloat(n) for n in domain]

def check(lfx, rfx):
	'Check if two functions are equivalent.'
	score, denom = 0, len(domain)
	for elt in domain:
		try:
			if equal(lfx(elt), rfx(elt)):
				score += 1
		except:
			denom -= 1
	print("Score = {0}/{1}...".format(score, denom))
	return score / denom > .5 if denom > (len(domain) / 4) else False

def differentiate(fx, k):
	return (fx(k + h) - fx(k)) / h

def derivative(fx):
	return lambda x: differentiate(fx, x)

def integrate(fx, a, b):
	traps = (fx(a + (b - a) * k / N) for k in range(1, N))
	return (b - a) * (fx(a) / 2 + fx(b) / 2 + fsum(traps)) / N

def integral(fx):
	return lambda x: integrate(fx, 0, x)

questions = [
	("f(x) = {0}. f'(x) = ?", "d/dx f(x)", derivative),
	("f(x) = {0}. f''(x) = ?", "d^2/dx^2 f(x)", lambda fx: derivative(derivative(fx))),
	("f(x) = {0}. F(x) = ? + C", "integral(f(x))", integral),
]

identities = [
	# Pythagorean Identities
	("sin(x)^2 + cos(x)^2 = ?", "1"),
	("cos(x)^2 = ?", "(1 + cos(2x)) / 2"),
	("sin(x)^2 = ?", "(1 - cos(2x)) / 2"),

	# Tan/Cot Identities
	("sin(u)/cos(u) = ?", "tan(u)"),
	("cos(u)/sin(u) = ?", "cot(u)"),

	# Reciprocal Identities
	("1/sin(u) = ?", "csc(u)"),
	("1/cos(u) = ?", "sec(u)"),
	("1/tan(u) = ?", "cot(u)"),
	("1/csc(u) = ?", "sin(u)"),
	("1/sec(u) = ?", "cos(u)"),
	("1/cot(u) = ?", "tan(u)"),

	# Even/Odd Formulas
	("sin(-u) = ?", "-sin(u)"),
	("cos(-u) = ?", "cos(u)"),
	("tan(-u) = ?", "-tan(u)"),

	# Double Angle Formulas
	("sin(2u) = ?", "2sin(u)cos(u)"),
	("(cos(u)^2) - (sin(u)^2) = ?", "cos(2u)"),
	("2(cos(u)^2) - 1 = ?", "cos(2u)"),
	("1 - 2(sin(u)^2) = ?", "cos(2u)"),
	("tan(2u) = ?", "2tan(u)/(1-(tan(u)^2))"),

	# Angle Conversion
	("pi radians = ? degrees", "180"),
	("180 degrees = ? radians", "pi"),

	# Half Angle Formulas
	("(1/2)(1 - cos(2u)) = ?", "sin(u)^2"),
	("(1/2)(1 + cos(2u)) = ?", "cos(u)^2"),
	("(1 - cos(2u))/(1 + cos(2u)) = ?", "tan(u)^2"),

	# Sum and Difference Formulas
	("sin(a + b) = ?", "sin(a)cos(b) + cos(a)sin(b)"),
	("cos(a + b) = ?", "cos(a)cos(b) - sin(a)sin(b)"),
	("tan(a + b) = ?", "(tan(a) + tan(b))/(1 - tan(a)tan(b))"),

	# Product to Sum Formulas
	("sin(a)sin(b) = ?", "(1/2)(cos(a - b) - cos(a + b))"),
	("cos(a)cos(b) = ?", "(1/2)(cos(a - b) + cos(a + b))"),
	("sin(a)cos(b) = ?", "(1/2)(sin(a + b) + sin(a - b))"),
	("cos(a)sin(b) = ?", "(1/2)(sin(a + b) - sin(a - b))"),

	# Sum to Product Formulas
	("sin(a) + sin(b) = ?", "2sin((a + b)/2)cos((a - b)/2)"),
	("sin(a) - sin(b) = ?", "2cos((a + b)/2)sin((a - b)/2)"),
	("cos(a) + cos(b) = ?", "2cos((a + b)/2)cos((a - b)/2)"),
	("cos(a) - cos(b) = ?", "-2sin((a + b)/2)sin((a - b)/2)"),

	# Cofunction Formulas
	("sin((pi/2) - a) = ?", "cos(a)"),
	("cos((pi/2) - a) = ?", "sin(a)"),
	("tan((pi/2) - a) = ?", "cot(a)"),
	("csc((pi/2) - a) = ?", "sec(a)"),
	("sec((pi/2) - a) = ?", "csc(a)"),
	("cot((pi/2) - a) = ?", "tan(a)"),

	# Basic Differentiation
	("d/dx a = ?", "0"),
	("d/dx x = ?", "1"),
	("d/dx a*x = ?", "a"),
	("d/dx a[f(x)] = ?", "a[f'(x)]"),
	("d/dx [f(x) + g(x)] = ?", "f'(x) + g'(x)"),
	("d/dx f(x)g(x) = ?", "f(x)g'(x) + f'(x)g(x)"),
	("d/dx f(x)/g(x) = ?", "[f'(x)g(x) - f(x)g'(x)] / g(x)^2"),
	("d/dx [1 / f(x)] = ?", "-f'(x) / f(x)^2"),
	("d/dx f(g(x)) = ?", "f'(g(x))g'(x)"),
	("d/dx u^n = ?", "n(u^(n-1))"),
	("d/dx a^u = ?", "ln(a)(a^u) du"),
	("d/dx log_a(u) = ?", "du/(u * ln(a))"),
	("d/dx e^u = ?", "(e^u) du"),
	("d/dx ln(u) = ?", "du/u"),

	# Trig Differentiation
	("d/dx sin(u) = ?", "cos(u) du"),
	("d/dx cos(u) = ?", "-sin(u) du"),
	("d/dx tan(u) = ?", "(sec(u)^2) du"),
	("d/dx sec(u) = ?", "sec(u)tan(u) du"),
	("d/dx csc(u) = ?", "-csc(u)cot(u) du"),
	("d/dx cot(u) = ?", "-(csc(u)^2) du"),

	# Inverse Trig Differentiation
	("d/dx arcsin(u) = ?", "1/sqrt(1-(x^2))"),
	("d/dx arccos(u) = ?", "-1/sqrt(1-(x^2))"),
	("d/dx arctan(u) = ?", "1/(1+(x^2))"),

	# Integration Formulas
	# Volume, surface area, polar area, arclen, parametrics...
]

def generate():
	'Generate a word problem and its solution.'
	if random.random() < 0.33:
		prob, soln = random.choice(identities)
		return prob, soln, parse(soln)
	else:
		fstr, fx = func_gen(random.randint(1, 3))
		problem, soln, solution = random.choice(questions)
		prob = problem.format(func_infix(fstr))
		return prob, soln, solution(fx)

def repl():
	print("Calculus Blasters (REPL)")
	while True:
		prob, soln, sfx = generate()
		print("\nCalculus> " + prob)
		fx = parse(input("Blast> "))
		if check(fx, sfx):
			print("Correct!")
		else:
			action = input("Incorrect. Expected {0}.\nOverride (y/n)? ".format(soln))
			print("OK. My bad." if 'y' in action.lower() else "Moving on then...")

if __name__ == '__main__':
	if sys.version_info.major < 3:
		print("You need a Python 3 interpreter to run this code.")
		exit(-1)

	repl()
