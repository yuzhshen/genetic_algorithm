from Tkinter import *
from time import sleep
import random

# 400px wide window, 4px moves per frame.
# Boxes are 40px * 40px (black)
# Player is 20px * 20px box (red), position is at bottom center (10px in)
# Jumping goes up 60 px;
# Controls: w, a, d, x (nothing)

# Constants
LV_HEIGHT = 400
LV_WIDTH = 1000
HOR_MV_SPD = 5
JUMP_INIT_SPD = 15
OBSTACLE_HEIGHT = 20
GRAVITY = 2
ONEBOX = '00001000011000100000'

random.seed(27)

class GameState(object):

    # Initial game state is position (20,0)
    def __init__(self):
        self.obstacles = ONEBOX
        self.frame = 0
        self.x = 20
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.jumping = False

    def drawCanvas(self,canvas,root):
        canvas.delete(ALL)
        canvas.create_rectangle(self.x, LV_HEIGHT-self.y, self.x+5, LV_HEIGHT-(self.y+15), fill="red", width="0")
        counter = 0
        for x in list(self.obstacles):
            if x == '1':
                canvas.create_rectangle(counter*50, LV_HEIGHT,(counter+1)*50, LV_HEIGHT-OBSTACLE_HEIGHT, fill="white", width="0")
            counter += 1
        root.update()

    def updatePosition(self):
        beforeY = self.y
        afterY = self.y + self.dy
        beforeX = self.x
        afterX = self.x + self.dx
        isObstacleBefore = self.obstacles[beforeX/50] == '1'

        if afterX >= LV_WIDTH:
            isObstacleAfter = False
        else:
            isObstacleAfter = self.obstacles[afterX/50] == '1'

        if not isObstacleBefore and isObstacleAfter:
            if afterY < OBSTACLE_HEIGHT:
                self.x = beforeX
                self.y = afterY
                if afterY <= 0:
                    self.y = 0
                    self.dy = 0
                    self.jumping = False
            else:
                self.x = afterX
                self.y = afterY
        else:
            self.x = afterX
            self.y = afterY
            if isObstacleAfter and afterY <= OBSTACLE_HEIGHT:
                self.y = OBSTACLE_HEIGHT
                self.dy = 0
                self.jumping = False
            elif not isObstacleAfter and afterY <= 0:
                self.y = 0
                self.dy = 0
                self.jumping = False

    # Updating state means 1) read input 2) update velocity 3) update position
    def processInput(self,inputString,canvas,root):
        while self.frame < 600:
            # read input
            inputChar = inputString[self.frame]
            # update velocity based on input
            if inputChar == 'w' and self.jumping == False:
                self.dy += JUMP_INIT_SPD
                self.dx = 0
                self.jumping = True
            elif inputChar == 'a':
                self.dx = -HOR_MV_SPD
            elif inputChar == 'd':
                self.dx = HOR_MV_SPD
            else:
                self.dx = 0
            # update velocity based on gravity
            self.dy -= GRAVITY

            # update position
            # - if y is on the floor make dy = 0
            # - if x is in an obstacle move x to start of obstacle
            self.updatePosition()
            self.frame += 1

            sleep(0.005)
            self.drawCanvas(canvas,root)

            # end condition
            if self.x >= LV_WIDTH or self.frame >= 600:
                frames_left = LV_WIDTH - self.x
                score = 13000 - 5*self.frame - 10*frames_left

                print 'Game Over, End Frame = '+str(self.frame)+', End X position: '+str(self.x)
                print 'Final Score: '+str(score)+' / 12005'
                return score

    def processInputNoDraw(self,inputString):
        while self.frame < 600:
            # read input
            inputChar = inputString[self.frame]
            # update velocity based on input
            if inputChar == 'w' and self.jumping == False:
                self.dy += JUMP_INIT_SPD
                self.dx = 0
                self.jumping = True
            elif inputChar == 'a':
                self.dx = -HOR_MV_SPD
            elif inputChar == 'd':
                self.dx = HOR_MV_SPD
            else:
                self.dx = 0
            # update velocity based on gravity
            self.dy -= GRAVITY

            # update position
            # - if y is on the floor make dy = 0
            # - if x is in an obstacle move x to start of obstacle
            self.updatePosition()
            self.frame += 1

            # end condition
            if self.x >= LV_WIDTH or self.frame >= 600:
                frames_left = LV_WIDTH - self.x
                score = 13000 - 5*self.frame - 10*frames_left

                return score

def genetic(populationSize, parentSelectionSize, iterations):

    population = []
    isOptimal = False

    # random initialization
    for i in range(populationSize):
        inputString = ''
        for j in range(600):
            rand_num = random.randint(0,5)
            if rand_num == 0:
                inputString+='w'
            elif rand_num == 1:
                inputString+='a'
            # weight for moveright is higher so that fewer iterations are needed
            #  for convergence to optimal solution.
            elif rand_num <= 4:
                inputString+='d'
            else:
                inputString+='x'
        population.append(inputString)

    # algorithm at work
    for x in range(iterations):
        print ('Currently performing iteration '+ str(x))
        #calculate fitnesses
        fitness = []
        fitnessSum = 0.0

        for elt in population:
            game = GameState()
            score = game.processInputNoDraw(elt)
            if score == 12005:
                isOptimal = True
                break
            fitness.append(score)
            fitnessSum += score

        if isOptimal:
            break

        #-----------------------------------------------------------------------
        # # stochastic selection of parents
        # selectedIndices = []
        # for x in range(parentSelectionSize):
        #     rand_num = random.random()
        #     fitnessSumThreshold = 0.0
        #     for index,item in enumerate(fitness):
        #         fitnessSumThreshold += (item/fitnessSum)
        #         if fitnessSumThreshold >= rand_num:
        #             selectedIndices.append(index)
        #             break
        #-----------------------------------------------------------------------
        # selection of parents based on fitness
        selectedIndices = []
        selectedFitnesses = []
        for index,item in enumerate(fitness):
            if len(selectedIndices) < parentSelectionSize:
                selectedIndices.append(index)
                selectedFitnesses.append(item)
            elif item > min(selectedFitnesses):
                mindex = selectedFitnesses.index(min(selectedFitnesses))
                selectedFitnesses.remove(selectedFitnesses[mindex])
                selectedIndices.remove(selectedIndices[mindex])
                selectedFitnesses.append(item)
                selectedIndices.append(index)
        #-----------------------------------------------------------------------

        # These are the parent strings of the next generation
        selectedParents = []
        children = []
        for index in selectedIndices:
            selectedParents.append(population[index])
        #-----------------------------------------------------------------------
        print ('pre-crossover max: '+str(max(fitness)))
        #-----------------------------------------------------------------------

        # crossover stage
        for index,item in enumerate(selectedParents):
            if index % 2 == 0:
                mate1 = selectedParents[index]
                mate2 = selectedParents[index+1]
                child = ''
                for x in range(600):
                    rand_num = random.random()
                    if rand_num >= 0.5:
                        child += mate1[x]
                    else:
                        child += mate2[x]
                children.append(child)

        # children replace the least fit of the older generation
        for c in children:
            mindex = fitness.index(min(fitness))
            population.remove(population[mindex])
            population.insert(mindex,c)
            fitness.remove(fitness[mindex])
            game = GameState()
            fitness.insert(mindex, game.processInputNoDraw(c))

        # mutation stage, 0.01 chance to randomly mutate each gene of each chromosome
        newPopulation = []
        for p in population:
            newchild = ''
            for c in p:
                if random.random() < 0.005:
                    rand_num = random.randint(0,5)
                    if rand_num == 0:
                        newchild+='w'
                    elif rand_num == 1:
                        newchild+='a'
                    elif rand_num <= 4:
                        newchild+='d'
                    else:
                        newchild+='x'
                else:
                    newchild+=c
            newPopulation.append(newchild)
        population = newPopulation

    # algorithm done, return the most fit member
    fitness = []
    for elt in population:
        game = GameState()
        fitness.append(game.processInputNoDraw(elt))
    # return best candidate
    return population[fitness.index(max(fitness))]


def main():
    print random.random()

    root = Tk()
    canvas = Canvas(root, width=LV_WIDTH, height=LV_HEIGHT)
    canvas.configure(background='black')
    canvas.pack()
    game = GameState()
    game.drawCanvas(canvas,root)

    userInput = input("How many iterations? ")
    inputString = genetic(500, 300, userInput)

    print game.processInput(inputString,canvas,root)

if  __name__ =='__main__':
    main()
