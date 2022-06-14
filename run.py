"""VS Code Python debugger run file
Run file in the root of project directory for execution of simulation with VS Code Python debugger attached.

Create a VS Code launch.json file from the template and place in .vscode/ directory to configure debugger.
"""

from experiments.run import run


if __name__ == '__main__':
    df, _exceptions = run()
    print(df)
