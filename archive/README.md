# Archive

Git tracks `archive/manifest.yaml`. The files themselves live in `archive/cache/` and are gitignored. That split keeps the ISE tarball and the Adept packages on this machine without putting proprietary installers in the repository. Manuals and photos are cached the same way so a retired Digilent page can disappear without taking the bring-up with it.

`make archive` runs `scripts/archive.py`.

- A row with a public file URL is downloaded when the cache copy is missing or its sha256 does not match.
- A row marked manual is skipped until you copy the file to `path`. This is the ISE tarball. AMD serves it only to a logged-in account. Adept `.deb` packages are manual too: put the runtime and the utilities package that provides `djtgcfg` at the paths in the manifest. The cached Adept pair is runtime 2.27.9 and utilities 2.7.1. Utilities supplies `djtgcfg`. Those packages need glibc 2.23 or newer, so they stay out of the CentOS 6 ISE image and run from the host Adept tree. The WebPACK license is `archive/cache/sdk/Xilinx.lic` (manifest id `ise-webpack-lic`). The ISE tarball is still the manual drop `Xilinx_ISE_DS_Lin_14.7_1015_1.tar`, the 6.09 GB Linux full installer, not the Windows 10 virtual-machine image.
- A file that already matches its sha256 is left alone.
- Size and retrieve date are written to `archive/cache/status.json`. When a download is a zip, the script lists the members there. Board pages link Gerbers or an IPC netlist only if that listing contains them. The reference-center links checked for this set are schematic PDFs, so the board pages say PCB and netlist files were not in the published package until a zip proves otherwise.
- After `make image` succeeds, `make archive-image` runs `docker save` of `xilinx-ise-hil` into `archive/cache/images/` and records that row. Restoring the toolchain is `docker load` of that tar, not another silent install.

## Kinds

| Kind | What goes here |
| --- | --- |
| `doc` | Reference manuals, UG230, UG130, the XC2-XL manual and sell sheet, the Breadboard 1 manual, schematic, and sell sheet, the BSS138 datasheet and level-shifter app notes, the JTAG-SMT2 manuals, the Huasheng bench-pod plates, the Bus Blaster v4.1a design overview and schematic, schematics, master UCF zips, the ADV7183B datasheet |
| `image` | Board photos, and the `docker save` of the ISE image |
| `sdk` | ISE 14.7 Linux tarball and Adept runtime and utilities. Proprietary. Not committed |
| `binary` | Bitstreams this repo builds, kept beside the run report. A vendor demo bitstream is added only when the reference center still publishes a stable file |

## Fields

Each manifest item has `id`, `kind`, `board`, `url`, `path`, `sha256`, and `license`. `sha256` may be empty until the first successful fetch, which fills it. `manual: true` means the script will not try the URL. `optional: true` means a failed download is reported and does not fail `make archive`.

The Docker build reads `archive/cache/sdk/`. A missing ISE tarball or a missing Adept package fails `make image` with the manifest id to fetch. Cable drivers are not installed. Programming is Adept inside the container.

## Licenses

Vendor PDFs and the ISE and Adept installers stay in the cache for local use. The lessons cite them by archive id. They are not copied into `docs/`.
