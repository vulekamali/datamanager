def get_items(financial_year):
    return [
        {"id": "homepage", "title": "Home", "url": "/"},
        {
            "id": "departments",
            "title": "Department Budgets",
            "url": "/%s/departments" % financial_year,
        },
        {
            "id": "learning-centre",
            "title": "Learning",
            "url": "/learning-resources",
            "subLinks": True,
            "children": [
                {
                    "title": "Videos",
                    "id": "videos",
                    "url": "/learning-resources/videos",
                },
                {
                    "title": "Glossary",
                    "id": "glossary",
                    "url": "/learning-resources/glossary",
                },
                {
                    "title": "Resources",
                    "id": "resources",
                    "url": "/learning-resources/resources",
                },
                {
                    "title": "Dataset Guides",
                    "id": "guides",
                    "url": "/learning-resources/guides",
                },
            ],
        },
        {
            "id": "infrastructure",
            "title": "Infrastructure",
            "url": None,
            "is_dropdown": True,
            "children": [
                {
                    "title": "National",
                    "url": "/infrastructure-projects/",
                    "id": "national",
                },
                {
                    "title": "Provincial",
                    "url": "/infrastructure-projects/provincial/",
                    "id": "provincial",
                },
            ],
        },
        {"id": "datasets", "title": "Data and Analysis", "url": "/datasets"},
        {
            "id": "about",
            "title": "About",
            "url": "/about",
            "align": "right",
            "subLinks": True,
            "children": [
                {
                    "title": "Background",
                    "url": "/about#background",
                    "connected": "background",
                },
                {
                    "title": "Development",
                    "url": "/about#development",
                    "connected": "development",
                },
                {
                    "title": "Project Status",
                    "url": "/about#project-status",
                    "connected": "project-status",
                },
                {
                    "title": "Your Contribution",
                    "url": "/about#your-contribution",
                    "connected": "your-contribution",
                },
                {"title": "Contacts", "url": "about#contacts", "connected": "contacts"},
                {
                    "title": "Media & Other Information",
                    "url": "/about#media-and-other-information",
                    "connected": "media-and-other-information",
                },
                {
                    "title": "Information for Developers and Data Scientists",
                    "url": "/about#data-scientists",
                    "connected": "data-scientists",
                },
            ],
        },
        {"id": "faq", "title": "FAQ", "url": "/faq", "align": "right"},
    ]
