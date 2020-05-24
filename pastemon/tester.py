import yaml
from condition import StringCondition, RegexCondition
from constants import NAME, STRING, REGEX
from argparse import ArgumentParser
    
def _match_conditions(conditions, pastebin_content):
    """
        If it matches some of the conditions provided, then is because we believe it could be 
        somehow an interesting paste
    """
    matched_conditions_names = []
    for line in pastebin_content.split('\n'):
        for condition in conditions:
            if condition.condition_name() not in matched_conditions_names:
                if len(matched_conditions_names) == len(conditions):
                    return matched_conditions_names
                else:
                    if condition.match(line):
                        matched_conditions_names.append(condition.condition_name())

    return matched_conditions_names

def help():
    return "Pastemon tester - Easy script to quickly test if a pastebin will match against defined condition\n"

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c",dest="conditions_yaml_file", help="Path to the conditions YAML file")
    parser.add_argument("-p",dest="pastebin_file", help="Path to the pastebin file to test")
    args = parser.parse_args()

    if not args.conditions_yaml_file or not args.pastebin_file:
        parser.error("Missing arguments")

    conditions = []
    with open(args.conditions_yaml_file) as f:
        yaml_conditions = yaml.safe_load(f)

    for condition_name, condition_properties in yaml_conditions.items():
        condition_properties.update({NAME:condition_name})
        if STRING in condition_properties:
            conditions.append(StringCondition(**condition_properties))
        elif REGEX in condition_properties:
            conditions.append(RegexCondition(**condition_properties))


    with open(args.pastebin_file) as f:
        pastebin_content = f.read()

    print("Conditions matched:")
    for condition_name in (_match_conditions(conditions, pastebin_content)):
        print ("\t- {}".format(condition_name))

