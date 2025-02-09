import heapq
from collections import deque

def calculate_s_core(G, s):
    weight_sum = {node: sum(G[u][v]['weight'] for u, v in G.edges(node)) for node in G.nodes}
    for node in G.nodes:
        G.nodes[node]['label'] = True
    s_core_num = len(G.nodes)
    coreness = {}

    # make heap with the key : weight sum
    heap = [(weight, node) for node, weight in weight_sum.items()]
    heapq.heapify(heap)

    # Calculating coreness L(u) = (c(u), l(u))
    # this loop for c(u)
    while heap:
        current_core, node = heap[0]
        # doesn't have to consider node with having coreness larger than s
        if current_core >= s:
            break
        
        # this loop for l(u)
        layer = 0
        while heap[0][0] <= current_core:
            layer += 1
            temp = []
            # The node deleted in this loop has coreness "(current_core, layer)"
            while heap[0][0] <= current_core:
                weight, node = heapq.heappop(heap)

                if node in coreness:
                    continue

                coreness[node] = (current_core, layer)

                for neighbor in G.neighbors(node):
                    weight_sum[neighbor] -= G[node][neighbor]['weight']
                    temp.append((weight_sum[neighbor], neighbor))

                G.nodes[node]['label'] = False
                s_core_num -= 1
            
            # renew the key of neighbors (quite ineffective?)
            for components in temp:
                heapq.heappush(heap, components)

    # debugging
    # print(coreness)
    return s_core_num, coreness


# not considering T yet
def computeDelta(G, s, e, t, coreness):
    u, v = e
    if u in coreness:
        c_u = coreness[u][0]
    else:
        c_u = s
    if v in coreness:
        c_v = coreness[v][0]
    else:
        c_v = s
    
    return s - min(c_u, c_v)


def FindFollowers(e, delta_e, G, s, coreness):
    F = set()

    # Initialize priority queue
    PQ = []
    for node in e:
        if not G.nodes[node]['label']:
            heapq.heappush(PQ, (coreness[node], node))

    sigma_plus = {}
    while PQ:
        _, x = heapq.heappop(PQ)

        # σ⁺(x)
        sigma_plus[x] = sum(
            G[x][neighbor]['weight']
            for neighbor in G.neighbors(x)
            if G.nodes[neighbor]['label'] or coreness[neighbor] >= coreness[x] or neighbor in F
        )

        # for debugging
        # sigma_plus[x] = 0
        # for neighbor in G.neighbors(x):
        #     # if neighbor in coreness:
        #     #     # print(neighbor, x)
        #     #     # print(coreness[neighbor], coreness[x])
        #     if G.nodes[neighbor]['label'] or coreness[neighbor] >= coreness[x] or neighbor in F:
        #         sigma_plus[x] += G[x][neighbor]['weight']
        # print(x, sigma_plus[x])

        # σ⁺(x) ≥ s
        if sigma_plus[x] >= s:
            F.add(x)
            for y in G.neighbors(x):
                if not G.nodes[y]['label'] and y not in F and coreness[y] > coreness[x]:
                    heapq.heappush(PQ, (coreness[y], y))

        # σ⁺(x) < s
        else:
            Q = deque()
            Q.append(x)
            while Q:
                y = Q.popleft()
                if y in F:
                    F.remove(y)

                for z in G.neighbors(y):
                    if z in F:
                        # update σ⁺(z)
                        sigma_plus[z] -= G[y][z]['weight']

                        if sigma_plus[z] < s:
                            Q.append(z)

    return F