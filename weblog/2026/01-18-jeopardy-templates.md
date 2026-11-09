# My Jeopardy Templates

*Enjoy my templates? [buy me a coffee](https://ko-fi.com/LeoCx1000)*

I've made some board templates for jeopardy games and spent quite a bit of time and effort into making them good for the host and players. And so, I decided to release them publicly. 

<section>

# Pirating PowerPoint


You can get powerpoint for free using the MassGrave activation scripts at [massgrave.dev](https://massgrave.dev/), here's a quick guide:

1. Open PowerShell (not cmd)
2. Run the command on the website
3. On the new window that appeared, use the interface to activate office:
   1. Press `2` to select `Ohook`
      - If you have office downloaded, press `2` 
      - If you don't, press `3`
      - 4. Enjoy free powerpoint

<section>

# A few words of caution

- These boards use Microsoft Visual Basic code to operate the scoreboards, so these don't work on Google Sheets.

- The wheel button uses a camera, so be careful as to not show your own camera if you have not set up OBS properly. (note that there is a failsafe slide with a "Show Camera" button to avoid this)

<section>

# The points buttons are not working!!!

As I mentioned in the words of caution, this board used VB Code to make the score trackers function. This obviously is blocked by Microsoft, and for good reason! Please check this article here, or click on **Learn More** on the security warning to learn how to unblock the file:

from support.microsoft.com: [A potentially dangerous macro has been blocked](https://support.microsoft.com/en-gb/topic/a-potentially-dangerous-macro-has-been-blocked-0952faa0-37e7-4316-b61d-5b5ed6024216)

### Still not working after the security warning is dismissed?

Are you using the invisible buttons? see the next section:

<section>

# How to use them?

1. This board is made for easy creation: Use search and replace with the title and question placeholders such as `[Category 1]`.
   >[Video guide for creating questions (its basically just a search and replace guide, why would anyone need this?)] ![@](https://leo.might-be.gay/board-guide-quicksetup.mp4) 

2. To display the wheel I use [OBS Studio](https://obsproject.com/) and [a hardware camera emulator plugin for OBS](https://github.com/dev47apps/droidcam-obs-virtual-output) because PowerPoint doesn't support virtual cameras. (you need to start it every time you open OBS under `Tools > DroidCam Virtual Output`)

3. I use two monitors and Microsoft PowerToys to pin things above the board, and then I stream the window that is under the board.

4. Next to each price on the main board, you will find **hidden buttons** (they are just coloured the same as the background). Clicking them will select the amount of money to add or remove to/from players. You can also see your currently selected amount in the bottom-right.

5. Use the green/orange buttons to add/remove scores to/from the players.

   >[Video guide for hosting this board] ![@](https://leo.might-be.gay/board-guide-hosting-the-board.mp4) 

<section>

# Customizing the boards

### Adding a category

If you want to add (or remove) a category, there are some things to take into consideration because of the way the board is set up (especially repositioning the hidden buttons), so I recorded a quick video of me doing that:

>[Video guide for adding a new category / column] ![@](https://leo.might-be.gay/board-guide-new-category.mp4) 

### The Design section

You can use the design tab to recolor and restyle the board to your liking. For example, changing **the color of each question button** both before/after clicking. 

> [Video guide to recolor links] ![@](https://leo.might-be.gay/board-guide-recolor.mp4)

> [Video guide to recolor links] ![Design Tab Image Guide](https://leo.might-be.gay/z2OS2ORK.png)

### How to use the Slide Master

The slide master is a feature that allows you to add things that appear in every slide. Some of my templates utilise this feature to add buttons and soundboards. You can use this to **change the waiting sound** or add any other thing that you want to persist across different slides.

> [Image guide for slide master] ![Slide Master](https://leo.might-be.gay/WhE3DOqK.png)

> [Video guide for slide master] ![@](https://leo.might-be.gay/board-guide-slidemaster.mp4)

PS: Some of the videos might be slightly out of date but they should generally represent the use cases.

<section>

# Template Downloads

==IMPORTANT:== Due to a PowerPoint limitation, the slide with the table of links (slide 1) should always stay as slide 1. Adding slides before it will break the code and make the points tally not work.

==**You CAN send a DM for help with using these templates, but only *after reading this entire website* since it has some guides on how to do common things.**==

## Extra Small Board Template

Download: [JeopardyTemplateXShort.pptm](https://leo.might-be.gay/JeopardyTemplateXShort.pptm)

*this template utilises the "Slide Master" feature for (a) each question/answer's buttons, and (b) the scoreboard. Click* ⚙️ *to edit player names*

![Extra Small Board Template](https://leo.might-be.gay/rxwD67SY.png)

## Small Board Template

Download: [JeopardyTemplateShort.pptm](https://leo.might-be.gay/JeopardyTemplateShort.pptm)

*this template utilises the "Slide Master" feature for (a) each question/answer's buttons, and (b) the scoreboard. Click* ⚙️ *to edit player names*

![Small Board Template](https://leo.might-be.gay/rxwD67SY.png)

## Large Board Template

Download: [JeopardyTemplate.pptm](https://leo.might-be.gay/JeopardyTemplate.pptm)

*this template utilises the "Slide Master" feature for (a) each question/answer's buttons, and (b) the scoreboard. Click* ⚙️ *to edit player names*

![Large Board Template](https://leo.might-be.gay/j4eJXl4l.png)

## Large Board Template 2

*this template utilises the "Slide Master" feature for (a) each question/answer's buttons, and (b) the scoreboard. Click* ⚙️ *to edit player names*

Download: [JeopardyTemplateLarge.pptm](https://leo.might-be.gay/JeopardyTemplateLarge.pptm)

![Large Board Template 2](https://leo.might-be.gay/Zd40GRGq.png)
