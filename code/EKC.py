import networkx as nx
from itertools import combinations
from collections import deque
import functions

def run(G, s, budget, t):

    G_prime = G.copy()
    A = []     # the set of (increased edge, delta) pair

    # 초기 s-core(=k-core) 계산
    coreness = {}
    s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)  # Calculate s-core and coreness
    sum = 0  # the budget used

    for _ in range(budget):
        if sum >= budget:
            break

        # 1) Theorem 4: 후보 엣지 집합 생성
        core_nodes = [u for u in G_prime.nodes if G_prime.nodes[u]['label']]
        shell_nodes = [u for u, c in coreness.items() if c[0] == s-1]
        num_shell = len(shell_nodes)

        candidate_edges = [(u, v) for u in shell_nodes for v in core_nodes if not G.has_edge(u, v)] # 어떻게 해야 겹치는 걸 뺄 수 있을까
        for i in range(num_shell):
            for j in range(i+1, num_shell):
                u, v = shell_nodes[i], shell_nodes[j]
                if not G.has_edge(u, v):
                    candidate_edges.append((u, v))
        
        # 2) Theorem 5: onion layers 기반 추가 프루닝
        candidate_edges = deque(prune_by_theorem5(G_prime, coreness, s, candidate_edges))

        best_edge, best_delta, best_FR = None, 0, 0.0

        # 3) 각 후보 엣지에 대해 follower 계산 및 Theorem 6 프루닝
        while candidate_edges:
            u, v = candidate_edges.popleft()

            # Upperbound 이용한 Pruning
            # ub = functions.Upperbound(G_prime, u, coreness, s)
            # upperbound 가 k보다 작은지 여부를 파악하는 건 가중치가 1일때만 가능

            F = functions.FindFollowers((u,v), 1, G_prime, s, coreness)

            FR = len(F)
            if FR > best_FR:
                best_edge, best_delta, best_FR, best_F = (u,v), 1, FR, F
                # ---- Theorem 6: follower 기반 pruning ----
                candidate_edges = prune_by_theorem6(G_prime, candidate_edges, best_F)

        # 4) 예산 소진 및 그래프 갱신
        if best_edge is None:
            break

        u, v = best_edge
        # if G_prime.has_edge(u, v):
        #     G_prime[u][v]['weight'] += best_delta
        # else:
        #     G_prime.add_edge(u, v, weight=best_delta)
        G_prime.add_edge(u, v, weight=best_delta)

        sum += 1
        A.append((best_edge, best_delta, best_FR, len(best_F)))

        # 5) 변경된 Gp로 다시 k-core 계산 (Section 5.2 캐싱 활용)
        coreness = {}
        s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)

    return A


def prune_by_theorem5(G, coreness, s, candidate_edges):
    pruned = []
    for u, v in candidate_edges:
        Lu = coreness[u] if not G.nodes[u]['label'] else (s, 0)
        Lv = coreness[v] if not G.nodes[v]['label'] else (s, 0)

        # u가 더 낮은 레이어가 되도록 swap
        if Lu > Lv:
            u, v = v, u
            Lu, Lv = Lv, Lu

        # print(u, v, Lu, Lv)
        # u의 활성 이웃 수 d*(u) 계산:
        # l(w) > l(u) 여야 함
        d_star = 0
        for w in G.neighbors(u):
            Lw = coreness[w] if not G.nodes[w]['label'] else (s, 0)
            if Lw > Lu:
                d_star += G[u][w]['weight']
        # print(d_star)

        # Theorem 5 조건: d*(u) = (s-1)
        if d_star == (s-1):
            pruned.append((u, v))

    return pruned

def prune_by_theorem6(G_prime, cand_queue, F_anchor):
    
    new_queue = deque()

    while cand_queue:
        u, v = cand_queue.popleft()

        if u in F_anchor and (v in F_anchor or G_prime.nodes[v]['label']):
            continue

        # 그 외의 경우는 유지
        new_queue.append((u, v))

    return new_queue