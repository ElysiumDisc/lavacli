"""Pure-Python 3D Perlin noise for organic lava flow animation."""
import math

# Classic Perlin permutation table
_PERM = [
    151, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233, 7, 225,
    140, 36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23, 190, 6, 148,
    247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32,
    57, 177, 33, 88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175,
    74, 165, 71, 134, 139, 48, 27, 166, 77, 146, 158, 231, 83, 111, 229, 122,
    60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54,
    65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169,
    200, 196, 135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3, 64,
    52, 217, 226, 250, 124, 123, 5, 202, 38, 147, 118, 126, 255, 82, 85, 212,
    207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42, 223, 183, 170, 213,
    119, 248, 152, 2, 44, 154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9,
    129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232, 178, 185, 112, 104,
    218, 246, 97, 228, 251, 34, 242, 193, 238, 210, 144, 12, 191, 179, 162, 241,
    81, 51, 145, 235, 249, 14, 239, 107, 49, 192, 214, 31, 181, 199, 106, 157,
    184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254, 138, 236, 205, 93,
    222, 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180,
]
_P = _PERM + _PERM  # doubled for overflow


def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(t, a, b):
    return a + t * (b - a)


def _grad(h, x, y, z):
    h &= 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h in (12, 14) else z)
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)


def noise3(x, y, z):
    """3D Perlin noise. Returns value roughly in [-1, 1]."""
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    zi = int(math.floor(z)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    zf = z - math.floor(z)
    u = _fade(xf)
    v = _fade(yf)
    w = _fade(zf)

    a = _P[xi] + yi
    aa = _P[a] + zi
    ab = _P[a + 1] + zi
    b = _P[xi + 1] + yi
    ba = _P[b] + zi
    bb = _P[b + 1] + zi

    return _lerp(w,
        _lerp(v,
            _lerp(u, _grad(_P[aa], xf, yf, zf),
                     _grad(_P[ba], xf - 1, yf, zf)),
            _lerp(u, _grad(_P[ab], xf, yf - 1, zf),
                     _grad(_P[bb], xf - 1, yf - 1, zf))),
        _lerp(v,
            _lerp(u, _grad(_P[aa + 1], xf, yf, zf - 1),
                     _grad(_P[ba + 1], xf - 1, yf, zf - 1)),
            _lerp(u, _grad(_P[ab + 1], xf, yf - 1, zf - 1),
                     _grad(_P[bb + 1], xf - 1, yf - 1, zf - 1))))


def fbm3(x, y, z, octaves=3):
    """Fractal Brownian Motion -- layered noise for richer detail.
    Returns value roughly in [-1, 1]."""
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_val = 0.0
    for _ in range(octaves):
        total += noise3(x * frequency, y * frequency, z * frequency) * amplitude
        max_val += amplitude
        amplitude *= 0.5
        frequency *= 2.0
    return total / max_val
