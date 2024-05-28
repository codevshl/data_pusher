from rest_framework import serializers
from .models import Account, Destination

# class AccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Account
#         fields = '__all__'

# class DestinationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Destination
#         fields = '__all__'




class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer to handle common attributes and methods for all models.
    
    This serializer provides a standard implementation for the 'validate' and 'save' methods,
    which can be used by all derived serializers to handle model-specific validation and
    error handling during the save process.
    """
    class Meta:
        # Default fields setting for all derived serializers.
        fields = '__all__'

    def validate(self, data):
        """
        Validate the data and handle any model-specific validation errors.
        
        This method can be overridden in derived serializers to add custom validation logic.
        
        Parameters:
        data (dict): The data to be validated.
        
        Returns:
        dict: The validated data.
        
        Raises:
        serializers.ValidationError: If there is an error in the validation process.
        """
        try:
            # Add custom validation logic here if needed
            return data
        except Exception as e:
            raise serializers.ValidationError(f"Error validating data: {str(e)}")

    def save(self, **kwargs):
        """
        Save the instance and handle any errors during the save process.
        
        This method can be overridden in derived serializers to add custom save logic.
        
        Parameters:
        **kwargs: Additional keyword arguments to be passed to the save method.
        
        Returns:
        object: The saved instance.
        
        Raises:
        serializers.ValidationError: If there is an error in the save process.
        """
        try:
            return super().save(**kwargs)
        except Exception as e:
            raise serializers.ValidationError(f"Error saving data: {str(e)}")

class AccountSerializer(BaseSerializer):
    """
    Serializer for the Account model, inheriting common behavior from BaseSerializer.
    """
    class Meta(BaseSerializer.Meta):
        # Specify the model for this serializer.
        model = Account

class DestinationSerializer(BaseSerializer):
    """
    Serializer for the Destination model, inheriting common behavior from BaseSerializer.
    """
    class Meta(BaseSerializer.Meta):
        # Specify the model for this serializer.
        model = Destination

