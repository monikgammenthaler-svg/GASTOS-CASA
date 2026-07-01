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

Los hogares (usuario, contraseña hasheada con bcrypt, nombre, personas) se guardan en la tabla `casas` de la DB — no en `secrets.toml`. Se crean desde la pantalla de login, pestaña "Crear hogar", protegida por un código de invitación (`st.secrets["auth"]["invite_code"]`, definido en `secrets.toml` local y en Streamlit Cloud → Settings → Secrets). Así se evita que gente ajena cree hogares en la base, y ninguna contraseña queda en texto plano en ningún archivo.

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

Tablas principales (todas con `casa_id`, salvo `casas`):
- `casas` — hogares: usuario, `password_hash` (bcrypt), nombre, persona_1, persona_2
- `gastos_variables` — gastos del mes cargados manualmente
- `gastos_fijos` — compromisos fijos mensuales (alquiler, servicios, etc.)
- `fijos_excluidos_mes` — overrides para excluir un fijo en un mes específico
- `compras_tarjeta` — compras en cuotas
- `tarjetas` — tarjetas configuradas por cada hogar (nombre + dueño: persona_1, persona_2 o "Compartida")
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
