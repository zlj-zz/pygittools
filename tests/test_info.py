from .utils import analyze_it
from pigit.git_utils import output_repository_info, output_git_local_config


@analyze_it
def test_info():

    output_repository_info()

    output_git_local_config()
