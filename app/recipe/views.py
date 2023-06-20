"""View for the list of recipie apis."""
from rest_framework import(
    viewsets,
    mixins,
    status
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewset(viewsets.ModelViewSet):
    """Viewset for manage recipe apis."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return objects for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return serializer class for request."""

        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class
    
    def perform_create(self, serializers):
        """Create a new recipe object."""
        serializers.save(user=self.request.user)

    # Custom actions
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(mixins.ListModelMixin, 
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin, 
                                viewsets.GenericViewSet):
    """Base class for recipe attributes."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')



class TagViewset(BaseRecipeAttrViewSet):
    """View manage tags in the database."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    
class IngredientViewset(BaseRecipeAttrViewSet):
    """View manage ingredients in the database."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

