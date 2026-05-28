def add(a, b):
	return a + b


def subtract(a, b):
	return a - b


def multiply(a, b):
	return a * b


def divide(a, b):
	if b == 0:
		raise ValueError("Cannot divide by zero")
	return a / b


def power(a, b):
	return a**b


def factorial(n):
	if n < 0:
		raise ValueError("Factorial is not defined for negative numbers")
	if n == 0 or n == 1:
		return 1

	result = 1
	for i in range(2, n + 1):
		result *= i
	return result


def fibonacci(n):
	if n < 0:
		raise ValueError("Fibonacci is not defined for negative numbers")
	if n == 0:
		return 0
	if n == 1:
		return 1

	a, b = 0, 1
	for _ in range(2, n + 1):
		a, b = b, a + b
	return b
