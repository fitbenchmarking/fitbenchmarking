import os


def get_file():
    """
    
    @param file_name :: the name the wanted file 
    @return :: the full path of the wanted file 
    """
    file_name = 'NIST_Misra1a.dat'
    mock_prob_dir = os.path.dirname(os.path.realpath(__file__))

    for root, dirs, files in os.walk(mock_prob_dir):
        if file_name in files:
            print(file_name)

    # return files


print(get_file())