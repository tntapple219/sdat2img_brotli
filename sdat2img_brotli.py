import brotli
import os
import sys
import errno
import argparse

# --- Core logic of original sdat2img.py adapted into a single function ---
# Source: https://gist.github.com/xpirt/2c11438a0f9077227d8905391c49926d
# This version includes changes to integrate it into a standalone script

def run_sdat2img_logic(transfer_list_file, new_dat_file, output_image_file):
    """
    Executes the core logic of sdat2img.py.
    This function processes the .dat and .transfer.list files to generate a .img file.
    """
    print(f"sdat2img module: Starting conversion from '{new_dat_file}' to '{output_image_file}'")

    BLOCK_SIZE = 4096

    def rangeset(src):
        src_set = src.split(',')
        num_set = [int(item) for item in src_set]
        if len(num_set) != num_set[0] + 1:
            print(f'sdat2img module: Error parsing rangeset:\n{src}', file=sys.stderr)
            return None
        return tuple([(num_set[i], num_set[i + 1]) for i in range(1, len(num_set), 2)])

    def parse_transfer_list_file(path):
        try:
            with open(path, 'r') as trans_list:
                version = int(trans_list.readline()) # Reads version, but it's not used for printing anymore
                new_blocks = int(trans_list.readline())

                if version >= 2:
                    trans_list.readline()  # stash entries
                    trans_list.readline()  # stash blocks

                commands = []
                for line in trans_list:
                    line = line.split(' ')
                    cmd = line[0]
                    if cmd in ['erase', 'new', 'zero']:
                        r_set = rangeset(line[1])
                        if r_set is None: return None, None, None
                        commands.append([cmd, r_set])
                    else:
                        if not cmd[0].isdigit():
                            print(f'sdat2img module: Invalid command "{cmd}".', file=sys.stderr)
                            return None, None, None
                return version, new_blocks, commands
        except FileNotFoundError:
            print(f"sdat2img module: Error: Transfer list file '{path}' not found.", file=sys.stderr)
            return None, None, None
        except Exception as e:
            print(f"sdat2img module: Error while parsing transfer list: {e}", file=sys.stderr)
            return None, None, None

    version, new_blocks, commands = parse_transfer_list_file(transfer_list_file)
    if commands is None:
        return False

    # The version detection and printing lines were removed as requested.

    try:
        output_img = open(output_image_file, 'wb')
    except IOError as e:
        if e.errno == errno.EEXIST:
            print(f'sdat2img module: Error: Output file "{e.filename}" already exists.', file=sys.stderr)
            return False
        else:
            raise

    try:
        new_data_file = open(new_dat_file, 'rb')
    except FileNotFoundError:
        print(f"sdat2img module: Error: Data file '{new_dat_file}' not found.", file=sys.stderr)
        output_img.close()
        return False

    all_block_sets = [i for command in commands for i in command[1]]
    if not all_block_sets:
        print("sdat2img module: No block operation commands found.", file=sys.stderr)
        output_img.close()
        new_data_file.close()
        return False

    max_file_size = max(pair[1] for pair in all_block_sets) * BLOCK_SIZE

    for command in commands:
        if command[0] == 'new':
            for block in command[1]:
                begin, end = block
                block_count = end - begin
                output_img.seek(begin * BLOCK_SIZE)
                while block_count > 0:
                    data_read = new_data_file.read(BLOCK_SIZE)
                    if not data_read:
                        print(f"sdat2img module: Error: Unexpected end of data file '{new_dat_file}'.", file=sys.stderr)
                        output_img.close()
                        new_data_file.close()
                        return False
                    output_img.write(data_read)
                    block_count -= 1
        else:
            pass  # skip 'erase' and 'zero' commands

    if output_img.tell() < max_file_size:
        output_img.truncate(max_file_size)

    output_img.close()
    new_data_file.close()
    print(f'sdat2img module: Conversion completed. Output image: {os.path.realpath(output_img.name)}')
    return True


def convert_rom_files(br_file_name, transfer_list_name, output_img_name):
    """
    Main function:
    1. Decompress .dat.br to .dat using Brotli.
    2. Convert .dat and .transfer.list to .img using sdat2img logic.
    Files must be in the same directory as the script, or paths provided.
    """
    
    print(f"🚀 ROM Extractor v1.4 Starting 🚀") # Updated version number!
    print("----------------------------------------")
    print(f"Processing files: '{br_file_name}' and '{transfer_list_name}'")
    print(f"Output image will be: '{output_img_name}'")
    print("----------------------------------------")

    if not os.path.exists(br_file_name):
        print(f"Error: '{br_file_name}' not found. Please ensure the path is correct.")
        return False

    if not os.path.exists(transfer_list_name):
        print(f"Error: '{transfer_list_name}' not found. Please ensure the path is correct.")
        return False

    dat_file_path = br_file_name.replace(".br", "")
    # Ensure the .dat file path is correctly formed, ideally in the same directory as the .dat.br.
    # For simplicity, we assume .dat.br is the full input path and .dat will be generated in the same directory.
    if not dat_file_path.endswith(".dat"):
        base, ext = os.path.splitext(br_file_name)
        if ext == ".br":
            dat_file_path = base # Remove .br
            if not dat_file_path.endswith(".dat"): # Ensure it ends with .dat
                dat_file_path += ".dat"
        else:
            # If not .br, it might already be .dat or another extension, simply append .dat suffix
            dat_file_path = br_file_name + ".dat"


    print(f"\nStep 1/2: Decompressing '{br_file_name}' to '{dat_file_path}'...")
    try:
        with open(br_file_name, 'rb') as f_in:
            decompressed_data = brotli.decompress(f_in.read())
            with open(dat_file_path, 'wb') as f_out:
                f_out.write(decompressed_data)
        print("✅ Decompression completed.")
    except brotli.error as e:
        print(f"❌ Brotli decompression failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unknown error during decompression: {e}")
        return False

    print(f"\nStep 2/2: Converting '{dat_file_path}' to '{output_img_name}'...")
    
    success = False
    try:
        success = run_sdat2img_logic(transfer_list_name, dat_file_path, output_img_name)
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
    finally:
        if os.path.exists(dat_file_path):
            print(f"\nCleaning up temporary file '{dat_file_path}'...")
            os.remove(dat_file_path)
            print("✅ Cleanup done.")
            
    return success


if __name__ == "__main__":
    
    if sys.version_info < (3, 6):
        print("This script requires Python 3.6 or newer. (ಥ﹏ಥ)")
        print(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.")
        input('Press Enter to exit...')
        sys.exit(1)

    # Set up command-line argument parser
    parser = argparse.ArgumentParser(
        description='✨ ROM Extractor: Decompresses .dat.br and converts to .img file. ✨',
        formatter_class=argparse.RawTextHelpFormatter # Preserve description formatting
    )
    
    parser.add_argument(
        '-d', '--datbr', 
        type=str, 
        default="system.new.dat.br",
        help='Specifies the path to the .dat.br file.\n'
             'Example: -d "C:\\roms\\my_system.new.dat.br"\n'
             'Default: system.new.dat.br'
    )
    parser.add_argument(
        '-t', '--transferlist', 
        type=str, 
        default="system.transfer.list",
        help='Specifies the path to the .transfer.list file.\n'
             'Example: -t "C:\\roms\\my_system.transfer.list"\n'
             'Default: system.transfer.list'
    )
    parser.add_argument(
        '-o', '--outputimg', 
        type=str, 
        default="system.img",
        help='Specifies the name and path for the output .img file.\n'
             'Example: -o "extracted_system.img"\n'
             'Default: system.img'
    )

    args = parser.parse_args()

    # Display the parameters being used
    print("\n----------------------------------------")
    print("🚀 Command-line arguments set:")
    print(f"  .dat.br file: {args.datbr}")
    print(f"  .transfer.list file: {args.transferlist}")
    print(f"  Output .img file: {args.outputimg}")
    print("----------------------------------------\n")

    overall_success = convert_rom_files(args.datbr, args.transferlist, args.outputimg)

    print("\n----------------------------------------")
    if overall_success:
        print("🎉 Conversion completed successfully! You're amazing! ٩(๑•̀ω•́๑)۶")
        print("You can now use tools like DiskGenius, 7-Zip, or Linux Reader to explore the .img file.")
    else:
        print("⚠️ Conversion failed. Please check the error messages above! (╯︵╰)")
    print("----------------------------------------")
    
    input('Press Enter to exit... (｡◕‿◕｡)')
