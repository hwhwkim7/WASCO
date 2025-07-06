import functions
import networkx as nx
from itertools import combinations

def run_reuse(G, s, b, t):

    G_prime = G.copy()
    A = set() # the set of (increased edge, delta) pair

    _, coreness = functions.calculate_s_core(G_prime, s)
    sum = 0 # the budget used

    upperbound = [-1] * (len(G_prime.nodes) + 1)
    comp_of, nodes_in, intra_best, inter_best = build_initial_caches(G_prime, s, t, b, coreness, upperbound)

    while sum < b:
        # 1. Cache 이용해서 max 값 찾기
        best_intra = max(intra_best.values(), key=lambda x:x[2], default=None)
        best_inter = max(inter_best.values(), key=lambda x:x[2], default=None)
        best = max([e for e in (best_intra,best_inter) if e], key=lambda x:x[2], default=None)
        if not best: break

        (u,v), delta, FR = best
        print(best)

        if delta > b - sum:
            print("ERROR : 예산 초과")
            break
            # if best is best_intra:
            #     intra_best.pop(comp_of[u], None)
            # else:
            #     inter_best.pop(tuple(sorted((comp_of[u], comp_of[v]))), None)
            # continue

        # 2. anchor 적용
        if G_prime.has_edge(u,v):
            G_prime[u][v]['weight'] += delta
        else:
            G_prime.add_edge(u,v, weight=delta)
        sum += delta
        A.add(((u,v), delta))

        # coreness 업데이트 (전역 계산 or 지역 계산? 확인해봐야 함)
        _, new_core = functions.calculate_s_core(G_prime, s)
        changed_nodes = {x for x in G_prime.nodes if not G_prime.nodes[x]['label'] and new_core[x] != coreness[x]}
        coreness = new_core

        # ----- 3. 캐시 갱신 --------------------------------
        # 3-A : intra vs inter 구분
        if best == best_intra:
            # same CC
            c = comp_of[u]
            affected = {c}
            invalidate(affected, intra_best, inter_best)

            # 재계산
            edge, delta2, FR2 = find_intra_best(G_prime, nodes_in[c], coreness, s, t, b-sum, upperbound)
            if edge: intra_best[c] = (edge, delta2, FR2)

            for z in nodes_in:
                if z == c: continue
                edge2, delta3, FR3 = find_inter_best(G_prime, nodes_in[c], nodes_in[z], coreness, s, t, b-sum, upperbound)
                if edge2:
                    inter_best[tuple(sorted((c,z)))] = (edge2, delta3, FR3)

        else:
            # inter : CC 병합
            c1, c2 = comp_of[u], comp_of[v]
            new_nodes = nodes_in[c1] | nodes_in[c2]

            if changed_nodes:
                new_nodes |= set(changed_nodes) # ? 꼭 필요한 작업인가?

            new_c = max(nodes_in)+1  # 새 id
            nodes_in[new_c] = new_nodes
            for x in new_nodes:
                comp_of[x] = new_c

            # old CC 삭제
            invalidate({c1,c2}, intra_best, inter_best)
            nodes_in.pop(c1); nodes_in.pop(c2)

            # 새 intra / inter
            edge, delta2, FR2 = find_intra_best(G_prime, new_nodes, coreness, s, t, b-sum)
            if edge: intra_best[new_c] = (edge, delta2, FR2)

            for z in nodes_in:
                if z == new_c: continue
                edge2, delta3, FR3 = find_inter_best(G_prime, nodes_in[new_c], nodes_in[z], coreness, s, t, b-sum)
                if edge2:
                    inter_best[tuple(sorted((new_c,z)))] = (edge2, delta3, FR3)

    return A


def build_initial_caches(G, s, t, B_left, coreness, upperbound):
    comp_of, nodes_in = {}, {}
    intra_best, inter_best = {}, {}

    # CC 분해
    for cid, nodes in enumerate(nx.connected_components(G)):
        nodes = set(nodes)
        nodes_in[cid] = nodes
        for v in nodes:
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

    return comp_of, nodes_in, intra_best, inter_best


def find_intra_best(G, nodes, coreness, s, t, budget_left, upperbound):
    
    # upperbound 계산
    for u in G.nodes:
        if not G.nodes[u]['label']:
            upperbound[u] = functions.Upperbound(G, u, coreness, s)

    # Filter candidate edges
    cand = [u for u in nodes if not G.nodes[u]['label']]
    cand.sort(key=lambda u: -upperbound[u])

    best_edge, best_delta, best_FR = None, 0, 0.0

    c = len(cand)
    for i in range(c):
        u = cand[i]

        # pruning
        if best_FR > functions.U_single(u, upperbound) * 2:
            break

        for j in range(i + 1, c):
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

    return best_edge, best_delta, best_FR   # best_edge is None → “이 CC에선 적합 엣지 없음”


def find_inter_best(G, nodesA, nodesB, coreness, s, t, budget_left, upperbound):

    # Filter candidate_edges
    candA = [u for u in nodesA if not G.nodes[u]['label']]
    candB = [v for v in nodesB if not G.nodes[v]['label']]

    candA.sort(key=lambda u: -upperbound[u])
    candB.sort(key=lambda v: -upperbound[v])

    best_edge, best_delta, best_FR = None, 0, 0.0

    # Upper-bound 배열을 한 번 미리 계산해 두면 U_single 재호출을 줄일 수 있음
    U_A = {u: functions.U_single(u, upperbound) for u in candA}
    U_B = {v: functions.U_single(v, upperbound) for v in candB}

    for i, u in enumerate(candA):
        if best_FR > U_A[u] + max(U_B.values()):
            break

        for v in candB:
            # 다시 확인해봐야 함. 두 조건이 같은 거 같기도
            if best_FR >= U_A[u] + U_B[v]:
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

    return best_edge, best_delta, best_FR


def invalidate(ccs, intra_best, inter_best):
    for c in ccs:
        intra_best.pop(c, None)
    for key in list(inter_best):
        if key[0] in ccs or key[1] in ccs:
            inter_best.pop(key, None)