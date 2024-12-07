# Homework 3 for CS 4470/6456

### Student Details:
**Full name:** Salman Azeez Syed <br>

**Email:** ssyed75@gatech.edu <br>

**GT SSO Account Name:** ssyed75 <br>


### Implementation Details:

Everything works and has been completed. I had to take certain liberties when doing this Homework and it was quite fun. These particularly included:
- Developing a heuristic for focus character selection.
- Scaling baselines and focus markers accoridng to font size so they don't mismatch.
- Adjustng per character spacing and differentiating among them based on word length.

I printed each character as a separate label which caused certain issues when trying to printed them together as a word. After a whole day of trying around this way, I had to get a bit creative and used the same method of font-size dependent scaling that I used for the baselines and focus markers, and honestly it worked quite well, visually. In addition, grad requirement for timecode support was fairly simple as it required a bit more regex, which can be like trying to knit with needles. Rest of the functionality was quite simple as it contained of simple buttons that were bind to kivy modules like the settings module. In addition, creating a scrollable spinner was a bit of an issue since I had tried a window style approach similar to how I've implemented wpm and font-size, but the popup window would not scroll, so I could not select from all the font options since I couldn't even access them. I tried to make this work, but it was causing a lot of issues, so I made a spinner instead taking inspiration from HW1 and some simple json-ing.

### External Build Requirements:
None
