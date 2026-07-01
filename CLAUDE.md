# DOMUS — Gastos del Hogar

App de gestión de gastos domésticos construida con Streamlit + PostgreSQL (Supabase).
Accesible desde cualquier dispositivo via Streamlit Community Cloud.

## Stack

- **Frontend/Backend**: Python + Streamlit
- **Base de datos**: PostgreSQL en Supabase (producción)
- **Deploy**: Streamlit Community Cloud → `gastos-casa-dsbg3njm4nnxmkwuncfe4d.streamlit.app`
- **Repo**: `github.com/monikgammenthaler-svg/GASTOS-CASA`, rama `main`

## Estructura de archivos

```
app.py               ← entrada: login, sidebar, routing (~90 líneas)
db.py                ← toda la lógica de base de datos
estilos.py           ← tokens de diseño (colores, fuentes) + CSS global
views/
  resumen.py         ← Resumen del mes + tarjeta compromisos
  cargar_gasto.py    ← Formulario nuevo gasto
  ver_gastos.py      ← Lista/filtro de gastos del mes
  cuotas.py          ← Cuotas de tarjeta
  gastos_fijos.py    ← Editor de gastos fijos mensuales
  pendientes.py      ← Lista de compras/pendientes
  personal.py        ← Gastos personales por persona
.streamlit/
  secrets.toml       ← NUNCA commitear. Tiene credenciales DB y contraseñas de hogares.
```

## Arquitectura multi-hogar (multi-tenant)

Cada hogar tiene su propio `casa_id` en la DB. **Todos** los queries filtran por `casa_id` — ningún hogar ve datos de otro.

Los hogares se configuran en `.streamlit/secrets.toml` (local) y en Streamlit Cloud → Settings → Secrets (producción):

```toml
[casas.mg]
nombre   = "Moni & Guille"
usuario  = "mg"
password = "mg2026"
personas = ["Moni", "Guille"]
id       = 1

[casas.ml]
nombre   = "Leandro & Mika"
usuario  = "ml"
password = "ml2026"
personas = ["Leandro", "Mika"]
id       = 2
```

Para agregar un nuevo hogar: añadir una sección `[casas.XX]` con `id` único y actualizar secrets en ambos lugares.

## Contexto de sesión (`ctx`)

Todas las vistas reciben un dict `ctx` con:
```python
ctx = {
    "casa_id": int,
    "personas": ["Nombre1", "Nombre2"],
    "persona_1": str,
    "persona_2": str,
    "anio_sel": int,
    "mes_sel": int,       # 1-12
    "mes_nombre": str,    # "Enero", "Febrero", etc.
    "casa_nombre": str,
}
```

## Tokens de diseño (estilos.py)

```python
NAVY="#0f1b35"  NAVY2="#1a3360"  BLUE="#2d6bc4"
GOLD="#c9a84c"  GOLD_L="#f5d060" GOLD_P="#fdf6e3" GOLD_T="#a87f2c"
WHITE="#ffffff" GRAY="#6b7280"
SERIF="Newsreader, serif"   DISPLAY="Cormorant, serif"
```

## Base de datos

Tablas principales (todas con `casa_id`):
- `gastos_variables` — gastos del mes cargados manualmente
- `gastos_fijos` — compromisos fijos mensuales (alquiler, servicios, etc.)
- `fijos_excluidos_mes` — overrides para excluir un fijo en un mes específico
- `compras_tarjeta` — compras en cuotas
- `pendientes` — lista de compras/to-do
- `gastos_personales` — gastos personales por persona (no impactan el total compartido)

## Performance

- `@st.cache_resource` en `_init_once()` → `db.init_db()` corre solo una vez por servidor
- `@st.cache_data(ttl=60)` en todas las funciones de lectura de DB
- `st.cache_data.clear()` (via `_invalidar()`) después de cada escritura
- Sin ping `SELECT 1` en `get_conn()` — reconexión lazy

## Conexión DB

- **Local**: URL directa Supabase puerto 5432 (en `secrets.toml`)
- **Cloud**: Transaction Pooler puerto 6543 — `aws-1-us-east-1.pooler.supabase.com`
  - El pooler es obligatorio en Streamlit Cloud (la conexión directa es bloqueada)

## Seguridad

- `secrets.toml` está en `.gitignore` — NUNCA commitear
- La contraseña de la DB es `MG963..gastos` — solo en secrets, nunca en código
- Cada hogar solo ve sus propios datos, incluso la admin

## Flujo de desarrollo

```bash
# Correr localmente
cd "C:\Users\Usuario\OneDrive\Desktop\PYTHON MONI\GASTOS MONI"
streamlit run app.py

# Deployar: push a main → Streamlit Cloud redeploya automático
git add <archivos>
git commit -m "descripción"
git push
```

## Buenas prácticas para este proyecto

- Cada vista nueva va en `views/nueva_vista.py` con una función `render(ctx)`
- Agregar la vista al routing en `app.py` (bloque `if/elif` al final)
- Los estilos HTML inline usan las constantes de `estilos.py` — no hardcodear colores
- Fuentes responsive: usar `clamp(min, vw, max)` para textos grandes en mobile
- Columnas de Streamlit en mobile: evitar más de 3-4 columnas, o usar proporciones amplias para botones
