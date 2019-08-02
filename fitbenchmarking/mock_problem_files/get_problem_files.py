import os


def get_file(file_name):
    """
    
    @param file_name :: the name the wanted file 
    @return :: the full path of the wanted file 
    """

    mock_prob_dir = os.path.dirname(os.path.realpath(__file__))
    mock_prob_path = ''

    for root, dirs, files in os.walk(mock_prob_dir):
        if file_name in files:
            mock_prob_path = os.path.join(root, file_name)

    return mock_prob_path
