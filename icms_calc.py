import tkinter as tk
from tkinter import messagebox



class IcmsCalc:
    def __init__(self):
        # Criando a janela principal
        self.root = tk.Tk()
        self.root.title("Calculadora de ICMS")
        self.root.geometry("350x250")

        # Label de instrução
        tk.Label(self.root, text="Digite o valor:", font=("Arial", 12)).pack(pady=10)

        # Entrada de valor
        self.entry_valor = tk.Entry(self.root, font=("Arial", 12), width=15)
        self.entry_valor.pack(pady=5)

        # Botão de cálculo
        self.btn_calcular = tk.Button(self.root, text="Calcular ICMS", font=("Arial", 12), command=self.calc_icms)
        self.btn_calcular.pack(pady=10)

        # Label para exibir o resultado
        self.resultado_texto = tk.StringVar()
        self.label_resultado = tk.Label(self.root, textvariable=self.resultado_texto, font=("Arial", 12), fg="blue", justify="left")
        self.label_resultado.pack(pady=10)

        # Rodar a interface gráfica
        self.root.mainloop()

    def calc_icms(self):
        try:
            valor = float(self.entry_valor.get().replace(',', '.'))  # Converte para float
            base_calculo = valor * 0.2732
            icms = base_calculo * 0.205

            self.resultado_texto.set(f"📊 Base de Cálculo: R$ {base_calculo:.4f}\n💰 ICMS: R$ {icms:.4f}")

        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido.")
if __name__ == '__main__':
    calculator = IcmsCalc()