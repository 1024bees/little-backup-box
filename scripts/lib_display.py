#!/usr/bin/env python

# Author: Stefan Saam, github@saams.de

#######################################################################
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################

import lib_log
import lib_setup
import lib_system

import datetime
import os
import pathlib
import re
import sys
import shutil
import subprocess


class display(object):

	def __init__(self):
		self.WORKING_DIR = os.path.dirname(__file__)

		self.log = lib_log.log()

		self.setup	= lib_setup.setup()
		self.conf_DISP						= self.setup.get_val('conf_DISP')
		self.const_DISPLAY_CONTENT_FOLDER	= self.setup.get_val('const_DISPLAY_CONTENT_FOLDER')
		self.const_DISPLAY_CONTENT_OLD_FILE	= self.setup.get_val('const_DISPLAY_CONTENT_OLD_FILE')

		self.python = shutil.which('python3')

		self.pgbar_len = 20

		self.__start_display()

	def __start_display(self):
		if self.conf_DISP and subprocess.run(f"pgrep -af 'python3' | grep '{self.WORKING_DIR}/display.p[y]'",shell=True,stdout=subprocess.DEVNULL).returncode == 1:
			# grep: returncode=1 if no matches found
			subprocess.run(f"sh -c '{self.python} {self.WORKING_DIR}/display.py &'",shell=True)

	def message(self,RawLines): # Lines = ['abc','def',...]
		self.__start_display()

		# cut RawLines (if a RawLine countains newline) and assemble Lines
		Lines = []
		for Line in RawLines:
			SubLines = Line.splitlines()
			for SubLine in SubLines:
				Lines.append(SubLine)

		if Lines:
			# ensure const_DISPLAY_CONTENT_FOLDER exists
			if not os.path.isdir(self.const_DISPLAY_CONTENT_FOLDER):
				pathlib.Path(self.const_DISPLAY_CONTENT_FOLDER).mkdir(parents=True, exist_ok=True)

			# if display is disabled, write message into const_DISPLAY_CONTENT_OLD_FILE to prevent repeating IP
			DisplayFilePath	= os.path.join(self.const_DISPLAY_CONTENT_FOLDER,"{:014d}.txt".format(int(lib_system.get_uptime_sec()*100))) if self.conf_DISP else self.const_DISPLAY_CONTENT_OLD_FILE

			with open(DisplayFilePath,'w') as DisplayFile:
				DisplayFile.write('\n'.join(str(Line) for Line in Lines))

			# format Lines to LogLines
			LogLines = []
			for Line in Lines:

				#skip set-lines or empty lines
				if Line.startswith('set:') or not Line:
					continue

				# remove format separated by ":"
				if ':' in Line:
					Line = Line.split(':',1)[1]

				# progressbar
				if Line.startswith('PGBAR='):
					Percent = Line.split('=',1)[1]
					if not Percent:
						Percent = 0

					Percent	= re.sub('[^0-9\.]', '', f"0{Percent}")
					Percent = float(Percent)

					pgbar_len_done = int(Percent * self.pgbar_len / 100)
					pgbar_len_todo = self.pgbar_len - pgbar_len_done

					Line = "{: 4.1f}% {}{}".format(Percent,'>' * pgbar_len_done,'_' * pgbar_len_todo)

				LogLines.append(Line)

			if LogLines:
				LogMessage = '\n'.join(LogLines)
				self.log.message(LogMessage)




if __name__ == "__main__":
	#catch all arguments as lines to display
	disp=display()

	Lines = sys.argv
	Lines.pop(0) # remove index 0 (script name)

	disp.message(Lines)

