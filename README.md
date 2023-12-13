# Python API for Controlling RS232/Text Based A/V Equipment (pyavcontrol)

![beta_badge](https://img.shields.io/badge/maturity-Beta-yellow.png)
[![PyPi](https://img.shields.io/pypi/v/pyavcontrol.svg)](https://pypi.python.org/pypi/pyavcontrol)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Build Status](https://github.com/rsnodgrass/pyavcontrol/actions/workflows/ci.yml/badge.svg)](https://github.com/rsnodgrass/pyavcontrol/actions/workflows/ci.yml)

This emulator exposes a `pyserial` (or IP2SL) compatible TCP port that can receive/respond to
commands sent using simple text based (often RS232 compatible) protocols used by various audio
visual equipment. This came about trying to develop client libraries for controlling
McIntosh, Xantech, and Anthem processors where the protocols were actually quite simple and
similar. After building several custom libraries, a "common" YAML based protocol definition
format was created so building additional librares was not necessary...plus this would allow
quickly spinning up libraries in other languages (Go, C, etc).


## Emulator

Of particular interest, is the included device emulator which takes a properly defined
device's protocol and starts a server that will respond to all commands as if the
a physical device was connected. This is exceptionally useful for testing AND can be
used by clients developed in other languages as well.

Example starting the McIntosh MX160 emulator:

```
./emulator.py --model mcintosh_mx160 -d
```


## Support

This supports any A/V equipment supported by [pyavcontrol]()

See [SUPPORTED.md](SUPPORTED.md) for the complete list of supported equipment.

## Background


## Connection URL

This interface uses URLs for specifying the communication transport
to use, as defined in [pyserial](https://pyserial.readthedocs.io/en/latest/url_handlers.html), to allow a wide variety of underlying mechanisms.

# Future Ideas

- Add ability to define EmulatorHandler class for each device model that allows additional programmatic
  override of handle_command() which can maintain state between calls for someone who wants to implement
  functionality where later queries should pickup previously set state.

# See Also

- [pyavcontrol](https://github.com/rsnodgrass/pyavcontrol)