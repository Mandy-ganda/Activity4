"""Programming works: area calculations."""
import math


def circle_area(radius: float) -> float:
    """Area of a circle: A = pi * r^2"""
    if radius < 0:
        raise ValueError("Radius cannot be negative.")
    return math.pi * radius ** 2


def triangle_area(base: float, height: float) -> float:
    """Area of a triangle: A = 1/2 * base * height"""
    if base < 0 or height < 0:
        raise ValueError("Base and height cannot be negative.")
    return 0.5 * base * height


def triangle_area_sides(a: float, b: float, c: float) -> float:
    """Area from three sides using Heron's formula."""
    if min(a, b, c) <= 0:
        raise ValueError("Sides must be greater than zero.")
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("These sides cannot form a triangle.")
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))
