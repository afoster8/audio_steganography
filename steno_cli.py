import wave
import numpy as np
import os
import argparse


def insert_data(audio_file, message, output_file):
    try: 
        with wave.open(audio_file, 'rb') as file:
            frame_bytes = bytearray(file.readframes(file.getnframes()))
            sr = file.getframerate()
        
        message += "#####"
        message_bits = ''.join(format(ord(char), '08b') for char in message)
        message_length = len(message_bits)
        
        if message_length * 2 > len(frame_bytes):
            raise ValueError("Message is too large to be embedded in the audio file.")
        
        for i in range(message_length):
            frame_bytes[i] &= 0xFE
            frame_bytes[i] |= int(message_bits[i])
        
        with wave.open(output_file, 'wb') as file:
            file.setparams((1, 2, sr, len(frame_bytes), 'NONE', 'not compressed'))
            file.writeframes(frame_bytes)
        
    except Exception as e:
        print("An error occurred while embedding the file: ", e)


def extract_data(audio_file):
    try:
        with wave.open(audio_file, 'rb') as file:
            frame_bytes = bytearray(file.readframes(file.getnframes()))
        
        extracted_bits = []
        for byte in frame_bytes:
            extracted_bit = byte & 1
            extracted_bits.append(extracted_bit)
        
        extracted_message = ''.join(chr(int(''.join(map(str, extracted_bits[i:i+8])), 2)) for i in range(0, len(extracted_bits), 8))
        
        end_index = extracted_message.find('#####')
        if end_index != -1:
            extracted_message = extracted_message[:end_index]
        
        return extracted_message
    
    except Exception as e:
        print("An error occurred while extracting the message", e)
        return None


def main():
    parser = argparse.ArgumentParser(description="Embed or extract a message from an audio file.")
    parser.add_argument("action", choices=["embed", "extract"], help="Action to perform: embed or extract")
    parser.add_argument("audio_file", help="Path to the input audio file")
    parser.add_argument("-m", "--message", help="Message to embed (required for 'embed' action)")
    args = parser.parse_args()

    if args.action == "embed":
        if not args.message:
            parser.error("Message is required for 'embed' action")
        output_file = os.path.splitext(args.audio_file)[0] + "_embedded.wav"
        insert_data(args.audio_file, args.message, output_file)
        print("Message embedded successfully.")
    elif args.action == "extract":
        extracted_message = extract_data(args.audio_file)
        if extracted_message:
            print("Extracted message:", extracted_message)
        else:
            print("Failed to extract message.")

if __name__ == "__main__":
    main()
