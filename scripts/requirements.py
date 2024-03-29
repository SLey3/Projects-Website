# Imports
from subprocess import PIPE, TimeoutExpired
import re
import os 
import subprocess
import click
import sys

# Command Utils
@click.group()
def cli():
    pass

def moduleInstall():
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')   
    click.secho("Installing modules...", fg="yellow")
    process = subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--no-warn-script-location'], stdin=PIPE, stdout=sys.stdout, stderr=PIPE)   
    click.echo(process.stdout)
    click.secho("Successfully installed modules", fg="green", underline=True)
    
def install_lighthouse():
    click.secho("Installing lighthouse...", fg="yellow")
    os.system("npm install -g lighthouse")
    click.secho("lighthouse installed", fg="green")

def installCallback(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    moduleInstall()
    ctx.exit()
    
def lighthouseInstallCallback(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    install_lighthouse()
    ctx.exit()
    

@click.command(help="Updates Requirements file")
@click.option("--install", expose_value=False, is_flag=True, callback=installCallback, help="install all modules")
@click.option("--install-lighthouse", expose_value=False, is_flag=True, callback=lighthouseInstallCallback, help="install lighthouse from npm")
@click.option("-u", nargs=1, default=None, help="upgrades module")
def update(u):
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')
    if u:
        command = subprocess.Popen(["pip", "install", "-U", f"{u}"], stdin=PIPE, stdout=sys.stdout, stderr=PIPE)
        try:
            outs, errs = command.communicate(timeout=9)
        except TimeoutExpired:
            command.kill()
        else:
            click.echo(errs)
        click.secho(f"{u} updated succesfully", fg="green")
        return
    command = subprocess.Popen(["pip-compile", "requirements.in"], stdin=PIPE, stdout=sys.stdout, stderr=PIPE, encoding="utf-8")
    try:
        outs, errs = command.communicate(timeout=9)
    except TimeoutExpired:
        command.kill()
    else: 
        click.echo(errs)
        click.secho("requirements file updated", fg="green")
    
@click.command(help="Adds specified module to in file")
@click.argument("module", nargs=1, type=str, required=True)
@click.option("--version", nargs=1, default=None, help="version of module")
@click.option("--greaterthan", is_flag=True, help=">= in requirements file")
def add_to_in_file(module, version, greaterthan):
    click.secho(f"Adding {module} to requirements.in...", fg="yellow")
    if version:
        if os.path.basename(os.getcwd()) == 'script':
            os.chdir('..')
        with open('requirements.in', 'a', encoding='utf-8') as r:
            if greaterthan:
                r.write(f"\n{module}>={version}")
            else:
                r.write(f"\n{module}=={version}")
    else:
        if os.path.basename(os.getcwd()) == 'script':
            os.chdir('..')
        with open('requirements.in', 'a', encoding='utf-8') as r:
            r.write(f"\n{module}")
    click.secho(f"Module {module} has been added to requirements.in", fg="green")
    
    
def un_install():
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')
    with open('requirements.in', 'r', encoding='utf-8') as r:
        lines = r.readlines()
    for line in lines:
        sub_line = re.sub(r"==[0-9.a-zA-Z]+", '', line)
        if sub_line == "click":
            continue
        else:
            click.secho(f"Uninstalling: {sub_line}...", fg="yellow")
            process = subprocess.run(['pip', 'uninstall', sub_line, '-y'], stdin=PIPE, stdout=sys.stdout, stderr=PIPE)
            click.echo(process.stdout)
            click.secho(f"Successfully uninstalled: {sub_line}", fg="green")
    
def uninstallCallback(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.secho("Uninstalling all modules...", fg="red", underline=True, bold=True)
    un_install()    
    click.secho("Operation Sucessful", fg="green")
    ctx.exit()
    
def uninstallLighthouseCallback(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.secho("Uninstalling lighthouse...", fg="red")
    os.system("npm uninstall -g lighthouse")
    click.secho("Successfully uninstalled lighthouse", fg="green")
    ctx.exit()
    
@click.command(help="uninstalls specified module")
@click.argument("module", nargs=-1, type=str, required=False)    
@click.option("-A", "-a", expose_value=False, is_flag=True, callback=uninstallCallback, help="Uninstalls all modules")
@click.option("--lighthouse", expose_value=False, is_flag=True, callback=uninstallLighthouseCallback, help="Uninstalls lighthouse with npm")
def uninstall(module):
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')
    with open('requirements.in', 'r', encoding="utf-8") as r:
        lines = r.readlines()
    with open('requirements.in', 'w', encoding="utf-8") as r:
        for line in lines:
            subbed_line = re.sub(r"==[0-9.a-zA-Z]+", '', line)
            if subbed_line.strip() not in module:
                r.write(line)
    command = subprocess.Popen(["pip-compile", "requirements.in"], stdin=PIPE, stdout=sys.stdout, stderr=PIPE)
    try:
        outs, errs = command.communicate(timeout=9)
    except TimeoutExpired:
        command.kill()
    else:
        click.echo(errs)
        
    for m in module:
        click.secho(f"Uninstalling: {m}...", fg="red")
        command = subprocess.Popen(["pip", "uninstall", m, "-y"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            outs, errs = command.communicate(timeout=7)
        except TimeoutExpired:
            command.kill()
        else:
            click.echo(errs)
        click.secho(f"Successfully uninstalled: {m}", fg="green")



@click.command(help="view the requirements.txt file")
def view():
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')   
        
    with open('requirements.txt', 'r', encoding="utf-8") as r:
        lines = r.readlines()
        
    for line in lines:
        click.echo(line)
    
# Command Script
if __name__ == "__main__":
    cli.add_command(update, "update")
    cli.add_command(add_to_in_file, "add")
    cli.add_command(uninstall, "uninstall")
    cli.add_command(view)
    cli()
    