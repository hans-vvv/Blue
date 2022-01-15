from lcm_scripts import construct_backbone
from lcm_scripts import create_migration_info
from lcm_scripts import update_sheet_1
from lcm_scripts import create_device_configurations
from lcm_scripts import parse_old_configs
from lcm_scripts import read_excel_data


def main():

    """
    Procedure to generate migration configurations for Life Cycle Management
    of switching equipment in EGL sites.

    :return: None
    """

    filename = 'result.xlsx'
    excel_data = read_excel_data(filename)
    old_config_data = parse_old_configs(excel_data, filename)
    update_sheet_1(old_config_data, filename)
    stackconfigs = construct_backbone(excel_data, filename)
    new_config_data = create_migration_info(
        excel_data, stackconfigs, old_config_data
    )
    create_device_configurations(new_config_data)
    print('Configs generated')


if __name__ == '__main__':
    main()
