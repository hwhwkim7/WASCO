import networkx as nx
from itertools import combinations
import sys
import functions
import exp_func

def run(G, s, b, t, T1_self_edge = True, T2_upperbound = True):
    # Time
    FT = 0
    UT = 0

    G_prime = G.copy()
    A = set()  # the set of (increased edge, delta) pair
    
    # calculate_s_core 에는 coreness 재선언이 없기 때문에 선언 후 시작
    coreness = {}
    s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)  # Calculate s-core and coreness
    print(s_core_num)
    spent = 0  # the budget used
    

    # self_edge theorem 을 사용하면 s-core 는 후보에서 영원히 제거된다.
    if T1_self_edge:
        non_s_core, s_cand = self_edge_pruning(G_prime) # pruned set

    # 딕셔너리 선언만 해두는 건 크게 잡아먹지 않을듯?
    upperbound = {}

    while spent < b:
        '''
        self_edge 전략과 upperbound 전략에 따라 아래 두 과정을 다르게 진행한다.
        1. Candidate 만드는 과정
        2. Candidate 에서 iteration 돌며 best edge 구하는 과정
        '''
        if T1_self_edge:
            # 1. Candidate 만드는 과정
            candidate_nodes = exp_func.make_candidate_nodes(G_prime, non_s_core, coreness, s, T2_upperbound, upperbound, UT)
            
            # 2. Candidate 에서 iteration 돌며 best edge 구하는 과정
            if T2_upperbound:
                best_edge, best_delta, most_FR = exp_func.iteration_nodes_upperbound(G_prime, candidate_nodes, coreness, s, b, t, upperbound, spent, FT)
            else:
                best_edge, best_delta, most_FR = exp_func.iteration_nodes_no_upperbound(G_prime, candidate_nodes, coreness, s, b, t, spent, FT)
        else:
            # 1. Candidate 만드는 과정
            candidate_edges = exp_func.make_candidate_edges(G_prime, G_prime.nodes, coreness, s, T2_upperbound, upperbound, UT)
            
            # 2. Candidate 에서 iteration 돌며 best edge 구하는 과정
            if T2_upperbound:
                best_edge, best_delta, most_FR = exp_func.iteration_edges_upperbound(G_prime, candidate_edges, coreness, s, b, t, upperbound, spent, FT)
            else:
                best_edge, best_delta, most_FR = exp_func.iteration_edges_no_upperbound(G_prime, candidate_edges, coreness, s, b, t, spent, FT)
                        
        # debugging 3
        # print()
        # print(best_edge)
        # print(best_delta)
        # print(most_FR)

        # Update G_prime
        if best_edge is not None:
            u, v = best_edge
            if u == v:
                v = s_cand

            # add edge weight
            if G_prime.has_edge(u, v):
                G_prime[u][v]['weight'] += best_delta
            else:
                G_prime.add_edge(u, v, weight=best_delta)

            # add budget
            spent += best_delta
            # add answer

            A.add(((u, v), best_delta))
            # calculate s-core again
            coreness = {}
            s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)
            
            # debugging 4
            # print(s_core_num)
        else:
            # print("no more")
            break
    print(s_core_num)
    return A, FT, UT


def self_edge_pruning(G):
    non_s_core = []
    s_cand = None
    for n, d in G.nodes(data=True):
        if not d['label']:
            non_s_core.append(n)
        else:
            if s_cand is None:
                s_cand = n
    
    if s_cand is None:
        print("No node in s-core. Change s value")
        sys.exit(1)
    
    return non_s_core, s_cand