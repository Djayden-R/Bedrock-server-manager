from dotenv import set_key

variables_to_save = []

#add example credentials here please
variables_to_save.append(("HOME_ASSISTANT_IP", "192.168.1.100"))
variables_to_save.append(("HOME_ASSISTANT_TOKEN", "your_home_assistant_token"))
variables_to_save.append(("DYNU_PASSWORD", "your_dynu_password"))
variables_to_save.append(("DYNU_DOMAIN", "your_dynu_domain"))
variables_to_save.append(("GITHUB_TOKEN", "your_github_token"))

for variable in variables_to_save:
    variable_name = variable[0]
    value = variable[1]
    set_key(".env", variable_name, value)
