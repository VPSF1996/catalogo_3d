"""Gera o produto rinoceronte com os STLs reais (corpo, chifre, olhos)."""
import os, sys

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
STL_DIR   = os.path.join(BASE_DIR, "catalogo", "rinoceronte")
sys.path.insert(0, BASE_DIR)
from gerador import gerar_produto

meta = {
    "nome":     "Rinoceronte",
    "slug":     "rinoceronte",
    "preco":    None,
    "descricao":"Personalize as cores e finalize pelo WhatsApp.",
    "numero":   "5555991224041",
}

pecas = [
    {
        "id":       "corpo",
        "rotulo":   "Corpo",
        "stl":      "Rhino body.stl",
        "_caminho": os.path.join(STL_DIR, "Rhino body.stl"),
        "corPadrao":"#7c3aed",
        "paleta": [
            {"nome":"Roxo",     "hex":"#7c3aed"},
            {"nome":"Azul",     "hex":"#2563eb"},
            {"nome":"Verde",    "hex":"#16a34a"},
            {"nome":"Vermelho", "hex":"#dc2626"},
            {"nome":"Preto",    "hex":"#111111"},
            {"nome":"Branco",   "hex":"#f5f5f5"},
        ],
    },
    {
        "id":       "chifre",
        "rotulo":   "Chifre",
        "stl":      "Rhino honr.stl",
        "_caminho": os.path.join(STL_DIR, "Rhino honr.stl"),
        "corPadrao":"#9ca3af",
        "paleta": [
            {"nome":"Cinza",   "hex":"#9ca3af"},
            {"nome":"Branco",  "hex":"#f5f5f5"},
            {"nome":"Preto",   "hex":"#111111"},
            {"nome":"Dourado", "hex":"#d4af37"},
            {"nome":"Marrom",  "hex":"#7c4a1e"},
        ],
    },
    {
        "id":       "olhos",
        "rotulo":   "Olhos",
        "stls":     ["Rhino eye1.stl", "Rhino eye2.stl"],
        "_caminhos":[
            os.path.join(STL_DIR, "Rhino eye1.stl"),
            os.path.join(STL_DIR, "Rhino eye2.stl"),
        ],
        "corPadrao":"#111111",
        "paleta": [
            {"nome":"Preto",  "hex":"#111111"},
            {"nome":"Marrom", "hex":"#7c4a1e"},
            {"nome":"Azul",   "hex":"#2563eb"},
            {"nome":"Verde",  "hex":"#16a34a"},
        ],
    },
]

opcoes = {
    "cor_livre":    True,
    "embutido":     True,
    "cor_primaria": "#7c3aed",
    "fundo":        "#ffffff",
    "auto_rot":     True,
    "rotacaoX":     -90,
    "rotacaoY":     0,
    "rotacaoZ":     0,
    "zoom":         2.5,    # afasta a câmera para o modelo caber melhor
}

saida, slug = gerar_produto(meta, pecas, opcoes)
tam_mb = os.path.getsize(saida) / (1024 * 1024)
print(f"✅  Gerado: {saida}  ({tam_mb:.1f} MB)")
