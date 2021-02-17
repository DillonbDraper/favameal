from django.db import models
from .mealrating import MealRating


class Meal(models.Model):

    name = models.CharField(max_length=55)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)

    # TODO: Add an user_rating custom properties
    
    # TODO: Add an avg_rating custom properties
    
    @property
    def favorite(self):
        return self.__favorite

    @favorite.setter
    def favorite(self, value):
        self.__favorite = value

    @property
    def user_rating(self):
        return self.__user_rating

    @user_rating.setter
    def user_rating(self, value):
        self.__user_rating = value

    @property
    def avg_rating(self):
        """Average rating calculated attribute for each game"""
        ratings = MealRating.objects.filter(meal=self)

        # Sum all of the ratings for the game
        total_rating = 0
        for rating in ratings:
            total_rating += rating.rating

        if len(ratings) == 0:
            return "No ratings found"
        else:
            return total_rating / len(ratings)