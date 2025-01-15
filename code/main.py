import argparse
import networkx as nx
import time

import naive
import adv

parser = argparse.ArgumentParser()
parser.add_argument('--s', type=int, default=10,
                    help='user parameter s')
parser.add_argument('--b', type=int, default=10,
                    help='budget b')
parser.add_argument('--t', type=str, default='',
                    help='a folder name for bound function') # 우선 bound가 없다고 가정하고 작성하시면 될 것 같습니다.
parser.add_argument('--algorithm', default='naive',
                    help='specify algorithm name')
parser.add_argument('--network', default="../dataset/test/network.dat",
                    help='a folder name containing network.dat')
args = parser.parse_args()

G = nx.read_weighted_edgelist(args.network, nodetype=int)
# G = nx.karate_club_graph()
print(G.edges(data=True)) # edge 및 weight 출력

print(f"data: {args.network.split('/')[2]}, nodes: {len(G.nodes())}, edges: {len(G.edges())}")

if args.algorithm == "naive":
    start_time = time.time()
    A = naive.run(G, args.s, args.b, args.t)
    end_time = time.time()
elif args.algorithm == "adv":
    start_time = time.time()
    A = adv.run(G, args.s, args.b, args.t)
    end_time = time.time()