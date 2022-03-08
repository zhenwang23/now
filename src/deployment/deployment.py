import subprocess
import tempfile


def cmd(command, output=True, error=True, wait=True):
    if output:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    else:
        with open("NUL", "w") as fh:
            if output:
                stdout = subprocess.PIPE
            else:
                stdout = fh
            if error:
                stderr = subprocess.PIPE
            else:
                stderr = fh
            process = subprocess.Popen(command.split(), stdout=stdout, stderr=stderr)
    if wait:
        output, error = process.communicate()
        return output, error

def apply_replace(f_in, replace_dict):
    with open(f_in, "r") as fin:
        with tempfile.NamedTemporaryFile(mode='w') as fout:
            for line in fin.readlines():
                for key, val in replace_dict.items():
                    line = line.replace('{' + key + '}', str(val))
                fout.write(line)
            fout.flush()
            cmd(f'kubectl apply -f {fout.name}')