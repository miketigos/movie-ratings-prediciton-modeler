"""
Name: movie_recommendations.py
Date: 
Author: 
Description: 
"""

import math
import csv
from scipy.stats import pearsonr

class BadInputError(Exception):
    pass

class Movie_Recommendations:
    # Constructor
    def __init__(self, movie_filename, training_ratings_filename):
        """
        Initializes the Movie_Recommendations object from 
        the files containing movie names and training ratings.  
        The following instance variables should be initialized:
        self.movie_dict - A dictionary that maps a movie id to
               a movie objects (objects the class Movie)
        self.user_dict - A dictionary that maps user id's to a 
               a dictionary that maps a movie id to the rating
               that the user gave to the movie.    
        """
        self.movie_dict = dict()
        try:
            f1 = open(movie_filename)
        except OSError:
            print("file not able to open")    

        csv_reader1 = csv.reader(f1, delimiter=',', quotechar='"')

        f1.readline() # skip the first row of labels

        for line in csv_reader1:
            mov_id, mov_title = int(line[0]), line[1]
            self.movie_dict[mov_id] = Movie(mov_id, mov_title)
        # print(self.movie_dict)   
        """
        create the userid dictionary to house the dictionary of movie titles
        and ratings for that user. We will create a .csv file reader, assign the
        userid to a variable and check if that is in the dictionary of users.
        If not, we will create a dictionary and assign it to the user id.
        We will then read the file and assign all non-zero movie ratings as the value
        to the keys(movie_ids)
        """
        self.user_dict = dict()
        try:
            f2 = open(training_ratings_filename)
        except OSError:
            print("file not able to open")  
     
        csv_reader2 = csv.reader(f2, delimiter=',')
        f2.readline()

        for line in csv_reader2:
            cur_user_id, mov_id, mov_rating = int(line[0]), int(line[1]), float(line[2])

            if cur_user_id not in self.user_dict:
                self.user_dict[cur_user_id] = dict()
            self.user_dict[cur_user_id][mov_id] = mov_rating     
            self.movie_dict[mov_id].users.append(cur_user_id)
                
        # print(self.user_dict)
        # for i in range(1, 6):
        #     print(self.movie_dict[i].users) 

    def predict_rating(self, user_id, movie_id):
        """
        Returns the predicted rating that user_id will give to the
        movie whose id is movie_id. 
        If user_id has already rated movie_id, return
        that rating.
        If either user_id or movie_id is not in the database,
        then BadInputError is raised.
        """
        if user_id not in self.user_dict or movie_id not in self.movie_dict:
            raise BadInputError("User or movie id not in database")
        ratings = self.user_dict[user_id]

        if movie_id in ratings:
            return ratings[movie_id]

        total, sum_of_similarities = 0, 0
        for key in ratings:
            similarity = self.movie_dict[key].get_similarity(movie_id, self.movie_dict, self.user_dict)
            total += similarity * ratings[key]
            sum_of_similarities += similarity

        if sum_of_similarities != 0:    
            return total / sum_of_similarities
        else:
            return 2.5    
        

    def predict_ratings(self, test_ratings_filename):
        """
        Returns a list of tuples, one tuple for each rating in the
        test ratings file.
        The tuple should contain
        (user id, movie title, predicted rating, actual rating)
        """

        try:
            f = open(test_ratings_filename)
        except OSError:
            print("file not able to open")  
     
        csv_reader = csv.reader(f, delimiter=',')
        f.readline()

        movie_tuples_lst = list() 

        for line in csv_reader:
            user_id, mov_id, mov_rating = int(line[0]), int(line[1]), float(line[2])
            movie_tuple = (user_id, str(self.movie_dict[mov_id]), 
                           self.predict_rating(user_id, mov_id), mov_rating)

            movie_tuples_lst.append(movie_tuple)
        return movie_tuples_lst

    def correlation(self, predicted_ratings, actual_ratings):
        """
        Returns the correlation between the values in the list predicted_ratings
        and the list actual_ratings.  The lengths of predicted_ratings and
        actual_ratings must be the same.
        """
        return pearsonr(predicted_ratings, actual_ratings)[0]
        
class Movie: 
    """
    Represents a movie from the movie database.
    """
    def __init__(self, id, title):
        """ 
        Constructor.
        Initializes the following instances variables.  You
        must use exactly the same names for your instance 
        variables.  (For testing purposes.)
        id: the id of the movie
        title: the title of the movie
        users: list of the id's of the users who have
            rated this movie.  Initially, this is
            an empty list, but will be filled in
            as the training ratings file is read.
        similarities: a dictionary where the key is the
            id of another movie, and the value is the similarity
            between the "self" movie and the movie with that id.
            This dictionary is initially empty.  It is filled
            in "on demand", as the file containing test ratings
            is read, and ratings predictions are made.
        """
        self.id = id
        self.title = title
        self.users = list()
        self.similarities = dict()


    def __str__(self):
        """
        Returns string representation of the movie object.
        Handy for debugging.
        """
        return self.title

    def __repr__(self):
        """
        Returns string representation of the movie object.
        """

        return str(self.title)

    def get_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        If the similarity has already been computed, return it.
        If not, compute the similarity (using the compute_similarity
        method), and store it in both
        the "self" movie object, and the other_movie_id movie object.
        Then return that computed similarity.
        If other_movie_id is not valid, raise BadInputError exception.
        """

        if other_movie_id not in movie_dict:
            raise BadInputError("Movie id not in database")
            
        elif other_movie_id in self.similarities:
            return self.similarities[other_movie_id]
        else:
            similarity = self.compute_similarity(other_movie_id, movie_dict, user_dict)
            self.similarities[other_movie_id] = similarity
            movie_dict[other_movie_id].similarities[self.id] = similarity
            return similarity

    def compute_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Computes and returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        """

        num_of_ratings, abs_diff_of_ratings = 0, 0

        for key in user_dict:
            if self.id in user_dict[key] and other_movie_id in user_dict[key]:
                rtg_1 = user_dict[key][self.id]
                rtg_2 = user_dict[key][other_movie_id]
                abs_diff_of_ratings += abs(rtg_1 - rtg_2)
                num_of_ratings += 1

        if num_of_ratings != 0:
            avg_difference = (abs_diff_of_ratings / num_of_ratings)
            return (1 - avg_difference/4.5) 
        else:
            return 0   
        

if __name__ == "__main__":
    #Create_movie_recommendations object.
    movie_recs = Movie_Recommendations("movies.csv", "training_ratings.csv")

    # Predict ratings for user/movie combinations
    rating_predictions = movie_recs.predict_ratings("test_ratings.csv")
    print("Rating predictions: ")
    for prediction in rating_predictions:
        print(prediction)
    predicted = [rating[2] for rating in rating_predictions]
    actual = [rating[3] for rating in rating_predictions]
    correlation = movie_recs.correlation(predicted, actual)
    print(f"Correlation: {correlation}")    
    