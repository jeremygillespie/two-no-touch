import random
import numpy as np

size = 10


def output(graph, zones):
    for y in range(size):
        for x in range(size):
            if graph[x, y]:
                print(zones[x, y], '*', end='\t')
            else:
                print(zones[x, y], end='\t')
        print()
    print()


def count_row(y, graph):
    result = 0
    for x in range(size):
        if graph[x, y]:
            result += 1
    return result


def valid_rows(x, graph):
    if x == 0:
        return list(range(size))

    result = []

    for y in range(size):
        if graph[x - 1, y]:
            continue

        if y > 0 and graph[x - 1, y - 1]:
            continue

        if y < size - 1 and graph[x - 1, y + 1]:
            continue

        if count_row(y, graph) >= 2:
            continue

        result.append(y)

    return result


def fill(x, graph):
    if x == size:
        return graph

    rows = valid_rows(x, graph)
    rows_a = rows
    rows_b = rows[:]

    random.shuffle(rows_a)
    random.shuffle(rows_b)

    for a in rows_a:
        for b in rows_b:
            if abs(a - b) > 1:

                graph_new = np.copy(graph)
                graph_new[x, a] = True
                graph_new[x, b] = True

                result = fill(x + 1, graph_new)
                if len(result) > 0:
                    return result

    return np.array([])


def adjacent_points(p):
    result = []
    x = p[0]
    y = p[1]
    for p1 in [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]:
        if p1[0] < 0 or p1[1] < 0:
            continue
        if p1[0] >= size or p1[1] >= size:
            continue
        result.append(p1)
    return result


def adjacent_zones(p, zones):
    result = []
    for p1 in adjacent_points(p):
        z = zones[p1]
        if z != -1:
            result.append(z)
    return result


def target_zones(count, accessible):
    valid = count < 2
    valid = accessible == min(accessible[valid])
    return np.array(range(size))[valid]


def update_accessible(graph, zones, accessible, center):
    for z in range(size):
        can_visit = np.full((size, size), True, dtype=np.bool)
        q = []
        q.append(center[z])
        found = 0

        while len(q) > 0:
            p = q.pop()
            can_visit[p] = False
            if graph[p]:
                found += 1

            for p1 in adjacent_points(p):
                if can_visit[p1] and (zones[p1] == -1 or zones[p1] == z):
                    q.append(p1)

        accessible[z] = found


def fill_zones(graph):
    result = np.full((size, size), -1, dtype=np.int8)
    zone_center = []
    zone_count = np.full((size), 0, dtype=np.int8)
    zone_accessible = np.full((size), 0, dtype=np.int32)

    points_empty = []
    for x in range(size):
        for y in range(size):
            points_empty.append((x, y))
    random.shuffle(points_empty)

    empty_zone = 0
    while empty_zone < size:
        p = points_empty.pop(0)

        if graph[p] == True and result[p] == -1:
            result[p] = empty_zone
            zone_count[empty_zone] += 1
            zone_center.append(p)
            empty_zone += 1
        else:
            points_empty.append(p)

    loop_count = 0
    while len(points_empty) > 0 and loop_count <= 2 * len(points_empty):
        p = points_empty.pop(0)

        target_zone = random.choice(target_zones(zone_count, zone_accessible))
        print(target_zone)

        if target_zone in adjacent_zones(p, result):
            result[p] = target_zone
            update_accessible(graph, result, zone_accessible, zone_center)
            loop_count = 0
        else:
            points_empty.append(p)
            loop_count += 1

    return result


graph = np.full((size, size), 0, dtype=np.bool)
zones = np.full((size, size), -1, dtype=np.int8)

graph = fill(0, graph)
output(graph, zones)

zones = fill_zones(graph)
output(graph, zones)
