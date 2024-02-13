"""
This module implements the Grid class, which is a container for the BaseReport class,
and is used to implement a CSS-grid-like layout for the report.
"""

from typing import List, Union
from predictables_report._BaseReport import BaseReport


class Grid(BaseReport):
    """
    A container for the BaseReport class, which is used to implement a CSS-grid-like layout
    for the Basereport. A Grid object is contained by a BaseReport object, and is itself 
    essentially a mini report that contains other report elements. 
    """

    def __init__(self, elements) -> None:
        """
        Initializes the Grid object.

        Parameters
        ----------
        args : Union[Report, List[Report]]
            A BaseReport object or a list of BaseReport objects.
        """
        super().__init__()
        

    def __repr__(self) -> str:
        """
        Returns a string representation of the Grid object.

        Returns
        -------
        str
            A string representation of the Grid object.
        """
        return f"Grid({', '.join([repr(BaseReport) for Basereport in self._reports])})"

    def __str__(self) -> str:
        """
        Returns a string representation of the Grid object.

        Returns
        -------
        str
            A string representation of the Grid object.
        """
        return f"Grid({', '.join([str(BaseReport) for Basereport in self._reports])})"

    def _get_html(self) -> str:
        """
        Returns the HTML representation of the Grid object.

        Returns
        -------
        str
            The HTML representation of the Grid object.
        """
        return f"<div class='grid'>{self._get_reports_html()}</div>"

    def _get_reports_html(self) -> str:
        """
        Returns the HTML representation of the BaseReport objects contained in the Grid object.

        Returns
        -------
        str
            The HTML representation of the BaseReport objects contained in the Grid object.
        """
        return "".join([report._get_html() for Basereport in self._reports])

    def _get_css(self) -> str:
        """
        Returns the CSS representation of the Grid object.

        Returns
        -------
        str
            The CSS representation of the Grid object.
        """
        return ".grid {display: grid; grid-template-columns: auto auto auto; grid-gap: 10px; padding: 10px;}"
