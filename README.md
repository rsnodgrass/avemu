# avemu - Test Emulator for A/V Equipment RS232 Control

[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=WREP29UDAMB6G)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg)](https://buymeacoffee.com/DYks67r)

## Overview

Avemu exposes a TCP port that can emulate responses to commands sent using simple text based
(typically RS232 compatible) protocols used by various A/V equipment so testing common cases can
occur without requiring physical hardware. This came about developing client libraries for
controlling McIntosh, Lyngdorf, Xantech, and Anthem processors where the protocols were basic
text based interactions and similar. After building several custom libraries, a "common" YAML
based protocol definition format was created so building additional librares was not necessary.

Additionally, the [pyavcontrol](https://github.com/rsnodgrass/pymcintosh) YAML format defining
commands, messages, and simple tests enables quickly spinning up libraries in other languages
(Go, C, etc) that support a wide variety of devices.

#### Supported Devices

See [SUPPORTED.md](https://github.com/rsnodgrass/pymcintosh/blob/main/SUPPORTED.md) for the complete list of supported equipment.

| Manufacturer | Model      |
|--------------|------------|
| McIntosh     | MX-160     |
| McIntosh     | MX-180     |
| Lyngdorf     | TDAI-3400  |
| Lyngdorf     | CD-2       |
| Xantech      | MRAUDIO8x8 |
| HDFury       | VRROOM     |

## Example Execution

The following is an example run `avemu` with the Lyngdorf CD-2 `lyngdorf_cd2` model from [pyavcontrol](https://github.com/rsnodgrass/pyavcontrol/):

```console
% ./avemu.py --model lyngdorf_cd2
2023-12-27 22:17:46 laptop.local __main__[38770] INFO Using default port 84 for lyngdorf_cd2
2023-12-27 22:17:46 laptop.local __main__[38770] INFO Emulating model lyngdorf_cd2 on socket://0.0.0.0:84/  (also on 192.168.1.25)
Supported commands:
!DEVICE?                      !ON                           !OFF                          !PWR                          
!NEXT                         !PLAY                         !STOP                         !PREV                         
!EJECT                        !REWIND                       !WIND                         !STOPWIND                     
!STATE?                       !DIGIT(1)                     !DIGIT(2)                     !TRACK?                       
!NOFTRACKS?                   !TIME?                        !REMTIME?                     !PLAYMODE({mode})             
!PLAYMODE(0)                  !PLAYMODE(1)                  !PLAYMODE(2)                  !PLAYMODE(3)                  
!DISPMODE({mode})             !DISPMODE(0)                  !DISPMODE(1)                  !DISPMODE(2)                  
!DISPMODE(3)                  !SAMPLERATE({sample_rate})    !GAIN({gain})                 !SRC?                         
2023-12-27 22:17:50 laptop.local __main__[38770] INFO 192.168.1.125:57620 connected.
2023-12-27 22:17:50 laptop.local __main__[38770] INFO 192.168.1.125:57620 connected.
2023-12-27 22:17:50 laptop.local __main__[38770] DEBUG Received: !DEVICE?
2023-12-27 22:17:50 laptop.local handlers.default[38770] INFO Received device.name cmd: !DEVICE?
2023-12-27 22:17:50 laptop.local handlers.default[38770] DEBUG Replying to device.name !DEVICE?: !DEVICE(CD2)
2023-12-27 22:17:50 laptop.local __main__[38770] DEBUG Received: !SRC?
2023-12-27 22:17:50 laptop.local handlers.default[38770] INFO Received source.get cmd: !SRC?
2023-12-27 22:17:50 laptop.local handlers.default[38770] DEBUG Replying to source.get !SRC?: !SRC(1,"CD")
```

# Future Ideas

- Add ability to define EmulatorHandler class for each device model that allows additional programmatic
  override of handle_command() which can maintain state between calls for someone who wants to implement
  functionality where later queries should pickup previously set state.

# See Also

- [pyavcontrol](https://github.com/rsnodgrass/pyavcontrol)
