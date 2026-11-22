# =============================================================================
# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programación (213023) - Fase 4
# Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas
# Empresa: Software FJ
# Descripción: Sistema orientado a objetos, sin base de datos, que gestiona
# clientes, servicios y reservas con manejo avanzado de excepciones y
# registro de eventos y errores en un archivo de logs.
# =============================================================================

import math  # Rechazar valores no finitos en números positivos.
from abc import ABC, abstractmethod  # Herramientas para crear clases abstractas.
import logging  # Módulo estándar para registrar eventos en archivos.

# Configura el archivo donde se registrarán eventos y errores del sistema.
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


# =============================================================================
# EXCEPCIONES PERSONALIZADAS
# =============================================================================

class SoftwareFJError(Exception):
    pass


class DatosInvalidosError(SoftwareFJError):
    pass


class ParametroFaltanteError(DatosInvalidosError):
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    pass


class ReservaError(SoftwareFJError):
    pass


class CalculoInconsistenteError(SoftwareFJError):
    pass


# =============================================================================
# FUNCIONES AUXILIARES DE VALIDACIÓN
# =============================================================================

def validar_texto(valor, campo):
    if valor is None:
        raise ParametroFaltanteError(f"Falta el parámetro obligatorio: {campo}.")
    if not isinstance(valor, str) or not valor.strip():
        raise DatosInvalidosError(f"El campo '{campo}' no puede estar vacío.")
    return valor.strip()


def validar_numero_positivo(valor, campo):
    if valor is None:
        raise ParametroFaltanteError(f"Falta el parámetro obligatorio: {campo}.")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise DatosInvalidosError(f"El campo '{campo}' debe ser numérico.")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise DatosInvalidosError(f"El campo '{campo}' debe ser un número finito.")
    if valor <= 0:
        raise DatosInvalidosError(f"El campo '{campo}' debe ser mayor que cero.")
    return valor


def validar_descuento(descuento):
    if descuento is None:
        raise ParametroFaltanteError("Falta el parámetro obligatorio: descuento.")
    if isinstance(descuento, bool) or not isinstance(descuento, (int, float)):
        raise DatosInvalidosError("El descuento debe ser un número entre 0 y 100.")
    if isinstance(descuento, float) and not math.isfinite(descuento):
        raise DatosInvalidosError("El descuento debe ser un número finito entre 0 y 100.")
    if not 0 <= descuento <= 100:
        raise DatosInvalidosError("El descuento debe ser un número entre 0 y 100.")
    return descuento


def validar_impuesto(impuesto, iva_defecto=19):
    if impuesto is None or impuesto is False:
        return 0
    if impuesto is True:
        return iva_defecto
    if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)):
        raise DatosInvalidosError("El impuesto debe ser True, False o un porcentaje entre 0 y 100.")
    if isinstance(impuesto, float) and not math.isfinite(impuesto):
        raise DatosInvalidosError("El impuesto debe ser un número finito entre 0 y 100.")
    if not 0 <= impuesto <= 100:
        raise DatosInvalidosError("El impuesto debe ser True, False o un porcentaje entre 0 y 100.")
    return impuesto


# =============================================================================
# CLASE ABSTRACTA GENERAL
# =============================================================================

class Entidad(ABC):

    def __init__(self, identificacion):
        if identificacion is None or not str(identificacion).strip():
            raise ParametroFaltanteError("La identificación no puede estar vacía.")
        self._identificacion = str(identificacion).strip()

    def obtener_identificacion(self):
        return self._identificacion

    @abstractmethod
    def describir(self):
        pass


# =============================================================================
# CLASE CLIENTE
# =============================================================================

class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion)

        if not self._identificacion.isdigit():
            raise DatosInvalidosError("La identificación debe contener únicamente números.")

        nombre = validar_texto(nombre, "nombre")
        correo = validar_texto(correo, "correo")
        telefono = validar_texto(telefono, "telefono")

        if not nombre.replace(" ", "").isalpha():
            raise DatosInvalidosError("El nombre solo puede contener letras y espacios.")

        partes = correo.split("@")
        if len(partes) != 2 or not partes[0] or "." not in partes[1]:
            raise DatosInvalidosError("El correo electrónico no es válido.")

        if not telefono.isdigit() or not 7 <= len(telefono) <= 10:
            raise DatosInvalidosError("El teléfono debe tener entre 7 y 10 dígitos numéricos.")

        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono

        logging.info(f"Cliente creado: {self._identificacion} - {self.__nombre}")

    def obtener_nombre(self):
        return self.__nombre

    def obtener_correo(self):
        return self.__correo

    def obtener_telefono_oculto(self):
        return "*" * (len(self.__telefono) - 4) + self.__telefono[-4:]

    def describir(self):
        return (
            f"Cliente: {self.__nombre} | "
            f"ID: {self._identificacion} | "
            f"Correo: {self.__correo} | "
            f"Tel: {self.obtener_telefono_oculto()}"
        )


# =============================================================================
# CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS
# =============================================================================

class Servicio(Entidad):

    IVA = 19

    def __init__(self, id_servicio, nombre, tarifa_base):
        super().__init__(id_servicio)
        self._nombre = validar_texto(nombre, "nombre del servicio")
        self._tarifa_base = validar_numero_positivo(tarifa_base, "tarifa base")
        self._disponible = True

    def obtener_id(self):
        return self._identificacion

    def obtener_nombre(self):
        return self._nombre

    def esta_disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        if not isinstance(estado, bool):
            raise DatosInvalidosError("La disponibilidad debe ser True o False.")
        self._disponible = estado

    def ocupar(self):
        self.cambiar_disponibilidad(False)

    def liberar(self):
        self.cambiar_disponibilidad(True)

    @abstractmethod
    def costo_base(self, duracion):
        pass

    @abstractmethod
    def validar_parametros(self):
        pass

    def calcular_costo(self, duracion, descuento=0, impuesto=None):
        validar_numero_positivo(duracion, "duración")
        descuento_validado = validar_descuento(descuento)
        porcentaje_impuesto = validar_impuesto(impuesto, self.IVA)

        base = self.costo_base(duracion)
        con_descuento = base - base * descuento_validado / 100
        total = con_descuento + con_descuento * porcentaje_impuesto / 100

        if total < 0 or math.isnan(total) or not math.isfinite(total):
            raise CalculoInconsistenteError(f"Costo inconsistente calculado: {total}")
        return round(total, 2)


class ServicioSala(Servicio):

    def __init__(self, id_servicio, nombre, tarifa_base, capacidad):
        super().__init__(id_servicio, nombre, tarifa_base)
        self._capacidad = capacidad
        self.validar_parametros()

    def validar_parametros(self):
        validar_numero_positivo(self._capacidad, "capacidad de la sala")

    def costo_base(self, duracion):
        recargo = 1.2 if self._capacidad > 20 else 1.0
        return self._tarifa_base * duracion * recargo

    def describir(self):
        return (
            f"Sala: {self._nombre} | "
            f"Capacidad: {self._capacidad} personas | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )


class ServicioEquipo(Servicio):

    def __init__(self, id_servicio, nombre, tarifa_base, cantidad_disponible):
        super().__init__(id_servicio, nombre, tarifa_base)
        self._cantidad_disponible = cantidad_disponible
        self.validar_parametros()
        self._disponible = self._cantidad_disponible > 0

    def validar_parametros(self):
        if not isinstance(self._cantidad_disponible, int) or isinstance(self._cantidad_disponible, bool):
            raise DatosInvalidosError("La cantidad disponible debe ser un número entero.")
        if self._cantidad_disponible < 0:
            raise DatosInvalidosError("La cantidad disponible no puede ser negativa.")

    def ocupar(self):
        # Valida explícitamente que haya existencias antes de descontar una unidad.
        if self._cantidad_disponible <= 0:
            self.cambiar_disponibilidad(False)
            raise ServicioNoDisponibleError(
                f"No hay unidades disponibles del equipo '{self._nombre}'."
            )
        self._cantidad_disponible -= 1
        if self._cantidad_disponible == 0:
            self.cambiar_disponibilidad(False)

    def liberar(self):
        self._cantidad_disponible += 1
        self.cambiar_disponibilidad(True)

    def costo_base(self, duracion):
        factor = 0.9 if duracion >= 8 else 1.0
        return self._tarifa_base * duracion * factor

    def describir(self):
        return (
            f"Equipo: {self._nombre} | "
            f"Disponibles: {self._cantidad_disponible} | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )


class ServicioAsesoria(Servicio):

    RECARGOS = {"ciberseguridad": 1.25, "inteligencia artificial": 1.3}

    def __init__(self, id_servicio, nombre, tarifa_base, especialidad):
        super().__init__(id_servicio, nombre, tarifa_base)
        self._especialidad = especialidad
        self.validar_parametros()

    def validar_parametros(self):
        self._especialidad = validar_texto(self._especialidad, "especialidad")

    def costo_base(self, duracion):
        recargo = self.RECARGOS.get(self._especialidad.lower(), 1.0)
        return self._tarifa_base * duracion * recargo

    def describir(self):
        return (
            f"Asesoría: {self._nombre} | "
            f"Especialidad: {self._especialidad} | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )


# =============================================================================
# CLASE RESERVA
# =============================================================================

class Reserva:

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    FALLIDA = "FALLIDA"

    def __init__(self, id_reserva, cliente, servicio, duracion, descuento=0, impuesto=None):
        if id_reserva is None or not str(id_reserva).strip():
            raise ParametroFaltanteError("El ID de la reserva no puede estar vacío.")

        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El cliente proporcionado no es válido.")

        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El servicio proporcionado no es válido.")

        validar_numero_positivo(duracion, "duración")
        validar_descuento(descuento)
        validar_impuesto(impuesto, servicio.IVA)

        self._id_reserva = str(id_reserva).strip()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._descuento = descuento
        self._impuesto = impuesto
        self._estado = Reserva.PENDIENTE
        self._costo_total = 0

    def confirmar(self):
        if self._estado != Reserva.PENDIENTE:
            raise ReservaError(f"La reserva ya fue procesada (estado: {self._estado}).")

        if not self._servicio.esta_disponible():
            raise ServicioNoDisponibleError(f"El servicio '{self._servicio.obtener_nombre()}' no está disponible.")

        self._servicio.ocupar()
        self._estado = Reserva.CONFIRMADA
        logging.info(f"Reserva confirmada: {self._id_reserva}")

    def cancelar(self):
        if self._estado == Reserva.CANCELADA:
            raise ReservaError("La reserva ya está cancelada.")

        if self._estado == Reserva.CONFIRMADA:
            self._servicio.liberar()

        self._estado = Reserva.CANCELADA
        logging.info(f"Reserva cancelada: {self._id_reserva}")

    def procesar(self):
        try:
            costo = self._servicio.calcular_costo(self._duracion, self._descuento, self._impuesto)
            self.confirmar()

        except (DatosInvalidosError, ServicioNoDisponibleError, ReservaError, CalculoInconsistenteError) as error:
            logging.error(f"Error al procesar reserva {self._id_reserva}: {error}")
            if self._estado == Reserva.PENDIENTE:
                self._estado = Reserva.FALLIDA
            raise ReservaError(f"No fue posible procesar la reserva {self._id_reserva}.") from error

        else:
            self._costo_total = costo
            logging.info(f"Reserva procesada: {self._id_reserva} - Costo: {self._costo_total}")
            return self._costo_total

        finally:
            logging.info(f"Finalizó el procesamiento de la reserva {self._id_reserva}")

    def obtener_estado(self):
        return self._estado

    def obtener_id(self):
        return self._id_reserva

    def describir(self):
        return (
            f"Reserva: {self._id_reserva} | "
            f"Cliente: {self._cliente.obtener_nombre()} | "
            f"Servicio: {self._servicio.obtener_nombre()} | "
            f"Duración: {self._duracion} h | "
            f"Estado: {self._estado} | "
            f"Costo: ${self._costo_total:,.0f}"
        )


# =============================================================================
# SISTEMA PRINCIPAL
# =============================================================================

class SistemaSoftwareFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El objeto proporcionado no es un cliente válido.")

        for registrado in self.clientes:
            if registrado.obtener_identificacion() == cliente.obtener_identificacion():
                raise DatosInvalidosError("Ya existe un cliente con esa identificación.")

        self.clientes.append(cliente)
        logging.info(f"Cliente registrado: {cliente.obtener_identificacion()}")

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El objeto proporcionado no es un servicio válido.")

        for registrado in self.servicios:
            if registrado.obtener_id() == servicio.obtener_id():
                raise DatosInvalidosError("Ya existe un servicio con ese ID.")

        self.servicios.append(servicio)
        logging.info(f"Servicio registrado: {servicio.obtener_id()}")

    def registrar_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise DatosInvalidosError("El objeto proporcionado no es una reserva válida.")

        for registrada in self.reservas:
            if registrada.obtener_id() == reserva.obtener_id():
                raise DatosInvalidosError("Ya existe una reserva con ese ID.")

        self.reservas.append(reserva)
        logging.info(f"Reserva registrada: {reserva.obtener_id()}")

    def crear_reserva(self, id_reserva, id_cliente, id_servicio, duracion, descuento=0, impuesto=None):
        try:
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(id_servicio)
        except DatosInvalidosError as error:
            raise ReservaError("No se pudo crear la reserva: datos de referencia inexistentes.") from error

        reserva = Reserva(id_reserva, cliente, servicio, duracion, descuento, impuesto)
        self.registrar_reserva(reserva)
        return reserva.procesar()

    def buscar_cliente(self, identificacion):
        for cliente in self.clientes:
            if cliente.obtener_identificacion() == str(identificacion):
                return cliente
        raise DatosInvalidosError(f"Cliente no encontrado: {identificacion}.")

    def buscar_servicio(self, id_servicio):
        for servicio in self.servicios:
            if servicio.obtener_id() == str(id_servicio):
                return servicio
        raise DatosInvalidosError(f"Servicio no encontrado: {id_servicio}.")

    def buscar_reserva(self, id_reserva):
        for reserva in self.reservas:
            if reserva.obtener_id() == str(id_reserva):
                return reserva
        raise ReservaError(f"Reserva no encontrada: {id_reserva}.")

    def listar_clientes(self):
        return [cliente.describir() for cliente in self.clientes]

    def listar_servicios(self):
        return [servicio.describir() for servicio in self.servicios]

    def listar_reservas(self):
        return [reserva.describir() for reserva in self.reservas]


# =============================================================================
# SIMULACIÓN DE OPERACIONES
# =============================================================================

def ejecutar_operacion(numero, descripcion, accion):
    print(f"\nOperación {numero}: {descripcion}")
    logging.info(f"--- Inicio operación {numero}: {descripcion} ---")
    try:
        resultado = accion()
    except SoftwareFJError as error:
        print(f"   [ERROR CONTROLADO] {type(error).__name__}: {error}")
        if error.__cause__:
            print(f"   Causa original -> {type(error.__cause__).__name__}: {error.__cause__}")
        logging.error(f"Operación {numero} fallida: {error} | Causa: {error.__cause__}")
        return False
    except Exception as error:
        print(f"   [ERROR INESPERADO] {type(error).__name__}: {error}")
        logging.exception(f"Error inesperado en la operación {numero}")
        return False
    else:
        print(f"   [OK] {resultado}")
        logging.info(f"Operación {numero} exitosa: {resultado}")
        return True
    finally:
        logging.info(f"--- Fin operación {numero} ---")


def main():
    sistema = SistemaSoftwareFJ()
    print("=" * 70)
    print(" SOFTWARE FJ - Sistema de Gestión de Clientes, Servicios y Reservas")
    print("=" * 70)
    logging.info("========== Inicio de la simulación de Software FJ ==========")

    def nuevo_cliente(*datos):
        cliente = Cliente(*datos)
        sistema.registrar_cliente(cliente)
        return f"Cliente registrado -> {cliente.describir()}"

    def nuevo_servicio(clase, *datos):
        servicio = clase(*datos)
        sistema.registrar_servicio(servicio)
        return f"Servicio registrado -> {servicio.describir()}"

    def nueva_reserva(*datos, **opciones):
        costo = sistema.crear_reserva(*datos, **opciones)
        return f"Reserva {datos[0]} confirmada. Costo total: ${costo:,.2f}"

    def cancelar(id_reserva):
        sistema.buscar_reserva(id_reserva).cancelar()
        return f"Reserva {id_reserva} cancelada y servicio liberado."

    operaciones = [
        ("Registrar cliente válido",
         lambda: nuevo_cliente("1098765432", "Laura Gómez", "laura.gomez@mail.com", "3001234567")),
        ("Registrar segundo cliente válido",
         lambda: nuevo_cliente("1005123456", "Carlos Pérez", "carlos.perez@mail.com", "3157654321")),
        ("Registrar cliente con correo inválido",
         lambda: nuevo_cliente("1122334455", "Ana Ruiz", "ana.ruiz-mail.com", "3209876543")),
        ("Registrar cliente sin nombre (parámetro faltante)",
         lambda: nuevo_cliente("1199887766", None, "pedro@mail.com", "3101112233")),
        ("Registrar cliente con identificación duplicada",
         lambda: nuevo_cliente("1098765432", "Laura Gómez", "laura2@mail.com", "3001234567")),
        ("Crear servicio de sala válido",
         lambda: nuevo_servicio(ServicioSala, "S01", "Sala de juntas", 50000, 12)),
        ("Crear servicio de equipo válido (1 unidad)",
         lambda: nuevo_servicio(ServicioEquipo, "E01", "Video beam", 30000, 1)),
        ("Crear servicio de asesoría válido",
         lambda: nuevo_servicio(ServicioAsesoria, "A01", "Asesoría en seguridad", 120000, "Ciberseguridad")),
        ("Crear sala con tarifa negativa",
         lambda: nuevo_servicio(ServicioSala, "S02", "Auditorio", -80000, 100)),
        ("Crear asesoría sin especialidad",
         lambda: nuevo_servicio(ServicioAsesoria, "A02", "Asesoría general", 90000, "   ")),
        ("Reservar sala 3 h con 10 % de descuento",
         lambda: nueva_reserva("R01", "1098765432", "S01", 3, descuento=10)),
        ("Reservar asesoría 2 h con IVA (19 %)",
         lambda: nueva_reserva("R02", "1005123456", "A01", 2, impuesto=True)),
        ("Reservar video beam 8 h con descuento e IVA del 19 %",
         lambda: nueva_reserva("R03", "1005123456", "E01", 8, descuento=5, impuesto=19)),
        ("Reservar video beam agotado (servicio no disponible)",
         lambda: nueva_reserva("R04", "1098765432", "E01", 2)),
        ("Reservar con duración negativa",
         lambda: nueva_reserva("R05", "1098765432", "S01", -4)),
        ("Reservar con descuento fuera de rango",
         lambda: nueva_reserva("R06", "1098765432", "A01", 1, descuento=150)),
        ("Reservar para un cliente inexistente",
         lambda: nueva_reserva("R07", "999", "S01", 2)),
        ("Cancelar reserva R03 (libera el video beam)",
         lambda: cancelar("R03")),
        ("Reservar de nuevo el video beam liberado",
         lambda: nueva_reserva("R08", "1098765432", "E01", 2)),
        ("Cancelar dos veces la misma reserva (operación no permitida)",
         lambda: cancelar("R03")),
    ]

    exitosas = 0
    for numero, (descripcion, accion) in enumerate(operaciones, start=1):
        if ejecutar_operacion(numero, descripcion, accion):
            exitosas += 1

    # Muestra el estado final del sistema.
    print("\n" + "=" * 70)
    print(f" RESUMEN DE EJECUCIÓN: {exitosas}/{len(operaciones)} operaciones exitosas")
    print("=" * 70)

    print("\n--- Clientes registrados ---")
    for linea in sistema.listar_clientes():
        print("  *", linea)

    print("\n--- Servicios registrados ---")
    for linea in sistema.listar_servicios():
        print("  *", linea)

    print("\n--- Reservas registradas ---")
    for linea in sistema.listar_reservas():
        print("  *", linea)

    logging.info(f"Simulación finalizada: {exitosas}/{len(operaciones)} operaciones exitosas.")


if __name__ == "__main__":
    main()