import networkx as nx
import numpy as np
from networkx.generators.community import LFR_benchmark_graph

# 1. 파라미터 설정
n = 1000
tau1 = 3.0
tau2 = 1.5
mu = 0.1
avg_degree = 10
max_degree = 50
min_community = 20
seed = 42

# 2. LFR 그래프 생성 및 정리
G = LFR_benchmark_graph(
    n, tau1, tau2, mu,
    average_degree=avg_degree,
    max_degree=max_degree,
    min_community=min_community,
    seed=seed
)
G = nx.Graph(G)
G.remove_edges_from(nx.selfloop_edges(G))

# 3. community ground truth 추출 및 ID 부여
communities = {frozenset(G.nodes[v]['community']) for v in G.nodes()}
ground_truth = [set(c) for c in communities]
comm_id = {node: idx for idx, comm in enumerate(ground_truth) for node in comm}

# 4. 정수 가중치 분포 설정 (예시)
#   같은 커뮤니티 내부 엣지: 1 ~ 10
#   다른 커뮤니티 간 엣지: 1 ~ 3
intra_weight_range = (1, 10)
inter_weight_range = (1, 3)

# 5. 엣지에 커뮤니티 기반 정수 가중치 할당
for u, v, data in G.edges(data=True):
    if comm_id[u] == comm_id[v]:
        # numpy.randint: low (inclusive), high (exclusive)
        w = np.random.randint(intra_weight_range[0],
                              intra_weight_range[1] + 1)
    else:
        w = np.random.randint(inter_weight_range[0],
                              inter_weight_range[1] + 1)
    data['weight'] = int(w)

# 6. edges.dat 쓰기: "u v weight"
edges_file = f"test/LFR_first.dat"
labels_file = f"test/LFR_labels.dat"

with open(edges_file, "w") as f:
    for u, v, data in G.edges(data=True):
        f.write(f"{u} {v} {data['weight']}\n")

# # 7. labels.dat 쓰기: "u community_id"
# with open(labels_file, "w") as f:
#     for node in G.nodes():
# #         f.write(f"{node} {comm_id[node]}\n")

# print("→ edges.dat 와 labels.dat 저장 완료")
print("저장완료")