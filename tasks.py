from invoke import task

@task
def install(c):
    c.run("pip install -e .[dev,test]", echo=True)