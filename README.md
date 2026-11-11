# fase4_programacion_software_fj

Sistema integral de gestión de clientes, servicios y reservas desarrollado en Python para la Fase 4 del curso Programación (213023) – UNAD.

## Cómo ejecutarlo

Requiere Python 3.9 o superior. No usa librerías externas ni base de datos.

```bash
python software_fase4.py
```

El programa simula 20 operaciones (registros válidos e inválidos de clientes, creación correcta e incorrecta de servicios, reservas exitosas y fallidas, y cancelaciones). Los eventos y errores quedan en el archivo `software_fj.log`.

## Estructura

| Elemento | Descripción |
|---|---|
| `SoftwareFJError` y derivadas | Excepciones personalizadas: `DatosInvalidosError`, `ParametroFaltanteError`, `ServicioNoDisponibleError`, `ReservaError`, `CalculoInconsistenteError`. |
| `Entidad` | Clase abstracta general del sistema. |
| `Cliente` | Hereda de `Entidad`; valida y encapsula los datos personales. |
| `Servicio` | Clase abstracta; define `calcular_costo` con variantes (descuento, impuesto, IVA por defecto). |
| `ServicioSala`, `ServicioEquipo`, `ServicioAsesoria` | Servicios especializados que sobrescriben `costo_base`, `describir` y `validar_parametros`. |
| `Reserva` | Integra cliente, servicio, duración y estado; confirma, cancela y procesa con `try/except/else/finally` y encadenamiento de excepciones. |
| `SistemaSoftwareFJ` | Administra las listas internas de clientes, servicios y reservas. |
| `main()` | Simulación de operaciones; cada una se ejecuta de forma aislada para que un error no detenga el programa. |
