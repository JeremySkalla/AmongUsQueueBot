# Discord Among Us Queue Bot - v0.1

![GitHub last commit](https://img.shields.io/github/last-commit/JeremySkalla/AmongUsQueueBot)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/JeremySkalla/AmongUsQueueBot)
![GitHub](https://img.shields.io/github/license/JeremySkalla/pysmashgg)

## Overview

#### This is a simple discord bot written in Python for managing Among Us and other game queues -- Not currently publicly running, but feel free to download and set up your own

## Authors

- **Jeremy Skalla: [https://github.com/JeremySkalla](https://github.com/JeremySkalla)**
- **George Owen: [https://github.com/gowin20](https://github.com/gowin20)**

## Motivation

It's as simple as the fact that we really like Among Us. Sometimes, when you've already got a full lobby, and three people want in, you have to decide who gets in. No more! Now, this bot will just remember who queued first, and no one has to get their feelings hurt because they didn't get picked first.

## Commands:

- `.queue`: **Adds player to queue and prints out the current queue**
  - Use: `.queue`
  - Other Names: `.q`, `.que`, `.queue`, `.joinqueue`, `.cue`

- `.unqueue`: **Removes player from queue**
  - Default Input: `"Among Us"`
  - Use: `.unqueue <name>`
  - Other Names: `.unq`, `.unque`, `.leave`, `.leaveq`, `.leaveque`, `.leavequeue`, `.dq`, `.deq`, `.deque`, `.dequeue`

- `.ping`: **Pings players in queue when spots are open**
  - Default Input: NONE
  - Use: `.ping <num> <name>` 
  - Other Names: `.ping`, `.pingplayer`, `.need`, `.needplayer`

- `.view`: **Prints out the queue with its name**
  - Default Input: `"Among Us"`
  - Use: `.view <game>`
  - Other Names: `.view`, `.viewq`, `.viewqueue`, `.print`, `.printq`, `.printqueue`

- `.length`: **Displays # of users in queue**
  - Default Input: `"Among Us"`
  - Use: `.length <name>`
  - Other Names: `.qlength`, `.quelength`, `.queuelength`

- `.spot`: **Displays how many players are ahead of user** 
  - Use: `.spot` 
  - Other Names: `.spotinq`, `.spotinque`, `.spotinqueue`, `.place`, `.placeinq`, `.placeinque`, `.placeinqueue`

- `.delete`: **Deletes specified queue** 
  - Default Input: `"Among Us"` 
  - Use: `.delete <name>`
  - Other Names: `.deleteq`, `.deleteque`, `.deletequeue`, `.delq`, `.delque`, `.delqueue`

- `.viewall`: Prints out all active queues
  - Use: `.viewall` 
  - Other Names: `.viewqs`, `.viewques`, `.viewqueues`, `.printall`, `.printqs`, `.printques`, `.printqueue`

## Discord.py

- PyPI Page: [https://pypi.org/project/discord.py/](https://pypi.org/project/discord.py/)

- Github Page: [https://github.com/Rapptz/discord.py](https://github.com/Rapptz/discord.py)