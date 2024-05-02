import ctypes
import io
import struct
import typing
import capstone
import keystone

from nylib.utils.win32 import memory as ny_mem
from ff_draw.mem import XivMem
from nylib.utils.win32.winapi import kernel32, MEMORY_STATE

if typing.TYPE_CHECKING:
    from . import Hacks

ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_64)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)


def cdata2pydata(cdata):
    if isinstance(cdata, ctypes.Array):
        return array2list(cdata)
    if isinstance(cdata, ctypes.Structure):
        return struct2dict(cdata)
    return getattr(cdata, 'value', cdata)


def array2list(array):
    if array._type_ == ctypes.c_uint8 or array._type_ == ctypes.c_int8 or array._type_ == ctypes.c_char:
        return bytes(array)
    return [cdata2pydata(v) for v in array]


def struct2dict(struct):
    return {k: cdata2pydata(getattr(struct, k)) for k, *_ in struct._fields_}


def pydata2cdata(pydata, cdata_type):
    if issubclass(cdata_type, ctypes.Array):
        return list2array(pydata, cdata_type)
    if issubclass(cdata_type, ctypes.Structure):
        return dict2struct(pydata, cdata_type)
    return pydata


def list2array(pydata, cdata_type):
    if cdata_type._type_ == ctypes.c_uint8 or cdata_type._type_ == ctypes.c_int8 or cdata_type._type_ == ctypes.c_char:
        return cdata_type.from_buffer_copy(pydata)
    if cdata_type._type_ == ctypes.c_wchar:
        return pydata
    l = cdata_type()
    for i, v in enumerate(pydata):
        l[i] = pydata2cdata(v, cdata_type._type_)
    return l


def dict2struct(d, struct_type):
    s = struct_type()
    for k, cdata_type in struct_type._fields_:
        if k in d:
            setattr(s, k, pydata2cdata(d[k], cdata_type))
    return s


class Patch:
    def __init__(self, at, repl):
        mem = XivMem.instance
        self.handle = mem.handle
        self.at = at
        self.repl = repl
        self.orig = mem.scanner_v2.get_original_text(self.at, len(self.repl))

    state = property(
        lambda self: ny_mem.read_bytes(self.handle, self.at, len(self.repl)) != self.orig,
        lambda self, value: ny_mem.write_bytes(self.handle, self.at, self.repl if value else self.orig)
    )


hacks = []


class Hack:
    def __init__(self, main: 'Hacks'):
        self.main = main

    def draw_panel(self):
        pass

    def on_cmd(self, args):
        pass

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        hacks.append(cls)


class ShellInject:
    jmp_code = 'jmp {shell_at:#X};'
    back_code = ''

    def __init__(self, inject_at, shell_code=None, jmp_code=None, back_code=None, size=0x1000):
        self.mem = XivMem.instance
        self.handle = self.mem.handle
        self.inject_at = inject_at
        self.shell_at = ny_mem.alloc_near(self.mem.handle, size, inject_at)
        self.size = size

        self.shell_code = shell_code
        self.jmp_code = jmp_code or self.jmp_code
        self.back_code = back_code or self.back_code

        if self.shell_code is None:
            self.inject_bytes = None
            self.shell_bytes = None
            self.original_bytes = self.mem.scanner_v2.get_original_text(self.inject_at, 0x10)
        else:
            self.compile()

    def compile(self):
        jmp_bytes = ks.asm(self.jmp_code.format(
            shell_at=self.shell_at,
        ), self.inject_at)[0] or []
        jmp_size = len(jmp_bytes)
        back_bytes = ks.asm(self.back_code.format(
        ), self.inject_at + jmp_size)[0] or []
        back_size = len(back_bytes)

        take_size = jmp_size + back_size
        orig_bytes = self.mem.scanner_v2.get_original_text(self.inject_at, take_size + 0x20)
        take_size_it = (inst.address for inst in md.disasm(orig_bytes, 0) if inst.address >= take_size)
        take_size = next(take_size_it)
        orig_bytes = orig_bytes[:take_size]
        taken_code = ''
        for inst in md.disasm(orig_bytes, 0):
            mnemonic = inst.mnemonic
            if mnemonic[0] == 'j' or mnemonic == 'call':
                raise NotImplementedError(f"{mnemonic} not supported")  # TODO: remap offset
            taken_code += f"{inst.mnemonic} {inst.op_str};"
        shell_bytes = ks.asm(self.shell_code.format(
            taken=taken_code,
            shell_at=self.shell_at,
            return_at=self.inject_at + jmp_size,
        ), self.shell_at)[0] or []
        shell_size = len(shell_bytes)

        if shell_size > self.size:
            raise NotImplementedError("shell too large")  # TODO: realloc
        self.inject_bytes = bytes(jmp_bytes or []) + bytes(back_bytes or [])
        if len(self.inject_bytes) < take_size:
            self.inject_bytes += b'\x90' * (take_size - len(self.inject_bytes))
        self.shell_bytes = bytes(shell_bytes or [])
        self.original_bytes = orig_bytes

        ny_mem.write_bytes(self.handle, self.shell_at, self.shell_bytes)

    @property
    def state(self):
        return ny_mem.read_bytes(self.handle, self.inject_at, len(self.inject_bytes)) != self.original_bytes

    @state.setter
    def state(self, value):
        if value:
            self.enable()
        else:
            self.disable()

    def enable(self):
        if self.inject_bytes is None: raise RuntimeError("not compiled")
        ny_mem.write_bytes(self.handle, self.inject_at, self.inject_bytes)

    def disable(self):
        ny_mem.write_bytes(self.handle, self.inject_at, self.original_bytes)

    def __del__(self):
        self.disable()
        kernel32.VirtualFreeEx(self.handle, self.shell_at, self.size, MEMORY_STATE.MEM_RELEASE)
