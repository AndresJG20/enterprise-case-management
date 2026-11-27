# CaseFlow | Gestión de casos

![Pruebas](https://github.com/AndresJG20/enterprise-case-management/actions/workflows/ci.yml/badge.svg)

CaseFlow es un proyecto de portafolio orientado a la gestión y seguimiento de solicitudes. La idea es tener en un mismo lugar los casos registrados, sus responsables, los cambios de estado y los indicadores de atención, en lugar de mantener esa información en archivos dispersos.

## Funciones

- Inicio y cierre de sesión.
- Dos roles: administrador y analista. El administrador puede crear usuarios y consultar todos los casos; cada analista accede únicamente a los que tiene asignados.
- Registro de casos con descripción, prioridad y responsable.
- Búsqueda por título, filtros por estado y paginación.
- Historial de cambios e indicadores por estado.
- Control de versiones para evitar que dos usuarios sobrescriban un cambio al mismo tiempo.

## Tecnologías

Python, FastAPI, SQLAlchemy, SQLite, PostgreSQL (configuración con Docker Compose), HTML, CSS y JavaScript. Las pruebas utilizan pytest y se ejecutan con GitHub Actions.

## Instalación en Windows

Con Python 3.12 instalado, abre PowerShell en la carpeta del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:CASEFLOW_ADMIN_PASSWORD = Read-Host "Contraseña local de al menos 12 caracteres"
python -m backend.seed
python -m uvicorn backend.main:app
```

Abre http://localhost:8000. El usuario inicial es `admin`, con la contraseña que definiste. Desde la interfaz se pueden crear analistas y registrar casos. La documentación de la API está en http://localhost:8000/docs.

Para probar el recorrido completo, crea un analista ficticio, registra un caso asignado a ese usuario, inicia sesión como analista y cambia el estado de Abierto a En proceso y luego a Resuelto. Consulta el historial para verificar los cambios.

## Ejecución con PostgreSQL

Copia `.env.example` a `.env` y define contraseñas propias (la de PostgreSQL debe ser apta para una URL). A continuación:

```bash
docker compose up -d --build
docker compose exec app python -m backend.seed
```

Utiliza una base nueva; no se incluyen migraciones desde la versión inicial.

## Estructura

| Carpeta | Contenido |
| --- | --- |
| backend/ | API, modelos, validaciones, seguridad y lógica de negocio |
| frontend/ | Interfaz y comunicación con la API |
| tests/ | Pruebas de integración |
| docs/ | Diseño técnico y decisiones de arquitectura |

## Pruebas

```bash
python -m pytest -q
```

GitHub Actions ejecuta las pruebas contra SQLite y construye la imagen Docker. Se comprueban autenticación, permisos, creación de usuarios, cambios de estado, auditoría, filtros y paginación. La configuración de PostgreSQL y la navegación completa aún requieren validación adicional.

## Alcance

Proyecto de aprendizaje y demostración local con datos ficticios. No corresponde a un sistema de ninguna institución. No incluye archivos adjuntos, migraciones, limitación de intentos de acceso ni configuración HTTPS. Antes de desplegarlo en Internet se requiere una revisión de seguridad.

Consulta el [documento de arquitectura](docs/architecture.md).
