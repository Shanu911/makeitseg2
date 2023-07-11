from header import *

def searchdate(day, year):
    l = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year%4==0 and year%100!=0) or year%400 ==0:
        l[1] += 1 
    i=0
    while day>l[i+1]:
        i+=1
        day = day - l[i]
    if i<9:
        mm = f'0{i+1}'
    else:
        mm = f'{i+1}'
    if day<10:
        dd = f'0{day}'
    else:
        dd = f'{day}'
    date = f'{dd}/{mm}/{year}'
    return date

def format_fh(k, info):
    """
    k = key
    f = 1: BINARY_FILE_HEADER_FORMAT
        2: TRACE_HEADER_FORMAT    
    """
    ak = list(BINARY_FILE_HEADER_FORMAT.keys())
    itlist = list(info.keys())

    if k == ak[0]:
        # ACQUISITION_DATE
        if 'day' and 'year' in itlist:
            date = searchdate(int(info['day']), int(info['year']))
        else:
            date = DEFAULTVALUES['date']
        return date

    elif k == ak[1]:
        # ACQUISITION_TIME
        if 'hh' in itlist:
            hh = f"{info['hh']}"
            mm = f"{info['mm']}"
            ss = f"{info['ss']}"
            if int(info['hh'])<9:
                hh = "0"+hh
            if int(info['mm'])<9:
                mm = "0"+mm
            if int(info['ss'])<9:
                ss = "0"+ss
            time = f"{hh}:{mm}:{ss}"
        else:
            time = DEFAULTVALUES['time']
        return time

    elif k == ak[2]:
        # CLIENT
        return DEFAULTVALUES['anystring']

    elif k == ak[3]:
        # COMPANY
        return DEFAULTVALUES['anystring']

    elif k == ak[4]:
        # GENERAL_CONSTANT
        return '000000000'

    elif k == ak[5]:
        # INSTRUMENT
        return DEFAULTVALUES['instrument']

    elif k == ak[6]:
        # JOB_ID
        if 'jobid' in itlist:
            name = info['jobid']
        else:
            name = '0000'
        return name

    elif k == ak[7]:
        # OBSERVER
        return DEFAULTVALUES['observer']
    elif k == ak[8]:
        # PROCESSING_DATE
        if 'day' in itlist:
            date = searchdate(int(info['day']), int(info['year']))
        else:
            date = DEFAULTVALUES['date']
        return date

    elif k == ak[9]:
        # PROCESSING_TIME
        if 'hh' in itlist:
            hh = f"{info['hh']}"
            mm = f"{info['mm']}"
            ss = f"{info['ss']}"
            if int(info['hh'])<9:
                hh = "0"+hh
            if int(info['mm'])<9:
                mm = "0"+mm
            if int(info['ss'])<9:
                ss = "0"+ss
            time = f"{hh}:{mm}:{ss}"
        else:
            time = DEFAULTVALUES['time']
        return time

    elif k == ak[10]:
        # TRACE_SORT
        m = info['tsort']
        if m == 1:
            return 'AS_ACQUIRED'
        elif m == 2:
            return 'COMMON_OFFSET'
        elif m == 5:
            return 'COMMON_SOURCE'
        elif m == 6:
            return 'COMMON_RECEIVER'
        elif m == 7:
            return 'COMMON_OFFSET'
        else:
            print('file contains an invalid TRACE SORT method, set a valid TRACE SORT method')
            return 'UNKNOWN'

    elif k == ak[11]:
        # UNITS
        m = info['unit']
        if m == 1:
            return 'METERS'
        elif m == 2:
            return 'FEET'
        else:
            print('file contains an invalid unit, set a valid unit')
            return 'UNKNOWN'

    elif k == ak[12]:
        # NOTE
        return "[]"


class TraceFormat(object):
    def __init__(self, file, fh_dict=None):
        self.fh_dict = fh_dict
        self.fname = file

    def format_th(self, k, th_dict, fdelflag=False, ftype='segy'):
        isSegy = True if ftype=='segy' else False

        ak = list(TRACE_HEADER_FORMAT.keys())
        if k == ak[0]:
            # ALIAS_FILTER
            return f"{th_dict['alias_filter_frequency']} {th_dict['alias_filter_slope']}"

        elif k == ak[1]:
            # AMPLITUDE_RECOVERY

            """
            need parameter list                                             ##############################
            """
            m = int(self.fh_dict['amplitude_recovery_method']) if isSegy else 0
            if m == 1:
                value = 'NONE'
            elif m == 2:
                value = 'SPHERICAL_DIVERGENCE'
            elif m == 3:
                value = 'AGC'
            elif m == 4:
                value = 'OTHER'
            else:
                value = 'UNKNOWN'

            return value

        elif k == ak[2]:
            # BAND_REJECT_FILTER
            return "0 0"

        elif k == ak[3]:
            # CDP_NUMBER
            return f"{th_dict['ensemble_number']}"

        elif k == ak[4]:
            # CDP_TRACE
            return f"{th_dict['trace_number_within_the_ensemble']}"

        elif k == ak[5]:
            # CHANNEL_NUMBER
            return f"{th_dict['trace_sequence_number_within_segy_file']}"

        elif k == ak[6]:
            # DATUM
            return f"{th_dict['datum_elevation_at_receiver_group']}"

        elif k == ak[7]:
            # DELAY
            return f"{th_dict['delay_recording_time']}"

        elif k == ak[8]:
            # DESCALING_FACTOR
            return "0.0"

        elif k == ak[9]:
            # DIGITAL_BAND_REJECT_FILTER
            return "0 0"

        elif k == ak[10]:
            # DIGITAL_HIGH_CUT_FILTER
            return "0 0"

        elif k == ak[11]:
            # DIGITAL_LOW_CUT_FILTER
            return "0 0"

        elif k == ak[12]:
            # END_OF_GROUP
            m = self.fh_dict['number_of_data_traces_per_ensemble'] if isSegy else 0
            if int(m) != int(th_dict['trace_number_within_the_ensemble']):
                return "0"
            else:
                return "1"

        elif k == ak[13]:
            # FIXED_GAIN
            if int(th_dict['gain_type_of_field_instruments']) == 1:
                m = self.fh_dict['instrument_early_or_initial_gain'] if isSegy else 0
                v = f"{m} DB"
                return v
            else:
                return "0 DB"

        elif k == ak[14]:
            # HIGH_CUT_FILTER
            return f"{th_dict['high_cut_frequency']} {th_dict['high_cut_slope']}"

        elif k == ak[15]:
            # LINE_ID
            return "1"

        elif k == ak[16]:
            # LOW_CUT_FILTER
            return f"{th_dict['low_cut_frequency']} {th_dict['low_cut_slope']}"

        elif k == ak[17]:
            # NOTCH_FREQUENCY
            return f"{th_dict['notch_filter_frequency']}"

        elif k == ak[18]:
            # POLARITY
            v = int(self.fh_dict['impulse_signal_polarity']) if isSegy else 0
            if v == 1:
                return '-1'
            elif v == 2:
                return "1"
            else:
                return "0"

        elif k == ak[19]:
            # RAW_RECORD
            return self.fname

        elif k == ak[20]:
            # RECEIVER
            m = self.fh_dict['number_of_data_traces_per_ensemble'] if isSegy else 0
            return f"VERTICAL_GEOPHONE {m}"

        elif k == ak[21]:
            # RECEIVER_GEOMETRY
            return "0"

        elif k == ak[22]:
            # RECEIVER_LOCATION
            if fdelflag:
                v = f"{th_dict['group_coordinate_x']/1000}"
                if float(th_dict['group_coordinate_y']) != 0:
                    v += f" {th_dict['group_coordinate_y']/1000}"
            else:
                v = f"{th_dict['group_coordinate_x']}"
                if float(th_dict['group_coordinate_y']) != 0:
                    v += f" {th_dict['group_coordinate_y']}"
            return v

        elif k == ak[23]:
            # RECEIVER_SPECS
            return " "

        elif k == ak[24]:
            # RECEIVER_STATION_NUMBER
            return "0"

        elif k == ak[25]:
            # SAMPLE_INTERVAL
            v = float(th_dict['sample_interval_in_ms_for_this_trace'])*10**(-6)
            return f"{v}"

        elif k == ak[26]:
            # SHOT_SEQUENCE_NUMBER
            return "1"

        elif k == ak[27]:
            # SKEW
            return "0.0"

        elif k == ak[28]:
            # SOURCE
            if 0 < int(th_dict['source_type_orientation']) < 4:
                return f"{th_dict['source_type_orientation']} {th_dict['sweep_frequency_at_end']}"
            else:
                return "HAMMER 1"

        elif k == ak[29]:
            # SOURCE_GEOMETRY
            return "0"

        elif k == ak[30]:
            # SOURCE_LOCATION
            if fdelflag:
                v = f"{th_dict['source_coordinate_x']/1000}"
                if float(th_dict['source_coordinate_y']) != 0:
                    v += f" {th_dict['source_coordinate_y']/1000}"
            else:
                v = f"{th_dict['source_coordinate_x']}"
                if float(th_dict['source_coordinate_y']) != 0:
                    v += f" {th_dict['source_coordinate_y']}"
            return v

        elif k == ak[31]:
            # SOURCE_STATION_NUMBER
            return "0"

        elif k == ak[32]:
            # STACK
            if int(th_dict['number_of_horizontally_stacked_traces_yielding_this_trace']) != 0:
                return f"{th_dict['number_of_horizontally_stacked_traces_yielding_this_trace']}"
            else:
                return "1"

        elif k == ak[33]:
            # STATIC_CORRECTIONS
            return f"{th_dict['source_static_correction_in_ms']} {th_dict['group_static_correction_in_ms']} {th_dict['total_static_applied_in_ms']}"

        elif k == ak[34]:
            # TRACE_TYPE
            m = int(th_dict['trace_identification_code'])
            if m == 1:
                return "SEISMIC_DATA"
            elif m == 2:
                return "DEAD"
            elif m == 5:
                return "UPHOLE"
            elif m == 0:
                return "UNKNOWN"
            elif int(th_dict['data_use']) == 2:
                return "TEST_DATA"
            else:
                return "OTHER"

        elif k == ak[35]:
            # NOTE
            return "[]"
