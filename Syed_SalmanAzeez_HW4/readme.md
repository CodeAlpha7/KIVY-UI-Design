# Homework 4 for CS 4470/6456

### Student Details:
**Full name:** Salman Azeez Syed <br>

**Email:** ssyed75@gatech.edu <br>

**GT SSO Account Name:** ssyed75 <br>


### Implementation Details:

Everything works great and has been completed. Here's how to use it:
- Jump Back - Seeks back 5 words - Left arrow (key) - Left swipe (gesture)
- Jump Forward - Seeks forward 5 words - Right arrow (key) - Right Swipe (gesture)
- Speed Up - Faster Playback by 50 WPM, max 1000 WPM - Up arrow (key) - Up swipe (gesture)
- Slow Down - Slower Playback by 50 WPM, min 50 WPM - Down arrow (key) - Down swipe (gesture)
- Font Bigger - Make font bigger by 5dp, max 100dp - (+ or = key) - L shape (gesture)
- Font Smaller - Make font smaller by 5dp, min 10dp - (- or _ key) - reverse L shape (gesture)
- Pause Toggle - pause/unpause playback - spacebar (key) - diagonal swipe (gesture)

Gestures only work in the text display window (darker rectangle encapsulating text). The diagonal swipe gesture for play/pause toggle is from left bottom to right top. The L-shape and reverse L-shape gestures for font increase/decrease are vertical line from top to bottom followed by a sharp continuous horizontal swipe toward right or left respectively.

Gestures use a minscore of 0.5 for accuracy strictness. Please check console log to check what gestures are being registered. Through thorough testing, the gestures drawn as indicated will always be identified with very drastically different gestures being rejected with the console log "No gesture matched". However, similar but unregistered gestures like wrongly drawn diagonals (start from top left/right or bottom right) will be mis-identified as something else (most commonly L-shapes). Gestures when identified will also show a confidence rating (as console logs) and when drawn as indicated, gestures will show more than 90% confidence ratings. Mis-identified gestures will have low confidence ratings and one way to avoid this would be to not do any gesture matching if confidence is below a certain threshold (let's say 80%). However, I have only included this as an idea in theory for robustness.

Normally, VLC player instantiation has a small delay which would often cause text on screen to go out of sync with audio. I have fixed this with a manual delay of 1000ms that seems to fix this issue. Audio sync works great on first playback, on play/pause and jumping forward or backward. This has been tested thoroughly and should not show issues. However, if audio shows slight delays in sync, simply jump forward and immediately backward, that should fix the issue and audio will be back in sync. This is only a contingency plan and only goes to show how well the seeking functionality has been implemented.

**NOTE:** The settings button has been left in from HW3, it works as normal as indicated in HW3, however, changing these values may affect the newly implemented keyboard functionality. I often found that changing settings through the settings button would disable keyboard functions in play/pause, seeking and so on. Lowering text speed (WPM) through the settings menu may also affect the audio sync, which will go back to normal if you seek forward and back again (using gestures). However, any action through the settings menu does NOT affect gestures. Since the professor gave us the option to remove the settings menu, I have opted to not address this edge case and make both work in tandem. Assume it does not exist.

### External Build Requirements:
None