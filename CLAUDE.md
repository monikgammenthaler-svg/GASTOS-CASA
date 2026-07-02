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
app.py               ← entrada: sidebar, routing (~95 líneas)
auth.py              ← pantalla de login / creación de hogar (signup con código de invitación)
db.py                ← toda la lógica de base de datos
estilos.py           ← tokens de diseño (colores, fuentes) + CSS global
views/
  resumen.py         ← Resumen del mes + tarjeta compromisos
  cargar_gasto.py    ← Formulario nuevo gasto
  ver_gastos.py      ← Lista/filtro de gastos del mes
  cuotas.py          ← Cuotas de tarjeta
  tarjetas.py        ← ABM de tarjetas del hogar (nombre + dueño)
  gastos_fijos.py    ← Editor de gastos fijos mensuales
  pendientes.py      ← Lista de compras/pendientes
  personal.py        ← Gastos personales por persona
.streamlit/
  secrets.toml       ← NUNCA commitear. Tiene la conexión a la DB y el código de invitación.
```

## Arquitectura multi-hogar (multi-tenant)

Cada hogar tiene su propio `casa_id` en la DB. **Todos** los queries filtran por `casa_id` — ningún hogar ve datos de otro.

Los hogares (usuario, contraseña hasheada con bcrypt, nombre) se guardan en la tabla `casas` de la DB — no en `secrets.toml`. Se crean desde la pantalla de login, pestaña "Crear hogar", protegida por un código de invitación (`st.secrets["auth"]["invite_code"]`, definido en `secrets.toml` local y en Streamlit Cloud → Settings → Secrets). Así se evita que gente ajena cree hogares en la base, y ninguna contraseña queda en texto plano en ningún archivo.

### Personas del hogar (N personas, no solo 2)

Un hogar puede tener **cualquier cantidad de personas** (1, 2, 3...), no solo 2. Se guardan en la tabla `personas_casa` (`casa_id`, `nombre`, `orden`), cargadas dinámicamente en el signup con un botón "+ Agregar persona". El reparto de gastos es **en partes iguales entre todos** (`total / cantidad de personas`), no necesariamente 50/50. La liquidación ("quién le debe a quién") usa un algoritmo de settle-up greedy (`resumen.py:_liquidar`) que da el mínimo de transferencias necesarias — para 2 personas da exactamente una transferencia (igual que el comportamiento original); para 1 persona sola, siempre da $0 (no hay a quién deberle).

Los colores por persona salen de `estilos.PALETA_PERSONAS` vía `estilos.color_persona(nombre, personas)` — asignación por posición, no por nombre fijo. Las columnas `casas.persona_1`/`persona_2` quedan en la tabla sin usarse (compatibilidad con datos viejos), todo el código lee de `personas_casa` / `db.obtener_personas_casa()`.

### Sesión persistente (cookie)

Al loguearse (o crear un hogar) se guarda una cookie `domus_session` con un token firmado (HMAC-SHA256, `st.secrets["auth"]["session_secret"]`) que expira a las 24hs. En cada carga, `app.py` valida esa cookie (`auth.verificar_token_sesion`) antes de mostrar el login, así un refresh de página no desloguea. Es stateless — no hay tabla de sesiones ni forma de revocar un token individual antes de tiempo, por eso la expiración es corta. Usa la librería `extra-streamlit-components` (`stx.CookieManager`).

## Contexto de sesión (`ctx`)

Todas las vistas reciben un dict `ctx` con:
```python
ctx = {
    "casa_id": int,
    "personas": ["Nombre1", "Nombre2", ...],   # cualquier cantidad, orden estable
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

`PALETA_PERSONAS` (lista de colores) + `color_persona(nombre, personas)` + `tint(hex, alpha)` — para asignarle un color consistente a cada persona del hogar sin hardcodear "persona 1 = azul, persona 2 = dorado".

## Base de datos

Tablas principales (todas con `casa_id`, salvo `casas`):
- `casas` — hogares: usuario, `password_hash` (bcrypt), nombre (`persona_1`/`persona_2` sin uso, ver abajo)
- `personas_casa` — personas de cada hogar: `casa_id`, `nombre`, `orden`. Cantidad libre (no solo 2).
- `gastos_variables` — gastos del mes cargados manualmente
- `gastos_fijos` — compromisos fijos mensuales (alquiler, servicios, etc.)
- `fijos_excluidos_mes` — overrides para excluir un fijo en un mes específico
- `compras_tarjeta` — compras en cuotas
- `tarjetas` — tarjetas configuradas por cada hogar (nombre + dueño: persona_1, persona_2 o "Compartida"). `UNIQUE(casa_id, nombre, dueno)` — permite nombres repetidos (ej. dos "OCA") si son de dueños distintos. En los selectores para elegir tarjeta se muestra/guarda como `"nombre (dueño)"` para desambiguar.
- `pendientes` — lista de compras/to-do
- `gastos_personales` — gastos personales por persona (no impactan el total compartido)

## Performance

- `@st.cache_resource` en `_init_once()` → `db.init_db()` corre solo una vez por servidor
- `@st.cache_data(ttl=60)` en todas las funciones de lectura de DB
- `st.cache_data.clear()` (via `_invalidar()`) después de cada escritura
- Conexión con `autocommit=True` (en `db._connect()`) — evita que una lectura deje una transacción "idle in transaction" abierta que bloquee `ALTER TABLE`/`CREATE TABLE` de futuras migraciones
- Sin ping `SELECT 1` en `get_conn()` — reconexión lazy

## Conexión DB

- **Local**: URL directa Supabase puerto 5432 (en `secrets.toml`)
- **Cloud**: Transaction Pooler puerto 6543 — `aws-1-us-east-1.pooler.supabase.com`
  - El pooler es obligatorio en Streamlit Cloud (la conexión directa es bloqueada)

## Seguridad

- `secrets.toml` está en `.gitignore` — NUNCA commitear
- La contraseña de la DB es `MG963..gastos` — solo en secrets, nunca en código
- Cada hogar solo ve sus propios datos, incluso la admin
- Las contraseñas de los hogares se guardan hasheadas con bcrypt en la tabla `casas` — nunca en texto plano
- El signup de hogares nuevos requiere el `invite_code` de `secrets.toml` (`[auth]`) — sin eso no se puede crear una cuenta

## Flujo de desarrollo

```bash
# Correr localmente
cd "C:\Users\Usuario\OneDrive\Desktop\PYTHON MONI\GASTOS MONI"
streamlit run app.py
```

### Versionado con ramas

Para cualquier cambio importante (nueva funcionalidad, refactor grande, algo que no sea un fix chico), crear una rama de feature desde `main` actualizado, y mergearla a `main` cuando esté probada:

```bash
git checkout main
git pull
git checkout -b feature/nombre-descriptivo

# ... trabajar, commitear ...

git push -u origin feature/nombre-descriptivo
# mergear a main (PR o merge directo) cuando esté listo y probado
```

- `main` es siempre la rama desplegable — Streamlit Cloud deploya automático al pushear/mergear ahí
- Fixes chicos y triviales pueden ir directo a `main`
- Si el proyecto escala mucho (varios colaboradores, releases más formales), evaluar sumar una rama `develop` intermedia (Git Flow clásico) — no hace falta hoy

```bash
# Deployar: push/merge a main → Streamlit Cloud redeploya automático
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
