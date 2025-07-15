import functions
import networkx as nx
from itertools import combinations

def run_reuse(G, s, b, t):

    G_prime = G.copy()
    A = set() # the set of (increased edge, delta) pair

    coreness = {}
    s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)
    sum = 0 # the budget used

    upperbound = {}
    comp_of, nodes_in, intra_best, inter_best, s_cand = build_initial_caches(G_prime, s, t, b, coreness, upperbound)

    while sum < b:
        # 1. Find best edge using Cache
        best_intra = max(intra_best.values(), key=lambda x:x[2], default=None)
        best_inter = max(inter_best.values(), key=lambda x:x[2], default=None)
        best = max([e for e in (best_intra,best_inter) if e], key=lambda x:x[2], default=None)
        if not best: break

        (u,v), delta, FR = best

        budget_left = b - sum

        if delta > budget_left:
            if best == best_intra:
                c = comp_of[u]
                intra_best.pop(c, None)

                # Renew the connected component where the best edge came from using budget_left
                edge2, d2, fr2 = find_intra_best(G_prime, nodes_in[c], upperbound, coreness, s, t, budget_left)
                if edge2 is not None:
                    intra_best[c] = (edge2, d2, fr2)

            else:
                c1, c2 = comp_of[u], comp_of[v]
                key = tuple(sorted((c1, c2)))
                inter_best.pop(key, None)

                # Renew the intra cc where the best edge came from using budget_left
                edge2, d2, fr2 = find_inter_best(G_prime, nodes_in[c],nodes_in[c2], upperbound, coreness, s, t, budget_left)
                if edge2 is not None:
                    inter_best[key] = (edge2, d2, fr2)

            continue 
    
         # debugging 3
        # print()
        # print(best[0])
        # print(best[1])
        # print(best[2])

        # 2. Apply anchor edge
        # self edge 인지 고려해야 함
        if u == v:
            v = s_cand

        if G_prime.has_edge(u,v):
            G_prime[u][v]['weight'] += delta
        else:
            G_prime.add_edge(u,v, weight=delta)
        sum += delta
        A.add(((u,v), delta))

        # coreness 업데이트 (전역 계산 or 지역 계산? 확인해봐야 함) - 지역으로 바꾸기
        # s_core_num = functions.calculate_s_core(G_prime, s)

        # ----- 3. Renew Cache --------------------------------
        # 3-A : intra vs inter
        if best == best_intra:
            # same CC
            c = comp_of[u]
            # calculate_s_core 에 new_nodes 를 넣을지 고민
            s_core_num = functions.calculate_s_core(G_prime, nodes_in[c], s, coreness)

            new_nodes = {v for v in nodes_in[c] if not G_prime.nodes[v]['label']}

            # CC 에 non-s-core 가 남아있는지 확인
            if not new_nodes:
                invalidate({c}, intra_best, inter_best)  # 캐시 엔트리 삭제
                nodes_in.pop(c)
            else:
                nodes_in[c] = new_nodes
                invalidate({c}, intra_best, inter_best)

                # Recompute
                edge, delta2, FR2 = find_intra_best(G_prime, nodes_in[c], coreness, s, t, b-sum, upperbound)
                if edge:
                    intra_best[c] = (edge, delta2, FR2)

                for z in nodes_in:
                    if z == c: continue
                    edge2, delta3, FR3 = find_inter_best(G_prime, nodes_in[c], nodes_in[z], coreness, s, t, b-sum, upperbound)
                    if edge2:
                        inter_best[tuple(sorted((c,z)))] = (edge2, delta3, FR3)

        else:
            # inter : Union CC
            c1, c2 = comp_of[u], comp_of[v]
            union_nodes = nodes_in[c1] | nodes_in[c2]

            # union_nodes or new_nodes 둘 중 머 넣을지 고민
            s_core_num = functions.calculate_s_core(G_prime, union_nodes, s, coreness)

            new_nodes = {x for x in union_nodes if not G_prime.nodes[x]['label']}

            # Delete old CC
            invalidate({c1,c2}, intra_best, inter_best)
            nodes_in.pop(c1); nodes_in.pop(c2)

            # non-s-core 가 존재해야만 새롭게 만든다.
            if new_nodes:
                new_c = max(nodes_in)+1  # New id
                nodes_in[new_c] = new_nodes
                for x in new_nodes:
                    comp_of[x] = new_c


                # New intra / inter
                edge, delta2, FR2 = find_intra_best(G_prime, new_nodes, coreness, s, t, b-sum, upperbound)
                if edge: intra_best[new_c] = (edge, delta2, FR2)

                for z in nodes_in:
                    if z == new_c: continue
                    edge2, delta3, FR3 = find_inter_best(G_prime, nodes_in[new_c], nodes_in[z], coreness, s, t, b-sum, upperbound)
                    if edge2:
                        inter_best[tuple(sorted((new_c,z)))] = (edge2, delta3, FR3)

    return A


def build_initial_caches(G, s, t, B_left, coreness, upperbound):
    comp_of, nodes_in = {}, {}
    intra_best, inter_best = {}, {}
    s_cand = None

    # Decompose CC
    for cid, nodes in enumerate(nx.connected_components(G)):
        # CC 저장은 non-s-core 만
        non_core = set()
        for v in nodes:
            if not G.nodes[v]['label']:
                non_core.add(v)
            else:
                if s_cand is None:
                    s_cand = v

        # CC 가 다 s-core 라면 저장 X
        if not non_core:
            continue

        nodes_in[cid] = non_core
        for v in non_core:
            comp_of[v] = cid

    # intra
    for cid, nodes in nodes_in.items():
        edge, delta, FR = find_intra_best(G, nodes, coreness, s, t, B_left, upperbound)
        if edge:
            intra_best[cid] = (edge, delta, FR)

    # inter
    for cid1, cid2 in combinations(nodes_in, 2):
        edge, delta, FR = find_inter_best(G,
                               nodes_in[cid1], nodes_in[cid2],
                               coreness, s, t, B_left, upperbound)
        if edge:
            inter_best[tuple(sorted((cid1,cid2)))] = (edge, delta, FR)

    return comp_of, nodes_in, intra_best, inter_best, s_cand


def find_intra_best(G, nodes, coreness, s, t, budget_left, upperbound):
    
    # Compute upperbound for only cand
    cand = []
    for u in nodes:
        if not G.nodes[u]['label']:
            upperbound[u] = functions.Upperbound(G, u, coreness, s)
            cand.append(u)

    cand.sort(key=lambda u: -upperbound[u])

    best_edge, best_delta, best_FR = None, 0, 0.0

    c = len(cand)
    for i in range(c):
        u = cand[i]

        # pruning
        if best_FR > functions.U_single(u, upperbound) * 2:
            break

        for j in range(i, c):
            v = cand[j]

            if best_FR >= functions.U_single(u, upperbound) + functions.U_single(v, upperbound):
                break
            if best_FR >= functions.U_double(u, v, upperbound, coreness, G):
                continue

            e = (u, v)
            delta_e = functions.computeDelta(G, s, e, t, coreness)
            
            if delta_e > 0 and delta_e <= budget_left:
                followers = functions.FindFollowers(e, delta_e, G, s, coreness)
                FR = len(followers) / delta_e
                if FR > best_FR:
                    best_edge, best_delta, best_FR = e, delta_e, FR

    return best_edge, best_delta, best_FR   # best_edge is None → No appropriate edge in this CC


def find_inter_best(G, nodesA, nodesB, coreness, s, t, budget_left, upperbound):
    # Filter candidate_edges
    candA = [u for u in nodesA if not G.nodes[u]['label']]
    candB = [v for v in nodesB if not G.nodes[v]['label']]

    candA.sort(key=lambda u: -upperbound[u])
    candB.sort(key=lambda v: -upperbound[v])

    best_edge, best_delta, best_FR = None, 0, 0.0

    for i, u in enumerate(candA):
        if best_FR > functions.U_single(u, upperbound) + functions.U_single(candB[0], upperbound):
            break

        for v in candB:
            if best_FR >= functions.U_single(u, upperbound) + functions.U_single(v, upperbound):
                break

            e = (u, v)
            delta_e = functions.computeDelta(G, s, e, t, coreness)
            
            if delta_e > 0 and delta_e <= budget_left:
                followers = functions.FindFollowers(e, delta_e, G, s, coreness)
                FR = len(followers) / delta_e
                if FR > best_FR:
                    best_edge, best_delta, best_FR = e, delta_e, FR

    return best_edge, best_delta, best_FR


def invalidate(ccs, intra_best, inter_best):
    for c in ccs:
        intra_best.pop(c, None)
    for key in list(inter_best):
        if key[0] in ccs or key[1] in ccs:
            inter_best.pop(key, None)