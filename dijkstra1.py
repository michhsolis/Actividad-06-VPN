import heapq
import json
import subprocess
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext

# ----------- Lógica de red y Dijkstra ------------------

def get_tailscale_network(log_callback):
    """
    Construye un grafo de la red Tailscale usando 'tailscale ping'
    y devuelve un diccionario con nodos y latencias.
    """
    try:
        result = subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True)
        data = json.loads(result.stdout)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener el estado de Tailscale: {e}")
        return {}

    nodes = [info['DNSName'] for _, info in data['Peer'].items()]
    graph = {node: {} for node in nodes}

    for src in nodes:
        for dst in nodes:
            if src == dst:
                continue
            try:
                ping_result = subprocess.run(
                    ["tailscale", "ping", dst, "--timeout=1s"],
                    capture_output=True,
                    text=True
                )
                match = re.search(r"in (\d+\.?\d*)ms", ping_result.stdout)
                if match:
                    latency = float(match.group(1))
                    graph[src][dst] = latency
                    log_callback(f"{src} → {dst}: {latency} ms")
                else:
                    log_callback(f"{src} → {dst}: sin respuesta")
            except Exception as e:
                log_callback(f"Error al hacer ping de {src} a {dst}: {e}")

    return graph

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous_nodes = {node: None for node in graph}
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, previous_nodes

def reconstruct_path(prev_nodes, end):
    path = []
    while end is not None:
        path.insert(0, end)
        end = prev_nodes[end]
    return path

# ----------- Interfaz gráfica (Tkinter) ------------------

class TailscaleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Red Tailscale")

        # Entradas para análisis de red
        tk.Label(root, text="Nodo origen:").grid(row=0, column=0, sticky="e")
        tk.Label(root, text="Nodo destino:").grid(row=1, column=0, sticky="e")

        self.entry_start = tk.Entry(root, width=40)
        self.entry_end = tk.Entry(root, width=40)
        self.entry_start.grid(row=0, column=1, padx=5, pady=5)
        self.entry_end.grid(row=1, column=1, padx=5, pady=5)

        self.button_run = tk.Button(root, text="Analizar Red", command=self.run_analysis)
        self.button_run.grid(row=2, column=0, columnspan=2, pady=10)

        # Entradas para transferencia de archivos
        tk.Label(root, text="Archivo local:").grid(row=3, column=0, sticky="e")
        self.entry_file = tk.Entry(root, width=60)
        self.entry_file.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(root, text="Destino (usuario@host:/ruta):").grid(row=4, column=0, sticky="e")
        self.entry_target = tk.Entry(root, width=60)
        self.entry_target.grid(row=4, column=1, padx=5, pady=5)

        self.button_transfer = tk.Button(root, text="Transferir archivo", command=self.transfer_file)
        self.button_transfer.grid(row=5, column=0, columnspan=2, pady=10)

        # Área de texto para salida
        self.output = scrolledtext.ScrolledText(root, width=80, height=20)
        self.output.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def log(self, message):
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)

    def run_analysis(self):
        self.output.delete(1.0, tk.END)
        start = self.entry_start.get().strip()
        end = self.entry_end.get().strip()

        if not start or not end:
            messagebox.showwarning("Entrada incompleta", "Por favor, ingresa ambos nodos.")
            return

        self.log(f"🔍 Escaneando red Tailscale...")
        graph = get_tailscale_network(self.log)

        if start not in graph or end not in graph:
            messagebox.showerror("Nodos inválidos", "Uno o ambos nodos no se encontraron en la red.")
            return

        distances, prev = dijkstra(graph, start)
        path = reconstruct_path(prev, end)

        if distances[end] == float('inf'):
            self.log(f"\n No hay ruta disponible de {start} a {end}.")
        else:
            self.log(f"\n Ruta óptima: {' -> '.join(path)}")
            self.log(f" Latencia total: {distances[end]} ms")

    def transfer_file(self):
        archivo = self.entry_file.get().strip()
        destino = self.entry_target.get().strip()

        if not archivo or not destino:
            messagebox.showwarning("Campos vacíos", "Debes especificar el archivo y el destino.")
            return

        self.log(f"\n Transfiriendo archivo: {archivo} → {destino}")

        try:
            result = subprocess.run(
                ["scp", archivo, destino],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log(" Transferencia completada exitosamente.")
            else:
                self.log(f" Error en la transferencia:\n{result.stderr}")
        except Exception as e:
            self.log(f" Excepción durante la transferencia: {e}")

# ----------- Ejecutar directamente ---------------

root = tk.Tk()
app = TailscaleGUI(root)
root.mainloop()
