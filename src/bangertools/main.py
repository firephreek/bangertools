from typer import Typer

from bangertools.ahf.app import ahf_app
from bangertools.reports.app import app as reports_app
from bangertools.viz.app import app as viz_app

app = Typer()
app.add_typer(viz_app, name="view")
app.add_typer(reports_app, name="report")
app.add_typer(ahf_app, name="ahf")

if __name__ == '__main__':
    app()
