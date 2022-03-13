def steffensen(f, p0, tol):
    for i in range(1, 100):
        p1 = p0 + f(p0)
        p2 = p1 + f(p1)
        # print(pow((p2 - p1),2))

        div = p2 - (2 * p1) + p0
        if div == 0:
            return float("nan"), 100, 0
        p = p2 - (pow((p2 - p1), 2) / (p2 - (2 * p1) + p0))
        # print(p-p0)
        if abs(p - p0) < tol:
            # print("Converge after %f iterations" % i)
            return p, i, 0
        p0 = p
    # print('failed to converge in %f iterations' % 100)
    return p, 100, 0
