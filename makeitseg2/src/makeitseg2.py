from struct import calcsize, unpack_from, pack_into
import obspy
from header import BINARY_FILE_HEADER_FORMAT, TRACE_HEADER_FORMAT
from formats import format_fh, TraceFormat
import os, datetime

def convert(filename, newFileName=None, **kwargs):
    """
    filename    : str | segy or su file name with location
    newFileName : str | seg2 file name if not
                provided new file will be saved 
                as segy file name with .dat extension
                in "Converted_SEG2" folder
    **kwargs : attribute dict contains

            DATE_TYPE : int | 1: 16-bit ; 2: 32-bit; 
            3: 20-bit, 4: 32-bit
            ======== File Desc Block ==========
            CLIENT : str | file description
                        Block CLIENT
            UNIT :    int | file description
                        Block Note 
            COMPANY : str | file description
                        Block COMPANY       
            INSTRUMENT : str | file description
                        Block INSTRUMENT
            OBSERVER : str | file description
                        Block OBSERVER
            File_NOTE : dict | file description
                        Block Note 
            
            ======== Trace Desc Block ==========
            for each atrribute listed here if only one 
            value is provieded inside the list then
            that value will be assigned for each traces.

            DESCALING_FACTOR : list() | Trace desc block
                        DESCALING FACTOR for each trace. 
            
            RECEIVER : list() | Reciver type
            RECEIVER_SPECS : list | Reciver Specification
            SKEW :  list | SKEW in each trace
            SOURCE : list(<source type>, <Source Param>) |
            Trace_NOTE : Dict | Trace Desc Block Note
            

    """
    
    # File opening
    strm = obspy.read(filename, unpack_trace_headers=True)

    # binary file header and 1st trace header opening for geting buffer size
    if filename.split('.')[-1] == 'su':
        trhead = strm[0].stats.su.trace_header
        binhead = None
        unit, jobid, tsort = [0, 0, 0]
        ftype = 'su'

    elif filename.split('.')[-1] == 'segy':
        trhead = strm[0].stats.segy.trace_header
        binhead = strm.stats.binary_file_header
        unit, jobid, tsort = [binhead.measurement_system, 
            binhead.job_identification_number, binhead.trace_sorting_code]
        ftype = 'segy'
    else:
        raise 'invalid file extention'

    # Strings for File Descriptor Block
    year =trhead.year_data_recorded; day = trhead.day_of_year
    if year==0:    
        today = datetime.date.today()
        year = today.year
    if day==0:
        today = datetime.date.today()
        day = today.day
    info = {
        'day': day,
        'year': year,
        'hh': trhead.hour_of_day,
        'mm': trhead.minute_of_hour,
        'ss': trhead.second_of_minute,
        'jobid': jobid,
        'tsort' : tsort,
        'unit': unit
    }

    fh_dict= dict()
    for k in list(BINARY_FILE_HEADER_FORMAT.keys()):
        fh_dict.update({k: format_fh(k, info)})

    #String of 1st Trace Descriptor Block
    trfmt = TraceFormat(fh_dict=binhead, file=filename)
    th_dict = dict()
    for key in list(TRACE_HEADER_FORMAT.keys()):
        th_dict.update({key: trfmt.format_th(key, strm[0].stats[ftype].trace_header, ftype=ftype)})

    #String Block of FBD
    st = '\x00'  # string terminetor
    str = ''
    for k in list(fh_dict.keys()):
        s = f'{k} {fh_dict[k]}'
        size = chr(len(s)+3)
        str += f'{size}{st}{s}{st}'    

    str = str[:-1] + f'\n\n{5*chr(0)}'
    fbd_sb = bytes(str, 'ascii')
    fbd_sb_size = len(str)
    #print(fbd_sb_size, fbd_sb)

    #String Block of 1st TBD
    st = '\x00'  # string terminetor
    str = ''
    for k in list(th_dict.keys()):
        s = f'{k} {th_dict[k]}'
        size = chr(len(s)+3)
        str += f'{size}{st}{s}{st}'    

    str = str[:-1] + f'\n\n{5*chr(0)}'
    tbd_sb = bytes(str, 'ascii')
    tbd_sb_size = len(str)
    #print(tbd_sb_size, tbd_sb)

    # Calculate Buffer size
    n_traces = len(strm)
    M = 4*n_traces
    NS = len(strm[0].data)
    backup = n_traces*50
    bufferSize = 32+M + fbd_sb_size + n_traces*(32+ tbd_sb_size + 4*NS) + backup
    #print(bufferSize)

    # Main Process
    #Starting the buffer
    buffer = bytearray(bufferSize)

    # first 32 byte
    fst_block = [85, 58, 1, M, n_traces, b'\x01', b'\x00', b'\x00', b'\x01', b'\n', b'\x00', bytes(f'{(31-13)*chr(0)}', 'ascii')]
    fmt = b'2B3H6c18s'
    pack_into(fmt, buffer, 0, *fst_block)

    # string block FDB
    fmt = b"%is"%(fbd_sb_size)
    offset = 32+M
    pack_into(fmt, buffer, offset, fbd_sb)

    #Trace pointer Sub-block
    offset = 32+M+fbd_sb_size
    pointer = []

    #Trace Block
    st = '\x00'  # string terminetor
    data_format = 4     # 32-bit floating point

    for i in range(n_traces):
        pointer.append(offset)
        trfmt = TraceFormat(fh_dict=binhead, file=filename)
        th_dict = dict()
        for key in list(TRACE_HEADER_FORMAT.keys()):
            th_dict.update({key: trfmt.format_th(key, strm[i].stats[ftype].trace_header, ftype=ftype)})

        str = ''
        for k in list(th_dict.keys()):
            s = f'{k} {th_dict[k]}'
            size = chr(len(s)+3)
            str += f'{size}{st}{s}{st}'    

        str = str[:-1] + f'\n\n{5*chr(0)}'
        tbd_sb = bytes(str, 'ascii')
        tbd_sb_size = len(str)

        Y = data_format*NS
        X = tbd_sb_size+32
        trblock = [17442, X, Y, NS, data_format, bytes(f'{(31-12)*chr(0)}', 'ascii'), tbd_sb]

        fmt = b"2H2IB19s%is"%(tbd_sb_size)
        pack_into(fmt, buffer, offset, *trblock)
        offset += tbd_sb_size 
        if data_format==4:
            fmt = b'%if'%(NS)
        pack_into(fmt, buffer, offset, *strm[i].data)
        offset += 4*NS
    
    # Trace Pointer Sub-block
    p_offset = 32
    fmt = b"%iI"%(n_traces)
    pack_into(fmt, buffer, p_offset, *pointer)

    #save File
    if newFileName == None:
        path = "Converted_SEG2"
        if not os.path.exists(path):
            os.mkdir(path)
        newFileName = path+'/'+filename.split('/')[-1][:-4] + "dat"
    datfile = open(newFileName, 'wb')
    datfile.write(buffer)
    datfile.close()
