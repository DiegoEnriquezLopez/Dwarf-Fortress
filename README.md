

![gui](https://github.com/user-attachments/assets/57ed2b07-e07d-4641-83c9-3d5fa40e6f62)

*Dwarf Colony Simulation*
A strategy and colony simulation game inspired by Dwarf Fortress and Clash of Clans, developed in Python using Pygame.

The player manages a small village inhabited by dwarves who work autonomously to gather resources, farm, build structures, and defend the colony from goblin attacks. The main objective is to keep the colony stable by managing its resources, food, construction, and defense.

*Main Features
- Autonomous Dwarves: Dwarves perform tasks such as mining, gathering wood, farming, building, and defending the colony.
- AI Task Assignment: The game determines which dwarf is best suited to perform each assigned task.
- Resource Management: Collect and manage wood, stone, wheat, milk, and eggs.
- Construction System: Build and repair structures using collected resources.
- Colony Defense: Goblins spawn randomly and attack the village, while defender dwarves automatically respond to threats.
- Character Systems: Dwarves have different skills, health, energy, and experience that affect their performance.
- Random Generation: Characters, animals, enemies, resources, and other elements are generated at random positions in each new game.
- Interactive Interface: Manage tasks, characters, resources, and structures through interactive menus.
- Animations: Characters have animated sprites for different activities and actions.

⚔️ Enemies and Challenges
- Goblins spawn at random positions and periodically attack the colony.
- Defender dwarves automatically detect and fight nearby enemies.
- Dwarves gain experience through their activities, improving their abilities over time.

🌾 Resource Production
- Farmers grow wheat, milk animals, and collect eggs.
- Lumberjacks gather wood, while miners collect stone.
- Resources are automatically stored in the corresponding chests and used for construction.

*Characters

🪓 Lumberjack
- Chops trees and collects wood.
- Stores collected wood in the Main Chest.
  
⛏ Miner
- Mines stone and gathers materials.
- Assists builders with construction.
  
🌾 Farmer
- Plants and harvests wheat.
- Milks animals and collects eggs.
- Stores food resources in the Food Chest.

🏗 Builder
- Builds new structures.
- Repairs damaged buildings.

⚔ Defender
- Protects the village from goblins.
- Patrols the surrounding area.
- Gains combat experience while defending the colony.

🏡 Resources and Storage
The colony uses different storage systems to manage its resources:
- Main Chest: Stores wood, stone, and tools.
- Food Chest: Stores wheat, milk, and eggs.
- Bar: Provides water and beer to the dwarves.

🧠 Artificial Intelligence
- The dwarves operate autonomously based on the needs of the colony.

- When the player assigns a task, the game sends the request to an internal system that determines which dwarf is best suited to perform it. The selected dwarf then moves through the map and performs the corresponding action.

- Defender dwarves can also react automatically when goblins enter the village.

- This creates a dynamic simulation where production, resource management, construction, and defense interact with each other.
  
🎨 Visual Interface
The game features a top-down map with:
- Character and resource information.
- Interactive menus and buttons.
- Animated characters.
- Resource storage interfaces.
- Real-time character status information.

🚀 How to run
1. Clone the repository.
2. Install the required dependencies.
3. Run the main Python file.
4. Select New Game from the main menu.
5. Manage the colony and keep it running for as long as possible.

🎯 Objective
Keep the colony stable for as long as possible by maintaining a balance between resources, food, construction, and defense while the dwarves autonomously carry out their assigned tasks.
