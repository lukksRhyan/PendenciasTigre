 🧾 Gerenciador de Notas Tigre  
  
 Este é um sistema desenvolvido em **Python com Tkinter** para auxiliar na organização e processamento de **Notas Fiscais Eletrônicas (NF-e)** do fornecedor Tigre, a partir de arquivos XML. O sistema agrupa automaticamente **notas mãe (CFOP 5922)** e **notas filhas (CFOP 5116)**, extrai os produtos, calcula ICMS e gera arquivos JSON organizados.  
  
 ---  
  
 ## 📦 Funcionalidades  
  
 - ✅ Interface gráfica intuitiva com Tkinter  
 - 📂 Listagem automática de notas salvas  
 - ➕ Adição de notas a partir de arquivos XML  
 - 🔍 Consulta de notas pelo número  
 - 🧮 Cálculo de ICMS sobre qualquer valor  
 - 🔁 Organização de notas filhas dentro da nota mãe  
 - 📉 Atualização automática dos `produtos_restantes` conforme notas filhas são icionadas  
  
 ---  
  
 ## 🗂️ Estrutura dos Arquivos JSON  
  
 Para cada nota mãe (NF com CFOP 5922), é gerado um arquivo `XXXXX.json` com a guinte estrutura:  
  
 ```json  
 {  
   "nºnotamãe": {  
     "Número da Nota": "534600",  
     "CFOP": "5922",  
     "Informações Adicionais": "...",  
     "Total": "41278.68",  
     "Produtos": [ ... ]  
   },  
   "produtos_restantes": [ ... ],  
   "notas_filhas": [  
     {  
       "Número da Nota": "534601",  
       "CFOP": "5116",  
       "Produtos": [ ... ]  
     }  
   ]  
 }  
 ```  
  
 ---  
  
 ## 🚀 Como Usar  
  
 1. **Clone o repositório ou baixe os arquivos**  
 2. Instale as dependências se necessário (somente padrão Python 3)  
 3. Execute o programa:  
  
 ```bash  
 python main.py  
 ```  
  
 > 🪟 A janela do sistema será aberta e você poderá:  
 > - Adicionar notas XML  
 > - Visualizar JSONs gerados  
 > - Calcular ICMS de valores  
 > - Consultar qualquer nota  
  
 ---  
  
 ## 📁 Diretórios e Arquivos Importantes  
  
 - `main.py`: interface gráfica com Tkinter  
 - `xml_handle.py`: lógica para processar os arquivos XML  
 - `icms_calc.py`: lógica de cálculo de ICMS  
 - `Notas Tigre/`: pasta onde os arquivos `.json` são salvos  
  
 ---  
  
 ## 🔧 Requisitos  
  
 - Python 3.9+  
 - Nenhuma biblioteca externa obrigatória  
 - Interface gráfica Tkinter (já inclusa com Python)  
  
 ---  
  
 ## 📌 Observações  
  
 - Os arquivos XML devem seguir o padrão da NFe Nacional (com namespace do SEFAZ)  
 - A extração de produtos ocorre com base na tag `<infCpl>` utilizando expressões regulares  
  
 ---  
  
 ## 👨‍💻 Autor  
  
 **Lucas Rhyan**  
 Desenvolvedor Python / Automação / Sistemas ERP  
  
 ---  
  
 ## 📜 Licença  
  
 Este projeto é de uso livre para fins educacionais e comerciais.  
 Contribuições são bem-vindas!  
