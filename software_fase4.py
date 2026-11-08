from abc import ABC, abstractmethod
import logging

# Configura el archivo donde se registrarán eventos y errores del sistema.
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Excepción para datos ingresados incorrectamente.
class DatosInvalidosError(Exception):
    pass


# Excepción para servicios que no se encuentran disponibles.
class ServicioNoDisponibleError(Exception):
    pass


# Excepción para errores relacionados con las reservas.
class ReservaError(Exception):
    pass

# Clase abstracta general para las entidades del sistema.
class Entidad(ABC):

    def __init__(self, identificacion):
        # Valida que la identificación exista.
        if not str(identificacion).strip():
            raise DatosInvalidosError(
                "La identificación no puede estar vacía."
            )

        self._identificacion = str(identificacion).strip()

    def obtener_identificacion(self):
        # Retorna la identificación de la entidad.
        return self._identificacion

    @abstractmethod
    def describir(self):
        # Cada clase hija debe definir su propia descripción.
        pass


# Representa a un cliente del sistema.
class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion)

        # Valida el nombre del cliente.
        if not nombre.strip():
            raise DatosInvalidosError(
                "El nombre del cliente no puede estar vacío."
            )

        # Realiza una validación básica del correo electrónico.
        if "@" not in correo or "." not in correo:
            raise DatosInvalidosError(
                "El correo electrónico no es válido."
            )

        # Valida que el teléfono contenga solo números.
        if not telefono.isdigit():
            raise DatosInvalidosError(
                "El teléfono debe contener únicamente números."
            )

        self._nombre = nombre.strip()
        self._correo = correo.strip()
        self._telefono = telefono.strip()

        logging.info(
            f"Cliente creado: {self._identificacion} - {self._nombre}"
        )

    def obtener_nombre(self):
        # Retorna el nombre del cliente.
        return self._nombre

    def describir(self):
        # Sobrescribe el método abstracto de la clase Entidad.
        return (
            f"Cliente: {self._nombre} | "
            f"ID: {self._identificacion} | "
            f"Correo: {self._correo}"
        )

    # Clase abstracta para los servicios ofrecidos por Software FJ.
class Servicio(ABC):

    def __init__(self, id_servicio, nombre, tarifa_base):
        # Valida los datos generales del servicio.
        if not str(id_servicio).strip():
            raise DatosInvalidosError(
                "El ID del servicio no puede estar vacío."
            )

        if not nombre.strip():
            raise DatosInvalidosError(
                "El nombre del servicio no puede estar vacío."
            )

        if tarifa_base <= 0:
            raise DatosInvalidosError(
                "La tarifa base debe ser mayor que cero."
            )

        self._id_servicio = str(id_servicio).strip()
        self._nombre = nombre.strip()
        self._tarifa_base = tarifa_base
        self._disponible = True

    def obtener_id(self):
        # Retorna el identificador del servicio.
        return self._id_servicio

    def esta_disponible(self):
        # Informa si el servicio se encuentra disponible.
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        # Cambia el estado de disponibilidad del servicio.
        self._disponible = estado

    @abstractmethod
    def calcular_costo(self, duracion, descuento=0):
        pass

    @abstractmethod
    def validar_parametros(self):
        pass

    @abstractmethod
    def describir(self):
        pass


# Servicio para reserva de salas.
class ServicioSala(Servicio):

    def __init__(
        self,
        id_servicio,
        nombre,
        tarifa_base,
        capacidad
    ):
        super().__init__(
            id_servicio,
            nombre,
            tarifa_base
        )

        self._capacidad = capacidad
        self.validar_parametros()

    def validar_parametros(self):
        # Valida que la capacidad de la sala sea correcta.
        if self._capacidad <= 0:
            raise DatosInvalidosError(
                "La capacidad de la sala debe ser mayor que cero."
            )

    def calcular_costo(self, duracion, descuento=0):
        # Calcula el costo según las horas de uso de la sala.
        if duracion <= 0:
            raise DatosInvalidosError(
                "La duración debe ser mayor que cero."
            )

        if descuento < 0 or descuento > 100:
            raise DatosInvalidosError(
                "El descuento debe estar entre 0 y 100."
            )

        costo = self._tarifa_base * duracion
        return costo - (costo * descuento / 100)

    def describir(self):
        # Retorna la información específica de la sala.
        return (
            f"Sala: {self._nombre} | "
            f"Capacidad: {self._capacidad} personas | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )


# Servicio para alquiler de equipos.
class ServicioEquipo(Servicio):

    def __init__(
        self,
        id_servicio,
        nombre,
        tarifa_base,
        cantidad_disponible
    ):
        super().__init__(
            id_servicio,
            nombre,
            tarifa_base
        )

        self._cantidad_disponible = cantidad_disponible
        self.validar_parametros()

    def validar_parametros(self):
        # Valida que exista al menos un equipo disponible.
        if self._cantidad_disponible < 0:
            raise DatosInvalidosError(
                "La cantidad disponible no puede ser negativa."
            )

    def calcular_costo(self, duracion, descuento=0):
        # Calcula el costo del alquiler del equipo.
        if duracion <= 0:
            raise DatosInvalidosError(
                "La duración debe ser mayor que cero."
            )

        if descuento < 0 or descuento > 100:
            raise DatosInvalidosError(
                "El descuento debe estar entre 0 y 100."
            )

        costo = self._tarifa_base * duracion
        return costo - (costo * descuento / 100)

    def describir(self):
        # Retorna la información específica del equipo.
        return (
            f"Equipo: {self._nombre} | "
            f"Disponibles: {self._cantidad_disponible} | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )


# Servicio de asesoría especializada.
class ServicioAsesoria(Servicio):

    def __init__(
        self,
        id_servicio,
        nombre,
        tarifa_base,
        especialidad
    ):
        super().__init__(
            id_servicio,
            nombre,
            tarifa_base
        )

        self._especialidad = especialidad.strip()
        self.validar_parametros()

    def validar_parametros(self):
        # Valida que la asesoría tenga una especialidad definida.
        if not self._especialidad:
            raise DatosInvalidosError(
                "La especialidad no puede estar vacía."
            )

    def calcular_costo(self, duracion, descuento=0):
        # Calcula el costo de la asesoría según su duración.
        if duracion <= 0:
            raise DatosInvalidosError(
                "La duración debe ser mayor que cero."
            )

        if descuento < 0 or descuento > 100:
            raise DatosInvalidosError(
                "El descuento debe estar entre 0 y 100."
            )

        costo = self._tarifa_base * duracion
        return costo - (costo * descuento / 100)

    def describir(self):
        # Retorna la información específica de la asesoría.
        return (
            f"Asesoría: {self._nombre} | "
            f"Especialidad: {self._especialidad} | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )

    # Representa una reserva realizada por un cliente.
class Reserva:

    def __init__(
        self,
        id_reserva,
        cliente,
        servicio,
        duracion,
        descuento=0
    ):
        # Valida los datos necesarios para crear la reserva.
        if not str(id_reserva).strip():
            raise DatosInvalidosError(
                "El ID de la reserva no puede estar vacío."
            )

        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError(
                "El cliente proporcionado no es válido."
            )

        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError(
                "El servicio proporcionado no es válido."
            )

        if duracion <= 0:
            raise DatosInvalidosError(
                "La duración debe ser mayor que cero."
            )

        self._id_reserva = str(id_reserva).strip()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._descuento = descuento
        self._estado = "PENDING"
        self._costo_total = 0

    def confirmar(self):
        # Confirma la reserva si el servicio está disponible.
        if self._estado != "PENDING":
            raise ReservaError(
                "La reserva ya fue procesada."
            )

        if not self._servicio.esta_disponible():
            raise ServicioNoDisponibleError(
                "El servicio no está disponible."
            )

        self._estado = "CONFIRMED"
        self._servicio.cambiar_disponibilidad(False)

        logging.info(
            f"Reserva confirmada: {self._id_reserva}"
        )

    def cancelar(self):
        # Cancela la reserva y libera nuevamente el servicio.
        if self._estado == "CANCELLED":
            raise ReservaError(
                "La reserva ya está cancelada."
            )

        if self._estado == "CONFIRMED":
            self._servicio.cambiar_disponibilidad(True)

        self._estado = "CANCELLED"

        logging.info(
            f"Reserva cancelada: {self._id_reserva}"
        )

    def procesar(self):
        # Procesa la reserva aplicando manejo avanzado de excepciones.
        try:
            costo = self._servicio.calcular_costo(
                self._duracion,
                self._descuento
            )

            self.confirmar()

        except (
            DatosInvalidosError,
            ServicioNoDisponibleError,
            ReservaError
        ) as error:

            logging.error(
                f"Error al procesar reserva "
                f"{self._id_reserva}: {error}"
            )

            # Encadena la excepción original con una excepción de reserva.
            raise ReservaError(
                "No fue posible procesar la reserva."
            ) from error

        else:
            # Solo se ejecuta si no ocurrió ningún error.
            self._costo_total = costo

            logging.info(
                f"Reserva procesada: {self._id_reserva} "
                f"- Costo: {self._costo_total}"
            )

            return self._costo_total

        finally:
            # Siempre registra que terminó el intento de procesamiento.
            logging.info(
                f"Finalizó el procesamiento de "
                f"la reserva {self._id_reserva}"
            )

    def obtener_estado(self):
        # Retorna el estado actual de la reserva.
        return self._estado
    
    def obtener_id(self):
        # Retorna el identificador de la reserva.
        return self._id_reserva

    def describir(self):
        # Retorna un resumen de la reserva.
        return (
            f"Reserva: {self._id_reserva} | "
            f"Cliente: {self._cliente.obtener_nombre()} | "
            f"Servicio: {self._servicio.describir()} | "
            f"Estado: {self._estado} | "
            f"Costo: ${self._costo_total:,.0f}"
        )

    # Sistema principal que administra clientes, servicios y reservas.
class SistemaSoftwareFJ:

    def __init__(self):
        # Crea las listas internas del sistema.
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        # Verifica que el objeto recibido sea un cliente válido.
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError(
                "El objeto proporcionado no es un cliente válido."
            )

        # Evita registrar identificaciones repetidas.
        for registrado in self.clientes:
            if (
                registrado.obtener_identificacion()
                == cliente.obtener_identificacion()
            ):
                raise DatosInvalidosError(
                    "Ya existe un cliente con esa identificación."
                )

        self.clientes.append(cliente)

        logging.info(
            f"Cliente registrado: "
            f"{cliente.obtener_identificacion()}"
        )

    def registrar_servicio(self, servicio):
        # Verifica que el objeto recibido sea un servicio válido.
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError(
                "El objeto proporcionado no es un servicio válido."
            )

        # Evita registrar servicios con el mismo ID.
        for registrado in self.servicios:
            if registrado.obtener_id() == servicio.obtener_id():
                raise DatosInvalidosError(
                    "Ya existe un servicio con ese ID."
                )

        self.servicios.append(servicio)

        logging.info(
            f"Servicio registrado: {servicio.obtener_id()}"
        )

    def registrar_reserva(self, reserva):
        # Verifica que el objeto recibido sea una reserva válida.
        if not isinstance(reserva, Reserva):
            raise DatosInvalidosError(
                "El objeto proporcionado no es una reserva válida."
            )

        # Evita registrar reservas con identificaciones repetidas.
        for registrada in self.reservas:
            if registrada.obtener_id() == reserva.obtener_id():
                raise DatosInvalidosError(
                    "Ya existe una reserva con ese ID."
                )

        self.reservas.append(reserva)

        logging.info(
            f"Reserva registrada: {reserva.obtener_id()}"
        )

    def buscar_cliente(self, identificacion):
        # Busca un cliente por su identificación.
        for cliente in self.clientes:
            if cliente.obtener_identificacion() == str(identificacion):
                return cliente

        raise DatosInvalidosError(
            "Cliente no encontrado."
        )

    def buscar_servicio(self, id_servicio):
        # Busca un servicio por su identificador.
        for servicio in self.servicios:
            if servicio.obtener_id() == str(id_servicio):
                return servicio

        raise DatosInvalidosError(
            "Servicio no encontrado."
        )

    def listar_clientes(self):
        # Retorna la descripción de todos los clientes registrados.
        return [
            cliente.describir()
            for cliente in self.clientes
        ]

    def listar_servicios(self):
        # Aplica polimorfismo al describir diferentes tipos de servicios.
        return [
            servicio.describir()
            for servicio in self.servicios
        ]

    def listar_reservas(self):
        # Retorna la descripción de todas las reservas.
        return [
            reserva.describir()
            for reserva in self.reservas
        ]

    