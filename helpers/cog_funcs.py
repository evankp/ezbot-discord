def cog_help(ctx):
    usages = [(c.name, c.brief, c.clean_params) for c in ctx.command.commands]

    help_string = 'Commands: ```'
    for command in usages:
        help_string += f'{command[0]} {[key for key in command[2].keys()]} - {command[1]} \n'

    help_string += '```'

    return help_string
