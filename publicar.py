#!/usr/bin/env python3
"""
Publica um produto no GitHub Pages.
Uso: python3 publicar.py [slug]
"""
import os, sys, subprocess, re, socket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOGO = os.path.join(BASE_DIR, "catalogo")

def run(cmd, cwd=None, capturar=False):
    resultado = subprocess.run(
        cmd, shell=True, cwd=cwd or BASE_DIR,
        capture_output=capturar, text=True
    )
    if resultado.returncode != 0:
        if capturar:
            print(resultado.stderr.strip())
        return False, resultado.stdout.strip() if capturar else ""
    return True, resultado.stdout.strip() if capturar else ""

def verificar_git():
    ok, _ = run("git rev-parse --is-inside-work-tree", capturar=True)
    return ok

def listar_produtos():
    if not os.path.isdir(CATALOGO):
        return []
    return [d for d in os.listdir(CATALOGO)
            if os.path.isdir(os.path.join(CATALOGO, d))
            and os.path.isfile(os.path.join(CATALOGO, d, "index.html"))]

def obter_remote():
    ok, url = run("git remote get-url origin", capturar=True)
    if not ok:
        return None
    m = re.search(r'github\.com[:/](.+?)(?:\.git)?$', url)
    return m.group(1) if m else None

def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Publicar produto no GitHub Pages                    ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    if not verificar_git():
        print("❌  Este diretório não é um repositório Git.")
        print("   Execute: git init && git remote add origin <URL>")
        sys.exit(1)

    produtos = listar_produtos()
    if not produtos:
        print("❌  Nenhum produto encontrado em catalogo/")
        print("   Execute gerador.py primeiro.")
        sys.exit(1)

    # Slug por argumento ou seleção interativa
    if len(sys.argv) > 1:
        slug = sys.argv[1]
    else:
        print("Produtos disponíveis:")
        for i, p in enumerate(produtos, 1):
            print(f"  {i} – {p}")
        escolha = input("\nNúmero do produto para publicar: ").strip()
        try:
            slug = produtos[int(escolha) - 1]
        except (ValueError, IndexError):
            print("❌  Seleção inválida.")
            sys.exit(1)

    pasta_produto = os.path.join(CATALOGO, slug)
    if not os.path.isdir(pasta_produto):
        print(f"❌  Produto não encontrado: {pasta_produto}")
        sys.exit(1)

    remote = obter_remote()
    if remote:
        usuario, repo = remote.split('/', 1) if '/' in remote else (remote, "")
        url_publica = f"https://{usuario}.github.io/{repo}/catalogo/{slug}/"
    else:
        url_publica = f"https://<usuario>.github.io/<repo>/catalogo/{slug}/"

    print(f"\nProduto  : {slug}")
    print(f"Pasta    : {pasta_produto}")
    print(f"URL prev.: {url_publica}")

    if remote is None:
        print("\n⚠  Nenhum remote 'origin' configurado.")
        print("   Configure com: git remote add origin <URL do repositório GitHub>")
        resp = input("Continuar mesmo assim? [s/N]: ").strip().lower()
        if resp != 's':
            sys.exit(0)

    print(f"\nAção: git add + commit + push do produto '{slug}'.")
    confirmar = input("Confirmar publicação? [s/N]: ").strip().lower()
    if confirmar != 's':
        print("Cancelado.")
        sys.exit(0)

    # Verificar se há algo para commitar
    caminho_rel = os.path.relpath(pasta_produto, BASE_DIR)
    ok, status = run(f'git status --porcelain "{caminho_rel}"', capturar=True)
    if ok and not status:
        print(f"\n✔  Produto '{slug}' já está sincronizado. Nada para commitar.")
    else:
        print(f"\n→ Adicionando arquivos de '{caminho_rel}'…")
        ok, _ = run(f'git add "{caminho_rel}"')
        if not ok:
            print("❌  Falha no git add.")
            sys.exit(1)

        msg = f"produto: publicar {slug}"
        ok, _ = run(f'git commit -m "{msg}"')
        if not ok:
            print("❌  Falha no git commit.")
            sys.exit(1)
        print("✔  Commit criado.")

    if remote:
        print("→ Fazendo push para origin…")
        ok, _ = run("git push origin HEAD")
        if not ok:
            print("❌  Falha no git push. Verifique sua autenticação e tente novamente.")
            sys.exit(1)
        print("✔  Push concluído.")
    else:
        print("⚠  Sem remote configurado — push ignorado.")

    print(f"\n✅  Pronto! Aguarde ~1 minuto e acesse:")
    print(f"   {url_publica}")
    print(f"\n   Cole esse link no catálogo do WhatsApp Business.\n")

if __name__ == "__main__":
    main()
