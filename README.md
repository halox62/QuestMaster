Epic Adventure GameEpic Adventure Game is an interactive text-based adventure game built with Angular. Players can explore mysterious worlds, solve puzzles, and uncover hidden treasures through a dynamic, choice-driven narrative. The game features a visually appealing interface with animations, a progress bar, and an immersive typewriter effect for the story text.Table of ContentsFeatures (#features)
Technologies (#technologies)
Installation (#installation)
Usage (#usage)
Backend API (#backend-api)
Project Structure (#project-structure)
Contributing (#contributing)
License (#license)

FeaturesInteractive Storytelling: Players make choices to progress through a dynamic narrative graph.
Animated UI: Includes a glowing title, particle effects, floating background elements, and a progress bar.
Typewriter Effect: Story text and title appear with a typing animation for an immersive experience.
Game Over States: Victory and defeat scenarios, with stats tracking the number of moves made.
Responsive Design: Optimized for desktop and mobile devices with smooth animations and layouts.
Error Handling: Displays user-friendly error messages for failed API calls or invalid game states.

TechnologiesAngular: Frontend framework for building the interactive UI.
TypeScript: For type-safe JavaScript code.
HTML/SCSS: For structuring and styling the game interface.
RxJS: For handling HTTP requests to the backend API.
Node.js: Required for running the Angular development server.
Backend API: A separate service (running at http://localhost:8080) to generate and serve the game graph.

InstallationPrerequisitesNode.js: Version 16 or higher.
Angular CLI: Install globally with npm install -g @angular/cli.
Backend API: Ensure the backend service is running at http://localhost:8080 (see Backend API (#backend-api)).

StepsClone the Repository:bash

git clone <repository-url>
cd epic-adventure-game

Install Dependencies:bash

npm install

Start the Development Server:bash

ng serve

The game will be available at http://localhost:4200.

UsageStart the Backend API:
Ensure the backend service is running to provide the game graph and story generation. Refer to the backend documentation for setup instructions.
Launch the Game:Open your browser and navigate to http://localhost:4200.
Click the Start Adventure button to begin the game.
Read the story text and select options to progress through the narrative.
Complete the adventure to achieve victory or face defeat, then choose New Adventure to restart.

Game Features:Progress Bar: Shows your progress through the story nodes.
Options: Choose from multiple actions to shape the story.
Game Over: Displays a victory or defeat screen with the number of moves made.
Animations: Enjoy particle effects, floating backgrounds, and typing animations.

Backend APIThe game relies on a backend service running at http://localhost:8080 to provide the game graph and story data. The following endpoints are used:GET /genStory: Generates a new story graph.
GET /getGraph: Retrieves the current game graph.

Ensure the backend is running before starting the game. If you encounter errors like "Error loading the game," verify that the backend is operational and accessible.Example Backend SetupThe backend should return a JSON object representing the game graph, structured as follows:json

{
  "node_1": {
    "description": "You find yourself in a mysterious forest...",
    "options": {
      "option_1": { "text": "Explore the cave", "target": "node_2" },
      "option_2": { "text": "Follow the river", "target": "node_3" }
    }
  },
  ...
}

Refer to the backend documentation for detailed setup and configuration.

Project Structure

epic-adventure-game/
├── src/
│   ├── app/
│   │   ├── app.component.ts        # Main game component logic
│   │   ├── app.component.html      # Game template
│   │   ├── app.component.scss      # Game styles
│   │   └── app.module.ts           # Angular module
├── package.json                    # Project dependencies and scripts
├── angular.json                    # Angular CLI configuration
└── README.md                       # Project documentation

ContributingContributions are welcome! To contribute:Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit (git commit -m 'Add your feature').
Push to the branch (git push origin feature/your-feature).
Open a pull request.

Please ensure your code follows the project's coding standards and includes appropriate tests.LicenseThis project is licensed under the MIT License. See the LICENSE

