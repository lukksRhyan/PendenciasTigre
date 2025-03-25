import xml.etree.ElementTree as ET
import json
import os
import re

# Namespace do XML
ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}

def extrair_produtos_infCpl(xml_root):
    """Extrai os produtos listados na tag <infCpl>."""
    produtos = []

    inf_cpl_element = xml_root.find(".//ns:infAdic/ns:infCpl", ns)
    if inf_cpl_element is not None and inf_cpl_element.text:
        inf_cpl_text = inf_cpl_element.text.strip()

        # Expressão regular para capturar os produtos no formato (Código @ Quantidade @ Descrição @ Unidade)
        pattern = re.findall(r"(\d+)\s*@\s*([\d,.]+)\s*@\s*([^@]+?)\s*@\s*([\w]+)", inf_cpl_text)

        for match in pattern:
            codigo, quantidade, descricao, unidade = match
            produtos.append({
                "Código": codigo.strip(),
                "Descrição": descricao.strip(),
                "Quantidade": float(quantidade.replace(',', '.')),  # Convertendo para número
                "Unidade": unidade.strip()
            })

    return produtos

def extrair_dados_nota(xml_file):
    """Extrai os dados principais da NF, incluindo número, CFOP, informações adicionais e produtos."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Pegando número da nota e removendo zeros à esquerda
    nNF_element = root.find(".//ns:ide/ns:nNF", ns)
    numero_nota = nNF_element.text.lstrip("0") if nNF_element is not None else "desconhecido"

    # Pegando valor da nota
    vNF_element = root.find(".//ns:total/ns:ICMSTot/ns:vNF", ns)
    valor_nota = vNF_element.text if vNF_element is not None else "desconhecido"

    # Pegando CFOP do primeiro produto
    cfop_element = root.find(".//ns:det/ns:prod/ns:CFOP", ns)
    cfop = cfop_element.text if cfop_element is not None else "0000"

    # Pegando informações adicionais
    inf_cpl_element = root.find(".//ns:infAdic/ns:infCpl", ns)
    inf_cpl_text = inf_cpl_element.text.strip() if inf_cpl_element is not None else ""

    # Extraindo produtos da infCpl
    produtos_infCpl = extrair_produtos_infCpl(root)

    # Se for uma Nota Filha (CFOP 5116), tentamos encontrar a Nota Mãe dentro de <infCpl>
    nota_mae_numero = None
    if cfop == "5116":
        match = re.search(r"NF\s*(\d+)", inf_cpl_text)
        if match:
            nota_mae_numero = match.group(1).lstrip("0")  # Removendo zeros à esquerda

    # Criando estrutura de dados da nota
    dados_nota = {
        "Número da Nota": numero_nota,
        "CFOP": cfop,
        "Informações Adicionais": inf_cpl_text,
        "Total": valor_nota,
        "Produtos": produtos_infCpl  # Adicionando produtos extraídos
    }

    return numero_nota, cfop, nota_mae_numero, dados_nota


def atualizar_produtos_restantes(produtos_restantes, produtos_filha):
    """Subtrai os produtos da nota filha dos produtos restantes da nota mãe."""

    if not isinstance(produtos_restantes, list):
        print("❌ Erro: produtos_restantes não é uma lista válida!")
        return produtos_restantes

    if not isinstance(produtos_filha, list):
        print("❌ Erro: produtos_filha não é uma lista válida!")
        return produtos_restantes

    for produto_filha in produtos_filha:
        codigo_filha = produto_filha["Código"].lstrip("0")  # Removendo zeros à esquerda do código

        # Encontrar o produto correspondente na lista de produtos restantes
        produto_encontrado = None
        for produto_mae in produtos_restantes:
            codigo_mae = produto_mae["Código"].lstrip("0")

            if codigo_mae == codigo_filha:
                produto_encontrado = produto_mae
                break

        if produto_encontrado:
            # Subtrai a quantidade da nota filha dos produtos restantes
            produto_encontrado["Quantidade"] -= produto_filha["Quantidade"]

            # Se a quantidade for menor que zero, zera
            if produto_encontrado["Quantidade"] <= 0:
                produtos_restantes.remove(produto_encontrado)  # Remove produto zerado
        else:
            print(f"⚠️ Aviso: Produto {codigo_filha} da nota filha não encontrado na nota mãe!")

    return produtos_restantes


def processar_nota(xml_file, destino):
    """Adiciona uma nota individualmente no JSON correto."""
    numero_nota, cfop, nota_mae_numero, dados_nota = extrair_dados_nota(xml_file)

    # Nome do arquivo JSON sem zeros à esquerda
    json_filename = os.path.join(destino, f"{numero_nota}.json")

    if cfop == "5922":  # 🟢 Nota Mãe (CFOP 5922)
        # Criando JSON da Nota Mãe com lista vazia de notas filhas e cópia dos produtos restantes
        json_data = {
            "nºnotamãe": dados_nota,
            "produtos_restantes": dados_nota["Produtos"].copy(),  # Criamos uma cópia da lista de produtos
            "notas_filhas": []
        }

        # Salvando JSON
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)

        print(f"✅ Arquivo JSON '{json_filename}' criado para a Nota Mãe.")

    elif cfop == "5116" and nota_mae_numero:  # 🔵 Nota Filha (CFOP 5116)
        json_filename_mae = os.path.join(destino, f"{nota_mae_numero}.json")

        print(f"📌 Buscando Nota Mãe {nota_mae_numero} no arquivo {json_filename_mae}...")

        # Verifica se o JSON da Nota Mãe já existe
        if os.path.exists(json_filename_mae):
            with open(json_filename_mae, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)
        else:
            # Se o JSON não existe, cria um novo JSON para a Nota Mãe
            print(f"⚠️ Nota Mãe {nota_mae_numero} não encontrada. Criando novo JSON.")
            json_data = {
                "nºnotamãe": {
                    "Número da Nota": nota_mae_numero,
                    "CFOP": "5922",
                    "Informações Adicionais": "Nota Mãe não encontrada no XML processado.",
                    "Produtos": [],
                },
                "produtos_restantes": [],
                "notas_filhas": []
            }

        # Atualiza produtos restantes da nota mãe
        json_data["produtos_restantes"] = atualizar_produtos_restantes(json_data["produtos_restantes"], dados_nota["Produtos"])

        # Verifica se a Nota Filha já foi adicionada
        if not any(filha["Número da Nota"] == numero_nota for filha in json_data["notas_filhas"]):
            json_data["notas_filhas"].append(dados_nota)

            # Atualizando o JSON
            with open(json_filename_mae, "w", encoding="utf-8") as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)

            print(f"✅ Nota Filha {numero_nota} adicionada ao JSON '{json_filename_mae}'.")
        else:
            print(f"⚠️ Nota Filha {numero_nota} já está presente no JSON '{json_filename_mae}', não foi adicionada novamente.")

