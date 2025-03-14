import os
import json
import glob
import tkinter as tk
from tkinter import filedialog, messagebox

from openpyxl.styles.builtins import comma

from icms_calc import IcmsCalc
from xml_handle import processar_nota

CAMINHO = "C:\\Users\\Cliente\\Desktop\\Notas Tigre\\"


class GerenciadorNotas:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Notas - Tigre")
        self.root.geometry("500x400")

        # Frame do título
        tk.Label(root, text="📜 Gerenciador de Notas Tigre", font=("Arial", 14, "bold")).pack(pady=10)

        # Botão para listar notas
        self.listar_btn = tk.Button(root, text="📂 Listar Notas", command=self.listar_notas, width=20, height=2)
        self.listar_btn.pack(pady=5)

        # Botão para adicionar notas
        self.adicionar_btn = tk.Button(root, text="➕ Adicionar Nota", command=self.adicionar_notas, width=20, height=2)
        self.adicionar_btn.pack(pady=5)

        # Campo de entrada para consultar nota
        self.label_consultar = tk.Label(root, text="Digite o número da nota:")
        self.label_consultar.pack(pady=5)

        self.entry_nota = tk.Entry(root)
        self.entry_nota.pack(pady=5)

        # Botão para consultar nota
        self.consultar_btn = tk.Button(root, text="🔍 Consultar Nota", command=self.consultar_nota, width=20, height=2)
        self.consultar_btn.pack(pady=5)

        self.calc_icms_btn = tk.Button(root, text="Calcular ICMS de produto",command=self.calc_icms, width=20, height=2  )
        self.calc_icms_btn.pack(pady=5)

        # Lista de notas (será preenchida dinamicamente)
        self.lista_notas = tk.Listbox(root, width=50, height=10)
        self.lista_notas.pack(pady=10)

    def listar_notas(self):
        """Lista todas as notas disponíveis."""
        self.lista_notas.delete(0, tk.END)  # Limpa a lista

        lista_jsons = glob.glob(os.path.join(CAMINHO, "*.json"))

        if not lista_jsons:
            self.lista_notas.insert(tk.END, "❌ Nenhuma nota encontrada!")
            return

        for nota in lista_jsons:
            nota = os.path.basename(nota).replace('.json', '')
            self.lista_notas.insert(tk.END, f"📝 Nota: {nota}")

    def adicionar_notas(self):
        """Abre o explorador de arquivos para selecionar um XML e salvar como JSON."""
        arquivo_xml = filedialog.askopenfilename(title="Selecione um arquivo XML",
                                                 filetypes=[("Arquivos XML", "*.xml")])

        if not arquivo_xml:
            messagebox.showwarning("Aviso", "❌ Nenhum arquivo selecionado.")
            return

        try:
            json_data = processar_nota(arquivo_xml, CAMINHO)

            # Criar nome do arquivo JSON baseado no número da nota
            numero_nota = os.path.splitext(os.path.basename(arquivo_xml))[0]
            json_filename = os.path.join(CAMINHO, f"{numero_nota}.json")

            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)

            messagebox.showinfo("Sucesso", f"✅ Nota {numero_nota} adicionada com sucesso!")
            self.listar_notas()  # Atualiza a lista de notas

        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao processar nota: {e}")

    def consultar_nota(self):
        """Consulta uma nota e exibe os detalhes em uma nova janela."""
        numero = self.entry_nota.get().strip()

        if not numero:
            messagebox.showwarning("Aviso", "Digite um número de nota válido.")
            return

        json_filename = os.path.join(CAMINHO, numero + ".json")

        if not os.path.exists(json_filename):
            messagebox.showerror("Erro", f"❌ Nota {numero} não encontrada!")
            return

        with open(json_filename, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)

        # Criar uma nova janela para exibir a nota
        janela_nota = tk.Toplevel(self.root)
        janela_nota.title(f"Detalhes da Nota {numero}")
        janela_nota.geometry("500x400")

        text_area = tk.Text(janela_nota, wrap="word", height=20, width=60)
        text_area.pack(pady=10)
        text_area.insert(tk.END, json.dumps(json_data, indent=4, ensure_ascii=False))
        text_area.config(state=tk.DISABLED)

    def calc_icms(self):
        calc = IcmsCalc()



# Iniciar a interface gráfica
if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorNotas(root)
    root.mainloop()
