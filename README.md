# Dorat

Dorat is a command line interface, and workflow enabler, for Ghidra Headless. It is intended to
make it simple to perform specific analyses on specific binaries.

# Usage

As of the initial release, you'll need to edit the script and update the path to your
Ghidra scripts directory and the Ghidra main directory. Future revisions will use
either environment variables or a file override.

```
Usage:
dorat --binary BINARY --script SCRIPT
```

# Examples:

Execute a script on a specified binary.
```
dorat --binary test_binary --script ListFunctionCalls.java
```

Show all the docs!
```
dorat --help
```

Run first time configuration.
```
dorat --config
```

List scripts
```
dorat --list
```

