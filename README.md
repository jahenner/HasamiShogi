# Hasami Shogi CS162 Portfolio Project

This project was the Portfolio Project for my CS162 class. The original requirements for this project were to just make a playable game, where 2 players can input legal moves. This is the story of this project, I hope this code helps you learn something or try something new.
**Wants:**
* Create an AI to play against
    * Created a random move generator so far
* Create a networked game
    * Possibly using JavaScript and a database
* Create a computer vision component
    * Possibly use your hand/finger to select and move the pieces


**Challenges:** 
* Creating a data structure
    * While a nested array would have solved this, I wanted to practice with the idea of linked lists. So I combined the two ideas. Each element in the nested array is a node that contains information about its' neighbors in all four locations.
* Linking the elements
    * The toughest part was linking the right and bottom pieces during the initialization phase. I had to run through the nested array a second time after everything was created to initialize the right and bottom neighbor.
* It was hard to visualize where all the pieces were at any given time
    * I created a way to pretty print the board.

![](https://i.imgur.com/Ri2VVT7.png)

This was tremendous help to find all the edge cases and test them out.

After it was turned in with the given requirements I started to implement pygame. I have worked in pygame before, so I didn't have any major implementation issues. This was thanks to my code structure with a separate class for the squares.
Here is the first run of the GUI.

![](https://i.imgur.com/nWHLwCj.gif)

I then wanted to have a visualization of possible moves, so I made the possible locations a green square. I was able to use the implemenation of checking to see if a move was legal into showing all the possible moves.

![](https://i.imgur.com/2A8xQbI.gif)

After getting all of the game play on the GUI down, I started to add some textures to the board and pieces.
**Challenges:**
* Creating space at the top of the screen for more information
    * I was able to solve this by creating a constant that would update all draw features by a certain amount. Once implemented it was easier to find a good size for the top of the screen.

![](https://i.imgur.com/k9rj7jy.gif)

My favorite part about this was the wood tiles. I implemented a random feature that would flip and rotate each tile, to make it look different and more like a board would look.

My current part of this project that I am trying to implement is to be able to play against an AI. So far I have just made it so the AI will make random legal moves. I achieved this by creating a new class for the AI that gathers information about the location of all of it's pieces and all of those pieces' possible moves. It would then randomly select one of those initial pieces and then a random possible move.

![](https://i.imgur.com/S1NJng2.gif)


If you would like to play the game, you can download the repository and install the requirements.txt file.

