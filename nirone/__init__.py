from .nirone import NIROne, Commands, ErrorBits, CtrlIrpStruct, ValVoieStruct


try:
    from . import version
    __version__ = version.version
except ImportError:
    __version__ = None

__copyright__ = 'Copyright 2020 HEIG-VD'