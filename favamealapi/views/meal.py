"""View module for handling requests about meals"""
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from favamealapi.models import Meal, MealRating, Restaurant, FavoriteMeal
from favamealapi.views.restaurant import RestaurantSerializer


class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for meals"""
    restaurant = RestaurantSerializer(many=False)
    # Properties for later: 'user_rating', 'avg_rating'
    class Meta:
        model = Meal
        fields = ('id', 'name', 'restaurant', 'favorite' )


class MealView(ViewSet):
    """ViewSet for handling meal requests"""

    def create(self, request):
        """Handle POST operations for meals

        Returns:
            Response -- JSON serialized meal instance
        """
        meal = Meal()
        meal.name = request.data["name"]
        meal.restaurant = Restaurant.objects.get(pk=request.data["restaurant_id"])


        try:
            meal.save()
            serializer = MealSerializer(
                meal, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single meal

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.get(pk=pk)

            # TODO: Get the rating for current user and assign to `user_rating` property

            # TODO: Get the average rating for requested meal and assign to `avg_rating` property
            try:
                FavoriteMeal.objects.get(
                    meal=meal, user=request.auth.user)
                meal.favorite = True

            except FavoriteMeal.DoesNotExist:
                meal.favorite = False
            

            serializer = MealSerializer(
                meal, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to meals resource

        Returns:
            Response -- JSON serialized list of meals
        """
        meals = Meal.objects.all()

        # TODO: Get the rating for current user and assign to `user_rating` property

        # TODO: Get the average rating for each meal and assign to `avg_rating` property

        # TODO: Assign a value to the `is_favorite` property of each meal
        
        for meal in meals:
            meal.favorite = None
            try:
                FavoriteMeal.objects.get(
                    meal=meal, user=request.auth.user)
                meal.favorite = True

            except FavoriteMeal.DoesNotExist:
                meal.favorite = False

        serializer = MealSerializer(
            meals, many=True, context={'request': request})

        return Response(serializer.data)

    # TODO: Add a custom action named `rate` that will allow a client to send a
    #  POST and a PUT request to /meals/3/rate with a body of..
    #       {
    #           "rating": 3
    #       }




    
    @action(methods=['post', 'delete'], detail=True)
    def star(self, request, pk=None):

        if request.method == "POST":
            meal = Meal.objects.get(pk=pk)
            try:
                favorite = FavoriteMeal.objects.get(meal=meal, user=request.auth.user)
                return Response(
                    {'message': 'Already a favorite'},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            except FavoriteMeal.DoesNotExist: 
                favorite = FavoriteMeal()
                favorite.user = request.auth.user
                favorite.meal = meal
                favorite.save()

                return Response({}, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":

            try:
                meal = Meal.objects.get(pk=pk)
            except Meal.DoesNotExist:
                return Response(
                    {'message': 'Favorite does not exist.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try: 
                favorite = FavoriteMeal.objects.get(meal=meal, user = request.auth.user)
                favorite.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except FavoriteMeal.DoesNotExist:
                return Response({'message': 'Not currently favorited.'},
                status=status.HTTP_404_NOT_FOUND
                )


        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

