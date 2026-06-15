#!/usr/bin/env python3
"""
Gerador de produtos para o configurador 3D.
Uso: python3 gerador.py
"""
import os, sys, re, json, base64, datetime, shutil

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE     = os.path.join(BASE_DIR, "template", "index.html")
CATALOGO_DIR = os.path.join(BASE_DIR, "catalogo")

# ── Paletas padrão ────────────────────────────────────────────────────────────
PALETAS_PADRAO = {
    "1 – Cores vibrantes": [
        {"nome":"Roxo",     "hex":"#7c3aed"},
        {"nome":"Azul",     "hex":"#2563eb"},
        {"nome":"Verde",    "hex":"#16a34a"},
        {"nome":"Vermelho", "hex":"#dc2626"},
        {"nome":"Preto",    "hex":"#111111"},
        {"nome":"Branco",   "hex":"#f5f5f5"},
    ],
    "2 – Neutros e terra": [
        {"nome":"Cinza",    "hex":"#9ca3af"},
        {"nome":"Bege",     "hex":"#d6c5a4"},
        {"nome":"Marrom",   "hex":"#7c4a1e"},
        {"nome":"Dourado",  "hex":"#d4af37"},
        {"nome":"Preto",    "hex":"#111111"},
        {"nome":"Branco",   "hex":"#f5f5f5"},
    ],
    "3 – Pastel": [
        {"nome":"Rosa",     "hex":"#fbcfe8"},
        {"nome":"Lavanda",  "hex":"#ddd6fe"},
        {"nome":"Menta",    "hex":"#bbf7d0"},
        {"nome":"Pêssego",  "hex":"#fed7aa"},
        {"nome":"Branco",   "hex":"#f5f5f5"},
        {"nome":"Creme",    "hex":"#fef9c3"},
    ],
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def limpar_tela():
    os.system("clear" if sys.platform != "win32" else "cls")

def slugify(texto):
    texto = texto.lower().strip()
    texto = re.sub(r'[àáâãäå]', 'a', texto)
    texto = re.sub(r'[èéêë]',   'e', texto)
    texto = re.sub(r'[ìíîï]',   'i', texto)
    texto = re.sub(r'[òóôõö]',  'o', texto)
    texto = re.sub(r'[ùúûü]',   'u', texto)
    texto = re.sub(r'[ç]',      'c', texto)
    texto = re.sub(r'[^a-z0-9]+', '-', texto)
    return texto.strip('-')

def perguntar(prompt, padrao=None):
    sufixo = f" [{padrao}]" if padrao else ""
    resp = input(f"{prompt}{sufixo}: ").strip()
    return resp if resp else padrao

def validar_numero_whatsapp(num):
    num = re.sub(r'\D', '', num)
    if len(num) < 10 or len(num) > 15:
        return None, "Número deve ter entre 10 e 15 dígitos (inclua DDD e código do país)."
    return num, None

def cor_hex_valida(hex_str):
    return bool(re.match(r'^#[0-9a-fA-F]{6}$', hex_str.strip()))

def stl_para_data_url(caminho_stl):
    with open(caminho_stl, 'rb') as f:
        dados = f.read()
    b64 = base64.b64encode(dados).decode('ascii')
    return f"data:model/stl;base64,{b64}"

# ── Seleção de STLs ────────────────────────────────────────────────────────────
def selecionar_stls():
    print("\n── Seleção de arquivos STL ──────────────────────────────────────────")
    usar_gui = False
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        usar_gui = True
    except Exception:
        pass

    if usar_gui:
        print("Abrindo seletor de arquivos… (selecione um ou mais STLs)")
        try:
            caminhos = filedialog.askopenfilenames(
                title="Selecione os arquivos STL do produto",
                filetypes=[("Arquivos STL", "*.stl"), ("Todos os arquivos", "*.*")]
            )
            root.destroy()
            caminhos = list(caminhos)
        except Exception:
            caminhos = []
    else:
        caminhos = []

    if not caminhos:
        print("\nDigite os caminhos dos STLs (um por linha, linha vazia para finalizar):")
        while True:
            c = input("  STL: ").strip()
            if not c:
                break
            if not os.path.isfile(c):
                print(f"  ⚠  Arquivo não encontrado: {c}")
                continue
            caminhos.append(c)

    if not caminhos:
        print("\n❌  Nenhum arquivo STL selecionado. Encerrando.")
        sys.exit(1)

    # Verificar existência de todos os arquivos
    for c in caminhos:
        if not os.path.isfile(c):
            print(f"\n❌  Arquivo não encontrado: {c}")
            sys.exit(1)

    print(f"\n✔  {len(caminhos)} STL(s) selecionado(s):")
    for c in caminhos:
        print(f"   • {os.path.basename(c)}")
    return caminhos

# ── Metadados do produto ───────────────────────────────────────────────────────
def coletar_metadados(caminhos_stl):
    print("\n── Metadados do produto ─────────────────────────────────────────────")

    nome = ""
    while not nome:
        nome = perguntar("Nome do produto (ex.: Rinoceronte)")
        if not nome:
            print("  ⚠  O nome é obrigatório.")

    slug_sugerido = slugify(nome)
    slug = perguntar("Slug (URL amigável)", slug_sugerido) or slug_sugerido
    slug = slugify(slug)

    preco_str = perguntar("Preço (opcional, ex.: R$ 85,00)", "")
    preco = preco_str if preco_str else None

    descricao = perguntar(
        "Descrição curta",
        "Personalize as cores e finalize pelo WhatsApp."
    )

    print("\n── Número de WhatsApp (para receber pedidos) ─────────────────────────")
    print("   Formato: código do país + DDD + número (ex.: 5555991224041)")
    numero_padrao = "5555991224041"
    while True:
        numero_raw = perguntar("Número", numero_padrao)
        numero, erro = validar_numero_whatsapp(numero_raw)
        if not erro:
            break
        print(f"  ⚠  {erro}")

    return {
        "nome":     nome,
        "slug":     slug,
        "preco":    preco,
        "descricao":descricao,
        "numero":   numero,
    }

# ── Configuração de peças ──────────────────────────────────────────────────────
def configurar_pecas(caminhos_stl):
    print("\n── Configuração das peças ───────────────────────────────────────────")
    print("   Para cada STL, informe: id, rótulo, cor padrão e paleta.")
    print("   Arquivos com a mesma cor (ex: dois olhos) podem ser agrupados.\n")

    # Listar arquivos numerados para facilitar agrupamento
    print("   Arquivos selecionados:")
    for i, c in enumerate(caminhos_stl, 1):
        print(f"   {i}. {os.path.basename(c)}")

    # Perguntar agrupamentos antes de configurar
    print("\n   Agrupamento: arquivos que compartilham a mesma cor formam uma peça.")
    print("   Informe quais números agrupar (ex: '3,4' para agrupar 3 e 4).")
    print("   Pressione Enter para continuar sem agrupar.\n")

    grupos_extra = []  # lista de sets de índices (0-based)
    usados = set()
    while True:
        entrada = input("  Grupo (ou Enter para encerrar): ").strip()
        if not entrada:
            break
        try:
            indices = [int(x.strip()) - 1 for x in entrada.split(",")]
            if any(i < 0 or i >= len(caminhos_stl) for i in indices):
                print(f"  ⚠  Use números de 1 a {len(caminhos_stl)}")
                continue
            if len(indices) < 2:
                print("  ⚠  Informe ao menos 2 números para agrupar.")
                continue
            grupos_extra.append(indices)
            usados.update(indices)
            nomes = [os.path.basename(caminhos_stl[i]) for i in indices]
            print(f"  ✔  Grupo: {' + '.join(nomes)}\n")
        except ValueError:
            print("  ⚠  Formato inválido. Ex: 3,4")

    # Construir lista de grupos final: grupos manuais + individuais restantes
    todos_grupos = list(grupos_extra)
    for i in range(len(caminhos_stl)):
        if i not in usados:
            todos_grupos.append([i])
    # Ordenar pelo menor índice de cada grupo para manter ordem natural
    todos_grupos.sort(key=lambda g: min(g))

    paleta_keys = list(PALETAS_PADRAO.keys())
    print("\n   Paletas disponíveis:")
    for k in paleta_keys:
        print(f"   {k}")
    print("   0 – Definir cores manualmente\n")

    pecas = []
    for grupo in todos_grupos:
        arquivos = [os.path.basename(caminhos_stl[i]) for i in grupo]
        print(f"── Peça: {' + '.join(arquivos)} ──")

        nome_sem_ext = os.path.splitext(arquivos[0])[0]
        id_peca = perguntar("  ID (sem espaços)", slugify(nome_sem_ext))
        rotulo  = perguntar("  Rótulo (exibido no painel)", nome_sem_ext.capitalize())

        cor_padrao = ""
        while not cor_hex_valida(cor_padrao):
            cor_padrao = perguntar("  Cor padrão (hex)", "#7c3aed")
            if not cor_hex_valida(cor_padrao):
                print("  ⚠  Use o formato #RRGGBB (ex.: #7c3aed)")

        escolha_paleta = perguntar("  Paleta (número)", "1")
        paleta = None
        for k in paleta_keys:
            if k.startswith(escolha_paleta):
                paleta = PALETAS_PADRAO[k]
                break

        if paleta is None:
            print("  → Definindo paleta manual (mín. 2 cores).")
            paleta = []
            while True:
                nome_cor = input("    Nome da cor (vazio para encerrar): ").strip()
                if not nome_cor:
                    if len(paleta) < 2:
                        print("  ⚠  Adicione ao menos 2 cores.")
                        continue
                    break
                hex_cor = ""
                while not cor_hex_valida(hex_cor):
                    hex_cor = input("    Hex da cor (ex.: #dc2626): ").strip()
                    if not cor_hex_valida(hex_cor):
                        print("  ⚠  Use o formato #RRGGBB")
                paleta.append({"nome": nome_cor, "hex": hex_cor})

        if len(grupo) > 1:
            pecas.append({
                "id":        id_peca,
                "rotulo":    rotulo,
                "stls":      arquivos,
                "_caminhos": [caminhos_stl[i] for i in grupo],
                "corPadrao": cor_padrao,
                "paleta":    paleta,
            })
        else:
            pecas.append({
                "id":       id_peca,
                "rotulo":   rotulo,
                "stl":      arquivos[0],
                "_caminho": caminhos_stl[grupo[0]],
                "corPadrao":cor_padrao,
                "paleta":   paleta,
            })
        print(f"  ✔  '{rotulo}' configurada ({len(paleta)} cores)\n")

    return pecas

# ── Opções extras ──────────────────────────────────────────────────────────────
def coletar_opcoes():
    print("── Opções extras ────────────────────────────────────────────────────")
    cor_livre_str = perguntar("Permitir cor personalizada (além da paleta)? [s/n]", "s")
    cor_livre = cor_livre_str.lower() not in ("n", "nao", "não")

    embutido_str = perguntar("Embutir STLs em base64 (arquivo único, sem servidor)? [s/n]", "s")
    embutido = embutido_str.lower() not in ("n", "nao", "não")

    cor_primaria = perguntar("Cor primária da marca (hex)", "#7c3aed")
    if not cor_hex_valida(cor_primaria):
        cor_primaria = "#7c3aed"

    fundo = perguntar("Cor de fundo (hex)", "#ffffff")
    if not cor_hex_valida(fundo):
        fundo = "#ffffff"

    auto_rot_str = perguntar("Auto-rotação inicial? [s/n]", "s")
    auto_rot = auto_rot_str.lower() not in ("n", "nao", "não")

    print("\n── Orientação e zoom do modelo ──────────────────────────────────────")
    print("   Se o modelo aparecer deitado, use rotacaoX=-90 para levantá-lo.")
    try:
        rx = float(perguntar("  Rotação X em graus", "-90"))
    except ValueError:
        rx = -90.0
    try:
        ry = float(perguntar("  Rotação Y em graus", "0"))
    except ValueError:
        ry = 0.0
    try:
        rz = float(perguntar("  Rotação Z em graus", "0"))
    except ValueError:
        rz = 0.0
    try:
        zoom = float(perguntar("  Zoom inicial (2.5 = afastado, 1.5 = padrão)", "2.5"))
    except ValueError:
        zoom = 2.5

    return {
        "cor_livre":   cor_livre,
        "embutido":    embutido,
        "cor_primaria":cor_primaria,
        "fundo":       fundo,
        "auto_rot":    auto_rot,
        "rotacaoX":    rx,
        "rotacaoY":    ry,
        "rotacaoZ":    rz,
        "zoom":        zoom,
    }

# ── Montar CONFIG JS ───────────────────────────────────────────────────────────
def montar_config_js(meta, pecas, opcoes):
    pecas_js = []
    for p in pecas:
        paleta_js = json.dumps(p["paleta"], ensure_ascii=False)
        tem_multi = "stls" in p  # múltiplos STLs para esta peça

        if tem_multi:
            if opcoes["embutido"]:
                refs = [f"__B64_{p['id']}_{i}__" for i in range(len(p["stls"]))]
            else:
                refs = p["stls"]
            stl_campo = f'stls:{json.dumps(refs)}'
        else:
            if opcoes["embutido"]:
                ref = f"__B64_{p['id']}__"
            else:
                ref = p["stl"]
            stl_campo = f'stl:{json.dumps(ref)}'

        pecas_js.append(
            f'    {{ id:{json.dumps(p["id"])}, rotulo:{json.dumps(p["rotulo"])}, '
            f'{stl_campo}, corPadrao:{json.dumps(p["corPadrao"])},\n'
            f'      paleta:{paleta_js} }}'
        )
    pecas_str = ',\n'.join(pecas_js)

    preco_val = json.dumps(meta["preco"]) if meta["preco"] else "null"
    rx   = opcoes.get("rotacaoX", 0)
    ry   = opcoes.get("rotacaoY", 0)
    rz   = opcoes.get("rotacaoZ", 0)
    zoom = opcoes.get("zoom", 1.5)

    config = f"""const CONFIG = {{
  produto: {{ nome: {json.dumps(meta["nome"])}, preco: {preco_val}, descricao: {json.dumps(meta["descricao"])} }},
  whatsappNumber: {json.dumps(meta["numero"])},
  marca: {{ corPrimaria: {json.dumps(opcoes["cor_primaria"])}, fundo: {json.dumps(opcoes["fundo"])} }},
  modelo: {{ autoRotacao: {str(opcoes["auto_rot"]).lower()}, rotacaoX: {rx}, rotacaoY: {ry}, rotacaoZ: {rz}, zoom: {zoom} }},
  pecas: [
{pecas_str},
  ],
  permitirCorLivre: {str(opcoes["cor_livre"]).lower()},
  stlEmbutido: {str(opcoes["embutido"]).lower()},
}};"""
    return config

# ── Gerar produto ──────────────────────────────────────────────────────────────
def gerar_produto(meta, pecas, opcoes):
    slug      = meta["slug"]
    destino   = os.path.join(CATALOGO_DIR, slug)
    os.makedirs(destino, exist_ok=True)

    # Ler template
    if not os.path.isfile(TEMPLATE):
        print(f"\n❌  Template não encontrado: {TEMPLATE}")
        sys.exit(1)
    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        html = f.read()

    # Montar bloco CONFIG
    config_js = montar_config_js(meta, pecas, opcoes)

    # Substituir placeholder
    placeholder_inicio = '<!--__CONFIG__-->'
    placeholder_fim    = '<!--/__CONFIG__-->'
    if placeholder_inicio not in html:
        print("\n❌  Placeholder <!--__CONFIG__--> não encontrado no template.")
        sys.exit(1)

    ini = html.index(placeholder_inicio)
    fim = html.index(placeholder_fim) + len(placeholder_fim)
    bloco_config = f"{placeholder_inicio}\n<script>\n{config_js}\n</script>\n{placeholder_fim}"
    html = html[:ini] + bloco_config + html[fim:]

    if opcoes["embutido"]:
        for p in pecas:
            if "_caminhos" in p:
                # múltiplos STLs por peça
                for i, caminho in enumerate(p["_caminhos"]):
                    data_url = stl_para_data_url(caminho)
                    html = html.replace(f'"__B64_{p["id"]}_{i}__"', f'"{data_url}"')
            else:
                data_url = stl_para_data_url(p["_caminho"])
                html = html.replace(f'"__B64_{p["id"]}__"', f'"{data_url}"')
    else:
        for p in pecas:
            if "_caminhos" in p:
                for caminho, nome_stl in zip(p["_caminhos"], p["stls"]):
                    dst = os.path.join(destino, nome_stl)
                    shutil.copy2(caminho, dst)
                    print(f"  → Copiado: {nome_stl}")
            else:
                dst = os.path.join(destino, p["stl"])
                shutil.copy2(p["_caminho"], dst)
                print(f"  → Copiado: {p['stl']}")

    # Gravar index.html
    saida = os.path.join(destino, "index.html")
    with open(saida, 'w', encoding='utf-8') as f:
        f.write(html)

    return saida, slug

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    limpar_tela()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Gerador de Produtos — Configurador 3D para WhatsApp ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    caminhos = selecionar_stls()
    meta     = coletar_metadados(caminhos)
    pecas    = configurar_pecas(caminhos)
    opcoes   = coletar_opcoes()

    print("\n── Gerando produto ──────────────────────────────────────────────────")
    saida, slug = gerar_produto(meta, pecas, opcoes)

    print(f"\n✅  Produto gerado com sucesso!")
    print(f"   Arquivo: {saida}")
    print(f"   Tamanho: {os.path.getsize(saida) / 1024:.1f} KB")
    print(f"\n── Como testar localmente ───────────────────────────────────────────")
    pasta_produto = os.path.dirname(saida)
    print(f"   cd \"{pasta_produto}\"")
    print(f"   python3 -m http.server 8080")
    print(f"   Abra: http://localhost:8080")

    try:
        ip_local = None
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        print(f"   No celular (mesma rede Wi-Fi): http://{ip_local}:8080")
    except Exception:
        pass

    print(f"\n── URL pública prevista (GitHub Pages) ──────────────────────────────")
    print(f"   https://<usuario>.github.io/<repo>/catalogo/{slug}/")
    print(f"\n   Execute publicar.py para fazer o deploy.\n")

if __name__ == "__main__":
    main()
