import subprocess
import tempfile


def cmd(command, output=True, wait=True):
    if output:
        process = subprocess.Popen(
            command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    else:
        with tempfile.NamedTemporaryFile() as fh:
            process = subprocess.Popen(command.split(), stdout=fh, stderr=fh)
    if wait:
        output, error = process.communicate()
        return output, error


def apply_replace(f_in, replace_dict, kubectl_path):
    with open(f_in, "r") as fin:
        with tempfile.NamedTemporaryFile(mode='w') as fout:
            for line in fin.readlines():
                for key, val in replace_dict.items():
                    line = line.replace('{' + key + '}', str(val))
                fout.write(line)
            fout.flush()
            cmd(f'{kubectl_path} apply -f {fout.name}')
