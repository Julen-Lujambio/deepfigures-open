"""Rename directories in output folder with pdf name.

See ``dir_rename.py --help`` for more information.
"""

import logging
import os
import click
import shutil

from deepfigures import settings
from scripts import dir_rename
logger = logging.getLogger(__name__)

@click.command(
    context_settings={
        'help_option_names': ['-h', '--help']
    })
    
@click.argument(
    'output_directory',
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True))

@click.argument(
    'input_directory',
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True))

def dir_rename(output_directory, input_directory):
    """Renames all output folders with pdfs + output format instead of pdf_hash name

    Pdfs with really long names sometimes do not get renamed for some reason
    You can manually rename them.
    """
    settings.Local_Output = output_directory # Set global output directory
    settings.Input_PDF_dir = input_directory # Set global input directory
    
    # Looping through every directory in pdfs
    for dir in os.listdir(output_directory):
        try:
            dir = os.path.join(output_directory, dir)
            for files in os.listdir(dir):
                if (files.endswith('.pdf')):
                    if (os.path.basename(files).replace('.pdf', '_output') != dir and os.path.basename(files).endswith('.pdf')):
                        shutil.move(dir, dir.replace(os.path.basename(dir), os.path.basename(files).replace('.pdf', '_output')))       
        except NotADirectoryError or FileNotFoundError:
            # Just skip if not a Directory
            continue

    print('Done Renaming')

if __name__ == '__main__':
    dir_rename()

