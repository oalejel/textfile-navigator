import sys, curses, argparse
from curses import wrapper 

filepath, width, height, row, column, max_height = None, None, None, None, None, None
max_window_widths = None
lines = list()

def get_args():
	parser = argparse.ArgumentParser(description='View a window of a file\'s text')
	parser.add_argument('-F', help='filepath for the file to be navigated', required=True)
	parser.add_argument('-W', help='maximum width of content window', required=False)
	parser.add_argument('-H', help='maximum height of content window', required=False)
	parser.add_argument('-R', help='window row start (0 indexing)', required=False)
	parser.add_argument('-C', help='window column start (0 indexing)', required=False)
	args = parser.parse_args()
	
	global filepath, width, height, row, column, max_height
	filepath = args.F
	
	some_none = (args.W == None) or (args.H == None) or (args.R == None) or (args.C == None)
	all_none = (args.W == None) and (args.H == None) and (args.R == None) and (args.C == None)
	
	if not some_none:
		width = int(args.W)
		height = int(args.H)
		row = int(args.R)
		column = int(args.C)
	elif not some_none == all_none:
		print("must specify R, C, W, and H (row, column, width, height) if you pass one of the options")
		exit 
	elif all_none: # all none. use default values 
		row = 0 
		column = 0 
		width = 10
		height = 5
		
		
# project-specific processing of file 
def process_file():
	global filepath, height, width, row, column, max_window_widths, lines, max_height
	f = open(filepath, "r")
	
	line_widths = list()
#	lines = list() # globally defined 
	# dump first line for this format 
	f.readline()
	_line = f.readline()
	while _line:
		if not _line[0] == '/':
			lines.append(_line[0:-1]) # cut off newline character
			line_widths.append(len(_line) - 1)
		_line = f.readline()
	f.close()
	
	max_height = len(lines)
	height = min(height, max_height)
	
	# create a list of the maximum width among a set of lines coming from the filepath
	max_window_widths = [0] * max(1, len(lines) - height + 1)
	
	# generate list of best widths within window given a row index 
	for w_index in range(0, len(max_window_widths)):
		local_max = 0
		for i in range(w_index, w_index + height):
			local_max = max(local_max, line_widths[i])
		max_window_widths[w_index] = local_max
		
	# if window too big, shrink width to match width of (longest) line
#	m = 0
#	for x in max_window_widths:
#		m = max(m, x)
	m = max(max_window_widths)
	if width > m:
		width = m
	
	# if window is out of bounds, shift it by the out of bounds amount 
	if row + height >= max_height:
		row = max(0, (max_height - height) - 1)

	if column + width >= max_window_widths[row]:
		column = max(0, max_window_widths[row] - width)
	
	

def draw_window(stdscr, pad):
	global width, height, row, column

	coord_string = "({},{}) ".format(row, column)
#	pad.addstr(0, 0, coord_string)
	stdscr.addstr(0, 0, coord_string, curses.color_pair(1))
	x_offset = len(coord_string)
	y_offset = 1

	# draw vertical bar beneath coordinate pair 
	for y in range(y_offset, y_offset + height + 1):
		if (y + row - 1) % 5 == 0:
			stdscr.addstr(y, x_offset, '├', curses.color_pair(1))
		else:
			stdscr.addstr(y, x_offset, '│', curses.color_pair(1))

	# draw horizontal bar beneath coordinate pair
	for x in range(x_offset, x_offset + width + 1):
		if (x + column - 1) % 5 == 0:
			stdscr.addstr(y_offset, x, '┬', curses.color_pair(1))
		else:
			stdscr.addstr(y_offset, x, '─', curses.color_pair(1))
			
	# clear old lines that may be below expanded coordinate pair ((99,99) --> (100, 99))
	for x in range(0, x_offset):
		for y in range(y_offset, y_offset + height + 1):
			stdscr.addch(y, x, ' ')
				
	# write out the dimensions being displayed as a reminder in the format [w: _, h: _]
	window_str = "  [w: {}, h: {}] ".format(width, height)
#	for x in range(x_offset + width, x_offset + width + len(window_str)):
	stdscr.addstr(y_offset + height + 1, x_offset + width - 1, window_str, curses.color_pair(1))
		
	# clear lines that are now beyond our old window
	
	
	# write contents of file in window
	for r_index in range(row, min(row + height, len(lines))):
		l = lines[r_index]
		for c_index in range(column, min(column + width, len(l))):
			stdscr.addch(1 + y_offset + r_index - row, 1 + x_offset + c_index - column, l[c_index])


def refresh_screen(stdscr):
	stdscr = curses.initscr()
	win = curses.initscr()
	# TODO: change THIS PADDING???
	pad = curses.newpad(300, 300)
	
	stdscr.clear()
	curses.noecho()
	pad.refresh(0,0, 0,0, width,height)
	
	# grab globals
	global row, column, max_height
	c = ""
	
	while 1:
		draw_window(stdscr, pad)
		c = win.getch()
		if c == curses.KEY_UP:
			if row == 0:
				continue 
			row -= 1
		elif c == curses.KEY_DOWN:
			if row + height == max_height:
				continue 
			row += 1
		elif c == curses.KEY_RIGHT:
			# no limit on column? 
			column += 1
		elif c == curses.KEY_LEFT:
			if column == 0:
				continue
			column -= 1
		elif c == 113: # 'q'
			quit()

	
#	stdscr.addstr("UP")
#			pad.addch(3,0, chr(c))
			
#			stdscr.addstr(chr(c))
	
def main(stdscr):
	curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
	get_args() # get arguments / default values (filepath, row, column, width, height)
	process_file()
	refresh_screen(stdscr)
	
#	print(filepath, row, column, width, height)
	

#if __name__=='__main__':
#		main()
wrapper(main)