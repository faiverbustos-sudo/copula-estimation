# WebApplication1.Hexagonal

API REST desarrollada con **ASP.NET Core**, **Entity Framework Core**, **ASP.NET Core Identity** y **JWT**, organizada bajo principios de **arquitectura hexagonal (Ports and Adapters)**.

El proyecto forma parte de un ejercicio de construcción de una aplicación backend con separación de responsabilidades, autenticación, autorización y persistencia en una base de datos existente.

## Tecnologías

- .NET / ASP.NET Core
- C#
- Entity Framework Core
- ASP.NET Core Identity
- JWT Bearer Authentication
- SQL Server o PostgreSQL, según la configuración del entorno
- Swagger / OpenAPI
- xUnit para pruebas
- Visual Studio

## Estructura de la solución

```text
WebApplication1.Hexagonal/
│
├── WebApplication1.Api/
├── WebApplication1.Application/
├── WebApplication1.Domain/
├── WebApplication1.Infrastructure/
├── WebApplication1.Hexagonal/
├── WebApplication1.Tests/
│
├── TestProject1.Test/
├── TestProject1.Tests/
├── hexagonal-backend-mvp/
│
├── .gitignore
├── .dockerignore
└── WebApplication1.Hexagonal.sln
```

> Los proyectos auxiliares de pruebas o prototipos pueden variar según el estado del ejercicio. La solución principal está organizada alrededor de `Api`, `Application`, `Domain` e `Infrastructure`.

## Arquitectura hexagonal

La arquitectura separa el núcleo de negocio de los detalles externos.

```text
                    ┌──────────────────────┐
                    │       API            │
                    │ Controllers / HTTP   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    APPLICATION       │
                    │ Casos de uso /       │
                    │ servicios / puertos  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       DOMAIN         │
                    │ Entidades y reglas   │
                    │ de negocio           │
                    └──────────────────────┘
                               ▲
                               │
                    ┌──────────┴───────────┐
                    │   INFRASTRUCTURE     │
                    │ EF Core / Identity   │
                    │ JWT / repositorios   │
                    └──────────────────────┘
```

### Principios utilizados

- El dominio no depende de ASP.NET Core, EF Core ni Identity.
- Application define los casos de uso y los puertos.
- Infrastructure implementa los puertos mediante adaptadores.
- API recibe las solicitudes HTTP y delega en Application.
- La inversión de dependencias apunta hacia el núcleo de la aplicación.

## Proyectos

### WebApplication1.Domain

Contiene el núcleo del negocio:

- Entidades de dominio.
- Reglas de negocio.
- Objetos propios del dominio.
- Contratos que no dependen de infraestructura.

### WebApplication1.Application

Contiene los casos de uso de la aplicación:

- Servicios de aplicación.
- DTOs.
- Puertos de entrada.
- Puertos de salida.
- Interfaces de repositorios y servicios externos.

Ejemplos de puertos:

```text
IAuthService
IPersonaService
IPersonaRepository
IUserIdentityPort
ITokenService
IRefreshTokenRepository
```

### WebApplication1.Infrastructure

Contiene las implementaciones concretas:

- `ApplicationDbContext`.
- Configuraciones de Entity Framework Core.
- Repositorios.
- ASP.NET Core Identity.
- `ApplicationUser`.
- Entidad `RefreshToken`.
- Generación y validación de JWT.
- Adaptadores de servicios externos.

### WebApplication1.Api

Contiene la entrada HTTP de la aplicación:

- Controllers.
- Configuración de servicios.
- Middleware.
- Autenticación y autorización.
- Swagger.
- Configuración de CORS.
- Punto de entrada `Program.cs`.

### WebApplication1.Tests

Contiene las pruebas automatizadas del backend.

## Flujo de dependencias

La dirección de las dependencias debe mantenerse de la siguiente manera:

```text
Api
 ↓
Application
 ↓
Domain

Infrastructure
 ↓
Application
 ↓
Domain
```

`Domain` no debe depender de `Infrastructure`.

`Application` no debe depender directamente de:

- `DbContext`.
- `UserManager`.
- `SignInManager`.
- `JwtSecurityTokenHandler`.
- Clases concretas de repositorios.

## Autenticación

La aplicación utiliza JWT Bearer para autenticar las solicitudes.

### Registro

```http
POST /api/Auth/register
```

Ejemplo de solicitud:

```json
{
  "email": "usuario@test.com",
  "password": "Password123!"
}
```

### Login

```http
POST /api/Auth/login
```

Ejemplo de solicitud:

```json
{
  "email": "usuario@test.com",
  "password": "Password123!"
}
```

Ejemplo de respuesta:

```json
{
  "accessToken": "...",
  "refreshToken": "...",
  "expires": "..."
}
```

### Refresh token

```http
POST /api/Auth/refresh-token
```

Ejemplo de solicitud:

```json
{
  "accessToken": "ACCESS_TOKEN_ACTUAL",
  "refreshToken": "REFRESH_TOKEN_ACTUAL"
}
```

El sistema utiliza rotación de refresh tokens:

1. Valida el access token.
2. Obtiene el usuario asociado.
3. Valida el refresh token almacenado.
4. Revoca el refresh token anterior.
5. Genera un nuevo access token.
6. Genera y almacena un nuevo refresh token.
7. Devuelve ambos tokens.

## Entidad RefreshToken

La aplicación reutiliza la tabla de refresh tokens existente en la base de datos.

La entidad contiene:

```csharp
public class RefreshToken
{
    public int Id { get; set; }

    public string Token { get; set; } = string.Empty;

    public DateTime Expires { get; set; }

    public DateTime Created { get; set; }

    public DateTime? Revoked { get; set; }

    public string UserId { get; set; } = string.Empty;

    public ApplicationUser User { get; set; } = null!;

    public bool IsExpired => DateTime.UtcNow >= Expires;

    public bool IsRevoked => Revoked.HasValue;

    public bool IsActive => !IsExpired && !IsRevoked;
}
```

Los nombres de las propiedades deben mantenerse alineados con la estructura existente de la base de datos.

## Autorización

Los endpoints protegidos utilizan:

```csharp
[Authorize]
```

Para restringir el acceso por roles:

```csharp
[Authorize(Roles = "Admin")]
```

O para permitir cualquiera de varios roles:

```csharp
[Authorize(Roles = "Admin,Medico")]
```

## Configuración local

La configuración se realiza mediante `appsettings.json`, `appsettings.Development.json` o variables de entorno.

Ejemplo de configuración JWT:

```json
{
  "Jwt": {
    "Key": "CLAVE_SECRETA_LARGA_Y_SEGURA",
    "Issuer": "WebApplication1",
    "Audience": "WebApplication1",
    "AccessTokenExpirationMinutes": 60
  }
}
```

### Recomendaciones

- No subir claves secretas al repositorio.
- No subir contraseñas de bases de datos.
- Utilizar User Secrets o variables de entorno para valores sensibles.
- Mantener `appsettings.Development.json` fuera del repositorio si contiene secretos.
- Utilizar una clave JWT de al menos 32 bytes para HS256.

## Base de datos

La aplicación utiliza una base de datos existente.

Antes de ejecutar cambios de esquema:

1. Revisar las tablas actuales.
2. Revisar las columnas y relaciones.
3. Revisar las configuraciones de EF Core.
4. Confirmar si el cambio requiere una migración.
5. Evitar recrear tablas que ya existen.

Las migraciones deben versionarse cuando representen cambios reales del modelo y sean parte del proceso de despliegue.

## Ejecución del proyecto

### Restaurar dependencias

```powershell
dotnet restore
```

### Compilar

```powershell
dotnet build
```

### Ejecutar la API

```powershell
dotnet run --project WebApplication1.Api
```

### Ejecutar las pruebas

```powershell
dotnet test
```

### Ejecutar con Visual Studio

1. Abrir `WebApplication1.Hexagonal.sln`.
2. Seleccionar `WebApplication1.Api` como proyecto de inicio.
3. Revisar la cadena de conexión.
4. Revisar la configuración JWT.
5. Ejecutar con `https` o `http` según el perfil configurado.
6. Abrir Swagger desde la URL mostrada por ASP.NET Core.

## CORS

Si el frontend React se ejecuta en Vite, normalmente utiliza un origen similar a:

```text
http://localhost:5173
```

El backend debe permitir explícitamente ese origen en desarrollo.

Ejemplo:

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("Frontend", policy =>
    {
        policy
            .WithOrigins("http://localhost:5173")
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});
```

Y el middleware debe ejecutarse antes de mapear los controllers:

```csharp
app.UseCors("Frontend");
```

La configuración exacta debe ajustarse al entorno de ejecución.

## Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/Auth/register` | Registra un usuario |
| POST | `/api/Auth/login` | Autentica un usuario |
| POST | `/api/Auth/refresh-token` | Renueva los tokens |
| GET | `/api/Personas` | Consulta personas |
| GET | `/api/Personas/{id}` | Consulta una persona |
| POST | `/api/Personas` | Crea una persona |
| PUT | `/api/Personas/{id}` | Actualiza una persona |
| DELETE | `/api/Personas/{id}` | Elimina una persona |

Los endpoints protegidos requieren un JWT válido en el encabezado:

```http
Authorization: Bearer ACCESS_TOKEN
```

## Git

El repositorio incluye un `.gitignore` para excluir archivos generados por:

- Visual Studio.
- .NET.
- Compilación.
- Pruebas.
- Archivos temporales.
- Configuración local.
- Variables de entorno.

Las migraciones, el código fuente y los archivos de configuración no sensibles deben mantenerse versionados.

## Estado del proyecto

Actualmente el ejercicio contempla:

- Arquitectura hexagonal.
- Separación entre Domain, Application, Infrastructure y API.
- Repositorios mediante puertos y adaptadores.
- Registro de usuarios.
- Login con JWT.
- Refresh tokens persistidos.
- Rotación de refresh tokens.
- Protección de endpoints con `[Authorize]`.
- Integración con una base de datos existente.
- Frontend React separado del backend.

## Próximos pasos

- Completar autorización basada en roles.
- Revisar validaciones de DTOs.
- Agregar pruebas unitarias para servicios y adaptadores.
- Agregar pruebas de integración para autenticación.
- Mejorar manejo global de errores.
- Incorporar logging estructurado.
- Preparar configuración para despliegue en la nube.
- Documentar variables de entorno por ambiente.
