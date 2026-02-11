import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.env import BlackjackEnv
from ai.agent import QLearningAgent
import numpy as np
import time


def train_agent(num_episodes=100000, save_interval=10000):
    """
    Train the Q-learning agent
    
    Args:
        num_episodes (int): Number of episodes to train
        save_interval (int): Save Q-table every N episodes
    """
    print("=" * 60)
    print("Q-LEARNING BLACKJACK AGENT TRAINING")
    print("=" * 60)
    print(f"Training for {num_episodes:,} episodes...")
    print()
    
    # Initialize environment and agent
    env = BlackjackEnv()
    agent = QLearningAgent(
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_decay=0.9995,
        epsilon_min=0.01
    )
    
    # Metrics tracking
    wins = 0
    losses = 0
    ties = 0
    total_reward = 0
    episode_rewards = []
    
    start_time = time.time()
    
    # Training loop
    for episode in range(1, num_episodes + 1):
        state = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            valid_actions = []
            if env.player_hand.value >= 16:
                valid_actions.append(1)
            if env.player_hand.num_of_cards() < 5 and env.player_hand.value <= 21:
                valid_actions.append(0)
            
            # If no valid actions or player must hit (value < 16), force HIT
            if not valid_actions or env.player_hand.value < 16:
                valid_actions = [0]
            
            # Get action from agent
            action = agent.get_action(state, valid_actions=valid_actions, training=True)
            
            # Take action
            next_state, reward, done = env.step(action)
            
            # Update Q-table
            agent.update(state, action, reward, next_state, done)
            
            state = next_state
            episode_reward += reward
        
        # Track results
        total_reward += episode_reward
        episode_rewards.append(episode_reward)
        
        if episode_reward > 0:
            wins += 1
        elif episode_reward < 0:
            losses += 1
        else:
            ties += 1
        
        # Decay epsilon
        agent.decay_epsilon()
        
        # Print progress
        if episode % save_interval == 0:
            elapsed_time = time.time() - start_time
            avg_reward = total_reward / episode
            win_rate = (wins / episode) * 100
            loss_rate = (losses / episode) * 100
            tie_rate = (ties / episode) * 100
            recent_avg = np.mean(episode_rewards[-1000:]) if len(episode_rewards) >= 1000 else np.mean(episode_rewards)
            
            print(f"Episode: {episode:,}/{num_episodes:,}")
            print(f"  Time elapsed: {elapsed_time:.1f}s")
            print(f"  Win rate: {win_rate:.2f}% | Loss rate: {loss_rate:.2f}% | Tie rate: {tie_rate:.2f}%")
            print(f"  Average reward: {avg_reward:.4f}")
            print(f"  Recent 1000 avg reward: {recent_avg:.4f}")
            print(f"  Epsilon: {agent.epsilon:.4f}")
            print()
            
            # Save Q-table
            save_path = os.path.join('ai', 'data', 'q_table.npy')
            agent.save(save_path)
    
    # Final save and statistics
    print("=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    
    total_time = time.time() - start_time
    final_win_rate = (wins / num_episodes) * 100
    final_loss_rate = (losses / num_episodes) * 100
    final_tie_rate = (ties / num_episodes) * 100
    final_avg_reward = total_reward / num_episodes
    
    print(f"Total training time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"Games per second: {num_episodes/total_time:.1f}")
    print()
    print(f"Final Win rate: {final_win_rate:.2f}%")
    print(f"Final Loss rate: {final_loss_rate:.2f}%")
    print(f"Final Tie rate: {final_tie_rate:.2f}%")
    print(f"Average reward: {final_avg_reward:.4f}")
    print()
    
    # Save final Q-table
    save_path = os.path.join('ai', 'data', 'q_table.npy')
    agent.save(save_path)
    
    print()
    print("Q-table has been saved to 'ai/data/q_table.npy'")
    print("You can now use this trained agent to play!")
    print("=" * 60)


def test_agent(num_games=1000):
    """
    Test the trained agent
    
    Args:
        num_games (int): Number of games to test
    """
    print("=" * 60)
    print("TESTING TRAINED AGENT")
    print("=" * 60)
    
    env = BlackjackEnv()
    agent = QLearningAgent()
    
    # Load trained Q-table
    save_path = os.path.join('ai', 'data', 'q_table.npy')
    if not agent.load(save_path):
        print("ERROR: No trained Q-table found. Please run training first.")
        return
    
    print(f"Testing for {num_games:,} games...")
    print()
    
    wins = 0
    losses = 0
    ties = 0
    
    for game in range(1, num_games + 1):
        state = env.reset()
        done = False
        
        while not done:
            valid_actions = []
            if env.player_hand.value >= 16:
                valid_actions.append(1)
            if env.player_hand.num_of_cards() < 5 and env.player_hand.value <= 21:
                valid_actions.append(0)
            
            if not valid_actions or env.player_hand.value < 16:
                valid_actions = [0]
            
            # Get action
            action = agent.get_action(state, valid_actions=valid_actions, training=False)
            
            # Take action
            next_state, reward, done = env.step(action)
            state = next_state
        
        if reward > 0:
            wins += 1
        elif reward < 0:
            losses += 1
        else:
            ties += 1
    
    # Print results
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Games played: {num_games:,}")
    print(f"Wins: {wins:,} ({(wins/num_games)*100:.2f}%)")
    print(f"Losses: {losses:,} ({(losses/num_games)*100:.2f}%)")
    print(f"Ties: {ties:,} ({(ties/num_games)*100:.2f}%)")
    print("=" * 60)


if __name__ == "__main__":
    train_agent(num_episodes=100000, save_interval=10000)
    print("\n\n")
    test_agent(num_games=10000)
