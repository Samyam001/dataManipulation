# import random
# import pickle


# # =========================================================
# # 1. GAME SETTINGS
# # =========================================================

# WINNING_COMBINATIONS = [
#     (0, 1, 2),
#     (3, 4, 5),
#     (6, 7, 8),
#     (0, 3, 6),
#     (1, 4, 7),
#     (2, 5, 8),
#     (0, 4, 8),
#     (2, 4, 6)
# ]

# q_table = {}


# # =========================================================
# # 2. DISPLAY BOARD
# # =========================================================

# def print_board(board):
#     print()
#     print(f" {board[0]} | {board[1]} | {board[2]}")
#     print("---+---+---")
#     print(f" {board[3]} | {board[4]} | {board[5]}")
#     print("---+---+---")
#     print(f" {board[6]} | {board[7]} | {board[8]}")
#     print()


# # =========================================================
# # 3. GAME FUNCTIONS
# # =========================================================

# def available_moves(board):
#     return [
#         i for i in range(9)
#         if board[i] == " "
#     ]


# def check_winner(board):
#     for a, b, c in WINNING_COMBINATIONS:

#         if (
#             board[a] != " "
#             and board[a] == board[b]
#             and board[b] == board[c]
#         ):
#             return board[a]

#     return None


# def is_draw(board):
#     return len(available_moves(board)) == 0


# def get_state(board):
#     return "".join(board)


# # =========================================================
# # 4. Q-LEARNING AGENT
# # =========================================================

# class QLearningAgent:

#     def __init__(
#         self,
#         learning_rate=0.1,
#         discount_factor=0.9,
#         epsilon=1.0,
#         epsilon_decay=0.9995,
#         min_epsilon=0.01
#     ):

#         self.q_table = {}

#         # Learning rate
#         self.alpha = learning_rate

#         # Future reward importance
#         self.gamma = discount_factor

#         # Exploration
#         self.epsilon = epsilon

#         # How quickly exploration decreases
#         self.epsilon_decay = epsilon_decay

#         # Minimum exploration
#         self.min_epsilon = min_epsilon

#     # -----------------------------------------------------
#     # Get Q-value
#     # -----------------------------------------------------

#     def get_q_value(self, state, action):

#         if state not in self.q_table:
#             self.q_table[state] = {}

#         return self.q_table[state].get(action, 0.0)

#     # -----------------------------------------------------
#     # Choose action
#     # -----------------------------------------------------

#     def choose_action(self, board, training=True):

#         moves = available_moves(board)

#         if not moves:
#             return None

#         state = get_state(board)

#         # Exploration
#         if training and random.random() < self.epsilon:
#             return random.choice(moves)

#         # Exploitation
#         q_values = [
#             self.get_q_value(state, move)
#             for move in moves
#         ]

#         max_q = max(q_values)

#         best_moves = [
#             move
#             for move, q_value
#             in zip(moves, q_values)
#             if q_value == max_q
#         ]

#         return random.choice(best_moves)

#     # -----------------------------------------------------
#     # Learn from experience
#     # -----------------------------------------------------

#     def update(
#         self,
#         state,
#         action,
#         reward,
#         next_state,
#         next_moves
#     ):

#         old_q = self.get_q_value(
#             state,
#             action
#         )

#         # If game is finished
#         if not next_moves:

#             future_q = 0

#         else:

#             future_q = max(
#                 self.get_q_value(
#                     next_state,
#                     move
#                 )
#                 for move in next_moves
#             )

#         # Q-learning formula
#         new_q = old_q + self.alpha * (
#             reward
#             + self.gamma * future_q
#             - old_q
#         )

#         self.q_table[state][action] = new_q

#     # -----------------------------------------------------
#     # Reduce exploration
#     # -----------------------------------------------------

#     def decay_epsilon(self):

#         self.epsilon = max(
#             self.min_epsilon,
#             self.epsilon * self.epsilon_decay
#         )

#     # -----------------------------------------------------
#     # Save model
#     # -----------------------------------------------------

#     def save(self, filename):

#         with open(filename, "wb") as file:
#             pickle.dump(self.q_table, file)

#     # -----------------------------------------------------
#     # Load model
#     # -----------------------------------------------------

#     def load(self, filename):

#         with open(filename, "rb") as file:
#             self.q_table = pickle.load(file)


# # =========================================================
# # 5. TRAINING
# # =========================================================

# def train(agent, episodes=100000):

#     print("\nTraining AI...")
#     print(f"Games: {episodes:,}\n")

#     for episode in range(episodes):

#         board = [" "] * 9

#         # AI plays X
#         current_player = "X"

#         while True:

#             state = get_state(board)

#             action = agent.choose_action(
#                 board,
#                 training=True
#             )

#             board[action] = current_player

#             winner = check_winner(board)

#             # ---------------------------------------------
#             # AI wins
#             # ---------------------------------------------

#             if winner == "X":

#                 reward = 1

#                 agent.update(
#                     state,
#                     action,
#                     reward,
#                     get_state(board),
#                     []
#                 )

#                 break

#             # ---------------------------------------------
#             # Draw
#             # ---------------------------------------------

#             if is_draw(board):

#                 reward = 0.5

#                 agent.update(
#                     state,
#                     action,
#                     reward,
#                     get_state(board),
#                     []
#                 )

#                 break

#             # ---------------------------------------------
#             # Opponent plays O randomly
#             # ---------------------------------------------

#             opponent_action = random.choice(
#                 available_moves(board)
#             )

#             board[opponent_action] = "O"

#             opponent_winner = check_winner(board)

#             # ---------------------------------------------
#             # AI loses
#             # ---------------------------------------------

#             if opponent_winner == "O":

#                 reward = -1

#                 agent.update(
#                     state,
#                     action,
#                     reward,
#                     get_state(board),
#                     []
#                 )

#                 break

#             # ---------------------------------------------
#             # Draw after opponent move
#             # ---------------------------------------------

#             if is_draw(board):

#                 reward = 0.5

#                 agent.update(
#                     state,
#                     action,
#                     reward,
#                     get_state(board),
#                     []
#                 )

#                 break

#             # ---------------------------------------------
#             # Continue learning
#             # ---------------------------------------------

#             next_state = get_state(board)

#             next_moves = available_moves(board)

#             agent.update(
#                 state,
#                 action,
#                 0,
#                 next_state,
#                 next_moves
#             )

#         agent.decay_epsilon()

#         # Show progress
#         if (episode + 1) % 10000 == 0:

#             print(
#                 f"Completed: {episode + 1:,} "
#                 f"| Epsilon: {agent.epsilon:.4f}"
#             )

#     print("\nTraining completed!")


# # =========================================================
# # 6. HUMAN VS AI
# # =========================================================

# def human_vs_ai(agent):

#     print("\n==============================")
#     print("      TIC-TAC-TOE ML")
#     print("==============================")

#     print("\nYou are O.")
#     print("AI is X.")

#     print("\nPositions:")

#     print(" 0 | 1 | 2")
#     print("---+---+---")
#     print(" 3 | 4 | 5")
#     print("---+---+---")
#     print(" 6 | 7 | 8")

#     board = [" "] * 9

#     while True:

#         # ---------------------------------------------
#         # AI turn
#         # ---------------------------------------------

#         ai_move = agent.choose_action(
#             board,
#             training=False
#         )

#         board[ai_move] = "X"

#         print("\nAI played:")
#         print_board(board)

#         winner = check_winner(board)

#         if winner == "X":

#             print("AI wins!")
#             break

#         if is_draw(board):

#             print("It's a draw!")
#             break

#         # ---------------------------------------------
#         # Human turn
#         # ---------------------------------------------

#         while True:

#             try:

#                 human_move = int(
#                     input("Choose a position (0-8): ")
#                 )

#                 if human_move not in available_moves(board):

#                     print("Invalid move. Try again.")
#                     continue

#                 break

#             except ValueError:

#                 print("Please enter a number.")

#         board[human_move] = "O"

#         print_board(board)

#         winner = check_winner(board)

#         if winner == "O":

#             print("You win!")
#             break

#         if is_draw(board):

#             print("It's a draw!")
#             break


# # =========================================================
# # 7. MAIN PROGRAM
# # =========================================================

# def main():

#     print("==============================")
#     print("  TIC-TAC-TOE MACHINE LEARNING")
#     print("==============================")

#     agent = QLearningAgent()

#     print("\n1. Train new AI")
#     print("2. Load trained AI")

#     choice = input("\nChoose option: ")

#     if choice == "2":

#         try:

#             agent.load("tic_tac_toe_model.pkl")

#             print("\nModel loaded successfully!")

#         except FileNotFoundError:

#             print("\nNo model found.")
#             print("Training a new model...")

#             train(agent, 100000)

#             agent.save(
#                 "tic_tac_toe_model.pkl"
#             )

#     else:

#         train(agent, 100000)

#         agent.save(
#             "tic_tac_toe_model.pkl"
#         )

#         print(
#             "\nModel saved as "
#             "'tic_tac_toe_model.pkl'"
#         )

#     # Play game
#     while True:

#         human_vs_ai(agent)

#         again = input(
#             "\nPlay again? (y/n): "
#         ).lower()

#         if again != "y":

#             print("\nThanks for playing!")
#             break


# # =========================================================
# # START PROGRAM
# # =========================================================

# if __name__ == "__main__":
#     main()