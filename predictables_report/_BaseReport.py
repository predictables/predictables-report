"""
The BaseReport class contains the basic functionality of a report. It is the base class for all other report classes.
"""

import datetime
import itertools
import os
import uuid
import warnings
from typing import List, Optional, Dict

import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore
import pygments  # type: ignore
from reportlab.lib.colors import black, lightgrey, white  # type: ignore
from reportlab.lib.enums import TA_CENTER  # type: ignore
from reportlab.lib.pagesizes import inch  # type: ignore
from reportlab.lib.styles import ParagraphStyle  # type: ignore
from reportlab.platypus import Image  # type: ignore
from reportlab.platypus import PageBreak  # type: ignore
from reportlab.platypus import Paragraph  # type: ignore
from reportlab.platypus import Spacer  # type: ignore
from reportlab.platypus import Table  # type: ignore
from reportlab.platypus import TableStyle  # type: ignore
from reportlab.platypus.flowables import Flowable  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet  # type: ignore


class BaseReport:
    elements: List[Flowable]
    styles: ParagraphStyle
    links: Dict[uuid.UUID, Dict[str, str]]
    names: Dict[str, uuid.UUID]

    def __init__(
        self,
    ) -> None:
        """
        Initializes the BaseReport object.

        Parameters
        ----------
        None

        Returns
        -------
        None. Initializes the BaseReport object.
        """

        self.elements: List[Flowable] = []
        self.styles = getSampleStyleSheet()
        self.links: Dict[uuid.UUID, Dict[str, str]] = {}
        self.names: Dict[str, uuid.UUID] = {}  # name to ref lookup

    def style(self, tag, **kwargs):
        """
        Styles the pdf document by updating the stylesheet with the keyword
        arguments passed in. This is used to change the font family, font
        size, etc. of the document."""
        for k, v in kwargs.items():
            if hasattr(self.styles.get(tag), k):
                setattr(self.styles.get(tag), k, v)
            else:
                warnings.warn(
                    f"Attribute {k} is not a valid attribute of the stylesheet. Ignoring.",
                    SyntaxWarning,
                    stacklevel=2,
                )

        return self

    def _add(
        self,
        element: Flowable,
        name: Optional[str] = None,
        ref: Optional[uuid.UUID] = None,
    ):
        """
        Adds an element to the report. This is a private method and should not be
        called directly. Instead, use one of the public methods like `p`, `h1`, etc,
        which call this method under the hood.

        Parameters
        ----------
        element : Flowable
            The element to add to the report.
        name : Optional[str], optional
            Optionally defines a human-readable name for the element, by default None. If
            provided, can be used to reference the element later.
        ref : Optional[uuid.UUID], optional
            The reference of the element to add to the report, by default None. If no reference
            is provided, a new one will be generated.

        Returns
        -------
        None. Adds an element to the report.
        """
        self.elements.append(element)

        # Update the links and names dictionaries
        if ref is not None:
            self.links[ref] = {"element": element}
            if name is not None:
                self.links[ref]["name"] = name
                self.names[name] = ref
            else:
                self.links[ref]["name"] = str(ref)

    def heading(
        self,
        level: int,
        text: str,
        return_self: bool = True,
        name: Optional[str] = None,
        ref: Optional[uuid.UUID] = None,
    ) -> Optional["BaseReport"]:
        """
        Adds a heading to the document that says, `text`. The heading is
        styled according to the level passed in.

        Parameters
        ----------
        level : int
            The level of the heading. Must be between 1 and 6, inclusive.
        text : str
            The text to display in the heading.
        return_self : bool, optional
            Whether or not to return the Report object itself. If True,
            returns the Report object itself. If False, returns None.
            Defaults to True.
        name : Optional[str], optional
            Optionally defines a human-readable name for the element, by default None. If
            provided, can be used to reference the element later.
        ref : Optional[uuid.UUID], optional
            The reference of the element to add to the report, by default None. If no reference
            is provided, a new one will be generated.


        Returns
        -------
        Optional[Report]
            The current Report object. This method should be called in a
            chain.
        """
        if level not in range(1, 7):
            raise ValueError(f"Level must be between 1 and 6, inclusive. Got {level}.")

        if ref is None:
            ref = uuid.uuid4()

        self._add(Paragraph(text, self.styles[f"Heading{level}"]), name, ref)
        return self if return_self else None

    def h1(
        self,
        text: str,
        element_id: Optional[str] = None,
        name: Optional[str] = None,
        ref: Optional[uuid.UUID] = None,
    ) -> "BaseReport":
        """
        Adds a h1-style heading to the document that says, `text`. If an `element_id`
        is passed, creates a bookmark location to return to with an inner link.

        Parameters
        ----------
        text : str
            The text to display in the heading.
        element_id : str, optional
            The id of the element to link to, by default None
        name : Optional[str], optional
            Optionally defines a human-readable name for the element, by default None. If
            provided, can be used to reference the element later.
        ref : Optional[uuid.UUID], optional
            The reference of the element to add to the report, by default None. If no reference
            is provided, a new one will be generated.


        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        heading : Adds a heading to the document that says, `text`.

        Examples
        --------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .h1("This is a heading.")
        ...     .h1("This is another heading.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with two headings.

        >>> (
        ...    Report("test_with_bookmark.pdf")
        ...     .h1("This is a heading.", element_id="test")
        ...     .h1("This is another heading.")
        ...     .inner_link("Go to the first heading", "test")
        ...     .build()
        ... ) # Will create a pdf called test_with_bookmark.pdf with two
              # headings and a link at the end pointing to the first
              # heading.
        """
        # Add element to chain
        self.heading(1, text, return_self=False, name=name, ref=ref)

        # Create bookmark, if necessary
        if element_id is not None:
            self.elements[-1].addBookmark(element_id, relative=1, level=0)
        return self

    def h2(self, text: str, element_id: Optional[str] = None) -> "BaseReport":
        """
        Adds a h2-style heading to the document that says, `text`. If an `element_id`
        is passed, creates a bookmark location to return to with an inner link.

        Parameters
        ----------
        text : str
            The text to display in the heading.
        element_id : str, optional
            The id of the element to link to, by default None

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        heading : Adds a heading to the document that says, `text`.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .h1("Top-level heading.")
        ...     .h2("Second-level heading.")
        ...     .h3("Third-level heading.")
        ...     .h4("Fourth-level heading.")
        ...     .h5("Fifth-level heading.")
        ...     .h6("Sixth-level heading.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with six headings.
        """
        # Add element to chain
        self.heading(2, text, return_self=False)

        # Create bookmark, if necessary
        if element_id is not None:
            self.elements[-1].addBookmark(element_id, relative=1, level=0)
        return self

    def h3(self, text: str, element_id: Optional[str] = None) -> "BaseReport":
        """
        Adds a h3-style heading to the document that says, `text`. If an `element_id`
        is passed, creates a bookmark location to return to with an inner link.

        Parameters
        ----------
        text : str
            The text to display in the heading.
        element_id : str, optional
            The id of the element to link to, by default None

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        heading : Adds a heading to the document that says, `text`.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .h1("Top-level heading.")
        ...     .h2("Second-level heading.")
        ...     .h3("Third-level heading.")
        ...     .h4("Fourth-level heading.")
        ...     .h5("Fifth-level heading.")
        ...     .h6("Sixth-level heading.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with six headings.
        """
        # Add element to chain
        self.heading(3, text, return_self=False)

        # Create bookmark, if necessary
        if element_id is not None:
            self.elements[-1].addBookmark(element_id, relative=1, level=0)
        return self

    def h4(self, text: str, element_id: Optional[str] = None) -> "BaseReport":
        """
        Adds a h4-style heading to the document that says, `text`. If an `element_id`
        is passed, creates a bookmark location to return to with an inner link.

        Parameters
        ----------
        text : str
            The text to display in the heading.
        element_id : str, optional
            The id of the element to link to, by default None

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        heading : Adds a heading to the document that says, `text`.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .h1("Top-level heading.")
        ...     .h2("Second-level heading.")
        ...     .h3("Third-level heading.")
        ...     .h4("Fourth-level heading.")
        ...     .h5("Fifth-level heading.")
        ...     .h6("Sixth-level heading.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with six headings.
        """
        # Add element to chain
        self.heading(4, text, return_self=False)

        # Create bookmark, if necessary
        if element_id is not None:
            self.elements[-1].addBookmark(element_id, relative=1, level=0)
        return self

    def h5(self, text: str, element_id: Optional[str] = None) -> "BaseReport":
        """
        Adds a h5-style heading to the document that says, `text`. If an `element_id`
        is passed, creates a bookmark location to return to with an inner link.

        Parameters
        ----------
        text : str
            The text to display in the heading.
        element_id : str, optional
            The id of the element to link to, by default None

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        heading : Adds a heading to the document that says, `text`.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .h1("Top-level heading.")
        ...     .h2("Second-level heading.")
        ...     .h3("Third-level heading.")
        ...     .h4("Fourth-level heading.")
        ...     .h5("Fifth-level heading.")
        ...     .h6("Sixth-level heading.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with six headings.
        """
        # Add element to chain
        self.heading(5, text, return_self=False)

        # Create bookmark, if necessary
        if element_id is not None:
            self.elements[-1].addBookmark(element_id, relative=1, level=0)
        return self

    def h6(self, text: str, element_id: Optional[str] = None) -> "BaseReport":
        """
        Adds a h6-style heading to the document that says, `text`. If an `element_id`
        is passed, creates a bookmark location to return to with an inner link.

        Parameters
        ----------
        text : str
            The text to display in the heading.
        element_id : str, optional
            The id of the element to link to, by default None

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        heading : Adds a heading to the document that says, `text`.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .h1("Top-level heading.")
        ...     .h2("Second-level heading.")
        ...     .h3("Third-level heading.")
        ...     .h4("Fourth-level heading.")
        ...     .h5("Fifth-level heading.")
        ...     .h6("Sixth-level heading.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with six headings.
        """
        # Add element to chain
        self.heading(6, text, return_self=False)

        # Create bookmark, if necessary
        if element_id is not None:
            self.elements[-1].addBookmark(element_id, relative=1, level=0)
        return self

    def p(self, text: str) -> "BaseReport":
        """
        Adds a paragraph to the document that says, `text`.

        Parameters
        ----------
        text : str
            The text to display in the paragraph.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        text : Alias for `p`. Adds a paragraph to the document that says, `text`.
        paragraph : Alias for `p`. Adds a paragraph to the document that says, `text`.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .p("This is a paragraph.")
        ...     .p("This is another paragraph.")
        ...     .text("This is a third paragraph with a different method.")
        ...     .paragraph("This is a fourth paragraph with a different method.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with four paragraphs that are
              # all the same, even though they were created with different methods.
        """
        # Add element to chain
        self.elements.append(Paragraph(text, self.styles["Normal"]))
        return self

    def text(self, text: str) -> "BaseReport":
        """
        Alias for `p`. Adds a paragraph to the document that says, `text`.

        Parameters
        ----------
        text : str
            The text to display in the paragraph.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        p : `text` is an alias for `p`. Adds a paragraph to the document that says, `text`.
        paragraph : Another alias for `p`. Adds a paragraph to the document that says, `text`.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .p("This is a paragraph.")
        ...     .p("This is another paragraph.")
        ...     .text("This is a third paragraph with a different method.")
        ...     .paragraph("This is a fourth paragraph with a different method.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with four paragraphs that are
              # all the same, even though they were created with different methods.
        """
        return self.p(text)

    def paragraph(self, text: str) -> "BaseReport":
        """
        Alias for `p`. Adds a paragraph to the document that says, `text`.

        Parameters
        ----------
        text : str
            The text to display in the paragraph.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        p : `text` is an alias for `p`. Adds a paragraph to the document that says, `text`.
        paragraph : Another alias for `p`. Adds a paragraph to the document that says, `text`.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .p("This is a paragraph.")
        ...     .p("This is another paragraph.")
        ...     .text("This is a third paragraph with a different method.")
        ...     .paragraph("This is a fourth paragraph with a different method.")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with four paragraphs that are
              # all the same, even though they were created with different methods.
        """
        return self.p(text)

    def inner_link(self, text: str, inner_link: str):
        """
        Creates a link to a defined inner location in the document. The link will say
        `text` and link to the inner location `inner_link`.

        Parameters
        ----------
        text : str
            The text to display in the link.
        inner_link : str
            The id of the element to link to.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        Raises
        ------
        ValueError
            If the inner_link does not exist.

        Notes
        -----
        1. The inner_link need not be defined before the link is created. However,
           the inner_link must be defined before the pdf is built.
        2. The inner_link is styled as a hyperlink, so it will be blue and underlined.
        """
        # Check if inner_link exists
        if inner_link not in self.doc._namedDests:
            raise ValueError(
                f"inner_link {inner_link} does not exist. Please define it before using it."
            )

        # Add element to chain
        self.elements.append(
            Paragraph(f'<a href="#{inner_link}">{text}</a>', self.styles["Hyperlink"])
        )
        return self

    def ul(self, text: List[str], bullet_char: str = "\u2022") -> "BaseReport":
        """
        Adds an unordered list to the document. For each item in `text`, a
        bullet point is added to the list. If a different bullet point
        character is desired, it can be passed in as `bullet_char`. Will
        default to the unicode bullet point character.

        Parameters
        ----------
        text : List[str]
            The items to add to the list.
        bullet_char : str, optional
            The character to use for the bullet point, by default "\u2022"
            (bullet point in unicode)

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        ol : Adds an ordered list to the document. For each item in `text`, an
             item number is added to the list.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .ul(["Item 1", "Item 2", "Item 3"])
        ...     .build()
        ... ) # Will create a pdf called test.pdf with an unordered list with three items.
        """
        for t in text:
            self.elements.append(Paragraph(f"{bullet_char} {t}", self.styles["Normal"]))
        return self

    def _number_style(self, n: int, style: str):
        """
        Returns an iterator of numbers in the given style.

        Parameters
        ----------
        n : int
            The number of numbers to return.
        style : str
            The style of the numbers. Must be one of "decimal", "lower-roman", "upper-roman", "lower-alpha", or "upper-alpha".

        Returns
        -------
        Iterator[str]
            An iterator of numbers in the given style.
        """

        def decimal_to_roman(number, is_upper=True):
            roman_symbols = [
                (1000, "M"),
                (900, "CM"),
                (500, "D"),
                (400, "CD"),
                (100, "C"),
                (90, "XC"),
                (50, "L"),
                (40, "XL"),
                (10, "X"),
                (9, "IX"),
                (5, "V"),
                (4, "IV"),
                (1, "I"),
            ]

            result = ""
            for value, symbol in roman_symbols:
                while number >= value:
                    result += symbol if is_upper else symbol.lower()
                    number -= value

            return result

        def decimal_to_abc(number, is_upper=True):
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

            result = ""
            while number > 0:
                number -= 1
                result += (
                    alphabet[number % 26] if is_upper else alphabet[number % 26].lower()
                )
                number //= 26

            return result[::-1]

        decimal_numb = itertools.count(1)

        if style == "decimal":
            return decimal_numb
        elif style == "lower-roman":
            return map(lambda x: decimal_to_roman(x, False), decimal_numb)
        elif style == "upper-roman":
            return map(lambda x: decimal_to_roman(x, True), decimal_numb)
        elif style == "lower-alpha":
            return map(lambda x: decimal_to_abc(x, False), decimal_numb)
        elif style == "upper-alpha":
            return map(lambda x: decimal_to_abc(x, True), decimal_numb)
        else:
            raise ValueError(f"Style {style} is not a valid number style.")

    def ol(self, text: List[str], number_style: str = "decimal") -> "BaseReport":
        """
        Adds an ordered list to the document. For each item in `text`, an item
        number is added to the list. If a different number style is desired, it
        can be passed in as `number_style`. Will default to the decimal number
        style.

        Parameters
        ----------
        text : List[str]
            The items to add to the list.
        number_style : str, optional
            The style to use for the item numbers, by default "decimal", but also
            accepts "lower-roman", "upper-roman", "lower-alpha", and "upper-alpha".

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        ul : Adds an unordered list to the document. For each item in `text`, a
             bullet point is added to the list.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .ol(["Item 1", "Item 2", "Item 3"])
        ...     .build()
        ... ) # Will create a pdf called test.pdf with an ordered list with three items.
        """
        styled_numbers = self._number_style(len(text), number_style)
        for t in text:
            self.elements.append(
                Paragraph(f"{next(styled_numbers)}. {t}", self.styles["Normal"])
            )
        return self

    def code(self, text: str, language: Optional[str] = None) -> "BaseReport":
        """
        Adds a code block to the document. Used for displaying code snippets.

        Parameters
        ----------
        text : str
            The code to display in the code block.
        language : str, optional
            The language of the code, by default None. If a language is provided,
            it must be one of "py", "r", "c", "cpp", "java", "js", "html", "css",
            "xml", "json", "yaml", "sql", "bash", "sh", "powershell", "dockerfile",
            "makefile", "cmake", "latex", "markdown", "plaintext", None. This
            functionality is provided by the Pygments library.

            Note that passing no language to this argument is functionally
            equivalent to passing "plaintext", in that either way a plaintext
            code block with no syntax highlighting will be generated.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        See Also
        --------
        math : Adds a math block to the document. Used for displaying math equations.

        Example
        -------
        >>> from predictables.util import Report
        >>> (
        ...    Report("test.pdf")
        ...     .code("print('Hello, world!')")
        ...     .build()
        ... ) # Will create a pdf called test.pdf with a plaintext code block that
              # says print('Hello, world!')

        >>> (
        ...    Report("test-python.pdf")
        ...     .code("print('Hello, world!')", language="py")
        ...     .build()
        ... ) # Will create a pdf called test-python.pdf with a python code block
              # that says print('Hello, world!'), and will be syntax highlighted
              # as python code.
        """
        if language is None:
            self.elements.append(Paragraph(text, self.styles["Code"]))
        else:
            self.elements.append(
                Paragraph(
                    pygments.highlight(
                        text, pygments.lexers.get_lexer_by_name(language)
                    ),
                    self.styles["Code"],
                )
            )
        return self

    def math(self, mathjax: str):
        """Adds a math block to the document. Used for displaying math equations."""
        self.elements.append(Paragraph(mathjax, self.styles["Math"]))
        return self

    def spacer(self, height: float):
        """
        Adds vertical space to the document. Used for adding additional margin
        between elements in the document. Height is in inches.

        Parameters
        ----------
        height : float
            The height of the spacer in inches.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        Example
        -------
        >>> (Report("test.pdf")
                .p("This is a paragraph that needs some space.")
                .spacer(1)
                .p("This is another paragraph that is 1 inch below the first.")
                .build()
            )

        """
        self.elements.append(Spacer(1, height * inch))
        return self

    def image(self, filename: str, width: float = 7, height: float = 7):
        """
        Adds an image to the document. Used to add a saved image to the
        document. Width and height are in inches.

        Parameters
        ----------
        filename : str
            The filename of the image to add.
        width : float
            The width of the image in inches.
        height : float
            The height of the image in inches.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        Example
        -------
        >>> report = Report("test.pdf")
        >>> report.image("test.png", 6, 4).build()
        """
        self.elements.append(Image(filename, width * inch, height * inch))
        return self

    def plot(self, func, width: float = 7, height: float = 7):
        """
        Adds a plot to the document. The plot is generated by the provided
        callable `func`. The plot is saved as a temporary image file and then
        added to the PDF document.

        Parameters
        ----------
        func : callable
            A function that generates and returns a matplotlib plot.
        width : float, optional
            Width of the plot in inches.
        height : float, optional
            Height of the plot in inches.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        Example
        -------
        >>> def my_plot():
        ...     fig, ax = plt.subplots()
        ...     ax.plot([1, 2, 3], [1, 4, 9])
        ...     return fig, ax

        >>> report = Report("test.pdf")
        >>> report.plot(my_plot, 6, 4, "Example plot").build()
        """
        temp_filename = f"temp_plot_{uuid.uuid4()}.png"

        # Generate the plot and save it as a temporary file
        ax = func()
        fig = ax.get_figure()
        fig.savefig(temp_filename, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)

        # Add the plot image to the report
        self = self.image(temp_filename, width, height)

        return self

    def page_break(self):
        """Adds a page break to the document. Used for adding a page break to the document."""
        self.elements.append(PageBreak())
        return self

    def caption(self, text: str, width: float = 7):
        """
        Adds a caption to the document. The caption is centered and has no top
        margin or padding.

        Parameters
        ----------
        text : str
            The text to display as a caption.
        width : float, optional
            The width of the plot/image/table/etc that the caption is for,
            by default 6. This is used to ensure the caption is centered
            under the plot.

        Returns
        -------
        Report
            The current Report object. This method should be called in a chain.

        Example
        -------
        >>> report = Report("test.pdf")
        >>> report.caption("This is a caption.").build()
        """

        # Calculate the left and right margins to center the caption under the plot
        page_width = self.pagesize[0] / inch  # Convert page width to inches
        total_margin = page_width - width
        left_margin = total_margin / 2  # Equal margins on both sides

        # Define a custom style for the caption
        caption_style = ParagraphStyle(
            "CaptionStyle",
            parent=self.styles["Normal"],
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
            leftIndent=left_margin * inch,
            rightIndent=left_margin * inch,
            fontSize=10,  # Adjust font size as needed
        )

        # Add the caption to the report
        self.elements.append(Paragraph(text, caption_style))

        return self

    def table(
        self,
        df: pd.DataFrame,
        style: TableStyle = None,
    ):
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"`df` must be a pandas DataFrame, but got {type(df)}.")

        def create_table_style(font: str = "Helvetica", fontsize: int = 10):
            style = TableStyle(
                [
                    # Background color of the first row
                    ("BACKGROUND", (0, 0), (-1, 0), lightgrey),
                    # Text color of the first row
                    ("TEXTCOLOR", (0, 0), (-1, 0), black),
                    # Font style of the first row
                    ("FONTNAME", (0, 0), (-1, 0), f"{font}-Bold"),
                    # Font size of the first row
                    ("FONTSIZE", (0, 0), (-1, 0), fontsize),
                    # Double line under the first row
                    ("LINEBELOW", (0, 0), (-1, 0), 1, black),
                    # Background color of the remaining rows
                    ("BACKGROUND", (0, 1), (-1, -1), white),
                    # Text color of the remaining rows
                    ("TEXTCOLOR", (0, 1), (-1, -1), black),
                    # Font style of the remaining rows
                    ("FONTNAME", (0, 1), (-1, -1), f"{font}"),
                    # Font size of the remaining rows
                    ("FONTSIZE", (0, 1), (-1, -1), fontsize),
                    # Single line under the remaining rows
                    ("LINEBELOW", (0, 1), (-1, -1), 1, black),
                    # Single line above the remaining rows
                    ("LINEABOVE", (0, 1), (-1, -1), 0.5, black),
                    # Single line before the first column
                    ("LINEBEFORE", (0, 0), (0, -1), 1, black),
                    # Background color of the first column
                    ("BACKGROUND", (0, 0), (0, -1), lightgrey),
                    # Text color of the first column
                    ("TEXTCOLOR", (0, 0), (0, -1), black),
                    # Font style of the first column
                    ("FONTNAME", (0, 0), (0, -1), f"{font}-Bold"),
                    # Font size of the first column
                    ("FONTSIZE", (0, 0), (0, -1), fontsize),
                    # Single line after the last column:
                    ("LINEAFTER", (-1, 0), (-1, -1), 1, black),
                    # Single line before the first column:
                    ("LINEBEFORE", (0, 0), (0, -1), 1, black),
                    # Thick black line around the entire table
                    ("BOX", (0, 0), (-1, -1), 2, black),
                ]
            )
            return style

        if style is None:
            style = create_table_style()

        data = [[""] + df.columns.tolist()] + [
            [df.index.tolist()[i]] + df.values.tolist()[i]
            for i, _ in enumerate(df.values.tolist())
        ]
        t = Table(data)
        if style is not None:
            t.setStyle(style)
        self.elements.append(t)
        return self

    def build(self):
        """Builds the pdf document and saves it to the filename specified in the constructor. This is the final command that must be called to generate the pdf document."""
        self.doc.build(self.elements)

        # Remove temporary plot files
        for file in os.listdir():
            if file.startswith("temp_plot_"):
                os.remove(file)

    def title(self, text: str):
        """Sets the title metadata attribute of the pdf document. Does not by itself make any visible changes to the document."""
        self.doc.title = text
        return self

    def author(self, text: str):
        """Sets the author metadata attribute of the pdf document. Does not by itself make any visible changes to the document."""
        self.doc.author = text
        return self

    def subject(self, text: str):
        """Sets the subject metadata attribute of the pdf document. Does not by itself make any visible changes to the document."""
        self.doc.subject = text
        return self

    def date(self, date: Optional[datetime.date] = None):
        """Sets the date metadata attribute of the pdf document. Does not by itself make any visible changes to the document."""
        if date is None:
            date = datetime.datetime.now()

        self.doc.date = date.strftime("%Y-%m-%d")

    def date_(self, date: Optional[datetime.date] = None) -> str:
        """Alias for `date`, it returns the date added to the document metadata. This allows you to ensure they are the same."""
        self.date(date)
        return self.doc.date

    def keywords(self, text: str):
        """Sets the keywords metadata attribute of the pdf document. Does not by itself make any visible changes to the document."""
        self.doc.keywords = text
        return self
