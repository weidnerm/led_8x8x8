
starts = [
    0	,
    59	,
    111	,
    156	,
    206	,
    249	,
    289	,
    326	,
    364	,
    400	,
    437	,
    467	,
    490	,
    500]


def main():
   
    vert_line_sweep('seq_vert_line_sweep.txt')
    horiz_line_sweep('seq_horiz_line_sweep.txt')
    red_green_full_rotate('seq_red_green_full_rotate.txt')
    # white_front_light('seq_white_front_light.txt')
    
def vert_line_sweep(filename):
    lines = []
    delay = 50
    
    lines.append("setup channel_1_count=500")
    lines.append("#https://github.com/tom-2015/rpi-ws2812-server")
    lines.append("brightness 1,32")
    lines.append("fill 1")
    lines.append("render")
    lines.append("")

    lines.append("")
    lines.append("do")
    lines.append("")

    for phase_raw in range(0,60,2):
        phase = phase_raw % 60
        lines.append('fill 1')  # wipe
        for index in range(len(starts)-1):
            line_len = starts[index+1]-starts[index]
            pos = int(phase*line_len/60)
            lines.append('fill 1,ffffff,%d,1' % (starts[index] + pos))
        lines.append('render')
        lines.append('delay %d' % (delay))
    lines.append('fill 1')  # wipe
    lines.append('render')

    for phase_raw in range(60-1,-1,-2):
        phase = phase_raw % 60
        lines.append('fill 1')  # wipe
        for index in range(len(starts)-1):
            line_len = starts[index+1]-starts[index]
            pos = int(phase*line_len/60)
            lines.append('fill 1,ffffff,%d,1' % (starts[index] + pos))
        lines.append('render')
        lines.append('delay %d' % (delay))
    lines.append('fill 1')  # wipe
    lines.append('render')

    lines.append("")
    lines.append("loop 2")
    lines.append("")

    fh = open(filename, "w")
    fh.write('\n'.join(lines)+'\n')
    fh.close()

def horiz_line_sweep(filename):
    lines = []
    delay = 50
    
    lines.append("setup channel_1_count=500")
    lines.append("#https://github.com/tom-2015/rpi-ws2812-server")
    lines.append("brightness 1,32")
    lines.append("fill 1")
    lines.append("render")

    lines.append("")
    lines.append("do")
    lines.append("")

    for index in range(len(starts)-1):
        lines.append('fill 1')  # wipe
        lines.append('fill 1,ffffff,%d,%d;render' % (starts[index],starts[index+1]-1-starts[index]))
        lines.append('delay %d' % (delay))

    for index in range(len(starts)-1-1,-1,-1):
        lines.append('fill 1')  # wipe
        lines.append('fill 1,ffffff,%d,%d;render' % (starts[index],starts[index+1]-1-starts[index]))
        lines.append('delay %d' % (delay))

    lines.append("")
    lines.append("loop 2")
    lines.append("")

    lines.append('fill 1')  # wipe
    lines.append('render')

    fh = open(filename, "w")
    fh.write('\n'.join(lines)+'\n')
    fh.close()


def red_green_full_rotate(filename):
    lines = []
    delay = 50
    
    lines.append("setup channel_1_count=500")
    lines.append("#https://github.com/tom-2015/rpi-ws2812-server")
    lines.append("brightness 1,32")
    lines.append("fill 1")
    lines.append("render")

    lines.append("")
    lines.append("do")
    lines.append("")

    for phase in range(20):
        lines.append('fill 1')  # wipe
        for index in range(len(starts)-1):
            row_length = starts[index+1]-1-starts[index]
            row_start = starts[index] + int(phase*row_length/20)
            lines.append('fill 1,ff0000,%d,%d' % (row_start,                   int(row_length/4)))
            lines.append('fill 1,00ff00,%d,%d' % (row_start+int(row_length/2), int(row_length/4)))

        lines.append('render;delay 50')

    lines.append("")
    lines.append("loop 5")
    lines.append("")

    # lines.append('fill 1')  # wipe
    # lines.append('render')

    fh = open(filename, "w")
    fh.write('\n'.join(lines)+'\n')
    fh.close()

        
def white_front_light(filename):
    lines = []
    delay = 50
    
    lines.append("setup channel_1_count=500")
    lines.append("#https://github.com/tom-2015/rpi-ws2812-server")
    lines.append("fill 1")
    lines.append("render")

    phase = 5
    lines.append('fill 1')  # wipe
    for index in range(len(starts)-1):
        row_length = starts[index+1]-1-starts[index]
        row_start = starts[index] + int(phase*row_length/20)
        lines.append('fill 1,ffffff,%d,%d' % (row_start,                   int(row_length/4)))

        lines.append('render;delay 50')


    # lines.append('fill 1')  # wipe
    # lines.append('render')

    fh = open(filename, "w")
    fh.write('\n'.join(lines)+'\n')
    fh.close()

        
# Using the special variable 
# __name__
if __name__=="__main__":
    main()
