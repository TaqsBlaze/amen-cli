import pytest
import os
import shutil
from amen.cli import create_project

@pytest.fixture
def temp_dir(tmpdir):
    return tmpdir

def test_project_creation(temp_dir):
    project_name = "test_project"
    framework = "flask"
    project_type = "webapp"
    
    # Create project in temporary directory
    project_path = os.path.join(temp_dir, project_name)
    create_project(project_path, framework, project_type)
    
    # Assert project structure
    assert os.path.exists(project_path)
    assert os.path.exists(os.path.join(project_path, "app"))
    assert os.path.exists(os.path.join(project_path, "requirements.txt"))
    assert os.path.exists(os.path.join(project_path, "README.md"))

def test_invalid_framework():
    with pytest.raises(ValueError):
        create_project("test_project", "invalid_framework", "webapp")

def test_invalid_project_type():
    with pytest.raises(ValueError):
        create_project("test_project", "flask", "invalid_type")
