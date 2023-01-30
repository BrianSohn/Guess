# Guess!

### Video Demo
https://youtu.be/taUD75ZNtNc

### Description: For Users

###### Overview
*Guess!* is a web application that allows users to form groups with others, guess results of sports games, and check out who had the best guesses. 

###### Register / Log In
A user is first required to register a username and a password to log in to the application. 

###### Creating / Joining Groups
Once users are logged in, they can create new groups or join *groups* that were created by others. To create a new group, they will choose a name and invite code for the group to share with others. To join an existing group, they can simply enter the group's name and invite code that was generated when the group was created. By creating/joining a group, the user will become a *member* of the group. 

###### My Groups
Users can access all groups that they are a member of through the My Groups tab. This can be found either in the navigation bar in the top left, or in the home page (index). 

###### Creating Games
Once users enter the page for a group that they are a member of, they can create *games*. Any sports game can be a guess! game. To create one, users can enter the name of the two teams that are playing against each other. This will automatically add the game to the *upcoming games* section for all members of the group.  

###### Guessing / Posting Game Results
In the *upcoming games* section, users will see all games within the group that do not have their results posted yet. They will see the name of the two teams for the game, and will be able to guess game results as well as post the actual results after the game. To make a guess for a game, users can enter in the scores for each team that they think are likely to happen. To post actual game results, they can enter in the actual scores for both teams. 

###### Game Results
After the result for a game is posted, the game will be moved to the *game results* section, where users will be able to check all game results as well as their own guesses for each game. If the game results were posted incorrectly, they will also be able to change the posted results. 

###### Leaderboard
Each group has a *leaderboard*. The leaderboard allows users to track which member of the group had the best guesses so far. A user will be given 1 point for each game that they guessed correctly. A correct guess will be a guess that accurately predicted the winner regardless of the scores for each team. For example, for a game between South Korea and Portugal that ended in a 2-1 win for South Korea, all users who predicted a South Korea win (1-0, 3-1, etc.) will be awarded a point. If the game ended in a draw, users that predicted a draw will be awarded a point. The leaderboard shows the sum of all points that each user gained within that group. 


### Description: For Developers
###### Overview
*Guess!* is a web application developed using HTML, CSS, Python (Flask), and Javascript. 

###### Register / Log In
The registration and login pages are created from *register.html* and *login.html*. To check out how filling in the forms will work, see routes */register*, */login*, and */logout* in *app.py*. Registering will insert a row into the *users* table. 

###### Creating / Joining Groups
Creating and joining groups can be done in the homepage, which is created from *index.html*. See routes */create-group* and *join-group* in *app.py* to check how these are performed. A new group will be stored in the *groups* table, and each new member of the group will be recorded as a row in the *userGroup* table.

###### My Groups
The *My Groups* page is created from *myGroups.html*. See route */groups*, with method GET, to check how this page is generated. When users select a group, they will be routed to */groups* with method POST, which will prompt users to a page created from *group.html*.

###### Creating Games
Creating a game is done when a user submits a form within */group.html* to route */create-game* in *app.py*. This inserts a new row into the *games* table, as well as inserting one row for each member in the group to the *userGame* table.

###### Guessing / Posting Game Results
Guessing and posting game results are also performed through submitting a form in */group.html*. Check routes */guess* and */results* in *app.py*. When a user makes a guess for a game, it will update the *userGame* table so that it records the users guess for the game. When a game result is posted, it will update the *games* table so that its results are recorded. Then, 1 point will automatically be rewarded for users who guessed correctly by updating the *userGame* table, which will also be reflected in the *userGroup* table to calculate the leaderboard. 

###### Game Results
Posted game results will be in the last section of */group.html*. 

###### Leaderboard
The leaderboard is generated in the first section of */group.html* and route */groups* in *app.py* with method POST. 