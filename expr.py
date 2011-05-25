import re
import ast
import random
import math
import operator

h = 10 ** -8
N = int(math.sqrt(1 / h))
idhash = lambda s: hash(s) % (10 ** 3)
static = lambda k: lambda x: k

unary = {
	"ln": math.log,
	"exp": math.exp,
	"abs": abs,
	"sqrt": math.sqrt,
	"sin": math.sin,
	"cos": math.cos,
	"tan": math.tan,
	"arcsin": math.asin,
	"arccos": math.acos,
	"arctan": math.atan,
	"csc": lambda x: 1 / math.sin(x),
	"sec": lambda x: 1 / math.cos(x),
	"cot": lambda x: 1 / math.tan(x),
}

binary = {
	ast.Add: ('+', operator.add),
	ast.Sub: ('-', operator.sub),
	ast.Mult: ('*', operator.mul),
	ast.Div: ('/', operator.truediv),
	ast.Pow: ('^', math.pow),
}

special = {
	"e": math.e,
	"pi": math.pi,
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

rewrite = (
	[r'\[', r'('],
	[r'\]', r')'],
	[r'\^', r'**'],
	[r'\'', r'_prime'],
	# "Var(" but not "Func("
	[re.compile(r'([a-z_\']+)\('), VarFunc_resolver],
	# "NumFunc|Var" or "Num(" or ")(" or ")Func|Var"
	[re.compile(r'(\)|\d+)([a-z_\'\(])'), r'\g<1>*\g<2>'],
)

def parse(s):
	'Create a nested-lambda expression from a string.'
	s = s.replace(' ', '')
	for rule, pattern in rewrite:
		s = re.sub(rule, pattern, s)
	print("I'll assume you meant to say '{0}'...".format(s))
	return build_expr(ast.parse(s))

ast_hints = ast.Name, ast.Num, ast.BinOp, ast.Call, ast.UnaryOp

def build_expr(node):
	'Search for a lambdify-able AST node.'
	child = ast.iter_child_nodes(node)
	for sub in child:
		if type(sub) in ast_hints:
			return lambdify(sub)
		return build_expr(sub)
	print(ast.dump(node))
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
	k = random.randint(2, 10)
	return "{0}x".format(k), lambda x: k * x

def func_gen(size):
	'Generate a function and its string representation given a size.'
	prob = random.random()
	if size <= 0 or prob < 0.25:
		return make_var()
	elif size <= 2 or prob < 0.50:
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
	return abs(lhs - rhs) < 0.005

domain = [0, .5, 1, 2, 9, 16, 25, math.e, math.pi]
domain.extend([-elt for elt in domain])

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
	return score / denom > .5 if denom > (len(domain) / 2) else False

def differentiate(fx, k):
	return (fx(k + h) - fx(k)) / h

def derivative(fx):
	return lambda x: differentiate(fx, x)

def integrate(fx, a, b):
	traps = (fx(a + (b - a) * k / N) for k in range(1, N))
	return (b - a) * (fx(a) / 2 + fx(b) / 2 + sum(traps)) / N

def integral(fx):
	return lambda x: integrate(fx, 0, x)

questions = [
	("f(x) = {0}. f'(x) = ?", derivative),
	("f(x) = {0}. f''(x) = ?", lambda fx: derivative(derivative(fx))),
	("f(x) = {0}. F(x) = ? + C", integral),
]

identities = [
	# Pythagorean Identities
	("sin(x)^2 + cos(x)^2 = ?", static(1)),
	("cos(x)^2 = ?", parse("(1 + cos(2x)) / 2")),
	("sin(x)^2 = ?", parse("(1 - cos(2x)) / 2")),
	
	# Tan/Cot Identities
	("sin(u)/cos(u) = ?", parse("tan(u)")),
	("cos(u)/sin(u) = ?", parse("cot(u)")),
	
	# Reciprocal Identities
	("1/sin(u) = ?", parse("csc(u)")),
	("1/cos(u) = ?", parse("sec(u)")),
	("1/tan(u) = ?", parse("cot(u)")),
	("1/csc(u) = ?", parse("sin(u)")),
	("1/sec(u) = ?", parse("cos(u)")),
	("1/cot(u) = ?", parse("tan(u)")),
	
	# Even/Odd Formulas
	("sin(-u) = ?", parse("-sin(u)")),
	("cos(-u) = ?", parse("cos(u)")),
	("tan(-u) = ?", parse("-tan(u)")),
	
	# Double Angle Formulas
	("sin(2u) = ?", parse("2sin(u)cos(u)")),
	("(cos(u)^2) - (sin(u)^2) = ?", parse("cos(2u)")),
	("2(cos(u)^2) - 1 = ?", parse("cos(2u)")),
	("1 - 2(sin(u)^2) = ?", parse("cos(2u)")),
	("tan(2u) = ?", parse("2tan(u)/(1-(tan(u)^2))")),
	
	# Angle Conversion
	("pi radians = ? degrees", static(180)),
	("180 degrees = ? radians", parse("pi")),
	
	# Half Angle Formulas
	("(1/2)(1 - cos(2u)) = ?", parse("sin(u)^2")),
	("(1/2)(1 + cos(2u)) = ?", parse("cos(u)^2")),
	("(1 - cos(2u))/(1 + cos(2u)) = ?", parse("tan(u)^2")),
	
	# Sum and Difference Formulas
	("sin(a + b) = ?", parse("sin(a)cos(b) + cos(a)sin(b)")),
	("cos(a + b) = ?", parse("cos(a)cos(b) - sin(a)sin(b)")),
	("tan(a + b) = ?", parse("(tan(a) + tan(b))/(1 - tan(a)tan(b))")),
	
	# Product to Sum Formulas
	("sin(a)sin(b) = ?", parse("(1/2)(cos(a - b) - cos(a + b))")),
	("cos(a)cos(b) = ?", parse("(1/2)(cos(a - b) + cos(a + b))")),
	("sin(a)cos(b) = ?", parse("(1/2)(sin(a + b) + sin(a - b))")),
	("cos(a)sin(b) = ?", parse("(1/2)(sin(a + b) - sin(a - b))")),
	
	# Sum to Product Formulas
	("sin(a) + sin(b) = ?", parse("2sin((a + b)/2)cos((a - b)/2)")),
	("sin(a) - sin(b) = ?", parse("2cos((a + b)/2)sin((a - b)/2)")),
	("cos(a) + cos(b) = ?", parse("2cos((a + b)/2)cos((a - b)/2)")),
	("cos(a) - cos(b) = ?", parse("-2sin((a + b)/2)sin((a - b)/2)")),
	
	# Cofunction Formulas
	("sin((pi/2) - a) = ?", parse("cos(a)")),
	("cos((pi/2) - a) = ?", parse("sin(a)")),
	("tan((pi/2) - a) = ?", parse("cot(a)")),
	("csc((pi/2) - a) = ?", parse("sec(a)")),
	("sec((pi/2) - a) = ?", parse("csc(a)")),
	("cot((pi/2) - a) = ?", parse("tan(a)")),

	# Basic Differentiation
	("d/dx a = ?", static(0)),
	("d/dx x = ?", static(1)),
	("d/dx a*x = ?", parse("a")),
	("d/dx a[f(x)] = ?", parse("a[f'(x)]")),
	("d/dx [f(x) + g(x)] = ?", parse("f'(x) + g'(x)")),
	("d/dx f(x)g(x) = ?", parse("f(x)g'(x) + f'(x)g(x)")),
	("d/dx f(x)/g(x) = ?", parse("[f'(x)g(x) - f(x)g'(x)] / g(x)^2")),
	("d/dx [1 / f(x)] = ?", parse("-f'(x) / f(x)^2")),
	("d/dx f(g(x)) = ?", parse("f'(g(x))g'(x)")),
	("d/dx u^n = ?", parse("n(u^(n-1))")),
	("d/dx a^u = ?", parse("ln(a)(a^u) du")),
	("d/dx log_a(u) = ?", parse("du/(u * ln(a))")),
	("d/dx e^u = ?", parse("(e^u) du")),
	("d/dx ln(u) = ?", parse("du/u")),
	# <Incomplete>

	# Trig Differentiation
	("d/dx sin(u) = ?", parse("cos(u) du")),
	("d/dx cos(u) = ?", parse("-sin(u) du")),
	("d/dx tan(u) = ?", parse("(sec(u)^2) du")),
	("d/dx sec(u) = ?", parse("sec(u)tan(u) du")),
	("d/dx csc(u) = ?", parse("-csc(u)cot(u) du")),
	("d/dx cot(u) = ?", parse("-(csc(u)^2) du")),
	
	# Inverse Trig Differentiation
	("d/dx arcsin(u) = ?", parse("1/sqrt(1-(x^2))")),
	("d/dx arccos(u) = ?", parse("-1/sqrt(1-(x^2))")),
	("d/dx arctan(u) = ?", parse("1/(1+(x^2))")),

	# <Incomplete>

	# Integration Formulas
	# Volume, surface area, polar area, arclen, parametrics...
]

def generate():
	'Generate a word problem and its solution.'
	if random.random() < 0.33:
		return random.choice(identities)
	else:
		fstr, fx = func_gen(random.randint(1, 4))
		problem, solution = random.choice(questions)
		question = problem.format(func_infix(fstr))
		return question, solution(fx)

def repl():
	print("Calculus Blasters (REPL)")
	while True:
		prob, soln = generate()
		print("\nCalculus> " + prob)
		fx = parse(input("Blast> "))
		if check(fx, soln):
			print("Correct!")
		else:
			action = input("Incorrect. Override (y/n)? ")
			print("OK. My bad." if 'y' in action.lower() else "Moving on then...")
