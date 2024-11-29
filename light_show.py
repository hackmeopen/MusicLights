import mido
import time
import fluidsynth
import pcf8574_io
import argparse
import random

note_light_dict = {}
next_light_index = 0
num_lights = 8
LOW = "LOW"
HIGH = "HIGH"


def init_io_expander():
    io_exp = pcf8574_io.PCF(0x27)
    #start the i2C with the address
    io_exp.pin_mode("p0", "OUTPUT")
    io_exp.pin_mode("p1", "OUTPUT")
    io_exp.pin_mode("p2", "OUTPUT")
    io_exp.pin_mode("p3", "OUTPUT")
    io_exp.pin_mode("p4", "OUTPUT")
    io_exp.pin_mode("p5", "OUTPUT")
    io_exp.pin_mode("p6", "OUTPUT")
    io_exp.pin_mode("p7", "OUTPUT")
    return io_exp

# Function to send all MIDI messages to FluidSynth
def parse_midi(synth, message, io_exp, channel):
    
    if message.type == 'note_on':
        synth.noteon(message.channel, message.note, message.velocity)
        
        if message.channel == channel:
            control_lights(message.note, 1, io_exp)
            # print(message)

    elif message.type == 'note_off':
        synth.noteoff(message.channel, message.note)
        
        if message.channel == channel:
            control_lights(message.note, 0, io_exp)

    elif message.type == 'control_change':
        synth.cc(message.channel, message.control, message.value)

    elif message.type == 'program_change':
        synth.program_change(message.channel, message.program)

def control_lights(note, on_off, io_exp):

    global next_light_index

    if on_off:
        command = "LOW"
    else:
        command = "HIGH"

    #check to see if the note is already in the dictionary
    if note in note_light_dict:
        light = note_light_dict[note]
        io_exp.write(light, command)
    else:
        light = 'p' + str(next_light_index)
        next_light_index += 1
        if next_light_index == num_lights:
            next_light_index = 0
        note_light_dict[note] = light

current_light = 0
next_light = 0
up_down = 0
num_patterns = 8
def play_light_pattern(pattern, io_exp, interval):

    global current_light
    global up_down
    light = 'p' + str(current_light)
    #up
    if pattern == 0:
        io_exp.write(light, LOW)
        time.sleep(interval)
        io_exp.write(light, HIGH)
        
        current_light += 1
        if current_light == num_lights:
            current_light = 0

    elif pattern == 1:
        io_exp.write(light, LOW)
        time.sleep(interval)
        io_exp.write(light, HIGH)
        
        current_light -= 1
        if current_light == -1:
            current_light = num_lights-1
    elif pattern == 2:
        io_exp.write(light, LOW)
        time.sleep(interval)
        io_exp.write(light, HIGH)
        
        if up_down == 0:
            current_light += 1
            if current_light == num_lights:
                current_light -= 2
                up_down = 1
        else:
            current_light -= 1
            if current_light == -1:
                current_light = 1
                up_down = 0
    elif pattern == 3:
        if up_down == 0:
            io_exp.write(light, LOW)
            time.sleep(interval)
            current_light += 1
            if current_light == num_lights:
                current_light -= 2
                up_down = 1
        else:
            io_exp.write(light, HIGH)
            time.sleep(interval)
            current_light -= 1
            if current_light == -1:
                current_light = 1
                up_down = 0
    elif pattern == 4:#outside_in
        if up_down == 0:
            io_exp.write(light, LOW)
            other_light = num_lights-1 -current_light
            index = 'p' + str(other_light)
            io_exp.write(index, LOW)
            time.sleep(interval)
            current_light += 1
            if current_light == num_lights/2:
                current_light -= 1
                up_down = 1
        else:
            io_exp.write(light, HIGH)
            other_light = num_lights-1 -current_light
            index = 'p' + str(other_light)
            io_exp.write(index, HIGH)
            time.sleep(interval)
            current_light -= 1
            if current_light == -1:
                current_light = 1
                up_down = 0
    elif pattern == 5:#inside_out
        index = 4 - current_light
        light = 'p' + str(index)
        if up_down == 0:
            
            io_exp.write(light, LOW)
            other_light = num_lights-1 -current_light
            index = 'p' + str(other_light)
            io_exp.write(index, LOW)
            time.sleep(interval)
            current_light += 1
            if current_light == num_lights/2:
                current_light -= 1
                up_down = 1
        else:
            io_exp.write(light, HIGH)
            other_light = num_lights-1 -current_light
            index = 'p' + str(other_light)
            io_exp.write(index, HIGH)
            time.sleep(interval)
            current_light -= 1
            if current_light == -1:
                current_light = 1
                up_down = 0
    elif pattern == 6:
        current_light = random.randint(1,num_lights-1)
        if up_down == 0:
            io_exp.write(light, LOW)
            up_down == 1
        else:
            io_exp.write(light, HIGH)
            up_down == 0
    elif pattern == 7:
        if up_down == 0:
            io_exp.write(light, LOW)
        else:
            io_exp.write(light, HIGH)
        time.sleep(interval)
        current_light += 1
        if current_light == num_lights:
            current_light = 0
            up_down = up_down ^ 1
           
    

    

# Function to play MIDI file events
def play_midi_file(synth, midi_file_path, io_exp, channel):
    # Open the MIDI file with Mido
    mid = mido.MidiFile(midi_file_path)
    print("Playing " + midi_file_path)
    # Create a MIDI input for receiving and processing events
    for message in mid.play():
        parse_midi(synth, message, io_exp,channel)


def main(midi, sf2, channel):
    global current_light
    io_exp = init_io_expander()
    # synth = init_synth(sf2)
    # channel = int(channel)
    pattern = random.randint(0,num_patterns-1)
    length = random.uniform(5,30)
    pattern_change_time = time.time() + length
    interval = random.uniform(0.025,3.0)
    print(pattern)
    print(interval)
    print(length)
    while(1):
        current_time = time.time()
        if current_time > pattern_change_time:
            pattern = random.randint(0,num_patterns-1)
            length = random.uniform(5,30)
            pattern_change_time = time.time() + length
            current_light = 0
            interval = random.uniform(0.025,3.0)
            print(pattern)
            print(interval)
            print(length)
        
        play_light_pattern(pattern,io_exp, interval)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--midi", help="MIDI File", default="jingle_bells_bb.mid")
    parser.add_argument("--sf2", help="SoundFont File", default='Nintendo_64_ver_2.0.sf2')
    parser.add_argument("--channel", help="MIDI Channel", default=0)
    args = parser.parse_args()

    main(args.midi, args.sf2, args.channel)