from gi.repository import GObject, Gedit

class AutomaticCdPlugihn(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "AutomaticCdPlugin"
	window = GObject.property(type=Gedit.Window)
	handler_id = -1
	current_dir = ""
	
	def __init__(self):
		GObject.Object.__init__(self)
	
	def do_activate(self):
		# Connect the handler
		self.handler_id = self.window.connect("active-tab-changed", self.update_terminal_location)
	
	def do_deactivate(self):
		# Disconnect the handler
		self.window.disconnect(self.handler_id)
	
	def do_update_state(self):
		pass
	
	def update_terminal_location(self, window, tab, data=None):
		# Get the file location & terminal panel wrapper.
		location = tab.get_document().get_file().get_location()
		terminal_panel = self.window.get_bottom_panel().get_child_by_name("GeditTerminalPanel");
		# Make sure there is a terminal panel and that there is a file location
		if location != None and terminal_panel != None:
			# Get the folder for the file, trimming off the leading "file://" and trailing filename & slash
			target_location = location.get_uri()
			target_location = target_location[7:target_location.rfind('/')]
			# Make sure you're not cd-ing to the directory you're already in
			if target_location != self.current_dir:
				# If you're launching gedit, not just opening a new tab, then clear the terminal so it looks like it launched this way.
				command_to_exec=""
				if self.current_dir == "":
					command_to_exec="clear\n"
				self.current_dir = target_location
				# Loop over the string and undo any uri encoding.
				# There is certainly a function that will do this, but considering how much time I spent poking around the docs to get it to work as it does, I'm just going to leave this here.
				start_at = 0
				while start_at < len(target_location)-2:
					find_index = target_location.find("%", start_at)
					if find_index == -1:
						break
					target_location = target_location[:find_index] + chr(int(target_location[find_index+1:find_index+3], 16)) + target_location[find_index+3:]
					start_at = find_index + 1
				# get the actual terminal object, not just the wrapper.
				terminal_target = terminal_panel.get_children()[0]
				# Assemble the command and send it
				# Will tack on the clear screen command if that was queued up at the start.
				command_to_exec = "cd " + target_location + "\n" + command_to_exec
				terminal_target.feed_child(command_to_exec.encode())
