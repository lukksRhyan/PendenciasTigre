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
                "Quantidade": quantidade.strip(),
                "Unidade": unidade.strip()
            })

    return produtos


def extrair_dados_nota(xml_file):
    """Extrai os dados principais da NF, incluindo número, CFOP, informações adicionais e produtos."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Pegando número da nota
    nNF_element = root.find(".//ns:ide/ns:nNF", ns)
    numero_nota = nNF_element.text if nNF_element is not None else "desconhecido"

    try:
        vNF_element = root.find(".//ns:ide/ns:vNF", ns)
        valor_nota = vNF_element.text if nNF_element is not None else "desconhecido"
    except AttributeError:
        vNF_element = root.find(".//ns:total/ns:ICMSTot/ns:vNF", ns)
        valor_nota = vNF_element.text if nNF_element is not None else "desconhecido"
    #None type has no attibute text

    # Pegando CFOP do primeiro produto (supondo que a nota tem um CFOP principal)
    cfop_element = root.find(".//ns:det/ns:prod/ns:CFOP", ns)
    cfop = cfop_element.text if cfop_element is not None else "0000"

    # Pegando informações adicionais (onde pode estar o número da nota mãe em notas filhas)
    inf_cpl_element = root.find(".//ns:infAdic/ns:infCpl", ns)
    inf_cpl_text = inf_cpl_element.text.strip() if inf_cpl_element is not None else ""

    # Extraindo produtos da infCpl
    produtos_infCpl = extrair_produtos_infCpl(root)

    # Se for uma Nota Filha (CFOP 5116), tentamos encontrar a Nota Mãe dentro de <infCpl>
    nota_mae_numero = None
    if cfop == "5116":
        match = re.search(r"NF\s*(\d+)", inf_cpl_text)
        if match:
            nota_mae_numero = int(match.group(1))

    # Criando estrutura de dados da nota
    dados_nota = {
        "Número da Nota": numero_nota,
        "CFOP": cfop,
        "Informações Adicionais": inf_cpl_text,
        "total": valor_nota,
        "Produtos": produtos_infCpl  # Adicionando produtos extraídos
    }

    return numero_nota, cfop, nota_mae_numero, dados_nota


def processar_nota(xml_file,destino):
    """Adiciona uma nota individualmente no JSON correto."""

    numero_nota, cfop, nota_mae_numero, dados_nota = extrair_dados_nota(xml_file)

    if cfop == "5922":  # 🟢 Nota Mãe (CFOP 5922)
        json_filename = f"{numero_nota}.json"

        # Criando JSON da Nota Mãe com lista vazia de notas filhas
        json_data = {
            "nºnotamãe": dados_nota,
            "notas_filhas": []
        }

        # Salvando JSON
        with open(destino+json_filename, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)

        print(f"✅ Arquivo JSON '{json_filename}' criado para a Nota Mãe.")

    elif cfop == "5116" and nota_mae_numero:  # 🔵 Nota Filha (CFOP 5116)
        json_filename = f"{nota_mae_numero}.json"

        # Verifica se o JSON da Nota Mãe já existe
        if os.path.exists(json_filename):
            with open(destino+json_filename, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)
        else:
            # Se o JSON não existe, cria um novo JSON para a Nota Mãe
            json_data = {
                "nºnotamãe": {
                    "Número da Nota": nota_mae_numero,
                    "CFOP": "5922",
                    "Informações Adicionais": "Nota Mãe não encontrada no XML processado.",
                    "Produtos": []  # Caso seja criado sem produtos
                },
                "notas_filhas": []
            }

        # Verifica se a Nota Filha já foi adicionada
        if not any(filha["Número da Nota"] == numero_nota for filha in json_data["notas_filhas"]):
            json_data["notas_filhas"].append(dados_nota)

            # Atualizando o JSON
            with open(destino+json_filename, "w", encoding="utf-8") as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)

            print(f"✅ Nota Filha {numero_nota} adicionada ao JSON '{json_filename}'.")
        else:
            print(
                f"⚠️ Nota Filha {numero_nota} já está presente no JSON '{json_filename}', não foi adicionada novamente.")


# 🟢 Testando com arquivos XML (mude os caminhos para os arquivos corretos)
xml_files = [
    "C:/NF ENTRADA/26250208862530000231550010005346001777645282.xml",  # Nota Mãe
    "C:/NF ENTRADA/26241008862530000231550010005150881988684269.xml",  # Nota Mãe
    "C:/NF ENTRADA/26250208862530000231550010005349561748604966.xml"   # Nota Filha
]

