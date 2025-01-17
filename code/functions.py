import heapq

def calculate_s_core(G, s):
    weight_sum = {node: sum(G[u][v]['weight'] for u, v in G.edges(node)) for node in G.nodes}
    s_core = G.copy()
    coreness = {}
    # make heap with the key : weight sum
    heap = [(weight, node) for node, weight in weight_sum.items()]
    heapq.heapify(heap)

    while heap:
        current_core, node = heap[0]
        # doesn't have to consider node with having coreness larger than s
        if current_core >= s:
            break
        
        # The node deleted has coreness "current_core"
        while heap[0][0] <= current_core:
            weight, node = heapq.heappop(heap)

            if node in coreness:
                continue

            coreness[node] = current_core

            for neighbor in s_core.neighbors(node):
                weight_sum[neighbor] -= s_core[node][neighbor]['weight']
                heapq.heappush(heap, (weight_sum[neighbor], neighbor))

            s_core.remove_node(node)

    
    return s_core, coreness


# not considering T yet
def computeDelta(G_prime, s, e, t, coreness):
    u, v = e
    if u in coreness:
        c_u = coreness[u]
    else:
        c_u = s
    if v in coreness:
        c_v = coreness[v]
    else:
        c_v = s
    
    return s - min(c_u, c_v)


def FindFollowers(e, delta_e, G_prime, s, current_s_core):
    new_s_core, _ = calculate_s_core(G_prime, s)
    return len(new_s_core) - len(current_s_core)