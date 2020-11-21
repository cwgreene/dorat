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
$ dorat --binary test_binary --script FunctionCalls.java
{
  "functions" : [ {
    "variables" : [ ],
    "calls" : [ {
      "funcName" : "__gmon_start__",
      "arguments" : [ "" ],
      "address" : "00100558"
    } ],
    "name" : "_init"
  }, {
    "variables" : [ {
      "name" : "local_10",
      "size" : 8,
      "stackOffset" : -16
    } ],
    "calls" : [ {
      "funcName" : "__libc_start_main",
      "arguments" : [ "main", "in_stack_00000000", "&stack0x00000008", "__libc_csu_init", "__libc_csu_fini", "param_3", "auStack8" ],
      "address" : "001005c4"
    } ],
    "name" : "_start"
  }, {
    "variables" : [ ],
    "calls" : [ ],
    "name" : "deregister_tm_clones"
  }, {
    "variables" : [ ],
    "calls" : [ ],
    "name" : "register_tm_clones"
  }, {
    "variables" : [ ],
    "calls" : [ {
      "funcName" : "__cxa_finalize",
      "arguments" : [ "__dso_handle" ],
      "address" : "0010067e"
    }, {
      "funcName" : "deregister_tm_clones",
      "arguments" : [ "" ],
      "address" : "00100683"
    } ],
    "name" : "__do_global_dtors_aux"
  }, {
    "variables" : [ ],
    "calls" : [ {
      "funcName" : "register_tm_clones",
      "arguments" : [ "" ],
      "address" : "001006a5"
    } ],
    "name" : "frame_dummy"
  }, {
    "variables" : [ {
      "name" : "local_10",
      "size" : 8,
      "stackOffset" : -16
    }, {
      "name" : "local_1a",
      "size" : 1,
      "stackOffset" : -26
    } ],
    "calls" : [ {
      "funcName" : "gets",
      "arguments" : [ "local_1a" ],
      "address" : "001006cd"
    }, {
      "funcName" : "__stack_chk_fail",
      "arguments" : [ "" ],
      "address" : "001006e6"
    } ],
    "name" : "main"
  }, {
    "variables" : [ ],
    "calls" : [ {
      "funcName" : "_init",
      "arguments" : [ "param_1" ],
      "address" : "0010071c"
    } ],
    "name" : "__libc_csu_init"
  }, {
    "variables" : [ ],
    "calls" : [ ],
    "name" : "__libc_csu_fini"
  }, {
    "variables" : [ ],
    "calls" : [ ],
    "name" : "_fini"
  } ]
}
```

