import random
import pandas as pd
import numpy as np
import copy
import graphic

MAX_EPOCH = 10
MAX_ITER = 10


class Som:
    def __init__(self):
        self.data_matrix = []
        self.som_grid = []
        self.parseInput()
        self.init_som_grid()
        self.main_loop()

    """
    The function converts the data in the input table to the data_matrix list
    """

    def parseInput(self):
        df = pd.read_csv('Elec_24.csv', sep=',')
        tuples = [tuple(x) for x in df.values]
        self.data_matrix = []
        for t in tuples:
            self.data_matrix.append((t[0], t[1], t[2],
                                     [t[3], t[4], t[5], t[6], t[7], t[8],
                                      t[9], t[10], t[11], t[12], t[13], t[14], t[15]]))

    """
    The function checks what is the smallest value obtained in the table
    and what is the greatest value. Using these values the initial random
    values range for the SOM grid will be calculated
    """

    def get_minmax_value(self):
        min_value = float('inf')
        max_value = float('-inf')
        for i in range(len(self.data_matrix)):
            for value in self.data_matrix[i][3]:
                if value > max_value:
                    max_value = value
                if value < min_value:
                    min_value = value

        return min_value, max_value

    """
    A function that creates a SOM grid consisting of 61 adjacent hexagons that creates
    one large hexagon. The function initializes random values
    for each hexagon and saves the entire grid in som_grid.
    """

    def init_som_grid(self):
        min_value, max_value = self.get_minmax_value()
        row_len = 4
        y_val = 4
        for i in range(0, 5):
            x_val = -4
            new_row = []
            row_len += 1
            for j in range(0, row_len):
                tmp = []
                for _ in range(0, 13):
                    tmp.append(random.randrange(min_value, max_value))
                new_row.append((tmp, (x_val, y_val)))
                x_val += 1
            y_val -= 1
            self.som_grid.append(new_row)

        y_val = -1
        for i in range(0, 4):
            x_val = i - 3
            new_row = []
            row_len -= 1
            for _ in range(0, row_len):
                tmp = []
                for _ in range(0, 13):
                    tmp.append(random.randrange(min_value, max_value))
                new_row.append((tmp, (x_val, y_val)))
                x_val += 1
            y_val -= 1
            self.som_grid.append(new_row)

    """
    A function that calculates the rmse (Root Mean Square Error) distance between 2 arrays of numbers
    """

    def rmse(self, predictions, targets):
        return np.sqrt(((predictions - targets) ** 2).mean())

    """
    The function receives a vector of values and goes through all the grid cells and calculates
    which cell is the closest to the vector obtained by using a call to the RMSE function
    :returns the min rmse to the vector
    """

    def calc_rmse(self, vec):
        tmp = []
        for i in range(len(self.som_grid)):
            for j in range(len(self.som_grid[i])):
                tmp.append((self.rmse(np.array(vec), np.array(self.som_grid[i][j][0])), i, j))

        min(tmp, key=lambda t: t[0])
        min_rmse = min(tmp)
        return min_rmse

    """
    The function receives a coordinate of a cell in the grid and the level of the neighbors
    according to the ring number around the point.
    Calculates all the neighbors in this ring and returns them as output.
    """

    def get_neighbors(self, coordinate, ring_level):
        x_val, y_val = coordinate[0], coordinate[1]
        ring_values = []
        for i in range(len(self.som_grid)):
            for j in range(len(self.som_grid[i])):
                dx = x_val - self.som_grid[i][j][1][0]
                dy = y_val - self.som_grid[i][j][1][1]
                if np.sign(dx) == np.sign(dy):
                    distance = abs(dx + dy)
                else:
                    distance = max(abs(dx), abs(dy))

                if distance == ring_level:
                    ring_values.append((i, j))

        return ring_values

    """
    Gets the vectors of the values, the percentage of the approximation quantity
    and performs an approximation to the values
    """

    def change_vec_values(self, vec_a, vec_b, percentage):
        for i in range(len(vec_a)):
            distance = abs(vec_a[i] - vec_b[0][i])
            distance *= percentage
            if vec_a[i] < vec_b[0][i]:
                vec_b[0][i] -= distance
            else:
                vec_b[0][i] += distance

    """
    Once the representative cell is found this function brings the cell's neighbors
    approximation by rings around it until it has no more neighbors (all the grid).
    for each ring it calculates the approximation as a function of the distance from the coordinate.
    """

    def update_som_grid(self, vector_in_data_mat, coordinate):
        ring_level = 0
        percentage = 0.5
        while True:
            neighbors = self.get_neighbors(coordinate, ring_level)
            if not neighbors:
                break
            for neighbor in neighbors:
                self.change_vec_values(vector_in_data_mat, self.som_grid[neighbor[0]][neighbor[1]], percentage)
            ring_level += 1
            percentage /= 2

    """
    The function calculates the grid SOM.
    The main loop run for the amount of epochs defined before on all the data received.
    The representative calculation and the grid approximation depending on the representative.
    Then of the epochs another RMSE is calculated to clustering the data information to a specific cell.
    Finally the average economic grade of the cell is calculated.
    :returns A dictionary containing the cells in the SOM grid and the localities associated with each cell.
    """

    def round_loop(self):
        epoch = 0
        while epoch < MAX_EPOCH:
            data_list = copy.deepcopy(self.data_matrix)
            while len(data_list):
                chosen_vector = random.choice(data_list)
                data_list.remove(chosen_vector)

                min_rmse = self.calc_rmse(chosen_vector[3])
                coordinate = self.som_grid[min_rmse[1]][min_rmse[2]][1]
                self.update_som_grid(chosen_vector[3], coordinate)
            epoch += 1

        clustering_dictionary = {}
        for row in self.data_matrix:
            rmse = self.calc_rmse(row[3])
            cluster = (rmse[1], rmse[2])
            if cluster in clustering_dictionary:
                clustering_dictionary[cluster].append(row[0])
            else:
                clustering_dictionary[cluster] = [row[0]]

        clustering_dictionary_for_graphic = {}
        for cluster in clustering_dictionary:
            cluster_elements = clustering_dictionary.get(cluster)
            economic_rate_sum = 0
            total_votes = 0
            for i in range(len(cluster_elements)):
                elm_in_data_mat = [item for item in self.data_matrix if item[0] == cluster_elements[i]]
                economic_rate_sum += (elm_in_data_mat[0][1] * elm_in_data_mat[0][2])
                total_votes += elm_in_data_mat[0][2]

            economic_rate_avg = economic_rate_sum / total_votes
            clustering_dictionary_for_graphic[cluster] = economic_rate_avg
        return clustering_dictionary_for_graphic

    """
    The main loop calculates the SOM grid defined before as maximum amount of rounds.
    Then calculate the best result by the Quantization Error method in which the distances
    of each vector in the input from their representative are measured and summed and select
    the result with the smallest distances.
    Finally the data dictionary is sent to the graphic with the information on the grid
    and then it is calculated and displayed to the screen.
    """

    def main_loop(self):
        distance_between_city_to_representor = []
        round_to_cluster_dictionary = {}
        for i in range(MAX_ITER):
            round_to_cluster_dictionary[i] = self.round_loop()
            cluster_total_distance = 0
            for j in range(len(self.data_matrix)):
                cluster_total_distance += self.calc_rmse(self.data_matrix[j][3])[0]

            distance_between_city_to_representor.append((cluster_total_distance, i))

        min(distance_between_city_to_representor, key=lambda t: t[0])
        min_distance = min(distance_between_city_to_representor)
        graphic.Graphic(round_to_cluster_dictionary.get(min_distance[1]))
