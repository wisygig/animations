from typing import Generator, List, Tuple
from bisect import bisect_left, bisect_right
from random import randrange, uniform
from pandas import DataFrame
from plotnine import ggplot, aes, geom_point, geom_abline, lims
from plotnine.animation import PlotnineAnimation

Points = List[complex]


def generate() -> Points:
    return [complex(uniform(0, 1), uniform(0, 1)) for _ in range(randrange(5, 20))]


def cleanup(zs: Points, a: float, b: float) -> Tuple[Points, float, float]:
    zs.sort(key=lambda z: z.real)
    xs = [z.real for z in zs]
    i, j = bisect_left(xs, a), bisect_right(xs, b)
    zs = zs[i:j+1]
    if a < zs[0].real:
        zs = [complex(a, 0)] + zs
    if b > zs[-1].real:
        zs = zs + [complex(b, 0)]
    return (zs, a, b)


def execute(zs: Points, a: float, b: float) -> Generator[Tuple[int, int, int, int], None, None]:
    j = bisect_left([z.real for z in zs], (b + a) / 2)
    if zs[j].real == (b + a) / 2:
        i, p, q = j, j, j
    else:
        i = j - 1
        p, q = i, j
    while True:
        yield (i, j, p, q)
        m = slope(zs[p], zs[q])
        b = intercept(zs[p], zs[q])
        print(check(m, b, zs[i:j+1]))
        if m >= 0:
            if i > 0:
                i -= 1
                # update p if necessary, and reset j
                y = m * zs[i].real + b 
                print("mx + b = {} > {}: {}".format(y, zs[i].imag, y > zs[i].imag))
                if cross_product(zs[q], zs[p], zs[i]) < 0:
                    print("update")
                    p, j = i, q
            elif j < len(zs) - 1:
                j += 1
                # update q if necessary, and reset i
                y = m * zs[j].real + b 
                print("mx + b = {} > {}: {}".format(y, zs[j].imag, zs[j].imag))
                if cross_product(zs[p], zs[q], zs[j]) > 0:
                    print("update")
                    q, i = j, p
            else:
                break
        elif m < 0:
            if j < len(zs) - 1:
                j += 1
                # update q if necessary, and reset i
                y = m * zs[j].real + b 
                print("mx + b = {} > {}: {}".format(y, zs[j].imag, y > zs[j].imag))
                if cross_product(zs[p], zs[q], zs[j]) > 0:
                    print("update")
                    q, i = j, p
            elif i > 0:
                i -= 1
                y = m * zs[i].real + b 
                print("mx + b = {} > {}: {}".format(y, zs[i].imag, y > zs[i].imag))
                # update p if necessary, and reset j
                if cross_product(zs[q], zs[p], zs[i]) < 0:
                    print("update")
                    p, j = i, q
            else:
                break
    m = slope(zs[p], zs[q])
    b = intercept(zs[p], zs[q])
    print(check(m, b, zs[i:j+1]))
    yield (i, j, p, q)
    return


def check(m: float, b: float, zs: Points): 
    return [(i, m * z.real + b, z.imag) for i, z in enumerate(zs) if m * z.real + b < z.imag ]

def slope(p: complex, q: complex) -> float:
    return (q - p).imag / (q-p).real


def intercept(p: complex, q: complex) -> float:
    return p.imag + (-p.real * (q - p).imag) / (q - p).real


# positive if pr is counter-clockwise from pq.
def cross_product(p: complex, q: complex, r: complex) -> float:
    return ((q-p).conjugate() * (r-p)).imag


def build_plot(ws: Points, i: int, j: int, p: int, q: int):
    df = DataFrame({
        'x': [w.real for w in ws],
        'y': [w.imag for w in ws],
        'include': [
            3 if k == p or k == q else
            -3 if i <= k and k <= j else
            0
            for k in range(len(ws))]});
    return (ggplot(df, aes('x', 'y', color='include'))
            + geom_point()
            + geom_abline(
                slope=slope(ws[p], ws[q]),
                intercept=intercept(ws[p], ws[q]))
            + lims(x=(0,1), y=(0,3), color=(-3.0, 3.0)))

def main():
    zs = generate()
    a, b = 0, 1
    ws, _, _ = cleanup(zs, a, b)
    plots = (build_plot(ws, *x) for x in execute(ws, 0, 1))
    ani = PlotnineAnimation(plots, interval=550, repeat_delay=500)
    ani.save('ani.gif')

if __name__ == '__main__':
    main()
