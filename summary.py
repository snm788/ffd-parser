import re, sys

RE_ENABLED = '^\\$.*Enabled.*==\\s"(.*)"'
RE_PROCEDURE = '^\\$.*Procedure.*==\\s"(.*)"'
RE_LABEL = '^\\$.*P3.*==\\s"(.*)"'
RE_MAX_DURATION = '^\\$.*Max_Duration.*==\\s"(.*)"'
RE_RESTART_ON_FAIL = '^\\$.*RestartOnFail.*==\\s"(.*)"'
RE_START_HOUR = '^\\$.*StartHour.*==\\s"(.*)"'
RE_END_HOUR = '^\\$.*EndHour.*==\\s"(.*)"'
RE_RUN_HOURS = '^\\$.*RunHours.*==\\s"(.*)"'
RE_RUN_DAYS = '^\\$.*RunDays.*==\\s"(.*)"'
RE_COMMENT = '^\\$.*Comment.*==\\s"(.*)"'
RE_DCL_COMMENT = '^\\$.*!'
RE_ASSIGN = '^\\$\\s(.*)\\s==?\\s"(.*)"'
RE_GOSUB = '^\\$\\sGosub\\s(.*)'
RE_RETURN = '^\\$.*RETURN'

KEY_ENABLED = 'Enabled'
KEY_PROCEDURE = 'Procedure'
KEY_LABEL = 'Label'
KEY_MAX_DURATION = 'MaxDuration'
KEY_RESTART_ON_FAIL = 'RestartOnFail'
KEY_START_HOUR = 'StartHour'
KEY_END_HOUR = 'EndHour'
KEY_RUN_HOURS = 'RunHours'
KEY_RUN_DAYS = 'RunDays'
KEY_COMMENT = 'Comment'
KEY_GOSUB = 'GoSub'

FORMAT_LIST = 1
FORMAT_CSV = 2

source_dir = r'/Users/snm788/work/ffd/ffd_source'

re_key_pairs = [
    (RE_ENABLED, KEY_ENABLED),
    (RE_PROCEDURE, KEY_PROCEDURE),
    (RE_LABEL, KEY_LABEL),
    (RE_MAX_DURATION, KEY_MAX_DURATION),
    (RE_RESTART_ON_FAIL, KEY_RESTART_ON_FAIL),
    (RE_START_HOUR, KEY_START_HOUR),
    (RE_END_HOUR, KEY_END_HOUR),
    (RE_RUN_HOURS, KEY_RUN_HOURS),
    (RE_RUN_DAYS, KEY_RUN_DAYS),
    (RE_COMMENT, KEY_COMMENT)
]

# find label inside procedure file and display content or read from the top if label does not exist
def parse_procedure(procedure, label, proc_params, first_try = True):
    with open( r'{}/{}'.format(source_dir, procedure[9:]), 'r', encoding='iso-8859-1') as file:
        lines = file.readlines()
        found = True if not first_try else False
        for line in lines:
            if found:
                m = re.search(RE_DCL_COMMENT, line)
                if m:
                    continue

                m = re.search(RE_GOSUB, line)
                if m:
                    proc_params[KEY_GOSUB] = m.group(1)
                    break
                if re.search(RE_RETURN, line):
                    break

                m = re.search(RE_ASSIGN, line)
                if m:
                    proc_params[m.group(1).strip()] = m.group(2)
            else:
                if re.search('{}:'.format(label), line):
                    found = True
        if not found and first_try:
            parse_procedure(procedure, label, proc_params, False)
    return 

def print_params(params):
        print('\n--------------------------')
        print('Job                   #{}'.format(job_id))
        print('Enabled             = {}'.format(params[KEY_ENABLED]))

        for key in [KEY_START_HOUR, KEY_END_HOUR, KEY_RUN_HOURS, KEY_RUN_DAYS, KEY_MAX_DURATION, KEY_RESTART_ON_FAIL]:
            if key in params:
                print('{:<20}= {}'.format(key, params[key]))
        
        print('Summary               {}'.format(params[KEY_COMMENT]))
        print('Procedure             {} @ {}'.format(params[KEY_LABEL], params[KEY_PROCEDURE]))

def print_procedure_params(proc_params):
    for key, value in proc_params.items():
        print('   {:<15}  = {}'.format(key, value))


def print_csv_header():
    print('Job#;StartHour;EndHour;RunHours;RunDays;Procedure(File);Label;PWM$id;PWM$usr;GoSub;Summary')

def print_csv_values(params, proc_params):
    pwmid = proc_params['PWM$id'] if 'PWM$id' in proc_params else proc_params['PWM_ID'] if 'PWM_ID' in proc_params else ''
    pwmusr = proc_params['PWM$usr'] if 'PWM$usr' in proc_params else proc_params['PWM_User'] if 'PWM_User' in proc_params else ''
    print('{};{};{};{};{};{};{};{};{};{};{}'.format(
        job_id,
        params[KEY_START_HOUR] if KEY_START_HOUR in params else '',
        params[KEY_END_HOUR] if KEY_END_HOUR in params else '',
        params[KEY_RUN_HOURS] if KEY_RUN_HOURS in params else '',
        params[KEY_RUN_DAYS] if KEY_RUN_DAYS in params else '',
        params[KEY_PROCEDURE],
        params[KEY_LABEL], 
        pwmid,
        pwmusr,
        proc_params[KEY_GOSUB] if KEY_GOSUB in proc_params else '',
        params[KEY_COMMENT]
        ))

# main loop
format = FORMAT_LIST
if len(sys.argv) > 1 and sys.argv[1] == '-csv':
    format = FORMAT_CSV
job_id = 1
with open( r'{}/FFD$PARAMS.COM'.format(source_dir), 'r', encoding='iso-8859-1') as file:
    lines = file.readlines()
    if format == FORMAT_CSV:
        print_csv_header()
    params = {}
    for line in lines:
        for re_stmt, key in re_key_pairs:
            m = re.search(re_stmt, line)
            if m:
                params[key] = m.group(1)
                if key == KEY_COMMENT:
                    proc_params = {}
                    parse_procedure(params[KEY_PROCEDURE], params[KEY_LABEL], proc_params)

                    if format == FORMAT_LIST:
                        print_params(params)
                        print_procedure_params(proc_params)
                    elif format == FORMAT_CSV:
                        print_csv_values(params, proc_params)
                    
                    params = {}
                    job_id += 1
                continue
