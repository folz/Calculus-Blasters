import re
import math
import operator
import random

h = 0.00000001
N = int(math.sqrt(1 / h))

syntax = r'\(|\)'
numeric = r'-?\d*\.?\d+'
opname = r'[a-z\+\-\*\/\^]+'
rx = re.compile('(' + '|'.join([syntax, opname, numeric]) + ')')

unary = {
	"ln": math.log,
	"exp": math.exp,
	"sqrt": math.sqrt,
	"sin": math.sin,
	"cos": math.cos,
	"tan": math.tan,
	"arcsin": math.asin,
	"arccos": math.acos,
	"arctan": math.atan,
}

binary = {
	"+": operator.add,
	"-": operator.sub,
	"*": operator.mul,
	"/": operator.truediv,
	"^": math.pow,
}

const = {
	"e": math.e,
	"pi": math.pi,
}

def tokenize(s):
	'Create a token stream out of the input.'
	return (tok for tok in rx.split(s) if tok.strip())

def parse(stream):
	'Create a function out of a token stream.'
	# stream = numeric || '(' + op + [stream] + ')'
	tok = next(stream)
	if tok == '(':
		op = next(stream)
		if op in unary:
			child = parse(stream)
			func = lambda x: unary[op](child(x))
		elif op in binary:
			lhs, rhs = parse(stream), parse(stream)
			func = lambda x: binary[op](lhs(x), rhs(x))
		assert next(stream) == ')'
		return func
	else:
		return lambda x: x if tok == 'x' else const.get(tok, float(tok))

pick_op = lambda table: random.choice(list(table.keys()))

def make_unary(child):
	op = pick_op(unary)
	fx = lambda x: unary[op](child[1](x))
	return (op, child[0]), fx

def make_binary(lhs, rhs):
	op = pick_op(binary)
	fx = lambda x: binary[op](lhs[1](x), rhs[1](x))
	return (op, lhs[0], rhs[0]), fx

def make_var():
	k = random.randint(1, 10)
	return '(* {0} x)'.format(k) if k > 1 else 'x', lambda x: k * x

def func_gen(size):
	'Generate a function and its string representation given a size.'
	prob = random.random()
	if size <= 0 or prob < 0.5:
		return make_var()
	elif size <= 2 or prob < 0.8:
		return make_unary(func_gen(size - 1))
	else:
		return make_binary(func_gen(size // 2), func_gen(size // 2))

def func_repr(elt):
	if isinstance(elt, tuple):
		return '(' + ' '.join([func_repr(sub) for sub in elt]) + ')'
	return elt

def equal(lhs, rhs):
	'Determine if two floats are similar enough to be equal.'
	return abs(lhs - rhs) < 0.001

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

def generate():
	'Generate a word problem and its solution.'
	problem = random.choice(questions)
	fstr, fx = func_gen(random.randint(2, 4))
	question = problem[0].format(func_repr(fstr))
	return question, problem[1](fx)

def test():
	print("Calculus Blasters")
	while True:
		question, soln = generate()
		print("\n?> " + question, '\n')
		fx = parse(tokenize(input("#> ")))
		pt = random.randint(1, 10)
		print("Correct!" if equal(fx(pt), soln(pt)) else "Incorrect.")

test()
