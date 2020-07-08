"""Run figure detection on a batch of PDFs.

See ``DetectFigures_Bulk.py --help`` for more information.
"""

import logging
import os
import click
import shutil

from deepfigures import settings
from scripts import build, execute, detectfigures

# Same module as in detectfigures.py in deepfigures_open
# However, this proved to be easiest and least error prone way to use function
def detectfigures(
        output_directory,
        pdf_path,
        skip_dependencies=False):
    """Run figure extraction on the PDF at PDF_PATH.

    Run figure extraction on the PDF at PDF_PATH and write the results
    to OUTPUT_DIRECTORY.
    """
    if not skip_dependencies:
        build.build.callback()

    cpu_docker_img = settings.DEEPFIGURES_IMAGES['cpu']
    
    # Paths so pdf can be added to docker env correctly
    pdf_directory, pdf_name = os.path.split(pdf_path)
    pdf_directory = settings.Input_PDF_dir
    internal_output_directory = '/work/host-output'
    internal_pdf_directory = '/work/host-input'

    internal_pdf_path = os.path.join(
        internal_pdf_directory, pdf_name)

    # Look up docker documentation for more explanations about what each -- does
    execute(
        'docker run'
        ' --rm'
        ' --env-file deepfigures-local.env'
        ' --volume {output_directory}:{internal_output_directory}'
        ' --volume {pdf_directory}:{internal_pdf_directory}'
        ' {tag}:{version}'
        ' python3 /work/scripts/rundetection.py'
        '   {internal_output_directory}'
        '   {internal_pdf_path}'.format(
            tag=cpu_docker_img['tag'],
            version=settings.VERSION,
            output_directory=output_directory,
            internal_output_directory=internal_output_directory,
            pdf_directory=pdf_directory,
            internal_pdf_directory=internal_pdf_directory,
            internal_pdf_path=internal_pdf_path),
        logger,
        raise_error=True)

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


def bulk_detectfigures(output_directory, input_directory):
    """Run figure extraction on the PDFs in input_directory.

    Writes the results to OUTPUT_DIRECTORY that is defined in settings.py in AWS_Linking.
    The results are a folder that consists of .json with coordinates of bounding box,
    pdf with bounding box overlay, and the original pdf.

    """
    settings.Local_Output = output_directory # Set global output directory
    settings.Input_PDF_dir = input_directory # Set global input directory
    for pdf in os.listdir(input_directory):
        if pdf.endswith(".pdf"):
            # Only process pdfs that haven't been before
            if (os.path.isdir(os.path.join(output_directory, os.path.basename(pdf).replace('.pdf', '_output')))):
                print('Skipped pdf because it has already been processed')
                continue
            detectfigures(output_directory, pdf)
            # Rename directory to pdf name + output, this currently loops through every directory
            try:
                # Looping through every directory in pdfs
                for dir in os.listdir(output_directory):
                    dir = os.path.join(output_directory, dir)
                    for files in os.listdir(dir):
                        if (os.path.basename(files).replace('.pdf', '_output') != dir and os.path.basename(files).endswith('.pdf')):
                            shutil.move(dir, dir.replace(os.path.basename(dir), os.path.basename(files).replace('.pdf', '_output')))
                            
            except NotADirectoryError or FileNotFoundError:
                # Just skip if not a Directory
                pass

    print('Detect Figures is Done')

if __name__ == '__main__':
    bulk_detectfigures()

