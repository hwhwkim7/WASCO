import functions
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

def run(G, s, b, t):

    G_prime = G.copy()
    A = set()  # the set of (increased edge, delta) pair
    
    coreness = {}
    s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)  # Calculate s-core and coreness
    sum = 0  # the budget used

    # debugging for Upperbound
    # for i in G_prime.nodes:
    #     if not G_prime.nodes[i]['label']:
    #         print(i, functions.Upperbound(G_prime, i, coreness))

    # debugging 1
    # print(s_core_num)
    # print(coreness)
    
    while sum < b:
        
        # Filter candidate edges
        non_s_core = []
        s_core = []
        for n, d in G_prime.nodes(data=True):
            if not d['label']:
                non_s_core.append(n)
            else:
                s_core.append(n)

        candidate_edges = []

        # Intra non-core
        non_len = len(non_s_core)
        for i in range(non_len):
            u = non_s_core[i]
            # self edge 반영하게끔 i+1 -> i ---> s-core 랑 잇는 부분이 있어서 필요 없을듯
            for j in range(i+1, non_len):
                v = non_s_core[j]
                candidate_edges.append((u, v))

        # core <-> non-core
        for u in non_s_core:
            for v in s_core:
                candidate_edges.append((u, v))
        
        # debugging 2
        # print(candidate_edges)
                
        # initial setting
        best_edge = None; best_delta = 0  # edge and delta with maximal FR
        max_FR = 0  # maximal follower rate


        # Search every candidate edges
        for e in candidate_edges:
            # compute delta (How much you need increasing edge weight)
            delta_e = functions.computeDelta(G_prime, s, e, t, coreness)
            
            if delta_e > 0 and sum + delta_e <= b:
                # calculate the follower in certain case
                followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                FR = len(followers) / delta_e  # follower rate

                # for debugging

                # print(len(followers), end = " ")

                # new_s_core_num, _ = functions.calculate_s_core(G_prime, s)
                # follower_num = new_s_core_num - s_core_num
                # FR = follower_num / delta_e
                # print(follower_num, end = " ")

                # print("edge : ", e, " edge weight: ", delta_e)
                # print(len(followers))
                # print(follower_num)
                
                # renew the maximum value
                if FR > max_FR:
                    best_edge = e
                    best_delta = delta_e
                    max_FR = FR

        # debugging 3
        # print()
        # print(best_edge)
        # print(best_delta)
        # print(max_FR)

        # Update G_prime
        if best_edge is not None:
            u, v = best_edge
            if u == v:
                v = s_core[0]

            # add edge weight
            if G_prime.has_edge(u, v):
                G_prime[u][v]['weight'] += best_delta
            else:
                G_prime.add_edge(u, v, weight=best_delta)

            # add budget
            sum += best_delta
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
    return A