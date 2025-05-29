# 📦 ROM Extractor (sdat2img + Brotli Support)

This Python script extracts and converts Android OTA update files—specifically `.dat.br` and `.transfer.list`—into a usable `.img` disk image. This is especially useful for unpacking `system`, `vendor`, or `product` partitions from A/B OTA packages.

## ✅ Features

* ✔️ Supports `.dat.br` files (Brotli compressed)
* ✔️ Converts `.dat` + `.transfer.list` into a flashable `.img`
* ✔️ Automatic decompression and cleanup
* ✔️ No command-line arguments needed
* ✔️ User-friendly logs and error messages

## 📂 Input Files

Place the following files in the same directory as the script:

* `system.new.dat.br`
* `system.transfer.list`

> You can also rename the script variables to process other partitions like `vendor` or `product`.

## 🧰 Requirements

* Python 3.6 or higher
* Brotli module for Python

Install Brotli using pip:

```bash
pip install brotli
```

## 🚀 Usage

Simply run the script:

```bash
python sdat2img_brotli.py
```

The script performs two main steps:

1. Decompresses `system.new.dat.br` into `system.new.dat`
2. Converts `.dat` and `.transfer.list` into `system.img`

## 👥 Output

* ✅ `system.img` — a raw disk image that can be opened with tools like:

  * 7-Zip
  * DiskGenius
  * Linux Reader (for Windows)
  * ext4 tools on Linux

## 🛠 Customization

To convert a different partition (e.g. `vendor`), modify the following variables at the top of the script:

```python
br_file_name = "vendor.new.dat.br"
transfer_list_name = "vendor.transfer.list"
output_img_name = "vendor.img"
```

## 🙏 Credits

* Based on [xpirt’s original sdat2img](https://gist.github.com/xpirt/2c11438a0f9077227d8905391c49926d)
* Modified for Brotli compatibility and easier usage

## 📄 License

This script is open-source and released under the MIT License. Use it freely and feel free to contribute!
