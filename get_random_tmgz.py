"""Simple CLI for generating cryptographically strong random integers."""

from __future__ import annotations

import sys
from secrets import randbelow


def read_bounds() -> tuple[int, int]:
	"""Prompt the user for integer bounds until valid input is provided."""

	while True:
		raw = input("Enter two integers (min max): ").strip()
		try:
			lower_str, upper_str = raw.split()
			lower, upper = int(lower_str), int(upper_str)
		except ValueError:
			print("Please enter exactly two integers separated by whitespace.\n")
			continue

		if lower > upper:
			print("The first number must be less than or equal to the second.\n")
			continue

		return lower, upper


def secure_randint(lower: int, upper: int) -> int:
	span = (upper - lower) + 1
	return lower + randbelow(span)


def main() -> None:
	print("Cryptographically strong random number generator\n")
	try:
		lower, upper = read_bounds()
		result = secure_randint(lower, upper)
	except KeyboardInterrupt:
		print("\nCancelled by user.")
		sys.exit(1)

	print(f"Random integer in [{lower}, {upper}]: {result}")


if __name__ == "__main__":
	main()

