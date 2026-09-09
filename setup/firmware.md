firmware

Klipper firmware for the V4.2.7 board — how it is built and how it is flashed.

The **host** half — the Docker stack, container gotchas, both web UIs and the
notifiers — is documented separately from this file.

firmware build

Klipper source lives inside the `mkuf/klipper` image at `/opt/klipper`, but that
image carries **no ARM toolchain**. Build in a throwaway container instead,
pinned to the same commit the runtime image uses:

```bash
mkdir -p /srv/klipper/fw
docker run --rm -v /srv/klipper/fw:/out debian:trixie bash -c '
set -e
apt-get update -qq
apt-get install -y -qq --no-install-recommends git make gcc-arm-none-eabi libnewlib-arm-none-eabi python3 ca-certificates
git clone -q https://github.com/Klipper3d/klipper /klipper
cd /klipper && git checkout -q d6ea62542
printf "%s\n" \
  CONFIG_MACH_STM32=y \
  CONFIG_MACH_STM32F103=y \
  CONFIG_STM32_FLASH_START_7000=y \
  CONFIG_STM32_SERIAL_USART1=y > .config
make olddefconfig
make -j"$(nproc)"
cp out/klipper.bin /out/firmware-427-1.bin
'
```

| Option | Why |
|---|---|
| `MACH_STM32F103` | Correct for STM32F103 **and** GD32F303 batches |
| `FLASH_START_7000` | 28 KiB the vendor bootloader offset |
| `SERIAL_USART1` | The CH340 is wired to PA10/PA9, **not** USB |

Result is ~30–40 KB. The firmware must be rebuilt to match whenever the
`mkuf/klipper` image tag changes on [knave](../README.md) —
Klipper refuses to run a host and MCU built from different commits.

flashing

SD card, **FAT32, ≤32 GB, 4096-byte allocation**, one file. Board can be USB-
powered for this.

**Use a new filename every single flash** — `firmware-427-1.bin`,
`firmware-427-2.bin`, … The bootloader skips a file whose name matches the last
one it flashed, so reusing `firmware.bin` silently does nothing and you spend an
hour debugging a flash that never happened.

Insert, power-cycle, wait ~15 s. Verification is Klipper connecting — there is
no success LED to trust.

---

Host: [`../knave/README.md`](../README.md) ·
Config: [`configuration.md`](configuration.md)
