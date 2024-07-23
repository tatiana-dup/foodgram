from django import forms
from recipes.models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not self.cleaned_data.get('ingredients'):
            raise forms.ValidationError(
                'Необходимо указать хотя бы один ингредиент.')

        instance.save()
        self.save_m2m()
        return instance
