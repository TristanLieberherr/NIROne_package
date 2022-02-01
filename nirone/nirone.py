import logging
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.interfaces import Singleton
from ctypes import BigEndianStructure, Union, c_uint16, c_uint32, c_int16, c_float
from cachetools import TTLCache, cached



class Commands(Singleton):
    MODE_NORMAL         = 0x0000
    MODE_ECHANTILLONAGE = 0x0001
    MODE_ETALONNAGE     = 0x0002
    RECETTE_PC          = 0x0010
    RECETTE_TOR         = 0x0020
    RECETTE_COM2        = 0x0030
    ECHANTILLONAGE      = 0x0100
    ETALONNAGE          = 0x0202


class ErrorBits(BigEndianStructure):
    _fields_ = [
        ("lamp_OFF", c_uint16, 1),
        ("regulation_error", c_uint16, 1),
        ("signal_overflow", c_uint16, 1),
        ("signal_underflow", c_uint16, 1),
        ("engine_OFF", c_uint16, 1),
        ("unused", c_uint16, 9),
        ("message_not_refreshed", c_uint16, 1)
    ]


class CtrlIrpRaw(BigEndianStructure):
    _fields_ = [("words", c_uint16 * 11)]


class CtrlIrpStruct(BigEndianStructure):
    _fields_ = [
        ("flag_erreur", ErrorBits),
        ("temperature", c_uint16),
        ("vitesse_moteur", c_uint16),
        ("cmpt_err_transmission", c_uint16),
        ("regul", c_int16),
        ("status", c_uint16),
        ("num_recette", c_uint16),
        ("mode_irp", c_uint16),
        ("vide1", c_uint16),
        ("vide2", c_uint32)
    ]


class CtrlIrpUnion(Union):
    _fields_ = [("raw", CtrlIrpRaw), ("struct", CtrlIrpStruct)]


class ValVoieRaw(BigEndianStructure):
    _fields_ = [("words", c_uint16 * 8)]


class ValVoieStruct(BigEndianStructure):
    _fields_ = [
        ("n_recette", c_uint16),
        ("flag_erreur", c_uint16),
        ("voie1", c_float),
        ("voie2", c_float),
        ("signal", c_uint32)
    ]


class ValVoieUnion(Union):
    _fields_ = [("raw", ValVoieRaw), ("struct", ValVoieStruct)]


class NIROne(ModbusSerialClient):
    def __init__(self, method="rtu", **kwargs):
        """ Initialize a serial client instance

        The methods to connect are::

          - ascii
          - rtu
          - binary

        :param method: The method to use for connection
        :param port: The serial port to attach to
        :param stopbits: The number of stop bits to use
        :param bytesize: The bytesize of the serial messages
        :param parity: Which kind of parity to use
        :param baudrate: The baud rate to use for the serial device
        :param timeout: The timeout between serial requests (default 3s)
        :param strict:  Use Inter char timeout for baudrates <= 19200 (adhere
        to modbus standards)
        :param handle_local_echo: Handle local echo of the USB-to-RS485 adaptor
        """
        super().__init__(method, **kwargs)
        ## Constants
        self.__ADDRESS_COMMANDE     = 0x6000
        self.__ADDRESS_NUMRECETTE   = 0x9000
        self.__ADDRESS_CTRLIRP      = 0x3000
        self.__ADDRESS_VALVOIES     = 0x7000
        self.__ADDRESS_COMMANDE     = 0x6000
        ## Attributes
        self._values_union = ValVoieUnion()
        self._ctrlirp_union = CtrlIrpUnion()

    ## Read methods
    @cached(cache=TTLCache(maxsize=1024, ttl=0.05))
    def read_controldata(self) -> CtrlIrpStruct:
        response = self.read_holding_registers(self.__ADDRESS_CTRLIRP, 11, unit=0x01)
        try:
            for i, word in enumerate(response.registers) :
                self._ctrlirp_union.raw.words[i] = word
        except Exception as e:
            logging.error(e)
        finally:
            return self._ctrlirp_union.struct

    @cached(cache=TTLCache(maxsize=1024, ttl=0.05))
    def read_values(self) -> ValVoieStruct:
        response = self.read_holding_registers(self.__ADDRESS_VALVOIES, 8, unit=0x01)
        try:
            for i, word in enumerate(response.registers) :
                self._values_union.raw.words[i] = word
        except Exception as e:
            logging.error(e)
        finally:
            return self._values_union.struct

    ## Write methods
    def write_command(self, value):
        return self.write_register(self.__ADDRESS_COMMANDE, value, unit=0x01)

    def write_recipe(self, command):
        return self.write_register(self.__ADDRESS_NUMRECETTE, command, unit=0x01)