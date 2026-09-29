# Contexto para Claude: cartas de Hitster personalizadas

> Resumen de la sesión del 28/09/2026 (laptop), para continuar en la PC de escritorio.

## Objetivo

Generar cartas imprimibles estilo **Hitster** a partir de playlists de Spotify, para ampliar el juego. Cada carta tiene:

- **Frente:** QR que abre la canción en Spotify.
- **Dorso:** artista, año y título.

Se escanean con la cámara del móvil (la app oficial de Hitster no lee estos QR).

## Repositorio

- Fork propio: **https://github.com/Fede1992/hitster-card-generator** (usuario GitHub `Fede1992`), rama `main`.
- Upstream: el repo original del que se hizo el fork.
- ⚠️ **No proponer PRs ni cambios al repo original** salvo que el usuario lo pida explícitamente.
- En la laptop está clonado en `Desktop\Proyectos\hitster-card-generator`, con un venv en `.venv` y Playwright + Chromium instalados.

## Qué se hizo

### 1. Primera prueba: playlist "Exitos exitosos"

- Enlace: `https://open.spotify.com/playlist/7hmRctDV8zh979wUeOL4UJ`. Tiene 145 canciones y es de rock clásico, no de running como se pensó al principio.
- Sin API se obtuvieron 100. Se quitaron 3 repetidas y quedaron **97 cartas**.
- Se corrigieron unos 22 años mal detectados, casi todos por remasters y recopilaciones.

### 2. Playlist grande: "Rockola!" (400 canciones)

- Enlace: `https://open.spotify.com/playlist/0uA7S3tCWvCcEdBKxy1EzA`.
- Las páginas públicas y embed de Spotify solo exponen **100 canciones**. La API de Spotify no está disponible porque no dejan crear credenciales nuevas en 2026.
- **Solución:** abrir la playlist en un navegador sin ventana, bajar por la lista virtualizada y recoger todos los enlaces. Se descartan las "canciones recomendadas" que Spotify muestra al final.
- Resultado: **400/400 canciones**, sin repetidas.
- Se corrigieron **59 años**. La lista está en `playlists/rockola/correcciones.txt`.
- Se limpiaron títulos con restos como "Remaster", "En Vivo" o "From *Titanic*".
- Se quitó el emoji de *bunda*, porque la fuente Montserrat no tiene emojis y salía un cuadrado.
- Se generó el PDF: 40 páginas A4, 20 cartas por hoja.

### 3. Cambios de código (ya en `main`)

| Commit | Cambio |
|---|---|
| `aa0d6ab` | **`src/fetch_full_playlist.py`** (nuevo): usa Playwright en modo headless para bajar *todas* las canciones de una playlist pública y guardarlas en `links.txt`. |
| `aa0d6ab` | `utils.scrape_playlist_track_links` lee primero la página **embed** (`__NEXT_DATA__`), que devuelve hasta 100 canciones en vez de unas 29. Esto mejora también la app de Streamlit. |
| `aa0d6ab` | Arreglado un fallo del CLI: `create_solution_side()` no aceptaba `card_label` y `hitster_card_creator.py` fallaba. |
| `8c9ece6` | **`src/build_pdf.py`** (nuevo): genera el PDF directamente desde un `songs.json`, sin volver a bajar nada. |
| `8c9ece6` | Carpeta **`playlists/`** con las playlists revisadas: `songs.json` con años corregidos y `links.txt`. `.gitignore` ajustado para versionar esos `.json`. |

Playwright **no** está en `requirements.txt` a propósito, para no hacer más pesada la app de Streamlit.

### 4. Mazo combinado (29/09/2026, PC del trabajo)

- **"Exitos exitosos"** completa (143 enlaces) + **"Para juego"** (`https://open.spotify.com/playlist/2ltM7bIUldq0kmfPsE79HG`, 206) → `playlists/combinada/`.
- Rockola! es un mazo **aparte** y **no debe haber cartas repetidas entre mazos**: se quitaron de la combinada 36 canciones que ya estaban en Rockola! (por enlace y por artista + título), más 3 repetidas internas. Se dejaron 3 covers a propósito (Joey Ramone, Heart, Sheryl Crow).
- Se corrigieron 28 años. 15 dudosos los resolvió el usuario (12 con año y 3 quitadas). Detalle en `correcciones.txt` y `quitadas.txt`.
- Resultado: **304 cartas**.

## Estado actual

- `playlists/rockola/songs.json`: 400 canciones revisadas.
- `playlists/exitos_exitosos/songs.json`: 97 canciones revisadas (versión vieja, incluida ahora en la combinada).
- `playlists/combinada/songs.json`: **304 canciones revisadas**, sin dudosos, sin repetidas con Rockola!.
- Los PDF **no están en el repo** (pesan 14 y 59 MB). Se regeneran con `build_pdf.py`.

### Años de "Rockola!" pendientes de confirmar

Quedaron como venían del scraper y el usuario debería revisarlos:

- *0303456* (Raffaella Carrà): 1974.
- *Luna de miel en la mano* (Virus): 1985, quizás 1984.
- *Par mil* (Divididos): 1996.
- *La Guitarra* y *Corazón* (Los Auténticos Decadentes): 1991.
- *Rock del gato* (Ratones Paranoicos): 1989.
- *Juntos a la par* (Pappo): 2003, probablemente de los 80.
- *Los caminos de la vida* (Vicentico): 1995.
- *Mediterráneo*: 1994. Es la versión en vivo con Ana Belén; el original de Serrat es de 1971.

## Cómo seguir en otra PC

Instalación (una sola vez):

```bash
git clone https://github.com/Fede1992/hitster-card-generator
cd hitster-card-generator
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt playwright
.venv\Scripts\python -m playwright install chromium
```

Regenerar el PDF de una playlist ya revisada:

```bash
.venv\Scripts\python src/build_pdf.py playlists/rockola/songs.json output/rockola.pdf
```

Opciones: `--card-draw-border` (bordes de corte), `--ink-save-mode` (fondo blanco), `--card-label "texto"`.

Playlist nueva:

```bash
.venv\Scripts\python src/fetch_full_playlist.py "https://open.spotify.com/playlist/..."
.venv\Scripts\python src/hitster_card_creator.py --fetch
```

Después:

1. Revisar `output/hitster_cards/songs.json`.
2. Copiarlo a `playlists/<nombre>/`.
3. Regenerar el PDF con `build_pdf.py`.

## Lecciones y consejos

- **Los años del scraper fallan mucho:** entre el 15 % y el 20 % vienen con el año de un remaster, una recopilación o una versión en vivo. Siempre hay que revisarlos antes de imprimir y marcar como dudosos los que no se puedan confirmar, en vez de adivinar.
- **Quitar repetidas.** Una misma canción puede aparecer dos veces en versiones distintas.
- Si falta un año, la página de la canción en Spotify tiene `<meta name="music:release_date">`, aunque suele ser la fecha del álbum o de la recopilación.
- **Al imprimir:**
  - Usar tamaño real (100 %), a doble cara, volteando por el borde largo. El dorso ya viene en espejo.
  - Probar primero solo las páginas 1 y 2.
