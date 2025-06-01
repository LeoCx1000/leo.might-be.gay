# Dealing with a faulty QTTabBar uninstaller

A while back, back when I used Windows 10, I installed this great program called
QTTabBar. It was great, because it allowed me to have multiple tabs open in file
explorer, greatly improving my productivity. However, after updating to Windows
11, the program started to have conflicts with the built-in tabs that the nex
explorer now includes, and since tabs were built-in, I could now uninstall this
program.

Unfortunately, the uninstaller tool for it seems to do a particularly poor job
at cleaning up after itself, because it left a tonne of random files and
registry entries for QTTabBer which were messing up with my file explorer.

## The Problem

Every time I double-clicked on a folder from file explorer, it opened on a new
window instead of opening in-place. This was particularly annoying because it
broke back/forwards functionality within the explorer, and made it really
annoying to use.

## The Solution

First off, I used [everything](https://www.voidtools.com/) which is a program
that indexes your entire drive for blazingly fast searching of files, and
searched for `QTTabBar`, and proceeded to go around deleting all the files and
folders with that name. Great, now I had less bloat on my system because of
useless files, however the problem at hand still persisted.

After looking around on the web, I found out that the issue was because the
uninstaller also left some registry entries dotted about, which added a context
menu item when right-clicking on a folder. I presume this was bound to opening
the folder in a new tab, but now that the program is gone, it seems to default
to opening a new window instead. It was specifically the following path in the
registry editor that contained a lot of entries pertaining QTTabBar:

```
Computer\HKEY_CLASSES_ROOT\Folder\shell
```

After deleting these, and then going around using the search tool in the
Registry Editor to delete a bunch that referenced `QTTabBar` (and then killing
and reopening Explorer), my PC was back to normal.

> Note: **DO NOT delete random registry entries if you don't know what you're
> doing (I don't) OR if you don't know how to fix it up if you _do_ delete
> something important (I do). Do this at your own risk.**
