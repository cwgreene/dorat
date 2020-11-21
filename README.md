# Dorat

Dorat is a command line interface, and workflow enabler, for Ghidra Headless. It is intended to
make it simple to perform specific analyses on specific binaries. Also, here are some useful
[scripts](https://github.com/cwgreene/ghidrascripts) that can be used with dorat.

# Usage

As of the initial release, you'll need to edit the script and update the path to your
Ghidra scripts directory and the Ghidra main directory. Future revisions will use
either environment variables or a file override.

```
usage: dorat.py [-h] [--binary BINARY] [--script SCRIPT] [--show-stderr]
                [--show-raw] [--list] [--config]

optional arguments:
  -h, --help       show this help message and exit

main group:
  --binary BINARY  REQUIRED: target binary
  --script SCRIPT  REQUIRED: target script
  --show-stderr    dump stderr
  --show-raw       dump raw output

list command:
  --list           list scripts

configuration options:
  --config         configure dorat
```

# Examples:
List scripts
```
$ dorat --list
FindLibcCalls.java
FunctionCalls.java
```
Execute a script on a specified binary.
```
$ dorat --binary example_binary --script DecompileFunction.java main
undefined8 main(void)

{
  long in_FS_OFFSET;
  char local_1a [10];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  gets(local_1a);
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```
