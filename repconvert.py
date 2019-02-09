import os
import subprocess




def pdf_files(pdf_folder) -> list:
    """
    -> [(pdf_filepath, pdf_filename),...]
    """
    return [((os.path.join(pdf_folder, f)), f) for f in os.listdir(pdf_folder)]


def covert(pdf_filepath, txt_output_filepath) -> None:
    """ Converts a pdf file to a txt file.
    """
    cmd = 'pdftotext.exe -enc UTF-8 -nopgbrk -table {} {}'.format(pdf_filepath, txt_output_filepath)
    subprocess.Popen(cmd, shell=True).wait()


def outputs_to(folder_name) -> str:
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    return folder_name

    
def main(pdf_folder, output_folder, print_state=True):
    output_folder = outputs_to(output_folder)

    for pdf_filepath, pdf_filename in pdf_files(pdf_folder):

        if print_state:
            print(pdf_filepath)
            
        txt_output_filepath = os.path.join(output_folder, pdf_filename.replace('.pdf', '.txt'))
        covert(pdf_filepath, txt_output_filepath)




if __name__ == '__main__':
    main(pdf_folder='reports', output_folder='reports_txt')











