# LCR API

Forked from: https://github.com/philipbl/LCR-API.  Updated in PIP as lcr-api-2 to pull the new version that works.

A Python API for Leader and Clerk Resources for the LDS Church. I've only tested it with Python 3.5+.

The following calls are supported, which correspond to a page in LCR:

- Birthday list (`birthday_list`)
- Members moved out (`members_moved_out`)
- Members moved in (`members_moved_in`)
- Member list (`member_list`)
- Calling list by organization (`callings`)
- Members with callings list (`members_with_callings_list`)
- Recommend Status (`recommend_status`)
- Individual Photo (`individual_photo`)
- Ministering List (`ministering`)
- Access Table (`access_table`)

More calls will be supported as I have time. Pull requests are welcomed!

## Disclaimer

This code is rough around the edges. I don't handle any cases where a person using this code doesn't have permissions to access the reports, so I don't know what will happen.

## Install

To install, run

```
pip3 install lcr-api-2
```

## Usage

```python
from lcr import API as LCR

lcr = LCR("<LDS USERNAME>", "<LDS PASSWORD>", <UNIT NUMBER>)

months = 5
move_ins = lcr.members_moved_in(months)

for member in move_ins:
    print("{}: {}".format(member['spokenName'], member['textAddress']))
```


### To Do
- Add more tests
- Support more reports and calls

