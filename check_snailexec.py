#!/usr/bin/env python

'''check_snailexec - Monitoring plugin for working with SnailEXEC output'''

developers = ['Joel Rangsmo <joel@rangsmo.se>']
description = __doc__
version = '0.2'
license = 'GPLv2'

try:
    import json
    import time
    import argparse
    
    from sys import exit

except ImportError as missing:
    print(
        'UNKNOWN - Could not import all required modules: "%s".\n' % missing +
        'The script requires Python 2.7 or 2.6 with the "argparse" module\n'
        'Installation with PIP: "pip install argparse"')

    exit(3)

# -----------------------------------------------------------------------------

def exit_plugin(output='No output was provided', state=3):
    '''Exits the plugin in a Nagios-compatible fashion'''

    print(unicode(output))
    exit(state)

# -----------------------------------------------------------------------------

def parse_args(description=None, version=None, developers=None, license=None):
    '''Parses commandline arguments provided by the user'''

    parser = argparse.ArgumentParser(
        description=description,
        epilog=(
            'Developed by %s - licensed under %s!'
            % (', '.join(developers), license)))

    parser.add_argument(
        '-f', '--file', dest='results_file',
        help='Path to version 1 compatible SnailEXEC output file',
        metavar='/path/to/results.json', type=argparse.FileType('r'),
        required=True)

    parser.add_argument(
        '-n', '--name', dest='command_name',
        help='Name of command for result output checking',
        metavar='check_example', type=str, required=True)

    parser.add_argument(
        '-a', '--age', dest='acceptable_age',
        help='Acceptable age of command result '
        'specified in seconds (default: %(default)i)',
        metavar='SECONDS', type=int, default=600)

    parser.add_argument(
        '-i', '--include-age',
        help='Include command result age in status output',
        action='store_true', default=True)

    return parser.parse_args()

# -----------------------------------------------------------------------------

def main():
    '''Main check plugin function'''

    # Parses commandline arguments
    args = parse_args(description, version, developers, license) 

    check_time = int(time.time())

    # -------------------------------------------------------------------------
    try:
        # Loads JSON and the version  of results file
        results = json.load(args.results_file)

        results_version = results['results_version']

        if results_version > 1:
            exit_plugin(
                'Results version "%s" is currently not supported by the plugin'
                % str(results_version))

        # Version 1 should include the following properties
        status = results['status']
        msg = results['msg']
        tag = results['tag']

        results = results['results']

        if status == 'ERROR':
            exit_plugin(
                'SnailEXEC failed during job execution: "%s"' % str(msg))

    except ValueError as error_msg:
        exit_plugin('Failed to load JSON from results file: "%s"' % error_msg)

    except KeyError as error_msg:
        exit_plugin(
            'Results file did not include required data: "%s"' % error_msg)

    # -------------------------------------------------------------------------
    try:
        # Tries to find command name in results
        command = None

        for result in results:
            if result['name'] == args.command_name:
                command = result

                break

        if not command:
            exit_plugin(
                'Could not find result for command "%s" in results file'
                % args.command_name)

        name = command['name']
        status = command['status']
        msg = command['msg']
        end_time = int(command['end_time'])

        stdout = command['stdout']
        stderr = command['stderr']
        exit_code = command['exit_code']

        if status == 'ERROR':
            exit_plugin(
                'SnailEXEC failed to execute command named "%s": "%s"'
                % (name, msg))

    except KeyError as error_msg:
        exit_plugin('Failed to extract required data: "%s"' % error_msg)

    # -------------------------------------------------------------------------
    try:
        # stderr is first since it could be handled as perfdata
        output = stderr + stdout

        if not exit_code in [0, 1, 2, 3]:
            exit_plugin(
                'Command "%s" exited with return code "%s" '
                'which is not a valid plugin status code'
                % (name, str(exit_code)))

        time_diff = check_time - end_time

        # Checks if the result data is too old
        if time_diff > args.acceptable_age:
            exit_plugin(
                'Result data for command "%s" is too old (%i seconds)'
                % (name, time_diff))

    except (ValueError, TypeError):
        exit_plugin(
            'Result data for command "%s" did not include required information'
            % name)

    # Exits the plugin if no result age should be added to output
    if not args.include_age:
        exit_plugin(output=output, state=exit_code)

    # -------------------------------------------------------------------------
    try:
        output = output.split('|')

        # Adds the data age before performance data (if any)
        output[0] += ' (checked %i seconds ago) ' % time_diff

        output = '|'.join(output)

    except Exception as error_msg:
        exit_plugin('Failed to add result age to output: "%s"' % error_msg)

    # -------------------------------------------------------------------------
    exit_plugin(output=output, state=exit_code)


if __name__ == '__main__':
    # Protects the plugin output from unhandled exceptions
    try:
        main()

    except SystemExit as exit_code:
        exit(int(str(exit_code)))

    except Exception as error_msg:
        exit_plugin('Plugin generated unhandled exception: "%s"' % error_msg)
