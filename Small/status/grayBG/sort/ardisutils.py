#!/usr/bin/python2
#coding: utf-8
import re
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--input", dest="in_filename", default='',
                  help="read report from FILE", metavar="FILE")
parser.add_option("-o", "--output", dest="out_filename", default='',
                  help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages")
parser.add_option("-c", "--clean", dest="el_to_clean",
                  help="skip a specific el, such as text")
parser.add_option("-f", "--filters", dest="filters",
                  help="filter using preset, ex: shadows:[hide|hexcolor], white:hexcolor, colorize:[newhex|hide], resize:Xpx,Ypx ... can be a ; seperated list")
parser.add_option("-e", "--export", dest="export_filename",
                  help="automatically use imagemagick to convert the outputfile to another as well\nHINT: use this with the resize filter for lossless and quick export. Can either be an absolute path with a filetype or just a filetype... REMEMBER THE DOT if doing just filetype")

(options, args) = parser.parse_args()

colorize_filter = None
shadow_filter = None
resize_filter = None
file_input = open(options.in_filename, 'r')
file_output = open(options.out_filename, 'w')
filters_list = []
if options.filters:
    filters_list = re.split(';', options.filters)
    for filter_x in filters_list:
        colorize_opt = re.match('colorize:(hide|[A-Fa-f0-9]+)', filter_x)
        if colorize_opt:
            colorize_filter = colorize_opt.group(1)
        white_opt = re.match('white:([A-Fa-f0-9]+)', filter_x)
        if white_opt:
            white_filter = white_opt.group(1)
        shadow_opt = re.match('shadows:(hide|[A-Fa-f0-9]+)', filter_x)
        if shadow_opt:
            shadow_filter = shadow_opt.group(1)
        resize_opt = re.match('resize:([0-9]+px)\,([0-9]+px)', filter_x)
        if resize_opt:
            resize_filter = {}
            resize_filter['width'] = resize_opt.group(1)
            resize_filter['height'] = resize_opt.group(2)
el_c = 0

try:
    for line in file_input:
        if options.el_to_clean == "text":
            m_start = None
            m_start = re.search(r'^\s*<text|^\s*<tspan', line)
            if m_start:
                el_c = el_c + 1
        if el_c == 0:
            filtered_line = line
            if resize_filter:
                resizematch = re.match('\s*(width|height)\=\"[0-9]+(em|ex|px|in|cm|mm|pt|pc|\%)?\"', line)
                if resizematch:
                    size_axis = str(resizematch.group(1))
                    resizedline = re.sub('((?<=\=\")([0-9]+(em|ex|px|in|cm|mm|pt|pc|\%)?)(?=\"))', resize_filter[size_axis], line)
                    filtered_line = resizedline
            if shadow_filter:
                shadowmatch = re.search('opacity\:(0\.(2|3)[0-9]*)[";]', line)
                if shadowmatch:
                    if shadow_filter == 'hide':
                        hiddenshadow_line = re.sub('opacity\:(0\.(2|3)[0-9]*)', 'opacity:0.0', filtered_line)
                        filtered_line = hiddenshadow_line
                    else:
                        hexshadow_line = re.sub('((?<=[";]fill\:\#)(([a-fA-F0-9]*)([a-eA-E0-9]+)([a-fA-F0-9]*))(?=[";]))', str(shadow_filter), filtered_line)
                        filtered_line = hexshadow_line
            if colorize_filter:
                if colorize_filter == 'hide':
                    hidcolor_line = re.sub('(((?<=[";]fill\:)(\#([a-fA-F0-9]*)([a-eA-E1-9]+)([a-fA-F0-9]*))(?=[";]))|((?<=\sfill\=\")(\#([a-fA-F0-9]*)([a-eA-E1-9]+)([a-fA-F0-9]*))(?=\")))', 'none', filtered_line)
                    filtered_line = hidcolor_line
                else:
                    colored_line = re.sub('(((?<=[";]fill\:\#)(([a-fA-F0-9]*)([a-eA-E1-9]+)([a-fA-F0-9]*))(?=[";]))|((?<=\sfill\=\"\#)(([a-fA-F0-9]*)([a-eA-E1-9]+)([a-fA-F0-9]*))(?=\")))', str(colorize_filter), filtered_line)
                    filtered_line = colored_line
            if white_filter:
                white_line = re.sub('(((?<=[";]fill\:\#)(([fF]+))(?=[";]))|((?<=\sfill\=\"\#)(([fF]+))(?=\")))', str(white_filter), filtered_line)
                filtered_line = white_line
            file_output.write(filtered_line)
        else:
            m_end = None
            m_end = re.search(r'^\s*..text.|.*\s/>', line)
            if m_end:
                el_c = el_c - 1
                
finally:
        file_input.close()
        file_output.close()
        
if options.export_filename:
    e_fname_pattern = re.match('.*(\.(png|xpm))', options.export_filename)
    if e_fname_pattern:
        export_ext = str(e_fname_pattern.group(1))
        new_e_fname = re.sub('\.svg$', export_ext, options.out_filename)
    else:
        new_e_fname = options.export_filename
    import shlex, subprocess
    command_line = str('/usr/bin/convert -background "none" "'+options.out_filename+'" "'+new_e_fname+'"')
    clargs = shlex.split(command_line)
    subprocess.Popen(clargs)
    
exit()