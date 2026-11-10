import pygame
import math
import random
import sys

# ============================================================
# JUEGO: NAVE ESPACIAL - GALAXIA
# Controles:
#   W / Flecha arriba: avanzar
#   S / Flecha abajo: retroceder
#   A-D / Flechas izquierda-derecha: girar
#   ESPACIO: disparar
#   C: comprar/cambiar rastro de fuego (5 puntos)
# ============================================================

pygame.init()

ANCHO, ALTO = 1000, 700
FPS = 60
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.DOUBLEBUF)
pygame.display.set_caption("Galaxia Vectorial - Supervivencia Espacial")
reloj = pygame.time.Clock()

# Colores
BLANCO = (240, 245, 255)
CIAN = (80, 225, 255)
ROJO = (255, 45, 65)
AMARILLO = (255, 210, 80)
GRIS = (145, 155, 180)
OSCURO = (5, 7, 22)
VERDE = (100, 255, 170)

fuente = pygame.font.Font(None, 28)
fuente_chica = pygame.font.Font(None, 21)
fuente_titulo = pygame.font.Font(None, 92)
fuente_boton = pygame.font.Font(None, 30)

# ------------------------------------------------------------
# FONDO ESPACIAL: estrellas, nebulosas y planetas
# ------------------------------------------------------------
estrellas = []
for _ in range(220):
    estrellas.append({
        "x": random.randrange(ANCHO),
        "y": random.randrange(ALTO),
        "radio": random.choice([1, 1, 1, 2]),
        "brillo": random.randint(90, 255),
        "fase": random.random() * math.tau
    })

# Planetas decorativos con anillos opcionales
planetas = [
    {"x": 150, "y": 150, "r": 42, "color": (90, 95, 180), "anillo": True},
    {"x": 850, "y": 120, "r": 26, "color": (190, 100, 75), "anillo": False},
    {"x": 800, "y": 560, "r": 52, "color": (45, 130, 160), "anillo": True},
]
# Nebulosas dibujadas como manchas translúcidas
nebulosa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
for _ in range(18):
    nx, ny = random.randint(0, ANCHO), random.randint(0, ALTO)
    nr = random.randint(45, 130)
    color = random.choice([
        (65, 25, 110, 15), (20, 65, 130, 18),
        (100, 25, 80, 13), (15, 100, 120, 12)
    ])
    pygame.draw.circle(nebulosa, color, (nx, ny), nr)


def dibujar_fondo(tiempo):
    pantalla.fill(OSCURO)
    pantalla.blit(nebulosa, (0, 0))

    # Galaxia espiral estilizada al fondo
    centro_x, centro_y = 500, 355
    for brazo in range(3):
        for i in range(48):
            t = i / 48
            radio = 18 + t * 180
            ang = tiempo * 0.025 + brazo * (math.tau / 3) + t * 4.2
            gx = int(centro_x + math.cos(ang) * radio)
            gy = int(centro_y + math.sin(ang) * radio * 0.48)
            tam = max(1, int(3 * (1 - t)))
            brillo = int(60 + 100 * (1 - t))
            color = (brillo, int(brillo * 0.65), min(255, brillo + 35))
            pygame.draw.circle(pantalla, color, (gx, gy), tam)

    # Estrellas titilantes
    for e in estrellas:
        brillo = int(e["brillo"] * (0.72 + 0.28 * math.sin(tiempo * 0.003 + e["fase"])))
        pygame.draw.circle(pantalla, (brillo, brillo, min(255, brillo + 12)),
                        (e["x"], e["y"]), e["radio"])

    # Planetas
    for p in planetas:
        pygame.draw.circle(pantalla, p["color"], (p["x"], p["y"]), p["r"])
        pygame.draw.circle(pantalla, tuple(min(255, c + 45) for c in p["color"]),
                           (p["x"] - p["r"] // 3, p["y"] - p["r"] // 3),
                           max(3, p["r"] // 3))
        if p["anillo"]:
            rect = pygame.Rect(p["x"] - p["r"] - 13, p["y"] - 8,
                               (p["r"] + 13) * 2, 16)
            pygame.draw.ellipse(pantalla, (165, 175, 220), rect, 2)


# ------------------------------------------------------------
# FUNCIONES GEOMETRICAS Y PANTALLA ENVOLVENTE
# ------------------------------------------------------------
def transformar_vertice(vertice, x, y, angulo_grados):
    vx, vy = vertice
    rad = math.radians(angulo_grados)
    x_rotado = vx * math.cos(rad) - vy * math.sin(rad)
    y_rotado = vx * math.sin(rad) + vy * math.cos(rad)
    return (x + x_rotado, y + y_rotado)


def envolver(objeto):
    objeto["x"] %= ANCHO
    objeto["y"] %= ALTO


# Nave con silueta de cohete/avión espacial
MODELO_NAVE = [
    (0, -27), (-8, -12), (-20, 7), (-18, 16),
    (-8, 12), (0, 19), (8, 12), (18, 16),
    (20, 7), (8, -12)
]
ALAS_NAVE = [(-13, 5), (-30, 18), (-17, 17)]
ALAS_NAVE_DER = [(13, 5), (30, 18), (17, 17)]


def dibujar_nave(x, y, angulo, tiempo, color_trail, invulnerable=False):
    # Rastro de fuego tras la nave; aparece cuando se mueve
    rad = math.radians(angulo)
    atras_x = -math.sin(rad)
    atras_y = math.cos(rad)
    largo = random.randint(13, 24)
    fuego_x = x + atras_x * 18
    fuego_y = y + atras_y * 18
    punta_fuego = (fuego_x + atras_x * largo, fuego_y + atras_y * largo)
    lado = 5
    perp_x, perp_y = math.cos(rad), math.sin(rad)
    fuego = [
        (fuego_x + perp_x * lado, fuego_y + perp_y * lado),
        punta_fuego,
        (fuego_x - perp_x * lado, fuego_y - perp_y * lado)
    ]
    if random.random() < 0.9:
        pygame.draw.polygon(pantalla, color_trail, fuego)
        nucleo = [
            (fuego_x + perp_x * 2, fuego_y + perp_y * 2),
            (fuego_x + atras_x * (largo * 0.7), fuego_y + atras_y * (largo * 0.7)),
            (fuego_x - perp_x * 2, fuego_y - perp_y * 2)
        ]
        pygame.draw.polygon(pantalla, (255, 245, 190), nucleo)

    # Si esta en invulnerabilidad, parpadea
    if invulnerable and int(tiempo / 100) % 2 == 0:
        return

    vertices = [transformar_vertice(v, x, y, angulo) for v in MODELO_NAVE]
    ala_izq = [transformar_vertice(v, x, y, angulo) for v in ALAS_NAVE]
    ala_der = [transformar_vertice(v, x, y, angulo) for v in ALAS_NAVE_DER]

    pygame.draw.polygon(pantalla, (65, 105, 160), ala_izq)
    pygame.draw.polygon(pantalla, (65, 105, 160), ala_der)
    pygame.draw.polygon(pantalla, (165, 205, 235), vertices)
    pygame.draw.polygon(pantalla, (55, 95, 135), vertices, 2)

    # Cabina y detalles metalicos
    cabina = [(-5, -11), (0, -19), (5, -11), (3, -3), (-3, -3)]
    pygame.draw.polygon(pantalla, (30, 210, 245),
                        [transformar_vertice(v, x, y, angulo) for v in cabina])
    linea = [(-9, 5), (0, 10), (9, 5)]
    pygame.draw.lines(pantalla, (35, 55, 90), False,
                    [transformar_vertice(v, x, y, angulo) for v in linea], 2)


def crear_explosion(x, y, grande=False):
    particulas = []
    cantidad = 34 if grande else 20
    for _ in range(cantidad):
        a = random.random() * math.tau
        velocidad = random.uniform(45, 220 if grande else 150)
        particulas.append({
            "x": x, "y": y,
            "vx": math.cos(a) * velocidad,
            "vy": math.sin(a) * velocidad,
            "vida": random.uniform(0.35, 0.85),
            "vida_total": 0.85,
            "radio": random.randint(2, 5),
            "color": random.choice([AMARILLO, (255, 120, 35), ROJO, (255, 245, 200)])
        })
    return particulas


def dibujar_explosion(particulas, dt):
    for p in particulas[:]:
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        p["vida"] -= dt
        p["vx"] *= 0.985
        p["vy"] *= 0.985
        if p["vida"] <= 0:
            particulas.remove(p)
        else:
            radio = max(1, int(p["radio"] * p["vida"] / p["vida_total"]))
            pygame.draw.circle(pantalla, p["color"], (int(p["x"]), int(p["y"])), radio)


# ------------------------------------------------------------
# OBJETOS DEL JUEGO
# ------------------------------------------------------------
def crear_meteorito():
    borde = random.choice(["arriba", "abajo", "izquierda", "derecha"])
    if borde == "arriba":
        x, y = random.randrange(ANCHO), -25
    elif borde == "abajo":
        x, y = random.randrange(ANCHO), ALTO + 25
    elif borde == "izquierda":
        x, y = -25, random.randrange(ALTO)
    else:
        x, y = ANCHO + 25, random.randrange(ALTO)
    return {
        "tipo": "meteorito", "x": float(x), "y": float(y),
        "vx": random.uniform(-65, 65), "vy": random.uniform(-65, 65),
        "radio": random.randint(14, 25), "vida": 1,
        "angulo": random.randrange(360), "giro": random.uniform(-70, 70)
    }


def crear_nave_enemiga():
    borde = random.choice(["arriba", "abajo", "izquierda", "derecha"])
    if borde == "arriba":
        x, y = random.randrange(ANCHO), -30
    elif borde == "abajo":
        x, y = random.randrange(ANCHO), ALTO + 30
    elif borde == "izquierda":
        x, y = -30, random.randrange(ALTO)
    else:
        x, y = ANCHO + 30, random.randrange(ALTO)
    return {
        "tipo": "enemigo", "x": float(x), "y": float(y),
        "vx": random.uniform(-55, 55), "vy": random.uniform(-55, 55),
        "radio": 19, "vida": 1, "angulo": 0
    }


def dibujar_meteorito(m):
    x, y, r = int(m["x"]), int(m["y"]), m["radio"]
    puntos = []
    for i in range(10):
        a = math.tau * i / 10
        rr = r * (random.uniform(0.78, 1.12))
        puntos.append((int(x + math.cos(a) * rr), int(y + math.sin(a) * rr)))
    pygame.draw.polygon(pantalla, (115, 91, 83), puntos)
    pygame.draw.polygon(pantalla, (180, 135, 100), puntos, 2)
    pygame.draw.circle(pantalla, (75, 68, 75), (x - r // 4, y - r // 5), max(2, r // 5))
    pygame.draw.circle(pantalla, (70, 60, 65), (x + r // 3, y + r // 4), max(2, r // 6))


def dibujar_enemigo(e):
    x, y = int(e["x"]), int(e["y"])
    puntos = [(x, y - 21), (x + 24, y), (x + 10, y + 7),
            (x + 6, y + 15), (x - 6, y + 15), (x - 10, y + 7),
            (x - 24, y)]
    pygame.draw.polygon(pantalla, (160, 55, 85), puntos)
    pygame.draw.polygon(pantalla, (255, 110, 140), puntos, 2)
    pygame.draw.ellipse(pantalla, (90, 220, 255), (x - 7, y - 7, 14, 9))
    pygame.draw.circle(pantalla, (255, 120, 65), (x, y + 15), 4)


def dibujar_texto(texto, fuente_usada, color, x, y, centro=False):
    superficie = fuente_usada.render(texto, True, color)
    rect = superficie.get_rect()
    if centro:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    pantalla.blit(superficie, rect)
    return rect


def boton(rect, texto, habilitado=True, color=None):
    color_fondo = color if color else ((35, 55, 85) if habilitado else (55, 58, 68))
    color_texto = BLANCO if habilitado else (135, 140, 150)
    pygame.draw.rect(pantalla, color_fondo, rect, border_radius=12)
    pygame.draw.rect(pantalla, (100, 190, 225) if habilitado else (90, 95, 105),
                    rect, 2, border_radius=12)
    dibujar_texto(texto, fuente_boton, color_texto, rect.centerx, rect.centery, True)


# ------------------------------------------------------------
# ESTADO Y REINICIO
# ------------------------------------------------------------
def reiniciar_juego():
    return {
        "x": ANCHO / 2, "y": ALTO / 2, "angulo": 0.0,
        "vx": 0.0, "vy": 0.0, "puntos": 0,
        "proyectiles": [], "objetos": [], "explosiones": [],
        "ultimo_disparo": -500, "ultimo_meteorito": 0,
        "ultimo_enemigo": 0, "invulnerable_hasta": 0,
        "trail_indice": 0, "estado": "jugando"
    }


colores_rastro = [
    (255, 130, 35),   # fuego naranja
    (70, 220, 255),   # fuego azul
    (190, 100, 255),  # fuego violeta
    (100, 255, 150),  # fuego verde
    (255, 70, 130)    # fuego rosa
]
nombres_rastro = ["Naranja", "Azul", "Violeta", "Verde", "Rosa"]
COSTO_RASTRO = 5
COSTO_CONTINUAR = 10

juego = reiniciar_juego()
tiempo_inicio = pygame.time.get_ticks()

# Botones de la pantalla de derrota
boton_reintentar = pygame.Rect(ANCHO // 2 - 190, 410, 170, 54)
boton_menu = pygame.Rect(ANCHO // 2 + 20, 410, 150, 54)
boton_continuar = pygame.Rect(ANCHO // 2 - 105, 485, 210, 54)
boton_menu_principal = pygame.Rect(ANCHO // 2 - 100, 430, 200, 55)

ejecutando = True
while ejecutando:
    dt = min(reloj.tick(FPS) / 1000.0, 0.04)
    ahora = pygame.time.get_ticks()
    tiempo = ahora - tiempo_inicio
    dibujar_fondo(ahora)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.KEYDOWN:
            if juego["estado"] == "jugando":
                if evento.key == pygame.K_SPACE:
                    if ahora - juego["ultimo_disparo"] >= 250:
                        rad = math.radians(juego["angulo"])
                        # La punta local es (0, -27); se transforma a pantalla
                        punta = transformar_vertice((0, -27), juego["x"], juego["y"], juego["angulo"])
                        juego["proyectiles"].append({
                            "x": punta[0], "y": punta[1],
                            "vx": math.sin(rad) * 470,
                            "vy": -math.cos(rad) * 470,
                            "vida": 2.2
                        })
                        juego["ultimo_disparo"] = ahora

                # Comprar/cambiar el rastro de fuego por 5 puntos
                if evento.key == pygame.K_c:
                    if juego["puntos"] >= COSTO_RASTRO:
                        juego["puntos"] -= COSTO_RASTRO
                        juego["trail_indice"] = (juego["trail_indice"] + 1) % len(colores_rastro)

            elif juego["estado"] == "perdiste":
                if evento.key == pygame.K_RETURN:
                    juego = reiniciar_juego()

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            mx, my = evento.pos
            if juego["estado"] == "perdiste":
                if boton_reintentar.collidepoint(mx, my):
                    juego = reiniciar_juego()
                elif boton_menu.collidepoint(mx, my):
                    juego["estado"] = "menu"
                elif boton_continuar.collidepoint(mx, my) and juego["puntos"] >= COSTO_CONTINUAR:
                    juego["puntos"] -= COSTO_CONTINUAR
                    juego["x"], juego["y"] = ANCHO / 2, ALTO / 2
                    juego["vx"], juego["vy"] = 0.0, 0.0
                    juego["angulo"] = 0.0
                    juego["objetos"].clear()
                    juego["proyectiles"].clear()
                    juego["invulnerable_hasta"] = ahora + 3000
                    juego["estado"] = "jugando"
            elif juego["estado"] == "menu":
                if boton_menu_principal.collidepoint(mx, my):
                    juego = reiniciar_juego()

    # --------------------------------------------------------
    # JUGANDO
    # --------------------------------------------------------
    if juego["estado"] == "jugando":
        teclas = pygame.key.get_pressed()

        # Rotacion suave en grados por segundo
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            juego["angulo"] -= 190 * dt
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            juego["angulo"] += 190 * dt

        # Avanzar y retroceder en la direccion a la que apunta la nave
        rad = math.radians(juego["angulo"])
        aceleracion = 230
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            juego["vx"] += math.sin(rad) * aceleracion * dt
            juego["vy"] -= math.cos(rad) * aceleracion * dt
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            juego["vx"] -= math.sin(rad) * aceleracion * dt
            juego["vy"] += math.cos(rad) * aceleracion * dt

        # Friccion espacial y limite de velocidad
        juego["vx"] *= 0.992
        juego["vy"] *= 0.992
        rapidez = math.hypot(juego["vx"], juego["vy"])
        max_rapidez = 260
        if rapidez > max_rapidez:
            juego["vx"] = juego["vx"] / rapidez * max_rapidez
            juego["vy"] = juego["vy"] / rapidez * max_rapidez

        juego["x"] += juego["vx"] * dt
        juego["y"] += juego["vy"] * dt

        # Pantalla envolvente por los cuatro bordes
        juego["x"] %= ANCHO
        juego["y"] %= ALTO

        # Generar meteoritos y enemigos con intervalos
        if ahora - juego["ultimo_meteorito"] > 1050:
            juego["objetos"].append(crear_meteorito())
            juego["ultimo_meteorito"] = ahora
        if ahora - juego["ultimo_enemigo"] > 3200:
            juego["objetos"].append(crear_nave_enemiga())
            juego["ultimo_enemigo"] = ahora

        # Actualizar proyectiles y eliminarlos al salir o caducar
        for p in juego["proyectiles"][:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vida"] -= dt
            if (p["vida"] <= 0 or p["x"] < 0 or p["x"] >= ANCHO
                    or p["y"] < 0 or p["y"] >= ALTO):
                juego["proyectiles"].remove(p)
            else:
                pygame.draw.circle(pantalla, AMARILLO, (int(p["x"]), int(p["y"])), 4)
                pygame.draw.circle(pantalla, (255, 250, 205), (int(p["x"]), int(p["y"])), 2)

        # Mover objetos enemigos
        for objeto in juego["objetos"][:]:
            objeto["x"] += objeto["vx"] * dt
            objeto["y"] += objeto["vy"] * dt
            objeto["angulo"] += objeto.get("giro", 0) * dt

            # Los objetos también envuelven la pantalla para que sigan siendo amenazas
            objeto["x"] %= ANCHO
            objeto["y"] %= ALTO

            if objeto["tipo"] == "meteorito":
                dibujar_meteorito(objeto)
            else:
                # Enemigos se orientan aproximadamente hacia el jugador
                objeto["angulo"] = math.degrees(math.atan2(
                    juego["y"] - objeto["y"], juego["x"] - objeto["x"]
                )) + 90
                dibujar_enemigo(objeto)

            # Impactos entre proyectiles y objetos
            impacto = False
            for p in juego["proyectiles"][:]:
                distancia = math.hypot(objeto["x"] - p["x"], objeto["y"] - p["y"])
                if distancia < objeto["radio"] + 5:
                    if p in juego["proyectiles"]:
                        juego["proyectiles"].remove(p)
                    impacto = True
                    break

            if impacto:
                juego["explosiones"].extend(crear_explosion(objeto["x"], objeto["y"]))
                if objeto["tipo"] == "meteorito":
                    juego["puntos"] += 1
                else:
                    juego["puntos"] += random.randint(2, 5)
                juego["objetos"].remove(objeto)
                continue

            # Colision con la nave: derrota, excepto durante invulnerabilidad
            distancia_nave = math.hypot(objeto["x"] - juego["x"], objeto["y"] - juego["y"])
            if distancia_nave < objeto["radio"] + 17 and ahora >= juego["invulnerable_hasta"]:
                juego["explosiones"].extend(crear_explosion(juego["x"], juego["y"], grande=True))
                juego["estado"] = "perdiste"
                break

        dibujar_explosion(juego["explosiones"], dt)

        # Dibujar la nave y su rastro de fuego
        dibujar_nave(
            juego["x"], juego["y"], juego["angulo"], ahora,
            colores_rastro[juego["trail_indice"]],
            ahora < juego["invulnerable_hasta"]
        )

        # Interfaz del juego
        pygame.draw.rect(pantalla, (5, 8, 25, 210), (10, 10, 430, 96), border_radius=10)
        dibujar_texto(f"PUNTOS: {juego['puntos']}", fuente, AMARILLO, 22, 18)
        dibujar_texto("W/↑ avanzar | S/↓ retroceder | A-D girar | ESPACIO disparar",
                    fuente_chica, BLANCO, 22, 47)
        dibujar_texto(f"C: cambiar rastro ({COSTO_RASTRO} pts) | Rastro: {nombres_rastro[juego['trail_indice']]}",
                    fuente_chica, colores_rastro[juego["trail_indice"]], 22, 72)

    # --------------------------------------------------------
    # PANTALLA DE DERROTA
    # --------------------------------------------------------
    elif juego["estado"] == "perdiste":
        # Continuar animando las explosiones aunque la partida haya terminado
        dibujar_explosion(juego["explosiones"], dt)

        velo = 1 + 0.06 * math.sin(ahora * 0.009)
        titulo = fuente_titulo.render("YOU LOST", True, ROJO)
        titulo = pygame.transform.rotozoom(titulo, 0, velo)
        titulo_rect = titulo.get_rect(center=(ANCHO // 2, 285 + math.sin(ahora * 0.006) * 8))
        pantalla.blit(titulo, titulo_rect)

        dibujar_texto(f"Puntos obtenidos: {juego['puntos']}", fuente, AMARILLO,
                      ANCHO // 2, 350, True)

        # Icono de reintentar con flecha curva aproximada
        boton(boton_reintentar, "↻  Reintentar")
        boton(boton_menu, "Menu")
        habilitado = juego["puntos"] >= COSTO_CONTINUAR
        boton(boton_continuar, "Continuar (10 pts)", habilitado)

        if not habilitado:
            dibujar_texto("Necesitas 10 puntos para continuar", fuente_chica, GRIS,
                          ANCHO // 2, 555, True)
        else:
            dibujar_texto("Gasta 10 puntos para volver con proteccion temporal",
                          fuente_chica, VERDE, ANCHO // 2, 555, True)

    # --------------------------------------------------------
    # MENU SENCILLO (SE PUEDE AMPLIAR DESPUES)
    # --------------------------------------------------------
    elif juego["estado"] == "menu":
        titulo = fuente_titulo.render("GALAXIA VECTORIAL", True, CIAN)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 280)))
        dibujar_texto("Menu provisional: vuelve al juego con una partida nueva.",
                      fuente, BLANCO, ANCHO // 2, 355, True)
        boton(boton_menu_principal, "Nueva partida")
        dibujar_texto("W/S mover | A/D girar | Espacio disparar | C cambiar rastro",
                      fuente_chica, GRIS, ANCHO // 2, 510, True)

    pygame.display.flip()

pygame.quit()
sys.exit()
