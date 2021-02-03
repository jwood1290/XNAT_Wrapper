'''
This example will open an XNAT connection using the `Connector` class, 
find studies using a list of study UIDs, download those studies from PACS 
into an XNAT project, convert the XNAT file structure to BIDS format, run 
the XNAT MRIQC docker container on the project, and finally save the MRIQC 
results to a CSV file.
'''

from constants import *
from ..xnat_wrapper import (
    Connector,
    format_err,
    json_to_csv
)

if __name__ == '__main__':
    '''
    Login to XNAT session using config file or via server, 
    username, and password. Also, supply the XNAT project name.
    This will contain the XNAT connection, the importer utility 
    (xnat.importer), and the command utility (xnat.commands).
    '''
    xnat = Connector(server=xnat_ip,
                    user=xnat_username,
                    password=xnat_password,
                    project=xnat_project)

    '''
    Import list of studies from PACS to an XNAT project
    '''
    try:
        '''
        Access the UIDImporter class via `xnat.importer` and define 
        the study UID(s) you want to add to your project and set 
        them in the importer utility.
        '''
        xnat.importer.set_uids(uid_list)

        '''
        Add filters to the import utility to filter out unwanted 
        data using keyword values in this case, the only returned 
        studies will have a series description containing either 
        `Ax T1` or `Ax T2`
        '''
        xnat.importer.set_filters(filters)

        '''
        Find all studies associated with the UID list (and filters). 
        The studies will be stored in `xnat.importer.studies`.
        '''
        xnat.importer.find_studies()

        '''
        Import the studies that were found into the project. You can 
        also supply a new project name to this function if you want 
        to import the studies to a different study. This will return
        `True` if the import was successful, otherwise `False`.
        '''
        if xnat.importer.import_studies():

            '''
            Monitor the status of the import process. Optionally, 
            this process can be called manually using:
                >> queue_status = xnat.importer.check_import_queue()
            You can also set the the timeout to stop monitoring after 
            a certain amount of seconds (defaults to 180). This timer 
            can also be set to refresh each time there is a change in 
            the import queue by setting time_refresh to `True` (default).
            '''
            xnat.importer.monitor_import_queue(timeout=180, time_refresh=True)

    except Exception as ex:
        format_err(ex)

    '''
    Run a series of commands on the XNAT project
    '''
    try:
        '''
        Access the CommandUtility class via `xnat.commands`, which will be used 
        to run a series of user-defined commands on the files that were uploaded 
        from the importer class. These commands can be added via `set_commands()` 
        or explicitly called when using the `run_commands{}` function.
        '''
        xnat.commands.set_commands(commands)
        
        '''
        Find all of the sessions and scans associated with a project
        '''
        xnat.commands.find_project_experiments()

        '''
        Check that some sessions/scans were found before moving on. Alternatively, 
        a dictionary containing sessions and scans can be retrieved using the 
        `get_project_experiments()` function.
        '''
        if not xnat.commands.has_experiments(): 
            raise ValueError('No scans or sessions found in {}.'.format(xnat_project))

        '''
        Run all of the commands. If the commands were not included in the 
        initilization of the command utility, they can be defined here.
        '''
        xnat.commands.run_commands()

        '''
        Write results to file. This function will check that results exist prior to file creation.
        The `.json` extension will be added if not supplied.
        '''
        xnat.commands.save_results(results_file)

        '''
        If the MRIQC function was successful, there should now be JSON files in the project. 
        Those need to be combined into a single CSV file so the results can be plotted.
        '''
        if xnat.commands.get_results():
            '''
            An XNAT project can also be supplied here if the JSON files are located under 
            a project other than what was supplied in the initialization of the XNAT instance.
            '''
            json_files = xnat.commands.download_json_files(resource=resource_dir)

            '''
            Define the name of the CSV file
            '''
            json_to_csv(json_files,results_csv,keys=add_keys)


    except Exception as ex:
        format_err(ex)

    '''
    Disconnect XNAT data to prevent multiple instances remaining open at once
    '''
    logging.info('Disconnecting from XNAT session...')
    xnat.close_session()

    logging.info('Process complete.')