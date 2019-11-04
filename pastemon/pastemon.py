import os.path

from argparse import ArgumentParser
from orchestrator import Orchestrator

if __name__== "__main__":
    parser = ArgumentParser()
    parser.add_argument('-d', dest ="downloaders", help="Amount of downloaders (will download the pastebin content)", default=1)
    parser.add_argument('-g', dest ="getters", help="Amount of getters (will check for new pastebins)", default=1)
    parser.add_argument('-a', dest ="analyzers", help="Amount of analyzers (will analyze the pastebin's content)", default=3)
    parser.add_argument('-s', dest ="storers", help="Amount of storers (will either store or delete a pastebin)", default=1)
    parser.add_argument('-r', dest ="analysis_dir_path", help="Path to store the pastes to be analyzed (temporary)")
    parser.add_argument('-o', dest ="output_dir_path", help="Path to store the pastes that accomplished some condition")
    parser.add_argument('-c', dest ="conditions_file_path", help="Path to the YAML conditions file")
    parser.add_argument('-t', dest ="time_to_wait", help="Amount of time (in secs) to wait between each time it goes for new pastes. Suggested and default (180)", default=180)
    parser.add_argument('-n', dest ="amount_of_pastes_to_fetch", help="Amount of pastes to fetch each time it goes for new pastes. Maximun and default is 250", default=250)


    args = parser.parse_args()

    if not args.analysis_dir_path or not args.output_dir_path or not args.conditions_file_path:
        parser.error("Missing arguments")
    
    if not os.path.isfile(args.conditions_file_path):
        parser.error("Conditions file '{}' doesn't exists.".format(args.conditions_file_path))


    pb_orchestrator = Orchestrator(args.downloaders, args.getters, args.analyzers, 
                                           args.storers, args.analysis_dir_path, args.output_dir_path, 
                                           args.conditions_file_path, args.time_to_wait, args.amount_of_pastes_to_fetch)
    pb_orchestrator.big_bang()
