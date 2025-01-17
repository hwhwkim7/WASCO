import functions
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

def run(G, s, b, t):

    G_prime = G.copy()
    A = set()  # the set of (increased edge, delta) pair
    
    current_s_core, coreness = functions.calculate_s_core(G_prime, s)  # Calculate s-core and coreness
    sum = 0  # the budget used

    # debugging 1
    # nx.draw(current_s_core, with_labels=True)
    # plt.show()
    # print(coreness)
    
    while sum < b:
        # Filter candidate_edges
        candidate_edges = []

        A_keys = set(edge for edge, _ in A)
        for u, v in combinations(G_prime.nodes, 2):
            # edges already in A
            if (u, v) in A_keys or (v, u) in A_keys:
                continue
            # edges connecting two nodes both in s-core
            if u in current_s_core and v in current_s_core:
                continue
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
            
            u, v = e
            if delta_e > 0 and sum + delta_e <= b:

                # assuming the case of edge anchored
                if G_prime.has_edge(u, v):
                    edge_added = False
                    G_prime[u][v]['weight'] += delta_e
                else:
                    edge_added = True
                    G_prime.add_edge(u, v, weight=delta_e)
                
                # calculate the follower in that case
                followers = functions.FindFollowers(e, delta_e, G_prime, s, current_s_core)
                FR = followers / delta_e  # follower rate

                # renew the maximum value
                if FR > max_FR:
                    best_edge = e
                    best_delta = delta_e
                    max_FR = FR
                
                # roll back the assumtion
                if edge_added:
                    G_prime.remove_edge(u, v)
                else:
                    G_prime[u][v]['weight'] -= delta_e

        # debugging 3
        # print(best_edge)
        # print(best_delta)

        # Update G_prime
        if best_edge is not None:
            u, v = best_edge

            # add edge weight
            if G_prime.has_edge(u, v):
                G_prime[u][v]['weight'] += best_delta
            else:
                G_prime.add_edge(u, v, weight=best_delta)

            # add budget
            sum += best_delta
            # add answer
            A.add((best_edge, best_delta))
            # calculate s-core again
            current_s_core, coreness = functions.calculate_s_core(G_prime, s)
            
            # debugging 4
            # print(len(current_s_core))
        else:
            # print("no more")
            break

    return A