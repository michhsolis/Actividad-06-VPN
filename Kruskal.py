import networkx as nx
import matplotlib.pyplot as plt

# -------------------------
# Entrada predefinida: GRAFO ORIGINAL
# -------------------------
# Reemplaza estos datos con los de tu red Tailscale
edges = [
    ('A', 'B', 10),
    ('A', 'C', 15),
    ('B', 'C', 5),
    ('B', 'D', 20),
    ('C', 'D', 30),
    ('C', 'E', 25),
    ('D', 'E', 10)
]

# -------------------------
# Implementación de Kruskal
# -------------------------
class DisjointSet:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}

    def find(self, v):
        if self.parent[v] != v:
            self.parent[v] = self.find(self.parent[v])
        return self.parent[v]

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)
        if root_u != root_v:
            self.parent[root_u] = root_v
            return True
        return False

def kruskal(vertices, edges):
    ds = DisjointSet(vertices)
    mst = []
    total_bandwidth = 0

    edges.sort(key=lambda x: x[2])

    for u, v, weight in edges:
        if ds.union(u, v):
            mst.append((u, v, weight))
            total_bandwidth += weight

    return mst, total_bandwidth

# -------------------------
# Obtener nodos únicos y aplicar Kruskal
# -------------------------
nodes = set()
for u, v, _ in edges:
    nodes.add(u)
    nodes.add(v)

mst, mst_bandwidth = kruskal(nodes, edges)

# -------------------------
# Comparación
# -------------------------
original_bandwidth = sum(weight for _, _, weight in edges)

print("=== Topología Original ===")
for edge in edges:
    print(edge)
print(f"Total de ancho de banda utilizado: {original_bandwidth} unidades")

print("\n=== Árbol de Expansión Mínima (Kruskal) ===")
for edge in mst:
    print(edge)
print(f"Total de ancho de banda utilizado: {mst_bandwidth} unidades")
print(f"\nAhorro: {original_bandwidth - mst_bandwidth} unidades\n")

# -------------------------
# Visualización con NetworkX
# -------------------------
def draw_graph(edges, title):
    G = nx.Graph()
    for u, v, weight in edges:
        G.add_edge(u, v, weight=weight)

    pos = nx.spring_layout(G, seed=42)  # Distribución de nodos
    weights = nx.get_edge_attributes(G, 'weight')

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=800, font_weight='bold', edge_color='gray')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)
    plt.title(title)
    plt.show()

# Mostrar gráficas
draw_graph(edges, "Topología Original de la Red (con todos los enlaces)")
draw_graph(mst, "Topología Optimizada (Árbol de Expansión Mínima - Kruskal)")
