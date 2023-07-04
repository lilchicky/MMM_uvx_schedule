# Magic Mirror Module for displaying the next UVX bus in the Provo/Orem, UT area!

Made a couple arrays of the UVX schedule for weekdays and saturdays, and used a couple checks to determine the next arrival for the 2230 North station in Provo.
The arrays are hard coded, but it should be pretty easy to adapt this code to work for any static bus schedules anywhere. You could probably also adjust the code
to read from JSON files to make uploading schedules easier.

Currently doesn't account for holiday schedules, because the UTA API is a nightmare to figure out for me, so I just added a static warning to check holiday times.

_To install through command line on Raspberry Pi:_
_cd ~/MagicMirror/modules_
_git clone https://github.com/lilchicky/MMM_uvx_schedule.git_
