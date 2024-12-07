# Homework 1 for CS 4470/6456

### Student Details:
**Full name:** Salman Azeez Syed <br>

**Email:** ssyed75@gatech.edu <br>

**GT SSO Account Name:** ssyed75 <br>


### Implementation Details:

Everything works and has been completed. The app consists of 4 phases:
- **Introductory phase:** A simple title screen with a "Start Assessment" Button
- **Scale Weight Phase:** A phase with 15 identical screens, each screen having a random combination of factors which helpds determine factor weight
- **Scale Value Phase:** A single-screen phase with a scale for each of the 6 factors allowing you to rate each factor using click, drag and arrow keys
- **Results Phase:** A screen that shows all tallies, weights and scale values for each factor along with a total workload score. Has a Button to restart test.

The entire app can be used solely using either mouse or keyboard only, individually. For the latter, tab is used to toggle through focusable elements and enter to select them. The scales on the scale value phase can be adjusted using the left and right arrow keys with the enter key only working on "previous" and "View results" buttons on that screen. The toggle cycle successfully goes through each of the 6 factor scales as well as the 2 buttons. Every button on every screen and phase is focusable, togglable and selectable using the keyboard alone. However, when on a screen, once mouse-button is clicked elsewhere in the app which causes an option to lose focus, the keyboard can no longer be used until either (a) An option is selected using a mouse-click to restablish focus or (b) You go back and return to the screen anew. This is acceptable as per the Homework description.

All fonts use scale-dependent pixels to adjust for different screen sizes and display densities, identical to the approach followed in Homework 1. Scale weight phase uses a slightly different method for randomization, but works exactly as per requirement. The custom scale has 20 markings total, each for every 5 value on the scale. Out of these, only 3 markings are longer than the rest - the first, middle and last ones.

Most new ideas were easily deciperable from the focus_demo.py file uploaded on class resources GitHub. Only one other novel idea had to be inferred from elsewhere - the grab functionality - at least the better way of doing it. Rest all were intuitive and some required multiple tweaks by self for multiple iterations and resources before finalization. Sometimes, so random other feature would affect my on screen render - which absolutely had no relation to the display. But changing every line of code one by one allowed me to figure out what caused it and fix it eventually.

### External Build Requirements:
None