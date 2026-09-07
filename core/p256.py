# NOTE(vanya): Magic idfk
# P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
# A = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
# B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B

# NOTE(vanya): Toy magic
P = 17
A = 2
B = 2


def point_is_on_curve(p_point: tuple[int, int]) -> bool:
    x, y = p_point

    return (
        y * y
        - (x * x * x + A * x + B)
    ) % P == 0


def point_add(
    p_point_a: tuple[int, int],
    p_point_b: tuple[int, int],
) -> tuple[int, int]:

    x1, y1 = p_point_a
    x2, y2 = p_point_b

    slope = (
        (y2 - y1)
        * pow(x2 - x1, -1, P) # NOTE(vanya): Some non-standard division?
    ) % P

    # NOTE(vanya): Calculate the output point
    x3 = (
        slope * slope
        - x1
        - x2
    ) % P

    y3 = (
        slope * (x1 - x3)
        - y1
    ) % P

    return x3, y3


def point_double(p_point: tuple[int, int],) -> tuple[int, int]:
    x1, y1 = p_point

    slope = (
        (3 * x1 * x1 + A)
        * pow(2 * y1, -1, P)
    ) % P

    x3 = (
        slope * slope
        - 2 * x1
    ) % P

    y3 = (
        slope * (x1 - x3)
        - y1
    ) % P

    return x3, y3


def point_mul(p_scalar: int, p_point: tuple[int, int]) -> tuple[int, int]|None:
    result = None
    current = p_point

    while p_scalar > 0:
        if p_scalar & 1:
            result = current if result is None else point_add(
                result,
                current,
            )

        current = point_double(current)
        p_scalar >>= 1

    return result


G = (5, 1)

for i in range(1, 10):
    point = point_mul(i, G)

    print(i, point)
    assert point_is_on_curve(point)
