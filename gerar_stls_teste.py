"""Gera 3 STLs simples (cubo, esfera aproximada, cilindro) para testes."""
import struct, math, os

def escrever_stl_binario(caminho, triangulos):
    with open(caminho, "wb") as f:
        f.write(b"\x00" * 80)
        f.write(struct.pack("<I", len(triangulos)))
        for normal, v0, v1, v2 in triangulos:
            f.write(struct.pack("<3f", *normal))
            f.write(struct.pack("<3f", *v0))
            f.write(struct.pack("<3f", *v1))
            f.write(struct.pack("<3f", *v2))
            f.write(struct.pack("<H", 0))

def cubo(s=1.0):
    h = s / 2
    faces = [
        # frente  normal  (0,0,1)
        ([0,0,1],[[-h,-h,h],[h,-h,h],[h,h,h]]),
        ([0,0,1],[[-h,-h,h],[h,h,h],[-h,h,h]]),
        # trás   (0,0,-1)
        ([0,0,-1],[[h,-h,-h],[-h,-h,-h],[-h,h,-h]]),
        ([0,0,-1],[[h,-h,-h],[-h,h,-h],[h,h,-h]]),
        # direita (1,0,0)
        ([1,0,0],[[h,-h,h],[h,-h,-h],[h,h,-h]]),
        ([1,0,0],[[h,-h,h],[h,h,-h],[h,h,h]]),
        # esquerda(-1,0,0)
        ([-1,0,0],[[-h,-h,-h],[-h,-h,h],[-h,h,h]]),
        ([-1,0,0],[[-h,-h,-h],[-h,h,h],[-h,h,-h]]),
        # topo   (0,1,0)
        ([0,1,0],[[-h,h,h],[h,h,h],[h,h,-h]]),
        ([0,1,0],[[-h,h,h],[h,h,-h],[-h,h,-h]]),
        # base   (0,-1,0)
        ([0,-1,0],[[-h,-h,-h],[h,-h,-h],[h,-h,h]]),
        ([0,-1,0],[[-h,-h,-h],[h,-h,h],[-h,-h,h]]),
    ]
    return [(n, v[0], v[1], v[2]) for n, v in faces]

def esfera(r=0.6, lat=12, lon=16):
    tris = []
    def v(la, lo):
        la_r = math.radians(la); lo_r = math.radians(lo)
        x = r * math.cos(la_r) * math.cos(lo_r)
        y = r * math.sin(la_r)
        z = r * math.cos(la_r) * math.sin(lo_r)
        return [x, y, z]
    def norm(pt):
        mag = math.sqrt(sum(c**2 for c in pt))
        return [c / mag for c in pt]
    for i in range(lat):
        for j in range(lon):
            la0 = -90 + i * 180 / lat; la1 = -90 + (i+1) * 180 / lat
            lo0 = j * 360 / lon;       lo1 = (j+1) * 360 / lon
            p00 = v(la0, lo0); p10 = v(la1, lo0)
            p01 = v(la0, lo1); p11 = v(la1, lo1)
            if i > 0:
                n = norm([(p00[k]+p10[k]+p01[k])/3 for k in range(3)])
                tris.append((n, p00, p10, p01))
            if i < lat - 1:
                n = norm([(p10[k]+p11[k]+p01[k])/3 for k in range(3)])
                tris.append((n, p10, p11, p01))
    return tris

def cilindro(r=0.4, h=1.2, segs=20):
    tris = []
    def anel(y, nr):
        pts = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            pts.append([r * math.cos(a), y, r * math.sin(a)])
        return pts, [0, nr, 0]
    bot, _ = anel(-h/2, -1); top, _ = anel(h/2, 1)
    centro_bot = [0, -h/2, 0]; centro_top = [0, h/2, 0]
    for i in range(segs):
        j = (i + 1) % segs
        # lateral
        p0 = bot[i]; p1 = bot[j]; p2 = top[i]; p3 = top[j]
        n01 = [(p0[0]+p1[0])/2, 0, (p0[2]+p1[2])/2]
        mag = math.sqrt(n01[0]**2 + n01[2]**2) or 1
        n01 = [n01[0]/mag, 0, n01[2]/mag]
        tris.append((n01, p0, p1, p2))
        tris.append((n01, p1, p3, p2))
        # tampa inferior
        tris.append(([0,-1,0], centro_bot, bot[j], bot[i]))
        # tampa superior
        tris.append(([0,1,0], centro_top, top[i], top[j]))
    return tris

pasta = os.path.join(os.path.dirname(__file__), "stls_teste")
os.makedirs(pasta, exist_ok=True)

escrever_stl_binario(os.path.join(pasta, "corpo.stl"),  cubo(1.0))
escrever_stl_binario(os.path.join(pasta, "chifre.stl"), esfera(0.6))
escrever_stl_binario(os.path.join(pasta, "olhos.stl"),  cilindro(0.4, 1.2))

print("STLs de teste gerados em:", pasta)
for nome in ["corpo.stl", "chifre.stl", "olhos.stl"]:
    tam = os.path.getsize(os.path.join(pasta, nome))
    print(f"  {nome}: {tam} bytes")
