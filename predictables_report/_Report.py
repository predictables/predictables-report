import copy
from predictables_report._BaseReport import BaseReport
import warnings
from typing import List, Optional
from reportlab.lib.pagesizes import letter  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
from reportlab.lib.units import inch  # type: ignore
from reportlab.platypus import SimpleDocTemplate, Flowable  # type: ignore
from reportlab.platypus.tableofcontents import TableOfContents  # type: ignore


class Report(BaseReport):
    def __init__(
        self,
        filename: str,
        margins: Optional[List[float]] = None,
        pagesize=letter,
        dpi: int = 200,
        include_toc: bool = True,
    ):
        """
        Creates a Report object that can be used to create a pdf document.

        Parameters
        ----------
        filename : str
            The name of the pdf file to create.
        margins : Optional[List[float]], optional
            The margins of the pdf document. Defaults to [0.5, 0.5, 0.5, 0.5]
            if not specified. The order is [left, right, top, bottom], and
            the units are inches.
        pagesize : tuple, optional
            The size of the pages in the pdf document. Defaults to letter
            size if not specified. The units are inches.
        dpi : int, optional
            The dpi of the images in the pdf document. Defaults to 200 if
            not specified.
        include_toc : bool, optional
            Whether to include a table of contents in the pdf document.
            Defaults to True if not specified.

        Returns
        -------
        None. Initializes the Report object, but need to call `build` to
        actually create the pdf document.
        """
        super().__init__()

        self.filename = filename
        self.pagesize = pagesize
        self.dpi = dpi
        self.include_toc = include_toc

        if margins is None:
            margins = [0.5, 0.5, 0.5, 0.5]
        self.doc = SimpleDocTemplate(filename, pagesize=pagesize)
        self.elements: List[Flowable] = []
        self.styles = getSampleStyleSheet()
        self.doc.leftMargin = margins[0] * inch
        self.doc.rightMargin = margins[1] * inch
        self.doc.topMargin = margins[2] * inch
        self.doc.bottomMargin = margins[3] * inch

    def __copy__(self) -> "Report":
        """
        Implements the copy method for the BaseReport class. Used to make a copy of the
        entire report object, including all of its elements.

        """
        new_report = self.__class__(
            filename=f"{self.filename.replace('.pdf', '')}-COPY.pdf"
        )
        new_report.elements = copy.copy(self.elements)

        return new_report

    def copy(self) -> "Report":
        """Implements the copy method for the BaseReport class."""
        return self.__copy__()

    def __deepcopy__(
        self,
    ) -> "Report":
        """Implements the deepcopy method for the BaseReport class."""
        new_report = self.__class__(
            filename=f"{self.filename.replace('.pdf', '')}-COPY.pdf"
        )
        new_report.elements = copy.deepcopy(self.elements)

        return new_report

    def deepcopy(self) -> "Report":
        """Implements the deepcopy method for the BaseReport class."""
        return self.__deepcopy__()

    def set(self, **kwargs):
        """Sets the document properties of the pdf document. Does not by itself make any visible changes to the document."""
        for k, v in kwargs.items():
            if hasattr(self.doc, k):
                setattr(self.doc, k, v)
            else:
                warnings.warn(
                    f"Attribute {k} is not a valid attribute of the document. Ignoring.",
                    SyntaxWarning,
                    stacklevel=2,
                )

        return self

    def footer(self, *args):
        """
        Sets the footer of the pdf document. Every page except for the first page will have this footer, which
        takes the passed args and formats them left to right in the footer.
        """
        # Number of args = number of columns in the footer to divide the page into
        # n_args = len(args)

        return self