# =============================================================================
# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programación (213023) - Fase 4
# Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas
# Empresa: Software FJ
# Descripción: Sistema orientado a objetos, sin base de datos, que gestiona
# clientes, servicios y reservas con manejo avanzado de excepciones y
# registro de eventos y errores en un archivo de logs.
# =============================================================================

from abc import ABC, abstractmethod  # Importa las herramientas para crear clases abstractas.
import logging  # Importa el módulo estándar para registrar eventos en archivos.

# Configura el archivo donde se registrarán eventos y errores del sistema.
logging.basicConfig(
    filename="software_fj.log",  # Nombre del archivo de logs.
    level=logging.INFO,  # Registra mensajes desde el nivel INFO en adelante.
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato: fecha - nivel - mensaje.
    encoding="utf-8"  # Permite guardar tildes y eñes correctamente.
)


# =============================================================================
# EXCEPCIONES PERSONALIZADAS
# =============================================================================

# Excepción base de la que heredan todas las excepciones del sistema.
class SoftwareFJError(Exception):
    pass  # No necesita lógica adicional; sirve para agrupar los errores propios.


# Excepción para datos ingresados incorrectamente.
class DatosInvalidosError(SoftwareFJError):
    pass  # Se lanza cuando un dato no cumple las validaciones.


# Excepción para parámetros obligatorios que no fueron enviados.
class ParametroFaltanteError(DatosInvalidosError):
    pass  # Se lanza cuando un parámetro llega vacío o como None.


# Excepción para servicios que no se encuentran disponibles.
class ServicioNoDisponibleError(SoftwareFJError):
    pass  # Se lanza cuando se intenta reservar un servicio ocupado.


# Excepción para errores relacionados con las reservas.
class ReservaError(SoftwareFJError):
    pass  # Se lanza ante operaciones no permitidas sobre una reserva.


# Excepción para cálculos de costo que producen resultados incoherentes.
class CalculoInconsistenteError(SoftwareFJError):
    pass  # Se lanza si un costo calculado resulta negativo o no numérico.


# =============================================================================
# FUNCIONES AUXILIARES DE VALIDACIÓN
# =============================================================================

def validar_texto(valor, campo):
    # Verifica que el parámetro haya sido enviado.
    if valor is None:
        raise ParametroFaltanteError(f"Falta el parámetro obligatorio: {campo}.")  # Parámetro ausente.
    # Verifica que el parámetro sea texto y no esté vacío.
    if not isinstance(valor, str) or not valor.strip():
        raise DatosInvalidosError(f"El campo '{campo}' no puede estar vacío.")  # Texto inválido.
    return valor.strip()  # Retorna el texto sin espacios sobrantes.


def validar_numero_positivo(valor, campo):
    # Verifica que el parámetro haya sido enviado.
    if valor is None:
        raise ParametroFaltanteError(f"Falta el parámetro obligatorio: {campo}.")  # Parámetro ausente.
    # Verifica que sea un número (se excluye bool porque en Python es subclase de int).
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise DatosInvalidosError(f"El campo '{campo}' debe ser numérico.")  # Tipo incorrecto.
    # Verifica que el número sea mayor que cero.
    if valor <= 0:
        raise DatosInvalidosError(f"El campo '{campo}' debe ser mayor que cero.")  # Valor fuera de rango.
    return valor  # Retorna el número validado.


# =============================================================================
# CLASE ABSTRACTA GENERAL
# =============================================================================

# Clase abstracta general para las entidades del sistema.
class Entidad(ABC):

    def __init__(self, identificacion):
        # Valida que la identificación exista y no esté vacía.
        if identificacion is None or not str(identificacion).strip():
            raise ParametroFaltanteError("La identificación no puede estar vacía.")  # Error de identificación.
        self._identificacion = str(identificacion).strip()  # Atributo protegido (encapsulación).

    def obtener_identificacion(self):
        # Retorna la identificación de la entidad.
        return self._identificacion

    @abstractmethod
    def describir(self):
        # Cada clase hija debe definir su propia descripción.
        pass


# =============================================================================
# CLASE CLIENTE
# =============================================================================

# Representa a un cliente del sistema.
class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion)  # Reutiliza la validación de la clase padre.

        # Valida que la identificación sea numérica (cédula o NIT).
        if not self._identificacion.isdigit():
            raise DatosInvalidosError("La identificación debe contener únicamente números.")

        nombre = validar_texto(nombre, "nombre")  # Valida que el nombre exista.
        correo = validar_texto(correo, "correo")  # Valida que el correo exista.
        telefono = validar_texto(telefono, "telefono")  # Valida que el teléfono exista.

        # Valida que el nombre solo tenga letras y espacios.
        if not nombre.replace(" ", "").isalpha():
            raise DatosInvalidosError("El nombre solo puede contener letras y espacios.")

        # Valida el correo: debe tener un único @ y un punto después de él.
        partes = correo.split("@")  # Separa el usuario del dominio.
        if len(partes) != 2 or not partes[0] or "." not in partes[1]:
            raise DatosInvalidosError("El correo electrónico no es válido.")

        # Valida que el teléfono contenga solo números y tenga 7 a 10 dígitos.
        if not telefono.isdigit() or not 7 <= len(telefono) <= 10:
            raise DatosInvalidosError("El teléfono debe tener entre 7 y 10 dígitos numéricos.")

        self.__nombre = nombre  # Atributo privado: solo accesible por métodos de la clase.
        self.__correo = correo  # Atributo privado del correo.
        self.__telefono = telefono  # Atributo privado del teléfono.

        logging.info(f"Cliente creado: {self._identificacion} - {self.__nombre}")  # Registra el evento.

    def obtener_nombre(self):
        # Retorna el nombre del cliente.
        return self.__nombre

    def obtener_correo(self):
        # Retorna el correo del cliente.
        return self.__correo

    def obtener_telefono_oculto(self):
        # Retorna el teléfono parcialmente oculto para proteger el dato personal.
        return "*" * (len(self.__telefono) - 4) + self.__telefono[-4:]

    def describir(self):
        # Sobrescribe el método abstracto de la clase Entidad.
        return (
            f"Cliente: {self.__nombre} | "
            f"ID: {self._identificacion} | "
            f"Correo: {self.__correo} | "
            f"Tel: {self.obtener_telefono_oculto()}"
        )


# =============================================================================
# CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS
# =============================================================================

# Clase abstracta para los servicios ofrecidos por Software FJ.
class Servicio(Entidad):

    IVA = 19  # Porcentaje de IVA vigente en Colombia, usado como valor por defecto.

    def __init__(self, id_servicio, nombre, tarifa_base):
        super().__init__(id_servicio)  # Valida el ID usando la clase Entidad.
        self._nombre = validar_texto(nombre, "nombre del servicio")  # Valida el nombre.
        self._tarifa_base = validar_numero_positivo(tarifa_base, "tarifa base")  # Valida la tarifa.
        self._disponible = True  # Todo servicio inicia disponible.

    def obtener_id(self):
        # Retorna el identificador del servicio.
        return self._identificacion

    def obtener_nombre(self):
        # Retorna el nombre del servicio.
        return self._nombre

    def esta_disponible(self):
        # Informa si el servicio se encuentra disponible.
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        # Cambia el estado de disponibilidad del servicio.
        if not isinstance(estado, bool):
            raise DatosInvalidosError("La disponibilidad debe ser True o False.")  # Valida el tipo.
        self._disponible = estado  # Actualiza el estado.

    def ocupar(self):
        # Marca el servicio como ocupado (las subclases pueden cambiar este comportamiento).
        self.cambiar_disponibilidad(False)

    def liberar(self):
        # Marca el servicio como disponible nuevamente.
        self.cambiar_disponibilidad(True)

    @abstractmethod
    def costo_base(self, duracion):
        # Cada servicio define cómo calcula su costo antes de descuentos e impuestos.
        pass

    @abstractmethod
    def validar_parametros(self):
        # Cada servicio valida sus propios atributos específicos.
        pass

    def calcular_costo(self, duracion, descuento=0, impuesto=None):
        # Método "sobrecargado" mediante parámetros opcionales:
        #   calcular_costo(duracion)                      -> costo base sin impuesto.
        #   calcular_costo(duracion, descuento)           -> costo con descuento.
        #   calcular_costo(duracion, descuento, impuesto) -> costo con descuento e impuesto.
        #   calcular_costo(duracion, impuesto=True)       -> aplica el IVA por defecto (19 %).
        validar_numero_positivo(duracion, "duración")  # La duración debe ser positiva.

        # Valida que el descuento sea un porcentaje entre 0 y 100.
        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)) or not 0 <= descuento <= 100:
            raise DatosInvalidosError("El descuento debe ser un número entre 0 y 100.")

        # Interpreta el parámetro de impuesto según el tipo recibido.
        if impuesto is None or impuesto is False:
            porcentaje_impuesto = 0  # Sin impuesto.
        elif impuesto is True:
            porcentaje_impuesto = self.IVA  # Usa el IVA por defecto.
        elif isinstance(impuesto, (int, float)) and 0 <= impuesto <= 100:
            porcentaje_impuesto = impuesto  # Usa el porcentaje indicado.
        else:
            raise DatosInvalidosError("El impuesto debe ser True, False o un porcentaje entre 0 y 100.")

        base = self.costo_base(duracion)  # Polimorfismo: cada subclase calcula su base.
        con_descuento = base - base * descuento / 100  # Aplica el descuento.
        total = con_descuento + con_descuento * porcentaje_impuesto / 100  # Aplica el impuesto.

        # Verifica que el resultado sea coherente.
        if total < 0 or total != total:  # total != total detecta valores NaN.
            raise CalculoInconsistenteError(f"Costo inconsistente calculado: {total}")
        return round(total, 2)  # Retorna el costo redondeado a dos decimales.


# Servicio para reserva de salas.
class ServicioSala(Servicio):

    def __init__(self, id_servicio, nombre, tarifa_base, capacidad):
        super().__init__(id_servicio, nombre, tarifa_base)  # Inicializa los datos generales.
        self._capacidad = capacidad  # Guarda la capacidad de la sala.
        self.validar_parametros()  # Valida los datos propios de la sala.

    def validar_parametros(self):
        # Valida que la capacidad sea un número positivo.
        validar_numero_positivo(self._capacidad, "capacidad de la sala")

    def costo_base(self, duracion):
        # Salas con más de 20 personas tienen un recargo del 20 % por logística.
        recargo = 1.2 if self._capacidad > 20 else 1.0
        return self._tarifa_base * duracion * recargo  # Tarifa por hora x horas x recargo.

    def describir(self):
        # Retorna la información específica de la sala.
        return (
            f"Sala: {self._nombre} | "
            f"Capacidad: {self._capacidad} personas | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )


# Servicio para alquiler de equipos.
class ServicioEquipo(Servicio):

    def __init__(self, id_servicio, nombre, tarifa_base, cantidad_disponible):
        super().__init__(id_servicio, nombre, tarifa_base)  # Inicializa los datos generales.
        self._cantidad_disponible = cantidad_disponible  # Unidades de equipo disponibles.
        self.validar_parametros()  # Valida los datos propios del equipo.
        self._disponible = self._cantidad_disponible > 0  # Sin unidades, no está disponible.

    def validar_parametros(self):
        # Valida que la cantidad sea un entero no negativo.
        if not isinstance(self._cantidad_disponible, int) or isinstance(self._cantidad_disponible, bool):
            raise DatosInvalidosError("La cantidad disponible debe ser un número entero.")
        if self._cantidad_disponible < 0:
            raise DatosInvalidosError("La cantidad disponible no puede ser negativa.")

    def ocupar(self):
        # Sobrescribe ocupar: descuenta una unidad en lugar de bloquear todo el servicio.
        self._cantidad_disponible -= 1  # Reduce las unidades disponibles.
        if self._cantidad_disponible == 0:
            self.cambiar_disponibilidad(False)  # Se agota el inventario.

    def liberar(self):
        # Sobrescribe liberar: devuelve una unidad al inventario.
        self._cantidad_disponible += 1  # Aumenta las unidades disponibles.
        self.cambiar_disponibilidad(True)  # Vuelve a estar disponible.

    def costo_base(self, duracion):
        # Alquileres de 8 horas o más tienen 10 % de descuento por uso prolongado.
        factor = 0.9 if duracion >= 8 else 1.0
        return self._tarifa_base * duracion * factor  # Tarifa por hora x horas x factor.

    def describir(self):
        # Retorna la información específica del equipo.
        return (
            f"Equipo: {self._nombre} | "
            f"Disponibles: {self._cantidad_disponible} | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )


# Servicio de asesoría especializada.
class ServicioAsesoria(Servicio):

    # Recargo por especialidad (las especialidades no listadas no tienen recargo).
    RECARGOS = {"ciberseguridad": 1.25, "inteligencia artificial": 1.3}

    def __init__(self, id_servicio, nombre, tarifa_base, especialidad):
        super().__init__(id_servicio, nombre, tarifa_base)  # Inicializa los datos generales.
        self._especialidad = especialidad  # Guarda la especialidad sin validar todavía.
        self.validar_parametros()  # Valida los datos propios de la asesoría.

    def validar_parametros(self):
        # Valida que la asesoría tenga una especialidad definida.
        self._especialidad = validar_texto(self._especialidad, "especialidad")

    def costo_base(self, duracion):
        # Aplica el recargo según la especialidad del asesor.
        recargo = self.RECARGOS.get(self._especialidad.lower(), 1.0)
        return self._tarifa_base * duracion * recargo  # Tarifa por hora x horas x recargo.

    def describir(self):
        # Retorna la información específica de la asesoría.
        return (
            f"Asesoría: {self._nombre} | "
            f"Especialidad: {self._especialidad} | "
            f"Tarifa por hora: ${self._tarifa_base:,.0f}"
        )


# =============================================================================
# CLASE RESERVA
# =============================================================================

# Representa una reserva realizada por un cliente.
class Reserva:

    PENDIENTE = "PENDIENTE"  # Estado inicial de toda reserva.
    CONFIRMADA = "CONFIRMADA"  # Estado de una reserva procesada con éxito.
    CANCELADA = "CANCELADA"  # Estado de una reserva anulada.
    FALLIDA = "FALLIDA"  # Estado de una reserva que no se pudo procesar.

    def __init__(self, id_reserva, cliente, servicio, duracion, descuento=0, impuesto=None):
        # Valida el identificador de la reserva.
        if id_reserva is None or not str(id_reserva).strip():
            raise ParametroFaltanteError("El ID de la reserva no puede estar vacío.")

        # Valida que el cliente sea un objeto de la clase Cliente.
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El cliente proporcionado no es válido.")

        # Valida que el servicio sea un objeto de la clase Servicio.
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El servicio proporcionado no es válido.")

        validar_numero_positivo(duracion, "duración")  # Valida la duración.

        self._id_reserva = str(id_reserva).strip()  # Identificador de la reserva.
        self._cliente = cliente  # Cliente que realiza la reserva.
        self._servicio = servicio  # Servicio reservado.
        self._duracion = duracion  # Duración en horas.
        self._descuento = descuento  # Porcentaje de descuento.
        self._impuesto = impuesto  # Impuesto a aplicar (None, True o porcentaje).
        self._estado = Reserva.PENDIENTE  # Toda reserva inicia pendiente.
        self._costo_total = 0  # El costo se asigna al procesar.

    def confirmar(self):
        # Solo se pueden confirmar reservas pendientes.
        if self._estado != Reserva.PENDIENTE:
            raise ReservaError(f"La reserva ya fue procesada (estado: {self._estado}).")

        # Verifica que el servicio esté disponible.
        if not self._servicio.esta_disponible():
            raise ServicioNoDisponibleError(f"El servicio '{self._servicio.obtener_nombre()}' no está disponible.")

        self._estado = Reserva.CONFIRMADA  # Cambia el estado.
        self._servicio.ocupar()  # Polimorfismo: cada servicio se ocupa a su manera.
        logging.info(f"Reserva confirmada: {self._id_reserva}")  # Registra el evento.

    def cancelar(self):
        # No se puede cancelar dos veces la misma reserva.
        if self._estado == Reserva.CANCELADA:
            raise ReservaError("La reserva ya está cancelada.")

        # Si estaba confirmada, libera el servicio.
        if self._estado == Reserva.CONFIRMADA:
            self._servicio.liberar()

        self._estado = Reserva.CANCELADA  # Cambia el estado.
        logging.info(f"Reserva cancelada: {self._id_reserva}")  # Registra el evento.

    def procesar(self):
        # Procesa la reserva aplicando manejo avanzado de excepciones.
        try:
            # Calcula el costo usando el método sobrecargado del servicio.
            costo = self._servicio.calcular_costo(self._duracion, self._descuento, self._impuesto)
            self.confirmar()  # Intenta confirmar la reserva.

        except (DatosInvalidosError, ServicioNoDisponibleError, ReservaError, CalculoInconsistenteError) as error:
            # Registra el error en el archivo de logs.
            logging.error(f"Error al procesar reserva {self._id_reserva}: {error}")
            # Marca la reserva como fallida si no alcanzó a confirmarse.
            if self._estado == Reserva.PENDIENTE:
                self._estado = Reserva.FALLIDA
            # Encadena la excepción original con una excepción de reserva.
            raise ReservaError(f"No fue posible procesar la reserva {self._id_reserva}.") from error

        else:
            # Solo se ejecuta si no ocurrió ningún error.
            self._costo_total = costo  # Asigna el costo final.
            logging.info(f"Reserva procesada: {self._id_reserva} - Costo: {self._costo_total}")
            return self._costo_total  # Retorna el costo calculado.

        finally:
            # Siempre registra que terminó el intento de procesamiento.
            logging.info(f"Finalizó el procesamiento de la reserva {self._id_reserva}")

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
            f"Servicio: {self._servicio.obtener_nombre()} | "
            f"Duración: {self._duracion} h | "
            f"Estado: {self._estado} | "
            f"Costo: ${self._costo_total:,.0f}"
        )


# =============================================================================
# SISTEMA PRINCIPAL
# =============================================================================

# Sistema principal que administra clientes, servicios y reservas.
class SistemaSoftwareFJ:

    def __init__(self):
        # Crea las listas internas del sistema (sin base de datos).
        self.clientes = []  # Lista de clientes registrados.
        self.servicios = []  # Lista de servicios registrados.
        self.reservas = []  # Lista de reservas registradas.

    def registrar_cliente(self, cliente):
        # Verifica que el objeto recibido sea un cliente válido.
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El objeto proporcionado no es un cliente válido.")

        # Evita registrar identificaciones repetidas.
        for registrado in self.clientes:
            if registrado.obtener_identificacion() == cliente.obtener_identificacion():
                raise DatosInvalidosError("Ya existe un cliente con esa identificación.")

        self.clientes.append(cliente)  # Agrega el cliente a la lista.
        logging.info(f"Cliente registrado: {cliente.obtener_identificacion()}")  # Registra el evento.

    def registrar_servicio(self, servicio):
        # Verifica que el objeto recibido sea un servicio válido.
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El objeto proporcionado no es un servicio válido.")

        # Evita registrar servicios con el mismo ID.
        for registrado in self.servicios:
            if registrado.obtener_id() == servicio.obtener_id():
                raise DatosInvalidosError("Ya existe un servicio con ese ID.")

        self.servicios.append(servicio)  # Agrega el servicio a la lista.
        logging.info(f"Servicio registrado: {servicio.obtener_id()}")  # Registra el evento.

    def registrar_reserva(self, reserva):
        # Verifica que el objeto recibido sea una reserva válida.
        if not isinstance(reserva, Reserva):
            raise DatosInvalidosError("El objeto proporcionado no es una reserva válida.")

        # Evita registrar reservas con identificaciones repetidas.
        for registrada in self.reservas:
            if registrada.obtener_id() == reserva.obtener_id():
                raise DatosInvalidosError("Ya existe una reserva con ese ID.")

        self.reservas.append(reserva)  # Agrega la reserva a la lista.
        logging.info(f"Reserva registrada: {reserva.obtener_id()}")  # Registra el evento.

    def crear_reserva(self, id_reserva, id_cliente, id_servicio, duracion, descuento=0, impuesto=None):
        # Busca el cliente y el servicio; si no existen, encadena el error.
        try:
            cliente = self.buscar_cliente(id_cliente)  # Busca el cliente.
            servicio = self.buscar_servicio(id_servicio)  # Busca el servicio.
        except DatosInvalidosError as error:
            raise ReservaError("No se pudo crear la reserva: datos de referencia inexistentes.") from error

        # Crea la reserva, la registra y la procesa.
        reserva = Reserva(id_reserva, cliente, servicio, duracion, descuento, impuesto)
        self.registrar_reserva(reserva)  # Guarda la reserva en la lista.
        return reserva.procesar()  # Procesa la reserva y retorna el costo.

    def buscar_cliente(self, identificacion):
        # Busca un cliente por su identificación.
        for cliente in self.clientes:
            if cliente.obtener_identificacion() == str(identificacion):
                return cliente  # Retorna el cliente encontrado.
        raise DatosInvalidosError(f"Cliente no encontrado: {identificacion}.")  # No existe.

    def buscar_servicio(self, id_servicio):
        # Busca un servicio por su identificador.
        for servicio in self.servicios:
            if servicio.obtener_id() == str(id_servicio):
                return servicio  # Retorna el servicio encontrado.
        raise DatosInvalidosError(f"Servicio no encontrado: {id_servicio}.")  # No existe.

    def buscar_reserva(self, id_reserva):
        # Busca una reserva por su identificador.
        for reserva in self.reservas:
            if reserva.obtener_id() == str(id_reserva):
                return reserva  # Retorna la reserva encontrada.
        raise ReservaError(f"Reserva no encontrada: {id_reserva}.")  # No existe.

    def listar_clientes(self):
        # Retorna la descripción de todos los clientes registrados.
        return [cliente.describir() for cliente in self.clientes]

    def listar_servicios(self):
        # Aplica polimorfismo al describir diferentes tipos de servicios.
        return [servicio.describir() for servicio in self.servicios]

    def listar_reservas(self):
        # Retorna la descripción de todas las reservas.
        return [reserva.describir() for reserva in self.reservas]


# =============================================================================
# SIMULACIÓN DE OPERACIONES
# =============================================================================

def ejecutar_operacion(numero, descripcion, accion):
    # Ejecuta una operación del sistema sin que un error detenga el programa.
    print(f"\nOperación {numero}: {descripcion}")  # Muestra la operación en consola.
    logging.info(f"--- Inicio operación {numero}: {descripcion} ---")  # Registra el inicio.
    try:
        resultado = accion()  # Ejecuta la función recibida.
    except SoftwareFJError as error:
        # Error controlado del sistema: se informa y se registra.
        print(f"   [ERROR CONTROLADO] {type(error).__name__}: {error}")
        if error.__cause__:  # Muestra la causa original si hubo encadenamiento.
            print(f"   Causa original -> {type(error.__cause__).__name__}: {error.__cause__}")
        logging.error(f"Operación {numero} fallida: {error} | Causa: {error.__cause__}")
        return False  # Indica que la operación falló.
    except Exception as error:
        # Error inesperado: se registra con traza completa y el sistema continúa.
        print(f"   [ERROR INESPERADO] {type(error).__name__}: {error}")
        logging.exception(f"Error inesperado en la operación {numero}")
        return False  # Indica que la operación falló.
    else:
        # Solo se ejecuta si la operación fue exitosa.
        print(f"   [OK] {resultado}")
        logging.info(f"Operación {numero} exitosa: {resultado}")
        return True  # Indica que la operación fue exitosa.
    finally:
        # Se ejecuta siempre, haya o no error.
        logging.info(f"--- Fin operación {numero} ---")


def main():
    # Punto de entrada del programa.
    sistema = SistemaSoftwareFJ()  # Crea el sistema con sus listas vacías.
    print("=" * 70)
    print(" SOFTWARE FJ - Sistema de Gestión de Clientes, Servicios y Reservas")
    print("=" * 70)
    logging.info("========== Inicio de la simulación de Software FJ ==========")

    # Funciones auxiliares que crean y registran objetos en un solo paso.
    def nuevo_cliente(*datos):
        cliente = Cliente(*datos)  # Crea el cliente (aquí se validan los datos).
        sistema.registrar_cliente(cliente)  # Lo registra en la lista.
        return f"Cliente registrado -> {cliente.describir()}"

    def nuevo_servicio(clase, *datos):
        servicio = clase(*datos)  # Crea el servicio del tipo indicado.
        sistema.registrar_servicio(servicio)  # Lo registra en la lista.
        return f"Servicio registrado -> {servicio.describir()}"

    def nueva_reserva(*datos, **opciones):
        costo = sistema.crear_reserva(*datos, **opciones)  # Crea y procesa la reserva.
        return f"Reserva {datos[0]} confirmada. Costo total: ${costo:,.2f}"

    def cancelar(id_reserva):
        sistema.buscar_reserva(id_reserva).cancelar()  # Busca y cancela la reserva.
        return f"Reserva {id_reserva} cancelada y servicio liberado."

    # Lista de operaciones a simular: (descripción, acción).
    operaciones = [
        # --- Registro de clientes ---
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
        # --- Creación de servicios ---
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
        # --- Reservas ---
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
        # --- Cancelaciones ---
        ("Cancelar reserva R03 (libera el video beam)",
         lambda: cancelar("R03")),
        ("Reservar de nuevo el video beam liberado",
         lambda: nueva_reserva("R08", "1098765432", "E01", 2)),
        ("Cancelar dos veces la misma reserva (operación no permitida)",
         lambda: cancelar("R03")),
    ]

    exitosas = 0  # Contador de operaciones exitosas.
    for numero, (descripcion, accion) in enumerate(operaciones, start=1):
        if ejecutar_operacion(numero, descripcion, accion):  # Ejecuta cada operación.
            exitosas += 1  # Suma si fue exitosa.

    # Muestra el estado final del sistema.
    print("\n" + "=" * 70)
    print(f" RESUMEN: {exitosas} operaciones exitosas y "
          f"{len(operaciones) - exitosas} fallidas controladas de {len(operaciones)}.")
    print("=" * 70)
    print("\nClientes registrados:")
    for linea in sistema.listar_clientes():
        print("  -", linea)
    print("\nServicios registrados:")
    for linea in sistema.listar_servicios():
        print("  -", linea)
    print("\nReservas registradas:")
    for linea in sistema.listar_reservas():
        print("  -", linea)
    print("\nEl detalle de eventos y errores quedó en el archivo software_fj.log")
    logging.info("========== Fin de la simulación: el sistema terminó sin interrupciones ==========")


# Ejecuta la simulación solo si el archivo se corre directamente.
if __name__ == "__main__":
    main()
