import brotli
import os
import sys
import errno

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
                version = int(trans_list.readline())
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

    version_names = {
        1: "Android Lollipop 5.0",
        2: "Android Lollipop 5.1",
        3: "Android Marshmallow 6.x",
        4: "Android Nougat 7.x / Oreo 8.x"
    }
    print(f"sdat2img module: Detected {version_names.get(version, 'Unknown Android version')}")

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


def convert_rom_files():
    """
    Main function:
    1. Decompress .dat.br to .dat using Brotli.
    2. Convert .dat and .transfer.list to .img using sdat2img logic.
    Files must be in the same directory as the script.
    """
    
    br_file_name = "system.new.dat.br"
    transfer_list_name = "system.transfer.list"
    output_img_name = "system.img"
    
    print(f"🚀 ROM Extractor v1.1 Starting 🚀")
    print("----------------------------------------")
    print(f"Processing files: '{br_file_name}' and '{transfer_list_name}'")
    print(f"Output image will be: '{output_img_name}'")
    print("----------------------------------------")

    if not os.path.exists(br_file_name):
        print(f"Error: '{br_file_name}' not found. Please place it in the same folder as this script.")
        return False

    if not os.path.exists(transfer_list_name):
        print(f"Error: '{transfer_list_name}' not found.")
        return False

    dat_file_path = br_file_name.replace(".br", "")
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
        print("This script requires Python 3.6 or newer.")
        print(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.")
        input('Press Enter to exit...')
        sys.exit(1)

    if len(sys.argv) > 1:
        print("Warning: This script is self-contained and does not accept command-line arguments.")
        print("To process other partitions (like product/vendor), modify the filenames in the script.")
        input('Press Enter to exit...')
        sys.exit(1)

    overall_success = convert_rom_files()

    print("\n----------------------------------------")
    if overall_success:
        print("🎉 Conversion completed successfully!")
        print("You can now use tools like DiskGenius, 7-Zip, or Linux Reader to explore the .img file.")
    else:
        print("⚠️ Conversion failed. Please check the error messages above.")
    print("----------------------------------------")
    
    input('Press Enter to exit...')
