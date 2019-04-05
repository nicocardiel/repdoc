import subprocess


def rsync_html_files(course=None):
    """Execute rsync of HTML files to server

    """

    if course is None:
        raise ValueError('Unexpected course=None value')

    command = 'rsync -arv --delete *html '
    command += 'ncl@nartex.fis.ucm.es:public_html/repdoc/'
    command += course
    command += '/'

    print('--> Executing rsync:\n' + command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    print(p.stdout.read().decode('utf-8'))
    p.stdout.close()
    p.wait()
