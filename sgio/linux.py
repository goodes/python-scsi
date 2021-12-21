import ctypes
import fcntl
import struct

from construct import Struct, Int32sn, Int8un,Int16un, Int32un, Int64un, Padding, IfThenElse, Pass

from sgio.constants import SG_INFO_OK_MASK, SD_INFO_OK, SG_IO, TIMEOUT
from sgio.constants import SG_DXFER_TO_DEV, SG_DXFER_FROM_DEV, SG_DXFER_NONE
from sgio.errors import UnspecifiedError, CheckConditionError

IS_64_BIT = struct.calcsize("P") == 8

sg_io_hdr = Struct(
    "interface_id" / Int32sn,  # int interface_id
    "dxfer_direction" / Int32sn,  # int dxfer_direction
    "cmd_len" / Int8un,  # unsigned char cmd_len
    "mx_sb_len" / Int8un,  # unsigned char mx_sb_len
    "iovec_count" / Int16un,  # unsigned short int iovec_count
    "dxfer_len" / Int32un,  # unsigned int dxfer_len
    "dxferp" / IfThenElse(IS_64_BIT, Int64un, Int32un),  # unsigned char * dxferp
    "cmdp" / IfThenElse(IS_64_BIT, Int64un, Int32un),  # unsigned char * cmdp
    "sbp" / IfThenElse(IS_64_BIT, Int64un, Int32un),  # unsigned char * sbp
    "timeout" / Int32un,  # unsigned int timeout
    "flags" / Int32un,  # unsigned int flags
    "pack_id" / Int32sn,  # int pack_id
    IfThenElse(IS_64_BIT, Padding(4), Pass),
    "usr_ptr" / IfThenElse(IS_64_BIT, Int64un, Int32un),  # void * usr_ptr
    "status" / Int8un,  # unsigned char status
    "masked_status" / Int8un,  # unsigned char masked_status
    "msg_status" / Int8un,  # unsigned char msg_status
    "sb_len_wr" / Int8un,  # unsigned char sb_len_wr
    "host_status" / Int16un,  # unsigned short int host_status
    "driver_status" / Int16un,  # unsigned short int driver_status
    "resid" / Int32sn,  # int resid
    "duration" / Int32un,  # unsigned int duration
    "info" / Int32un,  # unsigned int info
)

def execute(
    file_handle,
    cdb: bytearray,
    data_out: bytearray,
    data_in: bytearray,
    max_sense_data_length:int = 32,
    ):

    if data_out is not None and len(data_out) and data_in is not None and len(data_in):
        raise NotImplemented('Indirect IO is not suported')
    elif data_out is not None and len(data_out):
        dxfer_direction = SG_DXFER_TO_DEV
        data_buffer = data_out
    elif data_in is not None and len(data_in):
        dxfer_direction = SG_DXFER_FROM_DEV
        data_buffer = data_in
    else:
        dxfer_direction = SG_DXFER_NONE
        data_buffer = []

    if data_buffer is not None and data_buffer:
        c_buffer = ctypes.c_char * len(data_buffer)
        dxferp = ctypes.addressof(c_buffer.from_buffer(data_buffer))
    else:
        dxferp = 0

    sense_buffer = ctypes.create_string_buffer(max_sense_data_length)
    sbp = ctypes.addressof(sense_buffer)

    cdb_buffer = ctypes.c_char * len(cdb)
    cmdp = ctypes.addressof(cdb_buffer.from_buffer(cdb))

    io_hdr = sg_io_hdr.build(dict(
        interface_id = ord('S'),
        dxfer_direction = dxfer_direction,
        cmd_len = len(cdb),
        mx_sb_len = max_sense_data_length,
        iovec_count = 0,
        dxfer_len = len(data_buffer),
        dxferp = dxferp,
        cmdp = cmdp,
        sbp = sbp,
        timeout = TIMEOUT,
        flags = 0,
        pack_id = 0,
        usr_ptr = 0,
        status = 0,
        masked_status = 0,
        msg_status = 0,
        sb_len_wr = 0,
        host_status = 0,
        driver_status = 0,
        resid = 0,
        duration = 0,
        info = 0,
    ))

    result = fcntl.ioctl(file_handle.fileno(), SG_IO, io_hdr)

    resp = sg_io_hdr.parse(result)

    if resp.info & SG_INFO_OK_MASK != SD_INFO_OK:
        if resp.sb_len_wr > 0:
            raise CheckConditionError(bytes(sense_buffer[:resp.sb_len_wr]))
        else:
            raise UnspecifiedError()

    return resp.resid
