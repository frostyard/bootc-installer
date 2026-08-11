# End-to-end tests

The install-path end-to-end test lives in
[`tests/integration/test_e2e_install.py`](../integration/test_e2e_install.py).
It performs a destructive installation to a loop-backed disk and can optionally
boot the result with QEMU.

Run it as root with a locally built fisherman binary:

```bash
sudo FISHERMAN_BIN=/path/to/fisherman \
  pytest tests/integration/test_e2e_install.py -v -s
```

To include the QEMU boot verification:

```bash
sudo FISHERMAN_BIN=/path/to/fisherman BOOT_VERIFY=1 \
  pytest tests/integration/test_e2e_install.py -v -s
```

These tests are intentionally not part of pull-request CI because they require
root privileges, loop devices, host storage tools, and optionally hardware
virtualization. The nightly workflow runs the integration suite in a supported
environment.
