#!/usr/bin/env python
# newznab installer for python written by convict

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from time import sleep
import platform
import os, sys
import subprocess
import shutil
import urllib2
from getpass import getpass

'''	 __________________
	< Thanks to zombu2 >
	 ------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\   
		||----w |
                ||     ||'''

class toolbar():
	def __init__(self, commands):
		self.commands = commands
		self.toolbar_width = 100

		sys.stdout.write('[%s]' % (' ' * self.toolbar_width))
		sys.stdout.flush()
		sys.stdout.write("\b" * (self.toolbar_width+1))

	def update(self):
		sys.stdout.write('-' * int(100 / int(self.commands)))
		sys.stdout.flush()

	def end(self):
		sys.stdout.write('-' * int(100 % int(self.commands)))
		sys.stdout.write("\n")

def systemCheck():
	if not os.geteuid() == 0:
		sys.exit('You must be root to run this application')
	if platform.dist()[1] != '12.10':
		print '\033[1;31mTHIS HAS NOT BEEN TESTED ON ANY OTHER VERSION OF UBUNTU AND REQUIRES APT-GET. RUN AT YOUR OWN RISK. YOU HAVE BEEN WARNED\033[1;37m'
	if '.'.join(map(str, sys.version_info[:3])) != '2.7.3':
		print '\033[1;31mTHIS HAS ONLY BEEN TESTED ON PYTHON VERSION 2.7.3. RUN AT YOUR OWN RISK. YOU HAVE BEEN WARNED\033[1;37m'

def disclaimer():
	print 'If you fuck up, it\'s all on you.'
	response = raw_input('Do you Agree? (Y/N): ').lower()
	if 'y' in response or 'yes' in response:
		return True
	else:
		return False

def runCommand(command):
	process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	out, err = process.communicate()
	#do whatever we want with out and err here
	return out, err

def installPackages():
	print 'Updating apt repositories...'
	runCommand('apt-get update -q=3')
		
	print 'Installing newznab dependencies...'
	commands = ['apt-get install -y -q=3 build-essential checkinstall', 'mkdir -p /var/www/newznab', 'chmod 777 /var/www/newznab', 'apt-get install -y -q=3 php5',
		'apt-get install -y -q=3 php5-dev', 'apt-get install -y -q=3 php-pear',	'apt-get install -y -q=3 php5-gd', 'apt-get install -y -q=3 php5-mysql',
		'apt-get install -y -q=3 php5-curl', 'DEBIAN_FRONTEND=noninteractive apt-get -y install -q=3 mysql-server', 'apt-get -y install -q=3 git', 'apt-get -y install -q=3 php5-fpm',
		'apt-get -y install -q=3  mysql-client libmysqlclient-dev', 'apt-get -y install -q=3 apache2', 'a2dissite default', 'a2ensite newznab', 'a2enmod rewrite',
		'service apache2 restart', 'apt-get -y install -q=3 python-software-properties', 'add-apt-repository -y  ppa:jon-severinsson/ffmpeg',
		'add-apt-repository -y  ppa:shiki/mediainfo', 'apt-get -y install -q=3 subversion']

	progress = toolbar(len(commands))
	for command in commands:
		sleep(.3)
		#install packages here
		runCommand(command)

		#update progress bar here
		progress.update()
	progress.end()

	# set root password for mysql
	print 'Enter the new root password for mysql.'
	password1 = getpass('Enter password: ')
	password2 = getpass('Re-enter password: ')
	while password1 != password2:
		print 'Passwords do not match'
		password1 = getpass('Enter password: ')
	        password2 = getpass('Re-enter password: ')	
	runCommand('mysqladmin -u root password %s' % password1)

	print 'Newznab dependencies installed.'

def installSphinx():
	reply = raw_input('Do you want to install sphinx? (Y/N) ').lower()
	if 'y' in reply or 'yes' in reply:
		commands = ['add-apt-repository -y ppa:builds/sphinxsearch-stable', 'apt-get -q=3 update', 'apt-get install -y -q=3 sphinxsearch']
		progress = toolbar(len(commands))
		for command in commands:
			runCommand(command)
			progress.update()
		progress.end()
		print 'Sphinx is now installed.'
	else:
		print 'Skipping sphinx.'
	
def installFree():
	commands = ['apt-get -q=3 update', 'apt-get -y install -q=3 ffmpeg', 'apt-get -y install -q=3 x264', 'apt-get -y install -q=3 mediainfo', 'apt-get -y install -q=3 unrar', 'apt-get -y install -q=3 lame']
	reply = raw_input('Do you want to install post processing utilities? (Y/N) ').lower()
	if 'y' in reply or 'yes' in reply:
		print 'Installing ffmpeg x264 mediainfo unrar lame...'
	
		progress = toolbar(len(commands))
		for command in commands:
			runCommand(command)

			# update progress bar
			progress.update()
		progress.end()
		print 'ffmpeg x264 mediainfo unrar lame is now installed...'

def installNewznab():
	print 'Installing Newznab...'
	username = raw_input('Enter the newznab-plus SVN username: ')
	password = getpass('Enter the newznab-plus SVN password: ')
	commands = ['svn co svn://svn.newznab.com/nn/branches/nnplus /var/www/newznab --no-auth-cache --non-interactive --username %s --password %s' % (username, password), 'chmod -R 777 /var/www/newznab']
	progress = toolbar(len(commands))
	for i in xrange(len(commands)):
		runCommand(commands[i])
		progress.update()
	progress.end()
	print 'Newznab installed to /var/www/newznab.'

def modifySystem():
	# move original php.ini files
	try:
		shutil.move('/etc/php5/apache2/php.ini', '/etc/php5/apache2/php.ini.bak')
		shutil.move('/etc/php5/cli/php.ini', '/etc/php5/cli/php.ini.bak')
	except IOError:
		pass
	
	fsrc = ['http://bandofbrothers.3owl.com/nn/newznab', 'http://bandofbrothers.3owl.com/nn/apache/php.ini', 'http://bandofbrothers.3owl.com/nn/cli/php.ini']
	fdst = ['/etc/apache2/sites-available/newznab', '/etc/php5/apache2/php.ini', '/etc/php5/cli/php.ini']	

	try:
		for i in xrange(len(fsrc)):
			request = urllib2.Request(fsrc[i])
			data = urllib2.urlopen(request)
			fp = open(fdst[i], 'w+')
			fp.write(data.read())
	except urllib2.HTTPError, e:
		print 'HTTP Error:', e.code, fsrc[i]
	except urllib2.URLError, e:
		print 'URL Error:', e.reason, fsrc[i]

	commands = ['sudo a2dissite default', 'sudo a2ensite newznab', 'sudo a2enmod rewrite', 'service apache2 start', 'service mysql start']
	progress = toolbar(len(commands))
	for command in commands:
		runCommand(command)
		progress.update()
	progress.end()

def installTmux():
	reply = raw_input('Do you want to install jonnyboy\'s tmux scripts? (Y/N) ').lower()
	if 'y' in reply or 'yes' in reply:
		runCommand('git clone https://github.com/jonnyboy/newznab-tmux.git /var/www/newznab/misc/update_scripts/nix_scripts/tmux')
		try:
			shutil.move('/var/www/newznab/misc/update_scripts/nix_scripts/tmux/config.sh', '/var/www/newznab/misc/update_scripts/nix_scripts/tmux/defaults.sh')
		except IOError:
			print 'Unable to copy tmux config.sh to defaults.sh.'
		runCommand('apt-get install -y -q=3 php-apc')
		try:
			shutil.copy('/usr/share/doc/php-apc/apc.php', '/var/www/newznab/www/admin/apc.php')
		except IOError:
			print 'Unable to copy apc.php to newznab install.'	


if __name__ == '__main__':
	try:
		systemCheck()
		if disclaimer() == False:
			sys.exit(0)
		installPackages()
		installSphinx()
		installFree()
		runCommand('service apache2 stop')
		runCommand('service mysql stop')
		
		while not os.path.exists('/var/www/newznab/misc/update_scripts/nix_scripts'):
			installNewznab()
		modifySystem()
		installTmux()
		print 'Go to http://localhost/install to finish the newznab install. Good luck!'
	except KeyboardInterrupt:
		sys.exit()
