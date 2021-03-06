import numpy as np
import utils
import random


class Agent:
    
    def __init__(self, actions, Ne, C, gamma):
        self.actions = actions
        self.Ne = Ne # used in exploration function
        self.C = C
        self.gamma = gamma
        self.reset()

        # Create the Q and N Table to work with
        self.Q = utils.create_q_table()
        self.N = utils.create_q_table()

    # Change these flags to True/False depending on how you want the program to run.
    def train(self):
        self._train = True
        
    def eval(self):
        self._train = False

    # At the end of training save the trained model
    def save_model(self,model_path):
        utils.save(model_path, self.Q)
        utils.save(model_path.replace('.npy', '_N.npy'), self.N)

    # Load the trained model for evaluation
    def load_model(self,model_path):
        self.Q = utils.load(model_path)

    def reset(self):
        self.points = 0
        self.s = None
        self.a = None

    # Function to discretize state
    def discretize(self, state):
        # print(state)
        snake_head_x = state[0]
        snake_head_y = state[1]
        snake_body = state[2]
        food_x = state[3]
        food_y = state[4]
        # x,y: 40, 520 due to walls.

        # print("snake_head_x: {}".format(snake_head_x))
        # print("snake_head_y: {}".format(snake_head_y))
        # print("food_x: {}".format(food_x))
        # print("food_y: {}".format(food_y))
        # print("snake_body: {}".format(snake_body))

        # Adjoining_wall_x
        if snake_head_x <= 40:
            adjoining_wall_x = 1    
        elif snake_head_x >= 480:
            adjoining_wall_x = 2
        else:
            adjoining_wall_x = 0

        # Adjoining_wall_y
        if snake_head_y <= 40:
            adjoining_wall_y = 1    
        elif snake_head_y >= 480:
            adjoining_wall_y = 2
        else:
            adjoining_wall_y = 0
        
        # Note that [0, 0] is also the case when snake runs out of the 480x480 board

        # if (snake_head_x <= 0 or snake_head_y <=0) or (snake_head_x >= 480 or snake_head_y >= 480):
        if snake_head_x <= 0 or snake_head_y <=0 or snake_head_x >= 520 or snake_head_y >= 520:
            adjoining_wall_x = 0
            adjoining_wall_y = 0

        # food_dir_x
        if snake_head_x > food_x:
            food_dir_x = 1
        elif snake_head_x < food_x:
            food_dir_x = 2
        else:
            food_dir_x = 0

        # food_dir_y
        if snake_head_y > food_y:
            food_dir_y = 1
        elif snake_head_y < food_y:
            food_dir_y = 2
        else:
            food_dir_y = 0

        # Checks if there is snake body in adjoining square of snake head
        # print("snake_body: {}".format(snake_body))

        # adjoining top square has snake body
        if(snake_head_x, snake_head_y - 40) in snake_body:
            adjoining_body_top = 1
        else:
            adjoining_body_top = 0        
        
        # adjoining bottom square has snake body
        if(snake_head_x, snake_head_y + 40) in snake_body:
            adjoining_body_bottom = 1
        else:
            adjoining_body_bottom = 0
        
        # adjoining left square has snake body
        if(snake_head_x - 40, snake_head_y) in snake_body:
            adjoining_body_left = 1
        else:
            adjoining_body_left = 0
        
        # adjoining right square has snake body
        if(snake_head_x + 40, snake_head_y) in snake_body:
            adjoining_body_right = 1
        else:
            adjoining_body_right = 0



        state_tuple = (adjoining_wall_x, adjoining_wall_y, food_dir_x, food_dir_y, adjoining_body_top, adjoining_body_bottom, adjoining_body_left, adjoining_body_right)

        return state_tuple

    # Computing the reward
    def compute_reward(self, points, dead):
        if dead:
            return -1
        elif points > self.points:
            return 1
        else:
            return -0.1

    def act(self, state, points, dead):
        '''
        :param state: a list of [snake_head_x, snake_head_y, snake_body, food_x, food_y] from environment.
        :param points: float, the current points from environment
        :param dead: boolean, if the snake is dead
        :return: the index of action. 0,1,2,3 indicates up,down,left,right separately

        TODO: write your function here.
        Return the index of action the snake needs to take, according to the state and points known from environment.
        Tips: you need to discretize the state to the state space defined on the webpage first.
        (Note that [adjoining_wall_x=0, adjoining_wall_y=0] is also the case when snake runs out of the 480x480 board)

        '''
        s_prime = self.discretize(state)
        action = self.a
        # print("action: {}".format(action))
        # print("s_prime: {}".format(s_prime))
        # print(s_prime)

        # compute rewards
        reward = self.compute_reward(points, dead)
        # if training
        if self._train:
            # if last state is not none
            if self.s != None:
                # Update q table with best action (which maximize Q)

                next_q = np.max(self.Q[s_prime])
                # print("next_q: {}".format(next_q))
                
                # Piazza Post @1493
                alpha = self.C / (self.C + self.N[self.s + (action,)])
                curr_q = self.Q[self.s + (action,)]
                # print("curr_q: {}".format(curr_q))
                self.Q[self.s + (action,)] += alpha * (reward + self.gamma * next_q - curr_q)

            # Compute next action with exploration (prepare to return this one)
            max_val = float('-inf')
            best_action = 0
            for a in range(3,-1,-1):
                # print("action: {}".format(a))

                # returns 1 if n is less than a tuning parameter N
                if self.N[s_prime + (a,)] < self.Ne:
                    curr_f = 1
                # returns u
                else:
                    curr_f = self.Q[s_prime + (a,)]
                
                if curr_f > max_val:
                    max_val = curr_f
                    best_action = a
        
            # Update N table if not dead (for s_prime and next? action)
            if not dead:
                self.N[s_prime + (best_action,)] += 1
                self.points = points    
            # Cache of system state
            self.s = s_prime
            self.a = best_action
            
        else:
            # Compute best action (which maximize Q) (prepare to return this one)    
            best_action = np.argmax(self.Q[s_prime])
        # Reset system if dead
        if dead:
            self.reset()
        return best_action