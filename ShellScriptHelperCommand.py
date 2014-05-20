import sublime, sublime_plugin, subprocess, os, re

#
# SublimeText 2 Plugin for Shell Scripts
# (C) 2014 Andreas Hanisch
#
#	a context menu entry is added if current file has shell syntax (View->Syntax->Shell Script)
#
#	dependencies:
#		- bash
#		- grep
#

EXCLUDE_FILES_GLOB="*~"
LAST_OPENEND_VIEW_ID=None
GOTO_THIS_LINE=1

def is_shell_script_syntax_file(syntaxFile):
	return re.search("ShellScript", syntaxFile) != None


class ShellScriptHelpersCommand(sublime_plugin.TextCommand):

	def getPluginDir(self):
		return os.path.join(sublime.packages_path(), "ShellScriptHelpers")

	def run(self, edit):
		keyword = ""
		for region in self.view.sel():
			if region.begin() == region.end():
				word = self.view.word(region)
			else:
				word = region
			if not word.empty():
				keyword = self.view.substr(word)

		self.foundHits = []
		if len(keyword) > 0:
			self.foundHits = self.find_implementation_of_function(keyword)
			self.view.window().show_quick_panel([I[0] for I in self.foundHits], self.on_done)

	def on_done(self, picked):
		global LAST_OPENEND_VIEW_ID, GOTO_THIS_LINE
		pickedFile = self.foundHits[picked][0]
		lineNumber = self.foundHits[picked][1]
		GOTO_THIS_LINE = lineNumber
		view=self.view.window().open_file(pickedFile)
		LAST_OPENEND_VIEW_ID = view.id()
		view.run_command("goto_line", {"line": GOTO_THIS_LINE} )
		

	def is_visible(self):
		syntax = self.view.settings().get('syntax')
		return is_shell_script_syntax_file(syntax)

	def find_implementation_of_function_in_folder(self, funcName, folder):
		global EXCLUDE_FILES_GLOB
		script = 'cd "' + folder + '"; grep -rnE --exclude="' + EXCLUDE_FILES_GLOB +'" "^[ ]*function[ ]+'+ funcName +'([ ]|$)+" *'
		proc = subprocess.Popen(['bash', '-c', script],stdout=subprocess.PIPE)
		result = proc.stdout.read()
		hits = [I.split(":") for I in result.split("\n") if len(I) > 0]

		return hits

	def find_implementation_of_function(self, funcName):
		folders = self.view.window().folders()
		if len(folders) == 0:
			folders = [self.getPluginDir()]

		finalResult = []
		for folder in folders:
			resultList = self.find_implementation_of_function_in_folder(funcName, folder)
			for result in resultList:
				finalResult.append([os.path.join(folder, result[0]), result[1]])
		return finalResult



class ShellScriptHelpersViewEventListener(sublime_plugin.EventListener):

	def on_load(self, view):
		global LAST_OPENEND_VIEW_ID, GOTO_THIS_LINE

		if view.id() == LAST_OPENEND_VIEW_ID:
			print "Goto Line"
			view.run_command("goto_line", {"line": GOTO_THIS_LINE} )
			LAST_OPENEND_VIEW_ID = None
