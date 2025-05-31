# ⚠️ Recommended: Use the PyPI Version Instead! 🚀

> For easier installation and faster updates, we **highly recommend** using the [PyPI-ready version of this project](https://github.com/tntapple219/sdat2img_brotli_forPyPI)!  
> This repository may receive updates **slightly later**, so please consider switching to the PyPI version for the latest features and improvements. 🙌

## 📦 Quick Installation

```bash
pip install sdat2img_brotli
```

👉 [Go to sdat2img_brotli_forPyPI](https://github.com/tntapple219/sdat2img_brotli_forPyPI) 
---

# 📦 ROM Extractor (sdat2img + Brotli Support)

This Python script extracts and converts Android OTA update files—specifically `.dat.br` and `.transfer.list`—into a usable `.img` disk image. This is especially useful for unpacking `system`, `vendor`, or `product` partitions from A/B OTA packages.

---

## ✅ Features

* ✔️ Supports `.dat.br` files (Brotli compressed)
* ✔️ Converts `.dat` + `.transfer.list` into a flashable `.img`
* ✔️ Automatic decompression and cleanup
* ✔️ **Flexible input/output paths via command-line arguments (CLI)**
* ✔️ **Defaults to current directory files if no arguments are provided**
* ✔️ User-friendly logs and error messages

---

## 📂 Input Files

Place the following files in the same directory as the script, or specify their paths using **command-line arguments**:

* `system.new.dat.br` (Default)
* `system.transfer.list` (Default)

---

## 🧰 Requirements

* Python 3.6 or higher
* Brotli module for Python

Install Brotli using pip:

```bash
pip install brotli
```

---

## 🚀 Usage

This script offers **two convenient ways** to run it:

### 1. Simple Run (Using Default Files)

If your `system.new.dat.br` and `system.transfer.list` files are in the same directory as the script, just run:

```bash
python sdat2img_brotli.py
```

The script will automatically:
1.  Decompress `system.new.dat.br` into `system.new.dat`
2.  Convert `system.new.dat` and `system.transfer.list` into `system.img`

### 2. Advanced Run (Using Command-Line Arguments)

For more flexibility, you can specify the paths and output filename using arguments:

```bash
python sdat2img_brotli.py -d <path_to_dat_br_file> -t <path_to_transfer_list_file> -o <output_img_name>
```

**Arguments:**

* `-d` or `--datbr`: Specifies the path to the `.dat.br` file (e.g., `"C:\roms\vendor.new.dat.br"`)
* `-t` or `--transferlist`: Specifies the path to the `.transfer.list` file (e.g., `"C:\roms\vendor.transfer.list"`)
* `-o` or `--outputimg`: Specifies the name and path for the output `.img` file (e.g., `"extracted_vendor.img"`)

**Examples:**

* **Convert a `vendor` partition located in a specific folder:**
    ```bash
    python sdat2img_brotli.py -d "D:\OTA\vendor.new.dat.br" -t "D:\OTA\vendor.transfer.list" -o "vendor.img"
    ```
* **Generate an `img` with a custom name in the current directory:**
    ```bash
    python sdat2img_brotli.py -o "my_custom_system.img"
    ```
* **Get help and see all options:**
    ```bash
    python sdat2img_brotli.py --help
    ```

---

## 👥 Output

* ✅ A `.img` file (e.g., `system.img`, `vendor.img`) — a raw disk image that can be opened with tools like:

    * 7-Zip
    * DiskGenius
    * Linux Reader (for Windows)
    * ext4 tools on Linux

---

## 🛠 Customization

With the addition of command-line arguments, you no longer need to modify the script directly for different partitions! Simply use the `-d`, `-t`, and `-o` arguments as shown in the **Usage** section.

---

## 🙏 Credits

🔗 Based on [xpirt’s original sdat2img](https://github.com/xpirt/sdat2img), which is licensed under the MIT License.  
🔧 Modified to support Brotli-compressed `.dat.br` files and enhanced with command-line arguments for better usability.  
📦 Brotli support is powered by the [Google Brotli library](https://github.com/google/brotli), also licensed under the MIT License.

---

## 📄 License

This script is open-source and released under the MIT License. Use it freely and feel free to contribute!

---
