def cite_format(title, authors, year=None, url=None, style="apa"):
    """Format publication metadata as an APA 7 citation."""

    try:
        if not isinstance(style, str) or style.lower() != "apa":
            return {"error": f"Unsupported citation style: {style}. Only 'apa' is supported."}

        if not isinstance(title, str) or not title.strip():
            return {"error": "Title must be a non-empty string."}

        if not isinstance(authors, list) or not authors:
            return {"error": "Authors must be a non-empty list."}

        formatted_authors = []

        for author in authors:
            if not isinstance(author, str) or "," not in author:
                return {"error": f"Invalid author format: {author}. Expected 'Last, First'."}

            last_name, given_names = author.split(",", 1)
            last_name = last_name.strip()
            given_names = given_names.strip()

            if not last_name or not given_names:
                return {"error": f"Invalid author format: {author}."}

            initials = " ".join(
                f"{name[0].upper()}."
                for name in given_names.split()
                if name
            )

            formatted_authors.append(f"{last_name}, {initials}")

        if len(formatted_authors) == 1:
            author_text = formatted_authors[0]
        elif len(formatted_authors) == 2:
            author_text = f"{formatted_authors[0]}, & {formatted_authors[1]}"
        else:
            author_text = ", ".join(formatted_authors[:-1])
            author_text += f", & {formatted_authors[-1]}"

        if year is None:
            year_text = "(n.d.)"
        elif isinstance(year, int) and not isinstance(year, bool):
            year_text = f"({year})"
        else:
            return {"error": "Year must be an integer or None."}

        citation = f"{author_text} {year_text}. {title.strip()}."

        if url is not None:
            if not isinstance(url, str):
                return {"error": "URL must be a string or None."}
            if url.strip():
                citation = citation + f" {url.strip()}"

        return {"citation": citation}

    except Exception as exc:
        return {"error": str(exc)}
