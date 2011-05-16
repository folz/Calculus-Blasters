import re
import math
import operator
import random

h = 0.001
N = int(1 / h)

syntax = r'\(|\)'
numeric = r'-?\d*\.?\d+'
opname = r'[a-z\+\-\*\/\^]+'
numeric_rx = re.compile(numeric)
rx = re.compile(r'(' + r'|'.join([syntax, opname, numeric]) + r')')

unary = {
	"sin": math.sin,
	"cos": math.cos,
	"tan": math.tan,
	"exp": math.exp,
	"ln": math.log,
	"sqrt": math.sqrt,
}

binary = {
	"+": operator.add,
	"-": operator.sub,
	"*": operator.mul,
	"/": operator.truediv,
	"^": math.pow,
	"root": lambda k, n: math.pow(k, 1 / n),
}

def tokenize(s):
	'Create a token stream out of the input.'
	return (tok for tok in rx.split(s) if tok.strip())

def parse(stream):
	'Create a function out of a token stream.'
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
	elif numeric_rx.match(tok):
		k = float(tok)
		return lambda x: k

def generate():
	'Generate a word problem and its solution.'
	pass

def makeFunction(size):
	'Generate a function and its string representation given its size.'
	if size <= 0:
		k = random.randint(1, 10)
		return str(k), lambda x: k
	if random.random() < .5:
		arg = makeFunction(size - 1)
		name = random.choice(unary.keys())
		fx = lambda x: unary[name](arg[1](x))
		return (name, arg[0]), fx
	else:
		lhs = makeFunction(size // 2)
		rhs = makeFunction(size // 2)
		name = random.choice(binary.keys())
		fx = lambda x: binary[name](lhs[1](x), rhs[1](x))
		return (name, lhs[0], rhs[0]), fx

def equal(lhs, rhs):
	'Determine if two floats are similar enough to be equal.'
	return abs(lhs - rhs) < h

def differentiate(fx, k):
	return (fx(k + h) - fx(k)) / h

def differentiator(fx):
	return lambda x: differentiate(fx, x)

def integrate(fx, a, b):
	traps = (fx(a + (b - a) * k / N) for k in range(1, N))
	return (b - a) * (fx(a) / 2 + fx(b) / 2 + sum(traps)) / N

def integrator(fx):
	return lambda x: integrate(fx, 0, x)
