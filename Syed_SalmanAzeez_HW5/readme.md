# Homework 5 for CS 4470/6456

### Student Details:
**Full name:** Salman Azeez Syed <br>

**Email:** ssyed75@gatech.edu <br>

**GT SSO Account Name:** ssyed75 <br>


### Implementation Details:


Everything works great and has been completed. Extra credit has not been implemneted. Couldn't find time.

On start, must select level first otherwise the game will not start and terminal will display a message to select a level first. On selection, you can start. On default, game starts with Unlimited time, but if time is chosen, it starts with that. Team A always goes first and starting the game instantly starts timer for Team A. Here are the key features:

 - Piece Selection, Cloning, Jumping, Conversions and Game End  - all have sounds. Sometimes quick actions make not cause sounds due to a little longer tail in the previously played sound sort of cancelling the current sound. But logic is 100% correct.
  - Unique piece animations for selection (highlights piece and shows possible moves), cloning (a slide effect), jump (an arc effect) and conversion (a zoom in/out scale effect).
  - Move selection has been designed to be orthogonal, similar to the first example clone mentioned in the project description. So, L-shaped moves like a knight in chess is also possible.
  - The game handles draw conditions in 2 ways - (1) If time runs out for player A, he loses. (2) If no more cells left on board and scores are equal - a tie is declared on results screen.
  - Imports levels from levels-1.txt (this was the name of the exact levels.txt file when downloaded from canvas, so kept it same. Please use this named file when testing.)
  - Player vs Computer option exists in the menu dropdown - but hasnt been implemented. Clicking this will simply take you to Player vs Player regardless.

### External Build Requirements:
None