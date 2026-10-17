from rest_framework import serializers
from.models import Student

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'full_name', 'admission_number', 'gender', 'status', 'date_admitted']