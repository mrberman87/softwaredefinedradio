#!/usr/bin/env python

from distutils.core import setup
import subprocess, os

package_name = 'asdf'

p = subprocess.Popen('ls /usr/local/lib/ | grep python', stdout=subprocess.PIPE, shell=True)
tmp = os.read(p.stdout.fileno(), 1024)
p.wait()
tmp = tmp.split('\n')

for py_ver in tmp:
	if py_ver != '':
		if not os.path.exists('/usr/local/lib/' + py_ver + '/dist-packages'):
			os.mkdir('/usr/local/lib/' + py_ver + '/dist-packages')
		fd = open('/etc/bash.bashrc', 'r')
		tmp = True
		for l in fd:
			if l.startswith('export PATH=/usr/local/lib/' + py_ver + '/dist-packages/asdf'):
				tmp = False
		fd.close()
		fd = open('/etc/bash.bashrc', 'a')
		if tmp:
			fd.write('export PATH=/usr/local/lib/' + py_ver + '/dist-packages/asdf:\"${PATH}\"\n\n')
		fd.close()
		p = subprocess.Popen('chmod -R a+x /usr/local/lib/' + py_ver + '/dist-packages/*', shell=True)
		p.wait()

setup(author = "Michael Berman", name = 'hello', version = '1.0', packages = [package_name])
