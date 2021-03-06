README
======

This script was written for my own needs (extending Xubuntu desktop with external display) during one evening, so it's not very configurable. Most important facts are:
- it handles only two displays (I don't need more ;) ), 
- they are aligned to the bottom by default
- script can crash because of improper parameters etc. - there are some defaults or validation provided by argparse, but it's definitely not enough to be proud of how it works
- you can use it in any way you need, as long as it stays free: you can even print it and feed your dog with it if you want to ;)
- I did a few tests on my own computer with HDMI and VGA external display and everything was OK, but just in case: you use it on your own risk ;) 

Example:
--------

### There are two displays - LVDS1 and HDMI1:

    ```bash
    michal@laptop:~/displaymanager$ xrandr
    Screen 0: minimum 320 x 200, current 1366 x 768, maximum 8192 x 8192
    LVDS1 connected 1366x768+0+0 (normal left inverted right x axis y axis) 293mm x 164mm
       1366x768       60.0*+   40.0  
       1360x768       59.8     60.0  
       1024x768       60.0  
       800x600        60.3     56.2  
       640x480        59.9  
    VGA1 disconnected (normal left inverted right x axis y axis)
    HDMI1 connected (normal left inverted right x axis y axis)
       1920x1080      60.0 +
       1280x1024      75.0     60.0  
       1152x864       75.0  
       1024x768       75.1     60.0  
       800x600        75.0     60.3  
       640x480        75.0     60.0  
       720x400        70.1  
    DP1 disconnected (normal left inverted right x axis y axis)
    ```

### We want to have desktop like this with LVDS1 as primary:

```bash
                         ,-----------------------.
                         |                       |
        ,---------------.|                       |
        |               ||         HDMI1         |
        |     LVDS1     ||                       |
        |               ||                       |
        '---------------''-----------------------'
```

Displays need to be aligned this way because the bottom of the primary screen
has to be accessible for user to access the menu.

### The solution is (verbose is - obviously - optional):

```bash
./displaymanager.py -m dual -i "LVDS1;1366x768;60" -e "HDMI1;1920x1080;60" --verbose
```

"LVDS1;1366x768;60" means: 
- display name: LVDS1
- resolution: 1366x768
- refresh rate: 60 Hz

Analogously for HDMI1.

### Before (or after) unplugging the external monitor the default state can be 
restored with:

```bash
./displaymanager.py -m single -i "LVDS1;1366x768;60" -e "HDMI1" --verbose
```

The '-e' parameter is needed only for turning the display off - there's no need 
to provide other details like resolution. It works ONLY for external display and 
ONLY when switching to 'single' mode.

### Check `./displaymanager.py -h` for a bit (really a little bit) more details and info.

Tip 1: If you want to have external on the right, use: -o "EI" (default is "IE") 

Tip 2: using '--verbose' together with '--dryrun' makes it most useful to learn how
it works.


##### Author 
Michał Michalski <displaymanager@michalski.im>

http://devblog.michalski.im

https://github.com/regispl

Feel free to contact me with a feedback.
