import mido
import time
import fluidsynth
import pcf8574_io
import argparse
import os

note_light_dict = [{},{}]
next_light_index = [0,0]
CHANNEL_1 = 0
CHANNEL_2 = 1
num_lights = 8

song_dict = {"jingle_bells_bb.mid" : [0,4],
             "Never-Gonna-Give-You-Up-3.mid" : [15,5],
             'The Twelve Days of Christmas.mid' : [0,1], 
             'O Holy Night.mid' : [0,1], 
             'O Christmas Tree.mid' : [0,1], 
             'We Wish You a Merry Christmas.mid' : [0,1], 
             'Deck the Hall.mid' : [0,1], 
             'Silent Night.mid': [0,1]}
ch1 = 0
ch2 = 1

def init_synth(soundfont_path):
    
    synth = fluidsynth.Synth()
    synth.start()
    sfid = synth.sfload(soundfont_path)  # Load the SoundFont
    synth.program_select(0,sfid, 0, 0)  # Select bank, soundfont, preset, and channel
    synth.maxpolyphony = 128
    return synth

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
        # print(message.channel)
        # if message.channel == channel:
        control_lights(message.note, 1, io_exp, message.channel)
            # print(message)

    elif message.type == 'note_off':
        synth.noteoff(message.channel, message.note)
        
        # if message.channel == channel:
        control_lights(message.note, 0, io_exp, message.channel)

    elif message.type == 'control_change':
        synth.cc(message.channel, message.control, message.value)

    elif message.type == 'program_change':
        synth.program_change(message.channel, message.program)

def control_lights(note, on_off, io_exp, channel):

    global next_light_index
    global ch1
    global ch2

    if on_off:
        command = "LOW"
    else:
        command = "HIGH"

    if channel == ch1:
        index = 0
    elif channel == ch2:
        index = 1
    else:
        return

    #check to see if the note is already in the dictionary
    if note in note_light_dict[index]:
        light = note_light_dict[index][note]
        io_exp.write(light, command)
    else:
        light = 'p' + str(next_light_index[index])
        next_light_index[index] += 1
        if channel == ch1:
            if next_light_index[index] == num_lights/2:
                next_light_index[index] = 0
        else:

            if next_light_index[index] == num_lights:
                next_light_index[index] = 4
        note_light_dict[index][note] = light
    

# Function to play MIDI file events
def play_midi_file(synth, midi_file_path, io_exp, channel):
    # Open the MIDI file with Mido
    mid = mido.MidiFile(midi_file_path)
    print("Playing " + midi_file_path)
    # Create a MIDI input for receiving and processing events
    for message in mid.play():
        parse_midi(synth, message, io_exp,channel)


def main(midi, sf2, channel):
    io_exp = init_io_expander()
    synth = init_synth(sf2)

    # Get the current directory
    current_directory = os.getcwd()

    # List all files and directories in the current directory
    all_files_and_dirs = os.listdir(current_directory)

    # Filter only files
    files = [f for f in all_files_and_dirs if f.endswith('.mid')]

    print(files)


    channel = int(channel)
    

    while(1):
        for f in files:
            ch1 = song_dict[f][0]
            ch2 = song_dict[f][1]
            print(ch1)
            print(ch2)
            play_midi_file(synth, f, io_exp, channel)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--midi", help="MIDI File", default="jingle_bells_bb.mid")
    parser.add_argument("--sf2", help="SoundFont File", default='Nintendo_64_ver_2.0.sf2')
    parser.add_argument("--channel", help="MIDI Channel", default=0)
    args = parser.parse_args()

    main(args.midi, args.sf2, args.channel)